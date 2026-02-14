"""
Langfuse 集成
实现可观测性
"""
from typing import Optional, Any
from datetime import datetime
from contextlib import asynccontextmanager

from app.config import settings


class LangfuseClient:
    """Langfuse 客户端封装"""

    def __init__(self):
        self.client = None
        self._initialized = False

    def _ensure_initialized(self):
        """确保已初始化"""
        if not self._initialized:
            if settings.langfuse_public_key and settings.langfuse_secret_key:
                try:
                    from langfuse import Langfuse
                    self.client = Langfuse(
                        public_key=settings.langfuse_public_key,
                        secret_key=settings.langfuse_secret_key,
                        host=settings.langfuse_host
                    )
                    self._initialized = True
                except ImportError:
                    print("Warning: langfuse not installed")
            else:
                print("Warning: Langfuse not configured")

    @asynccontextmanager
    async def trace(self, name: str, metadata: dict = None):
        """创建追踪上下文"""
        self._ensure_initialized()

        if not self.client:
            # 无 Langfuse 时返回空上下文
            yield None
            return

        trace = self.client.trace(
            name=name,
            metadata=metadata or {}
        )

        try:
            yield trace
        finally:
            self.client.flush()

    def create_generation(
        self,
        trace_id: str,
        name: str,
        input: Any,
        output: Any,
        model: str = None,
        metadata: dict = None
    ):
        """创建生成记录"""
        self._ensure_initialized()

        if not self.client:
            return None

        return self.client.generation(
            trace_id=trace_id,
            name=name,
            input=input,
            output=output,
            model=model,
            metadata=metadata or {}
        )

    def create_span(
        self,
        trace_id: str,
        name: str,
        input: Any = None,
        output: Any = None,
        metadata: dict = None
    ):
        """创建跨度"""
        self._ensure_initialized()

        if not self.client:
            return None

        return self.client.span(
            trace_id=trace_id,
            name=name,
            input=input,
            output=output,
            metadata=metadata or {}
        )


# 全局实例
langfuse_client = LangfuseClient()
