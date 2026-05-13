# engine/interview.py
"""面试引擎：出题、评估、复盘报告、图表"""

import json
import random
import re
import datetime as dt
from typing import Dict, List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from engine.models import AnswerFeedback, InterviewSession
from engine.utils import clean_text, count_quantified_sentences, get_job_profile, normalize_score
from ai.llm_client import llm
from ai.prompts import STAR_TEMPLATE


# ========== 面试问题生成 ==========

def generate_interview_questions(
    resume_text: str,
    target_job: str,
    target_company: str,
    difficulty: str,
    count: int = 6,
) -> List[str]:
    profile = get_job_profile(target_job)

    system_prompt = """
你是一名严谨但友善的面试官。你需要根据候选人的简历、目标公司和目标岗位，生成定制化面试问题。
要求：
1. 问题要贴合简历经历，不能空泛。
2. 问题要覆盖自我介绍、项目深挖、岗位能力、行为面试、压力面试、反问准备。
3. 每个问题单独一行。
4. 不要输出解释。
""".strip()

    user_prompt = f"""
目标公司：{target_company or '某企业'}
目标岗位：{target_job}
难度：{difficulty}
问题数量：{count}
简历内容：{resume_text[:5000]}
""".strip()

    raw = llm.chat(system_prompt, user_prompt, temperature=0.6)
    questions = []
    if raw:
        for line in raw.splitlines():
            line = re.sub(r"^\s*[\-\d\.、)）]+\s*", "", line).strip()
            if line and (line.endswith("？") or line.endswith("?")):
                questions.append(line)

    if len(questions) >= count:
        return questions[:count]

    base = profile["sample_questions"].copy()
    random.shuffle(base)
    custom = [
        f"如果你加入{target_company or '我们公司'}担任{target_job}，你认为前 30 天最重要的学习目标是什么？",
        "请讲一次你遇到困难但最终解决问题的经历。",
        "请用 STAR 法则复盘你简历里最有含金量的一段经历。",
        "你觉得自己目前和这个岗位要求相比，最大的短板是什么？准备如何补足？",
        "如果面试官质疑你的项目贡献不够核心，你会如何回应？",
        "你有什么想反问我们的？请提出 2 个高质量问题。",
    ]
    fallback = base + custom
    return fallback[:count]


# ========== 回答评估 ==========

def evaluate_answer_locally(question: str, answer: str, target_job: str) -> AnswerFeedback:
    answer = clean_text(answer)
    length = len(answer)
    profile = get_job_profile(target_job)
    keywords = profile["keywords"]

    keyword_hits = sum(1 for kw in keywords if kw.lower() in answer.lower())
    has_star = sum(1 for term in ["背景", "目标", "任务", "行动", "结果", "负责", "最终", "提升", "优化"] if term in answer)
    quantified = count_quantified_sentences(answer)

    professional = normalize_score(45 + keyword_hits * 10 + quantified * 5)
    logic = normalize_score(40 + has_star * 8 + min(length / 10, 25))
    expression = normalize_score(50 + min(length / 12, 25) - max(0, (length - 650) / 20))
    pressure = normalize_score(55 + (10 if "不足" in answer or "改进" in answer or "复盘" in answer else 0) + min(has_star * 5, 20))

    score = normalize_score(professional * 0.35 + logic * 0.25 + expression * 0.2 + pressure * 0.2)

    strengths = []
    weaknesses = []

    if length >= 120:
        strengths.append("回答信息量较充足，不是简单一句话应付。")
    else:
        weaknesses.append("回答偏短，缺少背景、过程和结果。")

    if has_star >= 3:
        strengths.append("回答中已经体现出一定 STAR 结构。")
    else:
        weaknesses.append("回答结构不够清晰，建议按照'背景—任务—行动—结果'展开。")

    if quantified > 0:
        strengths.append("回答中包含量化表达，可信度更高。")
    else:
        weaknesses.append("缺少量化结果，建议加入具体数字、指标或对比。")

    if keyword_hits > 0:
        strengths.append("回答中出现了岗位相关关键词，能体现一定岗位匹配度。")
    else:
        weaknesses.append("回答与目标岗位连接不够强，建议主动嵌入岗位关键词。")

    better_answer = build_better_answer(question, target_job)
    next_question_hint = "下一题建议继续围绕项目细节深挖，重点追问个人贡献、技术难点和结果量化。"

    return AnswerFeedback(
        question=question,
        answer=answer,
        score=score,
        dimension_scores={
            "专业能力": professional,
            "表达逻辑": logic,
            "沟通表达": expression,
            "抗压复盘": pressure,
        },
        strengths=strengths or ["回答态度较积极，具备继续打磨的基础。"],
        weaknesses=weaknesses or ["回答整体不错，后续可进一步提高案例细节和岗位针对性。"],
        better_answer=better_answer,
        next_question_hint=next_question_hint,
    )


def build_better_answer(question: str, target_job: str) -> str:
    return f"""
可以按照这个结构回答：
1. 先用一句话正面回应问题："这个经历最能体现我和{target_job}岗位匹配的能力。"
2. 交代背景：项目目标、团队规模、时间周期和你的角色。
3. 说明行动：你具体做了哪些分析、设计、开发、沟通或复盘动作。
4. 给出结果：尽量补充量化指标，例如效率提升、错误率下降、用户增长、成本节约等。
5. 回扣岗位：说明这段经历如何证明你能胜任{target_job}。

示例句式：
"在这个项目中，我主要负责……。当时的难点是……，我采用了……方法，最终让……指标提升/降低了……。这段经历让我形成了……能力，和贵岗位要求的……高度匹配。"
""".strip()


def evaluate_answer(question: str, answer: str, target_job: str) -> AnswerFeedback:
    system_prompt = """
你是一名专业面试官和职业辅导老师。请评价候选人的回答。
输出必须是 JSON，不要输出 Markdown。
字段包括：score, dimension_scores, strengths, weaknesses, better_answer, next_question_hint。
dimension_scores 包含：专业能力、表达逻辑、沟通表达、抗压复盘。
分数为 0-100 的整数。
""".strip()

    user_prompt = f"""
目标岗位：{target_job}
面试问题：{question}
候选人回答：{answer}
请严格输出 JSON。
""".strip()

    raw = llm.chat(system_prompt, user_prompt, temperature=0.35)
    if raw:
        try:
            data = json.loads(re.search(r"\{.*\}", raw, flags=re.S).group(0))
            return AnswerFeedback(
                question=question,
                answer=answer,
                score=int(data.get("score", 70)),
                dimension_scores=dict(data.get("dimension_scores", {})),
                strengths=list(data.get("strengths", [])),
                weaknesses=list(data.get("weaknesses", [])),
                better_answer=str(data.get("better_answer", "")),
                next_question_hint=str(data.get("next_question_hint", "")),
            )
        except Exception:
            pass
    return evaluate_answer_locally(question, answer, target_job)


# ========== 复盘报告 ==========

def build_final_report(session: InterviewSession) -> Dict:
    feedbacks = [AnswerFeedback(**fb) for fb in session.feedbacks]
    if not feedbacks:
        return {}

    dimensions = ["专业能力", "表达逻辑", "沟通表达", "抗压复盘"]
    avg_dimension_scores = {}
    for dim in dimensions:
        values = [fb.dimension_scores.get(dim, 60) for fb in feedbacks]
        avg_dimension_scores[dim] = int(round(sum(values) / len(values)))

    avg_score = int(round(sum(fb.score for fb in feedbacks) / len(feedbacks)))

    common_weaknesses = []
    for fb in feedbacks:
        common_weaknesses.extend(fb.weaknesses)
    common_weaknesses = common_weaknesses[:6]

    if avg_score >= 85:
        level = "优秀：已经具备较强面试竞争力"
    elif avg_score >= 70:
        level = "良好：基础较好，但需要继续打磨表达和案例"
    elif avg_score >= 55:
        level = "待提升：需要系统训练 STAR 表达和岗位匹配"
    else:
        level = "风险较高：建议先重构简历与项目表达后再投递"

    suggestions = [
        "准备 3 个高质量项目故事，每个故事都按 STAR 法则整理。",
        "每个回答都要主动回扣目标岗位，不要只讲经历本身。",
        "把模糊表达替换成数字结果，例如'提升 30%''覆盖 200 名用户''减少 2 天流程时间'。",
        "准备一页'项目深挖清单'：背景、难点、方案、指标、复盘、个人贡献。",
        "每天录音模拟 2 道题，复听后删除口头禅和重复表达。",
    ]

    return {
        "avg_score": avg_score,
        "level": level,
        "dimension_scores": avg_dimension_scores,
        "common_weaknesses": common_weaknesses,
        "action_plan": suggestions,
        "generated_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def export_markdown_report(session: InterviewSession) -> str:
    diagnosis = session.diagnosis or {}
    report = session.final_report or {}
    lines = []
    lines.append(f"# OfferGenius 面试复盘报告")
    lines.append("")
    lines.append(f"- 候选人：{session.user_name or '未填写'}")
    lines.append(f"- 目标公司：{session.target_company or '未填写'}")
    lines.append(f"- 目标岗位：{session.target_job}")
    lines.append(f"- 生成时间：{report.get('generated_at', '')}")
    lines.append("")

    lines.append("## 一、简历诊断")
    lines.append(f"- 总分：{diagnosis.get('total_score', '暂无')}")
    lines.append(f"- 关键词匹配：{diagnosis.get('keyword_score', '暂无')}")
    lines.append(f"- 结构完整度：{diagnosis.get('structure_score', '暂无')}")
    lines.append(f"- 量化表达：{diagnosis.get('quantification_score', '暂无')}")
    lines.append(f"- 项目表达：{diagnosis.get('project_score', '暂无')}")
    lines.append("")

    lines.append("### 优势")
    for item in diagnosis.get("strengths", []):
        lines.append(f"- {item}")
    lines.append("")

    lines.append("### 待优化")
    for item in diagnosis.get("weaknesses", []):
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## 二、模拟面试表现")
    lines.append(f"- 平均分：{report.get('avg_score', '暂无')}")
    lines.append(f"- 综合评级：{report.get('level', '暂无')}")
    lines.append("")

    for i, fb in enumerate(session.feedbacks, start=1):
        lines.append(f"### 第 {i} 题")
        lines.append(f"**问题：** {fb.get('question', '')}")
        lines.append(f"**回答：** {fb.get('answer', '')}")
        lines.append(f"**得分：** {fb.get('score', '')}")
        lines.append("**改进建议：**")
        for w in fb.get("weaknesses", []):
            lines.append(f"- {w}")
        lines.append("")

    lines.append("## 三、行动计划")
    for item in report.get("action_plan", []):
        lines.append(f"- {item}")

    return "\n".join(lines)


# ========== 图表 ==========

def plot_radar(scores: Dict[str, int]):
    labels = list(scores.keys())
    values = list(scores.values())
    if not labels:
        return None

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values_closed = values + values[:1]
    angles_closed = angles + angles[:1]

    fig = plt.figure(figsize=(5.6, 5.6))
    ax = plt.subplot(111, polar=True)
    ax.plot(angles_closed, values_closed, linewidth=2)
    ax.fill(angles_closed, values_closed, alpha=0.2)
    ax.set_thetagrids(np.degrees(angles), labels)
    ax.set_ylim(0, 100)
    ax.set_title("面试能力雷达图", y=1.08)
    ax.grid(True)
    return fig


def plot_score_bar(diagnosis: Dict):
    score_map = {
        "岗位关键词": diagnosis.get("keyword_score", 0),
        "结构完整度": diagnosis.get("structure_score", 0),
        "量化表达": diagnosis.get("quantification_score", 0),
        "项目表达": diagnosis.get("project_score", 0),
    }
    df = pd.DataFrame({"维度": list(score_map.keys()), "分数": list(score_map.values())})
    fig = plt.figure(figsize=(7, 4))
    plt.bar(df["维度"], df["分数"])
    plt.ylim(0, 100)
    plt.ylabel("分数")
    plt.title("简历诊断维度分")
    plt.xticks(rotation=15)
    plt.tight_layout()
    return fig