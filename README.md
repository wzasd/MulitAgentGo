# 阿里商旅多智能体差旅助手

基于阿里商旅最佳实践，使用 AgentScope 构建的多智能体差旅助手。

## 项目简介

本项目是阿里商旅差旅助手的开源实现，完整还原了以下核心功能：

- **多智能体架构**：主规划智能体 + 意图识别 + 多个子智能体
- **分层意图识别**：快车道（规则引擎）+ 慢车道（LLM分析）
- **实时思考链**：基于 ReActAgent Hook 机制实现
- **上下文工程**：记忆管理、会话存储、动态 Prompt 状态机
- **知识库集成**：基于 MaxKB 的 RAG 能力
- **可观测性**：基于 Langfuse 的链路追踪
- **评测系统**：基于 LLM 的自动化评分

## 技术栈

- **智能体框架**: AgentScope
- **Web 框架**: FastAPI
- **大模型**: 阿里云 DashScope (qwen-plus)
- **知识库**: MaxKB
- **观测平台**: Langfuse
- **数据库**: SQLite (开发) / PostgreSQL (生产)

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/wzasd/MulitAgentGo.git
cd MulitAgentGo
```

### 2. 配置环境

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
DASHSCOPE_API_KEY=your_api_key_here
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 启动服务

```bash
# 启动 FastAPI 服务
uvicorn app.main:app --reload --port 8000
```

### 5. 启动周边服务（可选）

```bash
# 启动 MaxKB 和 Langfuse
docker-compose up -d
```

## API 使用

### 聊天接口

```bash
# 流式响应
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-001",
    "message": "帮我规划下周的北京出差行程",
    "stream": true
  }'
```

### 创建会话

```bash
curl -X POST "http://localhost:8000/api/v1/conversations" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-001",
    "title": "我的出差行程"
  }'
```

## 项目结构

```
agentchekong/
├── app/                    # FastAPI 应用
│   ├── main.py            # 入口
│   ├── config.py          # 配置
│   ├── models.py          # 数据模型
│   ├── database.py        # 数据库
│   └── routers/           # API 路由
├── agents/                # 智能体模块
│   ├── main_plan_agent.py # 主规划智能体
│   ├── trip_planner.py    # 行程规划智能体
│   ├── rag_agent.py       # RAG 智能体
│   └── tools/             # 工具定义
├── context/               # 上下文工程
│   ├── memory.py          # 记忆管理
│   └── prompt_builder.py  # 动态 Prompt
├── intent/                # 意图识别
│   ├── classifier.py      # 规则引擎
│   └── recognizer.py      # LLM 识别
├── chain/                 # 思考链
│   ├── collector.py       # TaskCollector
│   ├── hooks.py           # ReAct Hooks
│   └── streamer.py        # 流式输出
├── knowledge/             # 知识库
├── observability/         # 观测平台
├── evaluation/            # 评测系统
└── docker-compose.yml     # 容器编排
```

## 核心设计

### 分层意图识别

系统采用"快慢车道"设计：

- **快车道**：规则引擎处理简单明确的意图（如"为我规划行程"）
- **慢车道**：LLM 分析处理复杂多义的意图

### 实时思考链

基于 ReActAgent 的 Hook 机制，在工具调用时实时输出推理过程：

```
[思考] 正在调用工具: search_knowledge
[输入] {"query": "什么是差标"}
[结果] search_knowledge: 差标是指...
```

### 上下文工程

- **记忆架构**：通过 sessionId 实现跨智能体记忆共享
- **动态 Prompt**：基于状态机动态组装 Prompt

## 许可证

MIT License

## 参考

- [AgentScope](https://github.com/agentscope-ai/agentscope)
- [MaxKB](https://github.com/1Panel-dev/MaxKB)
- [Langfuse](https://github.com/langfuse/langfuse)
- [阿里商旅 AgentScope 实践](https://mp.weixin.qq.com/s/xxxxx)

---

本项目是对阿里商旅多智能体差旅助手最佳实践的技术复现，仅供学习参考。
