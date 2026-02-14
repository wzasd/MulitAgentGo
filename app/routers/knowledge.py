"""
知识库路由
"""
from fastapi import APIRouter, HTTPException

from app.models import KnowledgeQuery, KnowledgeResult
from knowledge.client import KnowledgeClient

router = APIRouter()
knowledge_client = KnowledgeClient()


@router.post("/knowledge/query")
async def query_knowledge(request: KnowledgeQuery):
    """查询知识库"""
    try:
        results = await knowledge_client.query(
            query=request.query,
            top_k=request.top_k,
            threshold=request.threshold
        )
        return {
            "query": request.query,
            "results": [r.dict() for r in results]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/health")
async def knowledge_health():
    """知识库健康检查"""
    try:
        status = await knowledge_client.health_check()
        return {"status": "healthy" if status else "unhealthy"}
    except Exception:
        return {"status": "unavailable"}
