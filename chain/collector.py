"""
TaskCollector - 任务状态收集器
管理思考链状态信息，实现任务的全生命周期管理
"""
from typing import Callable, Dict, List, Optional
from enum import Enum
import asyncio
from dataclasses import dataclass, field
from datetime import datetime


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "PENDING"
    DOING = "DOING"
    DONE = "DONE"
    FAILED = "FAILED"


@dataclass
class Task:
    """任务"""
    task_id: str
    name: str
    status: TaskStatus = TaskStatus.PENDING
    result: any = None
    error: str = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)


class TaskCollector:
    """
    任务状态收集器
    核心职责：
    1. 管理任务的完整生命周期
    2. 维护任务间的层级关系
    3. 通过发布-订阅模式实时推送状态更新
    4. 管理任务队列与订阅者列表
    """

    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.subscribers: Dict[str, List[Callable]] = {}
        self._task_counter = 0

    def create_task(self, name: str, parent_id: str = None) -> str:
        """创建新任务"""
        self._task_counter += 1
        task_id = f"task_{self._task_counter}"

        task = Task(
            task_id=task_id,
            name=name,
            parent_id=parent_id
        )

        if parent_id and parent_id in self.tasks:
            self.tasks[parent_id].children.append(task_id)

        self.tasks[task_id] = task
        self._notify_subscribers(task_id, "created")

        return task_id

    def add_use(self, task_id: str, tool_name: str, tool_input: dict) -> str:
        """添加工具调用任务"""
        subtask_id = f"{task_id}_tool_{tool_name}"
        task = Task(
            task_id=subtask_id,
            name=f"调用工具: {tool_name}",
            parent_id=task_id,
            status=TaskStatus.DOING
        )
        self.tasks[subtask_id] = task
        self.tasks[task_id].children.append(subtask_id)

        self._notify_subscribers(subtask_id, "tool_use", {
            "tool_name": tool_name,
            "tool_input": tool_input
        })

        return subtask_id

    def add_result(self, task_id: str, result: any):
        """记录工具执行结果"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = TaskStatus.DONE
            task.result = result
            task.updated_at = datetime.now()

            self._notify_subscribers(task_id, "result", result)

            # 如果有父任务，更新父任务状态
            if task.parent_id and task.parent_id in self.tasks:
                parent = self.tasks[task.parent_id]
                # 检查是否所有子任务都完成
                all_done = all(
                    self.tasks[child_id].status == TaskStatus.DONE
                    for child_id in parent.children
                )
                if all_done:
                    parent.status = TaskStatus.DONE
                    self._notify_subscribers(parent.id, "completed")

    def fail_task(self, task_id: str, error: str):
        """标记任务失败"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = TaskStatus.FAILED
            task.error = error
            task.updated_at = datetime.now()

            self._notify_subscribers(task_id, "failed", error)

    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self.tasks.get(task_id)

    def get_tasks(self) -> List[Task]:
        """获取所有任务"""
        return list(self.tasks.values())

    def subscribe(self, event: str, callback: Callable):
        """订阅任务事件"""
        if event not in self.subscribers:
            self.subscribers[event] = []
        self.subscribers[event].append(callback)

    def unsubscribe(self, event: str, callback: Callable):
        """取消订阅"""
        if event in self.subscribers:
            self.subscribers[event].remove(callback)

    def _notify_subscribers(self, task_id: str, event: str, data: any = None):
        """通知订阅者"""
        if event in self.subscribers:
            for callback in self.subscribers[event]:
                try:
                    callback(task_id, event, data)
                except Exception as e:
                    print(f"Error notifying subscriber: {e}")

    def clear(self):
        """清除所有任务"""
        self.tasks.clear()
        self.subscribers.clear()
        self._task_counter = 0
