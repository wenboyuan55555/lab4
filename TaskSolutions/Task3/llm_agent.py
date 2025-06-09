import sys
import os
import json
import asyncio
from dataclasses import dataclass
from typing import List, Dict, Any, Literal
import traceback

# 定义配置变量
BASE_URL = "https://api.chatfire.cn/v1"
API_KEY = "sk-zO8exlBicZh7nJeZn5GuC5X9SPuVrZzXoGyOW0i9BFvN62ON"
MODEL_NAME = "gpt-4o"

# 需求建模相关的提示词
REQUIREMENT_PROMPT = """
作为一个需求建模专家，请基于以下ATM系统描述，生成完整的需求模型，包括：
1. 用例图：识别主要参与者和用例，并定义它们之间的关系
2. 系统顺序图：为每个主要用例创建系统顺序图
3. 概念类图：识别系统中的主要类、它们的属性和关系
4. OCL合约：为关键操作提供OCL合约

ATM（自动取款机）系统描述：
ATM系统允许银行客户进行基本的银行交易，如查询账户余额、取款、存款和转账。
客户必须使用银行卡和个人识别码（PIN）登录系统。
系统会验证客户身份，然后显示可用的交易选项。
每次交易后，客户可以选择打印收据。
系统应记录所有交易并维护账户余额。
系统应具有超时功能，如果客户在一定时间内未操作，将自动退出当前会话。
系统应具备错误处理机制，如处理卡被吞、网络故障等异常情况。

请尽可能详细地生成需求模型，确保模型的完整性和准确性。
"""

print(f"BASE_URL: {BASE_URL}")
print(f"MODEL_NAME: {MODEL_NAME}")

# 添加agents所需的导入
try:
    from agents import Agent, Runner, RunResult, RunConfig, function_tool, OpenAIProvider
    from openai import AsyncOpenAI
    print("成功导入Agents相关包")
except ImportError as e:
    print(f"导入Agents相关包出错: {e}")
    traceback.print_exc()
    sys.exit(1)

# 定义DSL输出格式
@dataclass
class UsecaseDiagram:
    name: str
    actors: List[Dict[str, str]]
    usecases: List[Dict[str, Any]]

@dataclass
class SequenceDiagram:
    name: str
    actors: List[str]
    messages: List[Dict[str, str]]

@dataclass
class ClassDiagram:
    classes: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]

@dataclass
class OclContracts:
    contracts: List[Dict[str, str]]

@dataclass
class RequirementModel:
    usecase_diagram: UsecaseDiagram
    sequence_diagrams: List[SequenceDiagram]
    class_diagram: ClassDiagram
    ocl_contracts: OclContracts

@dataclass
class ModelReview:
    score: Literal["pass", "needs_improvement", "fail"]
    feedback: str

# 定义用于生成需求模型相关部分的函数工具
@function_tool
def get_domain_info(domain: str) -> str:
    """获取特定领域的背景信息"""
    domains = {
        "ATM": "ATM（自动取款机）是一种允许银行客户进行基本金融交易的电子设备，无需柜员、出纳员或银行职员的帮助。ATM通常由卡读卡器、键盘、显示屏、现金发放口和打印机组成。"
    }
    return domains.get(domain, "未找到该领域的信息")

@function_tool
def validate_uml_syntax(uml_content: str, diagram_type: str) -> str:
    """验证UML图的语法是否正确"""
    # 简化版的验证逻辑，实际应用中可以使用更复杂的验证器
    if diagram_type == "usecase":
        if "actor" in uml_content.lower() and "usecase" in uml_content.lower():
            return "用例图语法正确"
        return "用例图语法错误，缺少actor或usecase元素"
    elif diagram_type == "sequence":
        if "message" in uml_content.lower() and "from" in uml_content.lower() and "to" in uml_content.lower():
            return "顺序图语法正确"
        return "顺序图语法错误，缺少必要的消息流元素"
    elif diagram_type == "class":
        if "class" in uml_content.lower() and "attribute" in uml_content.lower():
            return "类图语法正确"
        return "类图语法错误，缺少类或属性定义"
    elif diagram_type == "ocl":
        if "pre" in uml_content.lower() and "post" in uml_content.lower():
            return "OCL合约语法正确"
        return "OCL合约语法错误，缺少前置或后置条件"
    return "未知图表类型"

async def main():
    try:
        # 创建OpenAI提供者
        provider = OpenAIProvider(
            openai_client=AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY),
            use_responses=False,
        )
        print("成功创建OpenAI Provider")
        
        # 创建参与协作的Agent
        print("开始创建Agent角色...")
        
        # 用例分析专家
        usecase_expert = Agent(
            name="usecase_expert",
            instructions="""
            你是一个用例建模专家，负责分析系统需求并创建用例图。
            分析用户需求，识别主要参与者和用例，并定义它们之间的关系。
            使用标准UML符号创建用例图的JSON表示。
            确保用例图完整、准确地反映系统功能。
            """,
            model=MODEL_NAME
        )
        
        # 顺序图专家
        sequence_expert = Agent(
            name="sequence_expert",
            instructions="""
            你是一个顺序图建模专家，负责创建系统顺序图。
            为每个主要用例创建系统顺序图，显示参与者与系统之间的交互。
            使用标准UML符号表示顺序图的JSON表示。
            确保顺序图清晰地展示系统行为和消息流。
            """,
            model=MODEL_NAME
        )
        
        # 类图专家
        class_expert = Agent(
            name="class_expert",
            instructions="""
            你是一个类图建模专家，负责创建概念类图。
            识别系统中的主要类、它们的属性和关系。
            使用标准UML符号创建类图的JSON表示。
            确保类图准确反映系统的静态结构。
            """,
            model=MODEL_NAME
        )
        
        # OCL合约专家
        ocl_expert = Agent(
            name="ocl_expert",
            instructions="""
            你是一个OCL合约专家，负责为关键操作提供OCL合约。
            为系统中的关键操作定义OCL合约，包括前置条件、后置条件和不变量。
            使用标准OCL语法创建合约的JSON表示。
            确保合约准确地规范了操作的行为。
            """,
            model=MODEL_NAME
        )
        
        # 需求模型集成专家
        integrator = Agent(
            name="integrator",
            instructions="""
            你是一个需求模型集成专家，负责整合各个专家提供的模型。
            审查并整合用例图、顺序图、类图和OCL合约。
            确保模型之间的一致性和完整性。
            生成最终的需求模型JSON表示。
            """,
            model=MODEL_NAME
        )
        
        # 模型审查专家
        reviewer = Agent(
            name="reviewer",
            model=MODEL_NAME,
            instructions="""
            你是一个需求模型审查专家，负责评估需求模型的质量。
            评估模型的完整性、一致性、准确性和可追溯性。
            提供具体的改进建议。
            给出评分：pass（通过）、needs_improvement（需要改进）或fail（不通过）。
            首次评审时至少提供一条改进建议。
            """,
            output_type=ModelReview
        )
        
        print("Agent角色创建完成")
        
        # 开始工作流执行
        print("开始执行MultiAgent需求建模工作流...")
        
        # 初始输入
        input_items = [{"content": REQUIREMENT_PROMPT, "role": "user"}]
        
        # 收集各专家的模型
        print("1. 用例专家正在分析需求...")
        usecase_result = await Runner.run(
            usecase_expert, 
            input_items,
            run_config=RunConfig(model_provider=provider)
        )
        usecase_output = usecase_result.final_output_as(str)
        print("用例分析完成")
        
        print("2. 顺序图专家正在创建系统顺序图...")
        sequence_result = await Runner.run(
            sequence_expert, 
            input_items + [{"content": f"用例图结果：{usecase_output}", "role": "user"}],
            run_config=RunConfig(model_provider=provider)
        )
        sequence_output = sequence_result.final_output_as(str)
        print("顺序图创建完成")
        
        print("3. 类图专家正在创建概念类图...")
        class_result = await Runner.run(
            class_expert, 
            input_items + [
                {"content": f"用例图结果：{usecase_output}", "role": "user"},
                {"content": f"顺序图结果：{sequence_output}", "role": "user"}
            ],
            run_config=RunConfig(model_provider=provider)
        )
        class_output = class_result.final_output_as(str)
        print("类图创建完成")
        
        print("4. OCL专家正在创建OCL合约...")
        ocl_result = await Runner.run(
            ocl_expert, 
            input_items + [
                {"content": f"用例图结果：{usecase_output}", "role": "user"},
                {"content": f"顺序图结果：{sequence_output}", "role": "user"},
                {"content": f"类图结果：{class_output}", "role": "user"}
            ],
            run_config=RunConfig(model_provider=provider)
        )
        ocl_output = ocl_result.final_output_as(str)
        print("OCL合约创建完成")
        
        print("5. 正在整合需求模型...")
        integrator_result = await Runner.run(
            integrator, 
            [
                {"content": REQUIREMENT_PROMPT, "role": "user"},
                {"content": f"用例图：{usecase_output}", "role": "user"},
                {"content": f"顺序图：{sequence_output}", "role": "user"},
                {"content": f"类图：{class_output}", "role": "user"},
                {"content": f"OCL合约：{ocl_output}", "role": "user"}
            ],
            run_config=RunConfig(model_provider=provider)
        )
        
        integrated_model = integrator_result.final_output_as(str)
        print("需求模型整合完成")
        
        # 模型评审和迭代改进
        integrated_model_input = [{"content": f"请评审以下需求模型：\n{integrated_model}", "role": "user"}]
        
        print("6. 开始模型评审...")
        iteration = 0
        max_iterations = 2  # 最多迭代改进3次（初始 + 2次改进）
        
        while iteration < max_iterations:
            reviewer_result = await Runner.run(
                reviewer, 
                integrated_model_input,
                run_config=RunConfig(model_provider=provider)
            )
            
            review_result = reviewer_result.final_output
            print(f"评审结果: {review_result.score}")
            print(f"评审反馈: {review_result.feedback}")
            
            if review_result.score == "pass":
                print("模型评审通过，无需进一步改进")
                break
            
            print(f"需要改进模型，正在进行第{iteration + 1}次迭代...")
            # 将评审反馈发送给整合专家以改进模型
            improver_result = await Runner.run(
                integrator,
                [
                    {"content": REQUIREMENT_PROMPT, "role": "user"},
                    {"content": f"当前模型：{integrated_model}", "role": "user"},
                    {"content": f"评审反馈：{review_result.feedback}", "role": "user"},
                    {"content": "请根据反馈改进需求模型", "role": "user"}
                ],
                run_config=RunConfig(model_provider=provider)
            )
            
            integrated_model = improver_result.final_output_as(str)
            integrated_model_input = [{"content": f"请评审以下需求模型：\n{integrated_model}", "role": "user"}]
            
            iteration += 1
            print(f"完成第{iteration}次模型改进")
        
        # 保存最终模型
        print("保存最终需求模型...")
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(output_dir, "requirement_model_task3.txt")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(integrated_model)
        
        print(f"需求模型已生成并保存到 {output_path}")
        print("MultiAgent需求建模工作流执行完成！")
        
    except Exception as e:
        print(f"执行过程中出现错误: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 