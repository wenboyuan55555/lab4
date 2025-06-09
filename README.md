# ATM系统智能模型驱动实验

本项目是对"实验四 智能模型驱动"的实现，通过大语言模型辅助实现自动化需求建模，以ATM系统作为目标模型。

## 项目结构

```
ATM/
├── TaskSolutions/             # 实验任务解决方案
│   ├── Common/                # 通用配置和工具
│   ├── Task1/                 # 任务1：基于纯Restful API的智能化需求建模
│   ├── Task2/                 # 任务2：基于OpenAI SDK的智能化需求建模
│   ├── Task3/                 # 任务3：基于LLM Agent的智能化需求建模
│   └── README.md              # 详细实验报告
├── Document/                  # 文档目录
├── RequirementsModel/         # 需求模型目录
└── README.md                  # 项目总体说明
```

## 实验内容

本项目实现了三个任务：

1. **基于纯Restful API的智能化需求建模**：使用HTTP请求直接调用OpenAI API生成ATM系统需求模型
2. **基于OpenAI SDK的智能化需求建模**：使用OpenAI Python SDK调用API生成需求模型
3. **基于LLM Agent的智能化需求建模**：使用MultiAgent工作流实现更复杂的需求建模过程

## 实验报告

详细的实验报告请查看 [TaskSolutions/README.md](TaskSolutions/README.md)，其中包含：

- 输入的Prompt设计
- 输出格式定义
- MultiAgent Workflow简要说明
- 生成的需求模型说明

## 运行环境

- Python 3.9+
- 依赖包：
  - requests
  - openai
  - openai-agents

## 运行方式

1. 安装依赖：
   ```
   pip install requests openai openai-agents
   ```

2. 运行任务1（基于纯Restful API）：
   ```
   python TaskSolutions/Task1/restful_api.py
   ```

3. 运行任务2（基于OpenAI SDK）：
   ```
   python TaskSolutions/Task2/openai_sdk.py
   ```

4. 运行任务3（基于LLM Agent）：
   ```
   python TaskSolutions/Task3/llm_agent.py
   ```

## 结果

各任务生成的需求模型保存在相应任务目录下的txt文件中：

- Task1: `TaskSolutions/Task1/requirement_model_task1.txt`
- Task2: `TaskSolutions/Task2/requirement_model_task2.txt`
- Task3: `TaskSolutions/Task3/requirement_model_task3.txt` 