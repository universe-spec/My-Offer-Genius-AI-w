# app.py
"""OfferGenius 主入口 —— Streamlit UI"""

import datetime as dt
import uuid
from dataclasses import asdict

import streamlit as st
import pandas as pd

from engine.config import APP_NAME, APP_SUBTITLE, DEFAULT_JOB_PROFILES
from engine.models import InterviewSession
from engine.utils import clean_text, extract_pdf_text
from engine.diagnosis import diagnose_resume
from engine.interview import (
    generate_interview_questions,
    evaluate_answer,
    build_final_report,
    export_markdown_report,
    plot_radar,
    plot_score_bar,
)
from engine.session import (
    get_all_sessions,
    get_current_session,
    set_current_session,
    save_current_session,
)
from ai.llm_client import llm


def init_page() -> None:
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        """
        <style>
        .main-title {
            font-size: 2.4rem;
            font-weight: 800;
            margin-bottom: 0.2rem;
        }
        .sub-title {
            font-size: 1.05rem;
            color: #666;
            margin-bottom: 1.2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    st.sidebar.markdown(f"## 🎯 {APP_NAME}")
    st.sidebar.markdown("一套适合创新创业大赛演示的 AI 求职辅导 SaaS 原型。")

    st.sidebar.divider()
    st.sidebar.markdown("### Demo 状态")
    if llm.enabled:
        st.sidebar.success("已接入真实大模型 API")
    else:
        st.sidebar.warning("当前为离线规则演示模式")
        st.sidebar.caption("无需用户填写 Key；商业化部署时由服务器统一配置。")

    st.sidebar.divider()
    sessions = get_all_sessions()
    st.sidebar.metric("历史训练次数", len(sessions))


def render_home():
    st.markdown(f"<div class='main-title'>🎯 {APP_NAME}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-title'>{APP_SUBTITLE}</div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("核心用户", "高校毕业生")
    c2.metric("核心场景", "简历 + 面试")
    c3.metric("Demo 形态", "Web SaaS")
    c4.metric("变现模型", "订阅 / 次卡")

    st.markdown("---")
    st.markdown("### 一句话介绍")
    st.success(
        "OfferGenius 是一个面向大学生和求职者的 AI 面试训练平台。"
        "用户上传简历并选择目标岗位后，系统会自动生成简历诊断、定制化模拟面试和面后复盘报告。"
    )


def render_resume_page():
    st.header("📄 一键简历诊断")

    with st.form("resume_form"):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            user_name = st.text_input("候选人姓名", value=st.session_state.get("user_name", "张同学"))
        with col2:
            target_job = st.selectbox("目标岗位", list(DEFAULT_JOB_PROFILES.keys()) + ["自定义岗位"])
        with col3:
            target_company = st.text_input("目标公司", value=st.session_state.get("target_company", "字节跳动"))

        if target_job == "自定义岗位":
            target_job = st.text_input("请输入自定义岗位", value="数据分析师")

        uploaded_pdf = st.file_uploader("上传 PDF 简历（可选）", type=["pdf"])
        resume_text = st.text_area(
            "或直接粘贴简历文本",
            height=260,
            value=st.session_state.get("resume_text", ""),
        )

        submitted = st.form_submit_button("开始诊断", use_container_width=True)

    if submitted:
        if uploaded_pdf is not None:
            resume_text = extract_pdf_text(uploaded_pdf)
        if len(clean_text(resume_text)) < 30:
            st.error("简历内容太短，请上传 PDF 或粘贴更完整的简历文本。")
            return

        with st.spinner("正在分析简历与岗位匹配度……"):
            diagnosis = diagnose_resume(resume_text, target_job)

        session = InterviewSession(
            session_id=str(uuid.uuid4()),
            created_at=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_name=user_name,
            target_job=target_job,
            target_company=target_company,
            resume_text=resume_text,
            diagnosis=asdict(diagnosis),
        )
        set_current_session(session)
        save_current_session(session)
        st.session_state.user_name = user_name
        st.session_state.target_company = target_company
        st.session_state.resume_text = resume_text
        st.success("诊断完成！可以进入'模拟面试'继续训练。")

    session = get_current_session()
    if session and session.diagnosis:
        diagnosis = session.diagnosis
        st.markdown("---")
        st.subheader("诊断结果")

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("总分", diagnosis["total_score"])
        c2.metric("关键词", diagnosis["keyword_score"])
        c3.metric("结构", diagnosis["structure_score"])
        c4.metric("量化", diagnosis["quantification_score"])
        c5.metric("项目", diagnosis["project_score"])

        left, right = st.columns([1.2, 1])
        with left:
            st.pyplot(plot_score_bar(diagnosis))
        with right:
            st.markdown("#### 匹配关键词")
            matched = diagnosis.get("matched_keywords", [])
            if matched:
                st.write("、".join(matched))
            else:
                st.warning("暂未匹配到明显岗位关键词。")

            st.markdown("#### 建议补充关键词")
            missing = diagnosis.get("missing_keywords", [])
            if missing:
                st.write("、".join(missing[:10]))
            else:
                st.success("关键词覆盖较完整。")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### ✅ 优势")
            for item in diagnosis.get("strengths", []):
                st.write(f"- {item}")
        with c2:
            st.markdown("#### ⚠️ 待优化")
            for item in diagnosis.get("weaknesses", []):
                st.write(f"- {item}")

        st.markdown("#### 🎯 修改建议")
        for item in diagnosis.get("suggestions", []):
            st.write(f"- {item}")

        st.markdown("#### ✍️ 经历改写示例")
        st.code(diagnosis.get("rewritten_example", ""), language="markdown")


def render_interview_page():
    st.header("🎙️ 定制化 AI 模拟面试")
    session = get_current_session()
    if not session:
        st.warning("请先在'简历诊断'页面创建一次诊断，再进入模拟面试。")
        return

    st.info(f"当前候选人：{session.user_name}｜目标公司：{session.target_company}｜目标岗位：{session.target_job}")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        difficulty = st.selectbox("面试难度", ["基础", "中等", "困难", "压力面"])
    with col2:
        question_count = st.slider("问题数量", min_value=3, max_value=10, value=6)
    with col3:
        st.write("")
        st.write("")
        generate = st.button("生成面试题", use_container_width=True)

    if generate or not session.questions:
        with st.spinner("正在生成定制化面试题……"):
            questions = generate_interview_questions(
                session.resume_text,
                session.target_job,
                session.target_company,
                difficulty,
                count=question_count,
            )
        session.questions = questions
        session.feedbacks = []
        session.final_report = None
        set_current_session(session)
        save_current_session(session)
        st.success("面试题已生成。")

    if not session.questions:
        return

    answered_count = len(session.feedbacks)
    current_index = min(answered_count, len(session.questions) - 1)
    st.progress(answered_count / len(session.questions) if session.questions else 0)
    st.caption(f"已完成 {answered_count}/{len(session.questions)} 题")

    if answered_count < len(session.questions):
        question = session.questions[current_index]
        st.markdown(f"### 第 {current_index + 1} 题")
        st.markdown(f"**面试官：** {question}")

        answer_key = f"answer_{session.session_id}_{current_index}"
        answer = st.text_area(
            "请输入你的回答",
            key=answer_key,
            height=220,
            placeholder="建议按照 STAR 法则作答：背景、任务、行动、结果。",
        )

        col1, col2 = st.columns([1, 3])
        with col1:
            submit_answer = st.button("提交并获得点评", type="primary", use_container_width=True)
        with col2:
            st.caption("答辩演示时，可以让评委现场出一个岗位，系统即时生成问题与点评。")

        if submit_answer:
            if len(clean_text(answer)) < 20:
                st.error("回答太短，建议至少写 20 个字以上，方便系统评价。")
            else:
                with st.spinner("AI 面试官正在点评……"):
                    feedback = evaluate_answer(question, answer, session.target_job)
                session.feedbacks.append(asdict(feedback))
                set_current_session(session)
                save_current_session(session)
                st.rerun()
    else:
        st.success("本轮模拟面试已完成，请进入'复盘报告'查看综合表现。")

    if session.feedbacks:
        st.markdown("---")
        st.subheader("已完成题目点评")
        for i, item in enumerate(session.feedbacks, start=1):
            with st.expander(f"第 {i} 题｜得分 {item.get('score', 0)}"):
                st.markdown(f"**问题：** {item.get('question', '')}")
                st.markdown(f"**你的回答：** {item.get('answer', '')}")
                cols = st.columns(4)
                dims = item.get("dimension_scores", {})
                for idx, dim in enumerate(["专业能力", "表达逻辑", "沟通表达", "抗压复盘"]):
                    cols[idx].metric(dim, dims.get(dim, 0))

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("#### ✅ 亮点")
                    for s in item.get("strengths", []):
                        st.write(f"- {s}")
                with c2:
                    st.markdown("#### ⚠️ 问题")
                    for w in item.get("weaknesses", []):
                        st.write(f"- {w}")

                st.markdown("#### 更优回答框架")
                st.write(item.get("better_answer", ""))


def render_report_page():
    st.header("📊 面后复盘报告")
    session = get_current_session()
    if not session:
        st.warning("还没有训练记录。请先完成简历诊断和模拟面试。")
        return
    if not session.feedbacks:
        st.warning("还没有面试回答记录。请先在'模拟面试'页面至少完成 1 道题。")
        return

    if st.button("生成 / 刷新复盘报告", type="primary") or not session.final_report:
        report = build_final_report(session)
        session.final_report = report
        set_current_session(session)
        save_current_session(session)
        st.success("复盘报告已生成。")

    report = session.final_report or build_final_report(session)
    st.subheader("综合结果")

    c1, c2, c3 = st.columns(3)
    c1.metric("平均得分", report.get("avg_score", 0))
    c2.metric("完成题数", len(session.feedbacks))
    c3.metric("目标岗位", session.target_job)
    st.info(report.get("level", ""))

    left, right = st.columns([1, 1])
    with left:
        st.markdown("#### 能力雷达图")
        fig = plot_radar(report.get("dimension_scores", {}))
        if fig:
            st.pyplot(fig)
    with right:
        st.markdown("#### 维度得分")
        score_df = pd.DataFrame(
            [{"维度": k, "得分": v} for k, v in report.get("dimension_scores", {}).items()]
        )
        st.dataframe(score_df, use_container_width=True, hide_index=True)

    st.markdown("### 高频问题")
    for item in report.get("common_weaknesses", [])[:6]:
        st.write(f"- {item}")

    st.markdown("### 7 天行动计划")
    action_plan = report.get("action_plan", [])
    for day, item in enumerate(action_plan, start=1):
        st.write(f"**Day {day}：** {item}")

    st.markdown("---")
    md = export_markdown_report(session)
    st.download_button(
        "下载 Markdown 复盘报告",
        data=md.encode("utf-8"),
        file_name=f"OfferGenius_Report_{session.user_name}_{dt.date.today()}.md",
        mime="text/markdown",
        use_container_width=True,
    )


def render_history_page():
    st.header("🗂️ 训练历史")
    sessions = get_all_sessions()
    if not sessions:
        st.info("暂无历史记录。")
        return

    rows = []
    for item in sessions:
        rows.append(
            {
                "时间": item.get("created_at", ""),
                "候选人": item.get("user_name", ""),
                "目标公司": item.get("target_company", ""),
                "目标岗位": item.get("target_job", ""),
                "简历分": (item.get("diagnosis") or {}).get("total_score", ""),
                "面试题数": len(item.get("feedbacks", [])),
                "平均面试分": (item.get("final_report") or {}).get("avg_score", ""),
                "session_id": item.get("session_id", ""),
            }
        )
    df = pd.DataFrame(rows)
    st.dataframe(df.drop(columns=["session_id"]), use_container_width=True, hide_index=True)

    st.markdown("### 载入某次训练")
    options = {
        f"{r['时间']}｜{r['候选人']}｜{r['目标岗位']}": r["session_id"] for r in rows
    }
    selected = st.selectbox("选择历史记录", list(options.keys()))
    if st.button("载入该记录", use_container_width=True):
        sid = options[selected]
        target = next((x for x in sessions if x.get("session_id") == sid), None)
        if target:
            st.session_state.current_session = target
            st.success("已载入该训练记录。")
            st.rerun()


def main():
    init_page()
    render_sidebar()

    page = st.tabs(["首页", "简历诊断", "模拟面试", "复盘报告", "训练历史"])

    with page[0]:
        render_home()
    with page[1]:
        render_resume_page()
    with page[2]:
        render_interview_page()
    with page[3]:
        render_report_page()
    with page[4]:
        render_history_page()


if __name__ == "__main__":
    main()