# engine/utils.py
"""工具函数：文本清洗、PDF解析、量化统计、分数归一化、岗位配置回退"""

import re

from engine.config import DEFAULT_JOB_PROFILES


def clean_text(text: str) -> str:
    text = text or ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_pdf_text(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(uploaded_file)
        texts = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            texts.append(page_text)
        return clean_text("\n".join(texts))
    except Exception as exc:
        return f"PDF 解析失败：{exc}"


def count_quantified_sentences(text: str) -> int:
    patterns = [r"\d+%", r"\d+\.\d+%", r"\d+人", r"\d+次", r"\d+万", r"\d+小时", r"\d+天", r"提升", r"降低", r"增长", r"优化"]
    return sum(len(re.findall(p, text)) for p in patterns)


def normalize_score(value: float, min_value: float = 0, max_value: float = 100) -> int:
    value = max(min_value, min(max_value, value))
    return int(round(value))


def get_job_profile(job_name: str) -> Dict:
    if job_name in DEFAULT_JOB_PROFILES:
        return DEFAULT_JOB_PROFILES[job_name]
    return {
        "keywords": ["项目", "实习", "沟通", "数据", "分析", "协作", "目标", "结果", "复盘", "学习"],
        "core_competencies": ["岗位理解", "项目经验", "表达能力", "学习能力", "结果意识"],
        "sample_questions": [
            f"请你先做一个 1 分钟自我介绍，并说明你为什么适合{job_name}。",
            "请介绍一个你最有代表性的项目经历。",
            "你在团队协作中遇到过什么冲突？如何解决？",
            "你如何理解这个岗位的核心价值？",
            "如果入职后发现工作内容和预期不一致，你会怎么办？",
        ],
    }