"""
ReActAgent Hooks
实现实时思考链的核心机制
"""
from typing import Optional
from agentscope.agents import ReActAgent
from agentscope.models import ModelResponse
from chain.collector import TaskCollector


# 全局任务收集器
task_collector = TaskCollector()


def task_print_hook(
    self: ReActAgent,
    msg: "Msg",
    chunk: Optional[ModelResponse] = None,
    **kwargs
) -> None:
    """
    任务打印钩子
    在 Agent 执行过程中实时拦截每一条生成的消息
    实现实时思考链展示
    """
    # 捕获 tool_use 类型消息
    if msg.metadata.get("type") == "tool_use":
        tool_name = msg.name
        tool_input = msg.content

        # 添加工具调用任务
        task_id = task_collector.create_task(f"Agent reasoning: {tool_name}")
        subtask_id = task_collector.add_use(task_id, tool_name, tool_input)

        # 输出思考链
        print(f"[思考] 正在调用工具: {tool_name}")
        print(f"[输入] {tool_input}")

    # 捕获 tool_result 类型消息
    elif msg.metadata.get("type") == "tool_result":
        tool_name = msg.name
        tool_result = msg.content

        # 记录工具执行结果
        # 查找对应的 tool_use 任务
        for task_id, task in task_collector.tasks.items():
            if f"tool_{tool_name}" in task_id:
                task_collector.add_result(task_id, tool_result)
                break

        print(f"[结果] {tool_name}: {tool_result[:100]}...")

    # 捕获文本消息
    elif msg.metadata.get("type") == "text":
        print(f"[回答] {msg.content[:200]}...")


def register_hooks(agent: ReActAgent):
    """
    注册 ReActAgent Hooks

    通过前置打印钩子函数，可在 Agent 执行过程中实时拦截每一条生成的消息；
    当捕获到 tool_use 类型消息时，自动调用 add_tool_use，
    而检测到 tool_result 类型消息时，则触发 add_tool_result，
    从而实现对工具调用及其结果的细粒度追踪与状态同步。
    """
    agent.register_class_hook(
        "print",
        "task_print_hook",
        task_print_hook
    )


async def stream_think_process(agent: ReActAgent, user_input: str, context: list = None):
    """
    流式输出思考过程

    Args:
        agent: ReActAgent 实例
        user_input: 用户输入
        context: 对话上下文
    """
    task_id = task_collector.create_task("Main Agent Task")

    # 订阅任务事件
    def on_event(task_id: str, event: str, data: any):
        print(f"[事件] {event}: {data}")

    task_collector.subscribe("tool_use", on_event)
    task_collector.subscribe("result", on_event)

    try:
        # 执行并流式输出
        async for chunk in agent.stream_run(user_input, context or []):
            yield chunk
    finally:
        task_collector.unsubscribe("tool_use", on_event)
        task_collector.unsubscribe("result", on_event)


def get_thought_chain() -> list:
    """
    获取完整的思考链

    Returns:
        思考链列表
    """
    thought_chain = []
    for task in task_collector.get_tasks():
        thought_chain.append({
            "task_id": task.task_id,
            "name": task.name,
            "status": task.status.value,
            "result": task.result,
            "error": task.error
        })
    return thought_chain
