"""Streamlit UI. Uses the FastAPI backend when API_URL is set, else runs the bot in-process
(handy for single-service deployment such as Streamlit Community Cloud)."""
import os
import requests
import streamlit as st

st.set_page_config(page_title="CEC Student Helpdesk AI", page_icon="🎓", layout="centered")
API_URL = os.getenv("API_URL", "")

WELCOME = ("Hello! 👋 I'm the City Engineering College helpdesk.\n\n"
           "I can help with admissions, courses, fees, internships, placements and general college information.")
ICONS = {"admission": "🎓", "courses_offered": "📚", "course_details": "📚", "fee": "💰", "scholarships": "💰",
         "internships": "💼", "placement": "🏢", "college_info": "📞"}

@st.cache_resource
def local_bot():
    from chatbot import HelpdeskBot
    return HelpdeskBot()

def ask(message: str) -> dict:
    if API_URL:
        try:
            r = requests.post(f"{API_URL.rstrip('/')}/chat", json={"message": message}, timeout=10)
            r.raise_for_status()
            return r.json()
        except requests.RequestException:
            return {"answer": "The backend is not reachable right now. Please try again shortly.", "intent": None, "confidence": 0.0}
    return local_bot().answer(message)

def icon_for(intent):
    return next((v for k, v in ICONS.items() if intent and intent.startswith(k)), "")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": WELCOME}]

st.markdown("""
<style>
.main-title {font-size: 2.1rem; font-weight: 800; color: #243b80; margin-bottom: 0;}
.subtitle {color: #64748b; font-size: 1.05rem; margin-bottom: 1rem;}
.dashboard-card {position: relative; min-height: 170px; padding: 20px 16px; border-radius: 20px;
    border: 1px solid rgba(255,255,255,.8); box-shadow: 0 8px 24px rgba(45,55,100,.08);
    transition: transform .25s ease, box-shadow .25s ease; margin-bottom: 12px;}
.dashboard-card:hover {transform: translateY(-6px); box-shadow: 0 14px 30px rgba(45,55,100,.15);}
.dashboard-icon {width: 46px; height: 46px; display: flex; align-items: center; justify-content: center;
    border-radius: 14px; font-size: 24px; margin-bottom: 12px;}
.dashboard-card h3 {font-size: 18px; margin: 0 0 6px 0; color: #243b80;}
.dashboard-card p {color: #64748b; font-size: 13.5px; line-height: 1.45; margin: 0;}
.c-adm {background: linear-gradient(145deg,#fff7ed,#fff);} .c-adm .dashboard-icon {background:#ffedd5;}
.c-crs {background: linear-gradient(145deg,#eff6ff,#fff);} .c-crs .dashboard-icon {background:#dbeafe;}
.c-fee {background: linear-gradient(145deg,#ecfdf5,#fff);} .c-fee .dashboard-icon {background:#d1fae5;}
.c-int {background: linear-gradient(145deg,#f5f3ff,#fff);} .c-int .dashboard-icon {background:#ede9fe;}
.c-plc {background: linear-gradient(145deg,#fdf2f8,#fff);} .c-plc .dashboard-icon {background:#fce7f3;}
.c-inf {background: linear-gradient(145deg,#f0f9ff,#fff);} .c-inf .dashboard-icon {background:#e0f2fe;}
@media (max-width: 640px) {.dashboard-card {min-height: 150px; padding: 14px;}}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🎓 CEC Helpdesk")
    st.write("Your virtual college assistant")
    st.markdown("### Available topics")
    for t in ["🎓 Admissions", "📚 Courses", "💰 Fees & scholarships", "💼 Internships", "🏢 Placements", "📞 College info"]:
        st.write(t)
    st.divider()
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": "Chat cleared! 👋 What would you like to know?"}]
        st.rerun()
    st.caption(f"Mode: {'API backend' if API_URL else 'local model'}")
    st.caption("City Engineering College · Minor Project")

st.markdown('<div class="main-title">🎓 CEC Student Helpdesk AI ✨</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Your assistant for City Engineering College questions</div>', unsafe_allow_html=True)

st.markdown("## ✨ Explore student services")
st.caption("Choose a topic below to get help.")
CARDS = [
    ("Admissions", "🎓", "Application process, eligibility and documents.", "c-adm", "How can I apply for admission?"),
    ("Courses", "📚", "Explore engineering branches and programmes.", "c-crs", "Which courses are offered?"),
    ("Fees", "💰", "Fee structure, payment and scholarships.", "c-fee", "What is the fee structure?"),
    ("Internships", "💼", "Internship opportunities and who to contact.", "c-int", "Are internships available?"),
    ("Placements", "🚀", "Placement statistics and preparation.", "c-plc", "Tell me about campus placements"),
    ("College info", "📞", "Address, phone number and timings.", "c-inf", "Where is the college located?"),
]
for start in range(0, len(CARDS), 3):
    for col, (title, icon, desc, css, question) in zip(st.columns(3), CARDS[start:start + 3]):
        with col:
            st.markdown(f'<div class="dashboard-card {css}"><div class="dashboard-icon">{icon}</div>'
                        f'<h3>{title}</h3><p>{desc}</p></div>', unsafe_allow_html=True)
            if st.button(f"Explore {title} →", key=f"card_{title}", use_container_width=True):
                st.session_state.pending = question
                st.rerun()

st.divider()
st.markdown("### 💬 Ask your question")
st.write("**Try asking:**")
QUICK = [("🎓 Admission process", "How can I apply for admission?"), ("📚 Available courses", "Which courses are offered?"),
         ("💰 Fee information", "What is the fee structure?"), ("💼 Internship guidance", "Are internships available?"),
         ("🏢 Placement preparation", "How should I prepare for placements?"), ("🎯 Scholarship information", "Are scholarships available?")]
c1, c2 = st.columns(2)
for i, (label, q) in enumerate(QUICK):
    if (c1 if i < 3 else c2).button(label, use_container_width=True, key=f"quick_{i}"):
        st.session_state.pending = q

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

typed = st.chat_input("Type your question here...")
prompt = st.session_state.pop("pending", None) or typed
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    res = ask(prompt)
    text = f"{icon_for(res.get('intent'))} {res['answer']}".strip()
    with st.chat_message("assistant"):
        st.markdown(text)
        if res.get("intent"):
            st.caption(f"Topic: {res['intent']} · Confidence: {res['confidence']:.2f}"
                       + ("" if res.get("verified") else " · ⚠️ please verify with the college"))
    st.session_state.messages.append({"role": "assistant", "content": text})

st.divider()
st.caption("Note: This is an educational project. Verify admission, fee, scholarship and placement details "
           "with the college office (9880411361) before making decisions.")
