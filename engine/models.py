# engine/models.py
"""数据模型定义"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ResumeDiagnosis:
    total_score: int
    keyword_score: int
    structure_score: int
    quantification_score: int
    project_score: int
    matched_keywords: List[str]
    missing_keywords: List[str]
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    rewritten_example: str


@dataclass
class AnswerFeedback:
    question: str
    answer: str
    score: int
    dimension_scores: Dict[str, int]
    strengths: List[str]
    weaknesses: List[str]
    better_answer: str
    next_question_hint: str


@dataclass
class InterviewSession:
    session_id: str
    created_at: str
    user_name: str
    target_job: str
    target_company: str
    resume_text: str
    diagnosis: Optional[Dict] = None
    questions: List[str] = field(default_factory=list)
    feedbacks: List[Dict] = field(default_factory=list)
    final_report: Optional[Dict] = None