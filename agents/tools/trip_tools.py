"""
智能体工具定义
"""
from typing import List
from agentscope.tools import function_tool


@function_tool
def search_knowledge(query: str, top_k: int = 3) -> str:
    """
    搜索知识库

    Args:
        query: 查询内容
        top_k: 返回结果数量

    Returns:
        搜索结果
    """
    from knowledge.client import KnowledgeClient

    client = KnowledgeClient()
    results = client.sync_query(query, top_k)

    if not results:
        return "未找到相关内容"

    output = "搜索结果：\n"
    for i, r in enumerate(results, 1):
        output += f"\n{i}. {r.content}\n"
        output += f"   来源: {r.source}, 相似度: {r.similarity:.2f}\n"

    return output


@function_tool
def query_trip_policy(policy_type: str = "差标") -> str:
    """
    查询差旅政策

    Args:
        policy_type: 政策类型（差标、预算、报销等）

    Returns:
        政策信息
    """
    from knowledge.client import KnowledgeClient

    client = KnowledgeClient()
    results = client.sync_query(f"什么是{policy_type}", top_k=1)

    if results:
        return results[0].content
    else:
        return f"未找到关于{policy_type}的相关政策"


@function_tool
def plan_trip(
    destination: str,
    start_date: str = None,
    end_date: str = None,
    purpose: str = None,
    budget: float = None
) -> str:
    """
    规划行程

    Args:
        destination: 目的地
        start_date: 开始日期
        end_date: 结束日期
        purpose: 出差目的
        budget: 预算

    Returns:
        行程规划结果
    """
    # 模拟行程规划
    output = f"""行程规划：
目的地：{destination}
时间：{start_date or '待定'} - {end_date or '待定'}
目的：{purpose or '待确认'}
预算：{budget or '待评估'}

交通建议：
- 建议乘坐高铁/飞机前往

住宿建议：
- 建议选择市区酒店，便于出行

注意事项：
- 提前预订机票/火车票
- 了解当地天气情况
"""
    return output


@function_tool
def book_ticket(
    ticket_type: str,
    from_city: str,
    to_city: str,
    date: str,
    budget: float = None
) -> str:
    """
    预订机票/火车票

    Args:
        ticket_type: 票类型（飞机、火车）
        from_city: 出发城市
        to_city: 目的城市
        date: 日期
        budget: 预算

    Returns:
        预订结果
    """
    return f"""订单申请：
票类型：{ticket_type}
出发：{from_city}
到达：{to_city}
日期：{date}
预算：{budget}

请确认以上信息，我将为您创建订单申请。


"""


@function_tool
def collect_trip_info(info_type: str, info: str) -> str:
    """
    收集出差信息

    Args:
        info_type: 信息类型
        info: 信息内容

    Returns:
        确认信息
    """
    return f"已收集 {info_type}: {info}，请问还有其他信息需要补充吗？"


# 工具列表
trip_tools = [
    plan_trip,
    book_ticket,
    collect_trip_info,
]

knowledge_tools = [
    search_knowledge,
    query_trip_policy,
]
