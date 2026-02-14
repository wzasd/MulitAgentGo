"""
流式输出模块
实现 Server-Sent Events (SSE) 流式输出
"""
import json
import asyncio
from typing import AsyncGenerator, Optional
from dataclasses import dataclass

from chain.collector import TaskCollector


@dataclass
class StreamChunk:
    """流式输出数据块"""
    type: str  # thought, text, tool_use, tool_result, done, error
    content: any
    metadata: dict = None


class Streamer:
    """
    流式输出器
    核心职责：
    1. 创建 TaskCollector 实例以统一管理任务状态
    2. 订阅任务状态更新，实时渲染思考链
    3. 处理智能体执行结果
    4. 构建结构化的最终响应并生成符合 SSE 格式的输出流
    """

    def __init__(self):
        self.collector = TaskCollector()
        self.final_response = []
        self.card_data = {}
        self._setup_subscriptions()

    def _setup_subscriptions(self):
        """设置订阅"""
        self.collector.subscribe("tool_use", self._on_tool_use)
        self.collector.subscribe("result", self._on_tool_result)
        self.collector.subscribe("completed", self._on_completed)
        self.collector.subscribe("failed", self._on_failed)

    def _on_tool_use(self, task_id: str, event: str, data: dict):
        """处理工具调用事件"""
        pass

    def _on_tool_result(self, task_id: str, event: str, data: any):
        """处理工具结果事件"""
        pass

    def _on_completed(self, task_id: str, event: str, data: any):
        """处理任务完成事件"""
        pass

    def _on_failed(self, task_id: str, event: str, error: str):
        """处理任务失败事件"""
        pass

    async def stream_response(
        self,
        generator: AsyncGenerator
    ) -> AsyncGenerator[dict, None]:
        """
        流式输出响应

        Args:
            generator: 异步生成器

        Yields:
            SSE 格式的数据块
        """
        try:
            async for chunk in generator:
                if isinstance(chunk, dict):
                    yield chunk
                elif isinstance(chunk, str):
                    yield {"type": "text", "content": chunk}
                else:
                    yield {"type": "unknown", "content": str(chunk)}
        except Exception as e:
            yield {"type": "error", "content": str(e)}
        finally:
            yield {"type": "done"}

    def build_sse_chunk(self, chunk: StreamChunk) -> str:
        """构建 SSE 数据块"""
        data = {
            "type": chunk.type,
            "content": chunk.content,
        }
        if chunk.metadata:
            data["metadata"] = chunk.metadata

        return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

    async def aggregate_response(self, chunks: list) -> dict:
        """
        聚合响应

        Args:
            chunks: 数据块列表

        Returns:
            结构化的最终响应
        """
        text_content = []
        thought_chain = []
        tools_used = []

        for chunk in chunks:
            if chunk.get("type") == "text":
                text_content.append(chunk.get("content", ""))
            elif chunk.get("type") == "thought":
                thought_chain.append(chunk)
            elif chunk.get("type") == "tool_use":
                tools_used.append(chunk.get("tool_name"))

        return {
            "message": "".join(text_content),
            "thought_chain": thought_chain,
            "tools_used": tools_used,
            "metadata": {
                "card_data": self.card_data,
                "task_status": self.collector.get_tasks()
            }
        }


def create_sse_response(generator: AsyncGenerator) -> AsyncGenerator[str, None]:
    """
    创建 SSE 响应

    Args:
        generator: 数据生成器

    Yields:
        SSE 格式字符串
    """
    async def _generate():
        streamer = Streamer()
        async for chunk in streamer.stream_response(generator):
            yield streamer.build_sse_chunk(
                StreamChunk(
                    type=chunk.get("type", "unknown"),
                    content=chunk.get("content", "")
                )
            )

    return _generate()
