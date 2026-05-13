# engine/session.py
from dataclasses import asdict
from typing import Dict, List, Optional
import streamlit as st
from engine.models import InterviewSession
from data.store import load_all_sessions, save_session


def get_all_sessions() -> List[Dict]:
    return load_all_sessions()


def save_current_session(session: InterviewSession) -> None:
    save_session(asdict(session))


def get_current_session() -> Optional[InterviewSession]:
    data = st.session_state.get("current_session")
    if not data:
        return None
    return InterviewSession(**data)


def set_current_session(session: InterviewSession) -> None:
    st.session_state.current_session = asdict(session)