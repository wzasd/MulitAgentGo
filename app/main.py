# FastAPI 入口
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.config import init_config, settings
from app.routers import chat, conversation, knowledge


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    init_config()
    print(f"🚀 {settings.app_name} 启动中...")

    # 初始化数据库
    from app.database import init_db
    await init_db()

    yield

    # 关闭时执行
    print(f"🛑 {settings.app_name} 关闭中...")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    description="阿里商旅多智能体差旅助手 API",
    version="1.0.0",
    lifespan=lifespan,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(
    chat.router,
    prefix=settings.api_prefix,
    tags=["对话"]
)
app.include_router(
    conversation.router,
    prefix=settings.api_prefix,
    tags=["会话"]
)
app.include_router(
    knowledge.router,
    prefix=settings.api_prefix,
    tags=["知识库"]
)


@app.get("/")
async def root():
    """根路由"""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
