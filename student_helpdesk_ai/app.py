import streamlit as st
from chatbot import get_answer, load_knowledge_base, INTENT_KEYWORDS

st.set_page_config(page_title="Student Helpdesk AI", page_icon="🎓", layout="wide")
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg,#f4f7ff 0%,#eefbf8 100%);}
.hero {font-size:2.4rem;font-weight:800;color:#172554;margin-bottom:.1rem;}
.sub {color:#526079;margin-bottom:1.3rem;}
.topic {border:1px solid #dfe5ff;border-radius:16px;padding:18px;background:white;min-height:120px;box-shadow:0 6px 22px #28375a0d;}
.topic-title {font-weight:750;color:#273469;font-size:1.05rem;}
.topic-desc {color:#596579;font-size:.9rem;margin-top:7px;}
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="hero"> Student Helpdesk AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Ask about admissions, courses, fees, scholarships, internships and placements.</div>', unsafe_allow_html=True)

try:
    faq_rows = load_knowledge_base()
except Exception as exc:
    st.error(f"Could not load the FAQ dataset: {exc}")
    st.stop()

with st.sidebar:
    st.header("Helpdesk")
    st.caption("Keyword-based FAQ retrieval")
    st.metric("FAQ entries", len(faq_rows))
    st.metric("Supported topics", len(INTENT_KEYWORDS))
    st.markdown("---")
    st.subheader("Suggested questions")
    suggestions = [
        "What documents are needed for admission?",
        "Which engineering courses are available?",
        "Where can I find the fee structure?",
        "How do I apply for a scholarship?",
        "How can I get internship information?",
        "Where can I find placement details?",
        "What is the college address?"
    ]
    for i, question in enumerate(suggestions):
        if st.button(question, key=f"suggest_{i}", use_container_width=True):
            st.session_state.pending_question = question
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_question = ""
        st.rerun()
    st.caption("Verify time-sensitive details with the college.")

cards = [
    (" Admissions", "Application steps, eligibility and documents"),
    (" Courses", "Programs and engineering branches"),
    (" Fees", "Fee structure and payment questions"),
    (" Scholarships", "Financial aid and scholarship guidance"),
    (" Internships", "Training and internship information"),
    (" Placements", "Placement and career information")
]
cols = st.columns(3)
for i, (title, desc) in enumerate(cards):
    with cols[i % 3]:
        st.markdown(f'<div class="topic"><div class="topic-title">{title}</div><div class="topic-desc">{desc}</div></div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = ""

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("details"):
            with st.expander("Matching details"):
                st.json(message["details"])

pending = st.session_state.pending_question
prompt = st.chat_input("Type your question here...")
if pending:
    prompt = pending
    st.session_state.pending_question = ""

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    result = get_answer(prompt, faq_rows)
    details = {
        "Detected intent": result["intent"],
        "Matched FAQ": result["matched_question"] or "No FAQ matched",
        "Keyword overlap score (rough indicator, not model confidence)": result["confidence"],
        "Source": result["source_url"] or "No source listed"
    }
    with st.chat_message("assistant"):
        st.markdown(result["answer"])
        if result["source_url"]:
            st.caption(f"Reference: {result['source_url']}")
        with st.expander("Matching details"):
            st.json(details)
    st.session_state.messages.append({"role": "assistant", "content": result["answer"], "details": details})
