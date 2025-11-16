# app.py
import streamlit as st
import json, logging, os

from config.config import settings
from utils.ingest_courses import ingest

from utils.retrieve import CourseRetriever, parse_profile_from_message, make_followup_for_missing

logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title='CourseAdvisor RAG', layout='wide')

st.markdown("""
<style>
.chat-container { max-width: 850px; margin: auto; padding: 20px; }
.user-bubble { background-color: #DCF8C6; color: #000; padding: 10px 15px; border-radius: 10px; margin: 8px; margin-left: 120px; text-align: right; }
.assistant-bubble { background-color: #F1F0F0; color: #000; padding: 10px 15px; border-radius: 10px; margin: 8px; margin-right: 120px; text-align: left; }
</style>
""", unsafe_allow_html=True)

st.title('Edu.AI - Student Advisor')

retriever = CourseRetriever()

# --------------------------
# Session state initialization
# --------------------------
if "conversation" not in st.session_state:
    st.session_state.conversation = []  # list of tuples (role, msg)

if "profile" not in st.session_state:
    st.session_state.profile = {
        k: None for k in [
            'field_of_interest',
            'skills_to_master',
            'preference',
            'level',
            'availability',
            'career_goal'
        ]
    }

if "retrieved_courses" not in st.session_state:
    st.session_state.retrieved_courses = []

# flags controlling flow
if "intent_active" not in st.session_state:
    st.session_state.intent_active = False   # user signalled intent to learn (profile collection in progress)

if "roadmap_generated" not in st.session_state:
    st.session_state.roadmap_generated = False  # roadmap already created

def update_profile(parsed: dict):
    for k, v in parsed.items():
        if k in st.session_state.profile and v:
            st.session_state.profile[k] = v

# --------------------------
# Render conversation
# --------------------------
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
for role, msg in st.session_state.conversation:
    if role == "user":
        st.markdown(f"<div class='user-bubble'>{msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='assistant-bubble'>{msg}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --------------------------
# Input form (clears on submit)
# --------------------------
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Message", placeholder="Type your message…")
    submitted = st.form_submit_button("Send")

# --------------------------
# Processing logic
# --------------------------
if submitted and user_input:
    # record user message
    st.session_state.conversation.append(("user", user_input))

    # If roadmap already generated -> normal chat via LLM
    if st.session_state.roadmap_generated:
        try:
            reply = retriever.continue_conversation(user_input, st.session_state.conversation)
        except Exception as e:
            logger.exception("Error continuing chat after roadmap")
            reply = "Sorry — I couldn't continue the conversation due to an internal error."
        st.session_state.conversation.append(("assistant", reply))
        st.rerun()

    # If intent already active (we are in the middle of gathering profile)
    if st.session_state.intent_active and not st.session_state.roadmap_generated:
        # parse any profile fragments from this message
        parsed = parse_profile_from_message(user_input)
        update_profile(parsed)

        # check whether we have the required fields now
        required = ["field_of_interest", "skills_to_master", "preference", "level", "availability"]
        missing = [k for k in required if not st.session_state.profile.get(k)]

        if missing:
            # ask targeted follow-up (only those missing)
            follow = make_followup_for_missing(missing)
            st.session_state.conversation.append(("assistant", follow))
            st.rerun()
        else:
            # all required info collected -> run retrieval + generate roadmap once
            query = ((st.session_state.profile.get("field_of_interest") or "") + " " +
                     (st.session_state.profile.get("skills_to_master") or "")).strip()

            retrieved = retriever.retrieve_courses(query, top_k=settings.TOP_K)
            st.session_state.retrieved_courses = retrieved

            llm_output = retriever.generate_learning_path(st.session_state.profile, retrieved)
            st.session_state.conversation.append(("assistant", llm_output))

            st.session_state.roadmap_generated = True
            st.session_state.intent_active = False
            st.rerun()

    # If no intent yet: check if this message indicates learning intent
    if (not st.session_state.intent_active) and (not st.session_state.roadmap_generated):
        if retriever.is_learning_intent(user_input):
            # start profile collection
            st.session_state.intent_active = True

            parsed = parse_profile_from_message(user_input)
            update_profile(parsed)

            # find missing fields
            required = ["field_of_interest", "skills_to_master", "preference", "level", "availability"]
            missing = [k for k in required if not st.session_state.profile.get(k)]

            if missing:
                follow = make_followup_for_missing(missing)
                st.session_state.conversation.append(("assistant", follow))
                st.rerun()
            else:
                # If user accidentally provided full profile in same message, generate immediately
                query = ((st.session_state.profile.get("field_of_interest") or "") + " " +
                         (st.session_state.profile.get("skills_to_master") or "")).strip()

                retrieved = retriever.retrieve_courses(query, top_k=settings.TOP_K)
                st.session_state.retrieved_courses = retrieved

                llm_output = retriever.generate_learning_path(st.session_state.profile, retrieved)
                st.session_state.conversation.append(("assistant", llm_output))

                st.session_state.roadmap_generated = True
                st.session_state.intent_active = False
                st.rerun()

        else:
            # Normal chat (user didn't ask to learn yet) - forward to LLM with full conversation
            try:
                reply = retriever.continue_conversation(user_input, st.session_state.conversation)
            except Exception as e:
                logger.exception("Chat failed")
                reply = "Sorry — something went wrong while chatting."
            st.session_state.conversation.append(("assistant", reply))
            st.rerun()

# (Optional) show retrieved courses for debugging - set to True to display
if False:
    if st.session_state.retrieved_courses:
        st.subheader("Recommended Courses (raw)")
        for item in st.session_state.retrieved_courses:
            p = item.get("payload", {})
            st.write(f"### {p.get('title')}")
            st.write(p.get("url"))
            st.write(p.get("short_intro") or p.get("Short Intro", ""))
