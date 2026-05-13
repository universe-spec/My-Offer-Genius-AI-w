# engine/diagnosis.py
"""简历诊断引擎：本地规则 + LLM 增强"""

import json
import re
from typing import List

from engine.models import ResumeDiagnosis
from engine.utils import clean_text, count_quantified_sentences, normalize_score, get_job_profile
from ai.llm_client import llm


def build_rewritten_resume_example(target_job: str, matched_keywords: List[str], missing_keywords: List[str]) -> str:
    profile = get_job_profile(target_job)
    key = matched_keywords[:2] or profile["keywords"][:2]
    missing = missing_keywords[:2] or profile["keywords"][2:4]
    return f"""
【修改前】
参与某项目开发，负责部分功能实现，完成老师/主管安排的任务。

【修改后】
在某项目中担任核心成员，围绕“{target_job}”岗位要求，负责{key[0]}相关模块的设计与实现；
通过引入{missing[0]}和{missing[1]}相关方法，优化了核心流程，使处理效率提升约 30%，
并沉淀接口文档和复盘报告，提升了团队后续迭代效率。

【优化逻辑】
这段表达补充了岗位关键词、个人动作、技术方法和量化结果，更符合 STAR 法则。
""".strip()


def diagnose_resume_locally(resume_text: str, target_job: str) -> ResumeDiagnosis:
    text = clean_text(resume_text)
    profile = get_job_profile(target_job)
    keywords = profile["keywords"]

    matched_keywords = [kw for kw in keywords if kw.lower() in text.lower()]
    missing_keywords = [kw for kw in keywords if kw.lower() not in text.lower()]

    keyword_score = normalize_score(len(matched_keywords) / max(len(keywords), 1) * 100)
    structure_terms = ["教育", "项目", "实习", "技能", "获奖", "校园", "经历", "自我评价", "工作", "实践"]
    structure_hits = sum(1 for term in structure_terms if term in text)
    structure_score = normalize_score(structure_hits / 6 * 100)
    quantified_count = count_quantified_sentences(text)
    quantification_score = normalize_score(quantified_count * 12)
    project_terms = ["负责", "实现", "优化", "设计", "开发", "搭建", "分析", "完成", "推动", "上线"]
    project_hits = sum(1 for term in project_terms if term in text)
    project_score = normalize_score(project_hits * 10)

    total_score = normalize_score(
        keyword_score * 0.35 + structure_score * 0.2 + quantification_score * 0.2 + project_score * 0.25
    )

    strengths = []
    weaknesses = []
    suggestions = []

    if keyword_score >= 70:
        strengths.append("岗位关键词覆盖较好，简历与目标岗位具有一定匹配度。")
    else:
        weaknesses.append("岗位关键词覆盖不足，容易被招聘系统或 HR 初筛过滤。")
        suggestions.append(f"建议补充与{target_job}相关的关键词，例如：{ '、'.join(missing_keywords[:5]) }。")

    if structure_score >= 70:
        strengths.append("简历模块较完整，基本信息、经历和能力展示较清晰。")
    else:
        weaknesses.append("简历结构不够清晰，模块边界可能不明显。")
        suggestions.append("建议按照'教育背景—专业技能—项目经历—实习经历—获奖证书'重新组织。")

    if quantification_score >= 60:
        strengths.append("部分经历有量化表达，能够体现结果意识。")
    else:
        weaknesses.append("成果描述偏笼统，缺少数字化结果。")
        suggestions.append("每段项目经历建议至少补充 1 个可量化结果，如效率提升、用户数量、准确率、成本下降等。")

    if project_score >= 60:
        strengths.append("项目经历中包含一定动作动词，能体现个人贡献。")
    else:
        weaknesses.append("项目经历对个人贡献描述不足，容易显得像团队介绍。")
        suggestions.append("把'项目做了什么'改为'我具体做了什么'，突出工具、方法、难点和结果。")

    if not strengths:
        strengths.append("简历已经具备基础信息，可以在此基础上继续优化。")
    if not weaknesses:
        weaknesses.append("当前简历基础较好，后续重点是提高针对性和表达精度。")
    if not suggestions:
        suggestions.append("建议针对不同岗位制作不同版本简历，突出最匹配的项目和技能。")

    rewritten_example = build_rewritten_resume_example(target_job, matched_keywords, missing_keywords)

    return ResumeDiagnosis(
        total_score=total_score,
        keyword_score=keyword_score,
        structure_score=structure_score,
        quantification_score=quantification_score,
        project_score=project_score,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
        strengths=strengths,
        weaknesses=weaknesses,
        suggestions=suggestions,
        rewritten_example=rewritten_example,
    )


def diagnose_resume(resume_text: str, target_job: str) -> ResumeDiagnosis:
    system_prompt = """
你是一名资深校园招聘 HR、职业规划导师和简历优化专家。
你需要基于目标岗位，对学生简历进行客观、具体、可执行的诊断。
输出必须是 JSON，不要输出 Markdown。
字段包括：total_score, keyword_score, structure_score, quantification_score, project_score,
matched_keywords, missing_keywords, strengths, weaknesses, suggestions, rewritten_example。
分数为 0-100 的整数。
""".strip()

    user_prompt = f"""
目标岗位：{target_job}
简历内容：{resume_text[:6000]}
请输出 JSON。
""".strip()

    raw = llm.chat(system_prompt, user_prompt)
    if raw:
        try:
            data = json.loads(re.search(r"\{.*\}", raw, flags=re.S).group(0))
            return ResumeDiagnosis(
                total_score=int(data.get("total_score", 70)),
                keyword_score=int(data.get("keyword_score", 70)),
                structure_score=int(data.get("structure_score", 70)),
                quantification_score=int(data.get("quantification_score", 70)),
                project_score=int(data.get("project_score", 70)),
                matched_keywords=list(data.get("matched_keywords", [])),
                missing_keywords=list(data.get("missing_keywords", [])),
                strengths=list(data.get("strengths", [])),
                weaknesses=list(data.get("weaknesses", [])),
                suggestions=list(data.get("suggestions", [])),
                rewritten_example=str(data.get("rewritten_example", "")),
            )
        except Exception:
            pass
    return diagnose_resume_locally(resume_text, target_job)