"""
知识库客户端
集成 MaxKB
"""
from typing import List, Optional
import httpx
from pydantic import BaseModel

from app.config import settings


class KnowledgeResult(BaseModel):
    """知识库查询结果"""
    content: str
    source: str
    similarity: float


class KnowledgeClient:
    """MaxKB 知识库客户端"""

    def __init__(self):
        self.base_url = settings.maxkb_base_url
        self.api_key = settings.maxkb_api_key
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0
        )

    async def query(
        self,
        query: str,
        top_k: int = 3,
        threshold: float = 0.7
    ) -> List[KnowledgeResult]:
        """异步查询知识库"""
        if not self.api_key:
            return self._mock_query(query, top_k)

        try:
            response = await self.client.post(
                "/api/v1/knowledge/chat",
                json={
                    "query": query,
                    "top_k": top_k
                },
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            data = response.json()

            return [
                KnowledgeResult(
                    content=item.get("content", ""),
                    source=item.get("source", ""),
                    similarity=item.get("score", 0.0)
                )
                for item in data.get("results", [])
            ]
        except Exception as e:
            print(f"知识库查询失败: {e}")
            return self._mock_query(query, top_k)

    def sync_query(
        self,
        query: str,
        top_k: int = 3,
        threshold: float = 0.7
    ) -> List[KnowledgeResult]:
        """同步查询知识库"""
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.query(query, top_k, threshold))

    def _mock_query(self, query: str, top_k: int) -> List[KnowledgeResult]:
        """模拟查询（知识库不可用时）"""
        mock_data = [
            KnowledgeResult(
                content="差标是指本次差旅形成中，出行人乘坐飞机以及入住酒店等差旅类目的费用标准。",
                source="差旅政策",
                similarity=0.95
            ),
            KnowledgeResult(
                content="预算指的是本次差旅出行的整体预算费用，包括交通、住宿、餐饮等各项支出。",
                source="差旅政策",
                similarity=0.85
            ),
            KnowledgeResult(
                content="阿里商旅支持机票、火车票、酒店等多种差旅预订服务。",
                source="服务说明",
                similarity=0.75
            ),
        ]
        return mock_data[:top_k]

    async def health_check(self) -> bool:
        """健康检查"""
        if not self.api_key:
            return False

        try:
            response = await self.client.get(
                "/api/v1/health",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            return response.status_code == 200
        except Exception:
            return False

    async def close(self):
        """关闭客户端"""
        await self.client.aclose()
