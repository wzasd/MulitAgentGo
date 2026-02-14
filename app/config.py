# 配置管理
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    app_name: str = "阿里商旅差旅助手"
    debug: bool = True
    api_prefix: str = "/api/v1"

    # DashScope 配置
    dashscope_api_key: str = Field(default="", description="阿里云 DashScope API Key")
    dashscope_model: str = "qwen-plus"

    # AgentScope 配置
    agentscope_model_type: str = "dashscope"
    agentscope_model_name: str = "qwen-plus"

    # Langfuse 配置
    langfuse_public_key: Optional[str] = Field(default=None, description="Langfuse Public Key")
    langfuse_secret_key: Optional[str] = Field(default=None, description="Langfuse Secret Key")
    langfuse_host: str = "http://localhost:3000"

    # MaxKB 配置
    maxkb_base_url: str = "http://localhost:8080"
    maxkb_api_key: Optional[str] = Field(default=None, description="MaxKB API Key")

    # 数据库配置
    database_url: str = "sqlite+aiosqlite:///./data/agentchekong.db"

    # 会话配置
    session_expire_hours: int = 24

    class Config:
        env_file = ".env"
        extra = "allow局配置实例"


# 全
settings = Settings()


# 配置初始化
def init_config():
    """初始化配置"""
    # 确保必要的目录存在
    os.makedirs("./data", exist_ok=True)
    os.makedirs("./logs", exist_ok=True)

    # 检查必要的配置
    if not settings.dashscope_api_key:
        print("警告: 未设置 DASHSCOPE_API_KEY，请在 .env 文件中配置")
