"""API Server —— 让 React 能调用你现有的功能"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 导入你现有的功能
from engine.diagnosis import diagnose_resume
from engine.interview import generate_interview_questions, evaluate_answer

app = FastAPI()

# 允许 React 前端调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class DiagnoseRequest(BaseModel):
    resume_text: str
    target_job: str

class QuestionsRequest(BaseModel):
    resume_text: str
    target_job: str
    target_company: str
    difficulty: str
    count: int

class EvaluateRequest(BaseModel):
    question: str
    answer: str
    target_job: str

@app.post("/api/diagnose")
def diagnose(req: DiagnoseRequest):
    result = diagnose_resume(req.resume_text, req.target_job)
    return result.__dict__ if hasattr(result, '__dict__') else result

@app.post("/api/generate_questions")
def generate_questions(req: QuestionsRequest):
    questions = generate_interview_questions(
        req.resume_text,
        req.target_job,
        req.target_company,
        req.difficulty,
        req.count
    )
    return {"questions": questions}

@app.post("/api/evaluate")
def evaluate(req: EvaluateRequest):
    result = evaluate_answer(req.question, req.answer, req.target_job)
    if hasattr(result, '__dict__'):
        return result.__dict__
    return result

@app.get("/api/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 API Server 启动在 http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)