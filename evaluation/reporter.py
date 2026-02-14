"""
评测报告生成器
"""
from typing import List, Dict
from datetime import datetime
from collections import defaultdict


class EvaluationReporter:
    """评测报告生成器"""

    def __init__(self):
        self.results = []

    def add_result(self, result: dict):
        """添加评测结果"""
        self.results.append({
            **result,
            "timestamp": datetime.now().isoformat()
        })

    def generate_report(self) -> dict:
        """生成评测报告"""
        if not self.results:
            return {
                "summary": "No evaluation results",
                "total_cases": 0
            }

        # 计算统计数据
        accuracy_scores = [r.get("accuracy_score", 0) for r in self.results]
        relevance_scores = [r.get("relevance_score", 0) for r in self.results]

        summary = {
            "total_cases": len(self.results),
            "avg_accuracy": sum(accuracy_scores) / len(accuracy_scores),
            "avg_relevance": sum(relevance_scores) / len(relevance_scores),
            "pass_rate": sum(1 for s in accuracy_scores if s >= 75) / len(accuracy_scores) * 100,
            "generated_at": datetime.now().isoformat()
        }

        # 按测试用例分组
        by_case = defaultdict(list)
        for r in self.results:
            by_case[r.get("test_case_id", "unknown")].append(r)

        case_summary = {}
        for case_id, results in by_case.items():
            acc_scores = [r.get("accuracy_score", 0) for r in results]
            case_summary[case_id] = {
                "count": len(results),
                "avg_accuracy": sum(acc_scores) / len(acc_scores)
            }

        return {
            "summary": summary,
            "by_case": case_summary,
            "results": self.results
        }

    def generate_markdown(self) -> str:
        """生成 Markdown 格式报告"""
        report = self.generate_report()
        summary = report["summary"]

        md = f"""# 评测报告

## 概览

- 总测试用例: {summary['total_cases']}
- 平均准确率: {summary['avg_accuracy']:.2f}%
- 平均相关性: {summary['avg_relevance']:.2f}%
- 通过率: {summary['pass_rate']:.2f}%
- 生成时间: {summary['generated_at']}

## 测试用例详情

| 测试用例 | 测试次数 | 平均准确率 |
|---------|---------|-----------|
"""

        for case_id, data in report.get("by_case", {}).items():
            md += f"| {case_id} | {data['count']} | {data['avg_accuracy']:.2f}% |\n"

        md += "\n## 详细结果\n\n"

        for result in self.results:
            md += f"""### {result.get('test_case_id')}

**输入**: {result.get('input_text', '')[:100]}...

**期望输出**: {result.get('expected_output', '')[:100]}...

**实际输出**: {result.get('actual_output', '')[:100]}...

**准确率**: {result.get('accuracy_score', 0)}%
**相关性**: {result.get('relevance_score', 0)}%

**反馈**: {result.get('feedback', '')}

---

"""

        return md
