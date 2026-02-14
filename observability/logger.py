"""
日志管理
"""
import logging
import json
from datetime import datetime
from typing import Optional

from app.config import settings


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('./logs/agentchekong.log'),
            logging.StreamHandler()
        ]
    )


class AgentLogger:
    """智能体日志记录器"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.session_id = None

    def set_session(self, session_id: str):
        """设置会话ID"""
        self.session_id = session_id

    def log_request(self, query: str, intent: str = None):
        """记录请求"""
        self.logger.info(
            f"[请求] session={self.session_id} intent={intent} query={query[:100]}"
        )

    def log_response(self, response: str, tools_used: list = None):
        """记录响应"""
        self.logger.info(
            f"[响应] session={self.session_id} tools={tools_used} response={response[:100]}"
        )

    def log_tool_call(self, tool_name: str, args: dict, result: any):
        """记录工具调用"""
        self.logger.info(
            f"[工具] session={self.session_id} tool={tool_name} args={args} result={str(result)[:100]}"
        )

    def log_error(self, error: str, context: dict = None):
        """记录错误"""
        self.logger.error(
            f"[错误] session={self.session_id} error={error} context={context}"
        )


class JSONLogger:
    """JSON 格式日志"""

    @staticmethod
    def log(level: str, event: str, data: dict):
        """记录 JSON 日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "event": event,
            **data
        }
        print(json.dumps(log_entry, ensure_ascii=False))
