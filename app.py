import streamlit as st
import random
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="Student Helpdesk AI",
    page_icon="🎓",
    layout="centered"
)

# ---------------- KNOWLEDGE BASE ----------------
# Replace these sample details with your college's
# official information before presenting the project.

knowledge_base = [
    {
        "category": "Admissions",
        "questions": [
            "How can I apply for admission?",
            "What is the admission process?",
            "How do I get admission to college?",
            "Which documents are required for admission?",
            "What is the eligibility for admission?",
            "When does admission start?"
        ],
        "answer": (
            "🎓 **Admission Information**\n\n"
            "1. Visit your college's official website.\n"
            "2. Check the eligibility requirements.\n"
            "3. Complete the application form.\n"
            "4. Submit the required documents.\n"
            "5. Follow the official selection and fee-payment process.\n\n"
            "Required documents may include marks cards, "
            "ID proof, photographs, and applicable certificates. "
            "Confirm the exact requirements with your college."
        )
    },
    {
        "category": "Courses",
        "questions": [
            "Which courses are available?",
            "What engineering branches are offered?",
            "Tell me about computer science",
            "Do you offer artificial intelligence?",
            "Which course should I choose?",
            "What are the available departments?"
        ],
        "answer": (
            "📚 **Courses Information**\n\n"
            "Colleges may offer programs such as:\n"
            "- Computer Science and Engineering\n"
            "- Information Science and Engineering\n"
            "- Electronics and Communication Engineering\n"
            "- Mechanical Engineering\n"
            "- Civil Engineering\n"
            "- Artificial Intelligence and Data Science\n\n"
            "Available programs vary by college. Check your "
            "college's official course list for confirmation."
        )
    },
    {
        "category": "Fees",
        "questions": [
            "What is the college fee?",
            "How much is the tuition fee?",
            "What are the semester fees?",
            "Are scholarships available?",
            "Can I pay fees in installments?",
            "How do I pay college fees?"
        ],
        "answer": (
            "💰 **Fee Information**\n\n"
            "Fees depend on the course, admission category, "
            "and college policies. For accurate amounts:\n"
            "1. Check the official fee structure.\n"
            "2. Contact the accounts department.\n"
            "3. Ask about scholarships and eligible concessions.\n"
            "4. Confirm payment deadlines and accepted methods.\n\n"
            "This demo does not contain verified college fee amounts."
        )
    },
    {
        "category": "Internships",
        "questions": [
            "How can I get an internship?",
            "Where can I find internships?",
            "Are internships available for students?",
            "How do I prepare a resume?",
            "Which skills are needed for internships?",
            "How can I apply for a technical internship?"
        ],
        "answer": (
            "💼 **Internship Guidance**\n\n"
            "1. Build a resume highlighting your skills and projects.\n"
            "2. Learn relevant technical skills.\n"
            "3. Create projects to demonstrate your knowledge.\n"
            "4. Check your college placement cell and career portals.\n"
            "5. Apply through official company career pages.\n"
            "6. Prepare for interviews and aptitude tests.\n\n"
            "Choose internships that match your interests and goals."
        )
    },
    {
        "category": "Placements",
        "questions": [
            "What is the placement process?",
            "Which companies visit the campus?",
            "What is the placement percentage?",
            "How can I prepare for placements?",
            "What is the average package?",
            "What skills are required for campus placements?"
        ],
        "answer": (
            "🏢 **Placement Information**\n\n"
            "Campus placement processes commonly include:\n"
            "1. Aptitude and reasoning tests.\n"
            "2. Technical assessments.\n"
            "3. Technical interviews.\n"
            "4. HR interviews.\n\n"
            "Improve your programming, communication, problem-solving, "
            "and interview skills. Company lists, placement rates, "
            "and salary packages must be checked using official "
            "college placement reports."
        )
    },
    {
        "category": "Contact",
        "questions": [
            "How can I contact the college?",
            "Where is the college located?",
            "What are the office timings?",
            "How do I contact student support?",
            "Where can I get more information?"
        ],
        "answer": (
            "📞 **College Support**\n\n"
            "For verified contact details, visit your college's "
            "official website or contact the admissions office, "
            "student support desk, or placement cell."
        )
    }
]

# ---------------- NLP MODEL ----------------
all_questions = []
question_categories = []

for item in knowledge_base:
    for question in item["questions"]:
        all_questions.append(question)
        question_categories.append(item["category"])

vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2)
)

question_vectors = vectorizer.fit_transform(all_questions)


def get_response(user_message):
    """Find the most similar question using TF-IDF."""

    message = user_message.strip()

    if not message:
        return "Please type a question so I can help you."

    normalized = re.sub(r"[^a-z0-9\s]", "", message.lower())
    greetings = {"hi", "hello", "hey", "good morning",
                 "good afternoon", "good evening"}

    if normalized in greetings:
        return (
            "Hello! 👋 Welcome to Student Helpdesk AI.\n\n"
            "You can ask me about admissions, courses, fees, "
            "internships, or placements. How can I help you?"
        )

    if normalized in {"thanks", "thank you", "thankyou"}:
        return "You're welcome! 😊 Feel free to ask another question."

    if normalized in {"bye", "goodbye", "see you"}:
        return "Goodbye! 👋 Best wishes for your studies and career."

    user_vector = vectorizer.transform([message])

    similarities = cosine_similarity(
        user_vector, question_vectors
    ).flatten()

    best_index = similarities.argmax()
    best_score = similarities[best_index]

    # Conservative threshold helps avoid unrelated answers.
    if best_score < 0.16:
        return (
            "I'm not fully sure about that question yet. 🤔\n\n"
            "Please try asking about:\n"
            "- Admissions and eligibility\n"
            "- Courses and branches\n"
            "- College fees and scholarships\n"
            "- Internships and skills\n"
            "- Placements and interview preparation\n\n"
            "For official college information, please contact "
            "the relevant department."
        )

    category = question_categories[best_index]

    for item in knowledge_base:
        if item["category"] == category:
            return item["answer"]

    return "Sorry, I couldn't find an answer. Please try again."


# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! 👋 I'm your Student Helpdesk AI.\n\n"
                "I can help with admissions, courses, fees, "
                "internships, and placements. Ask me anything "
                "about these topics!"
            )
        }
    ]


# ---------------- MODERN CUSTOM DESIGN ----------------
st.markdown("""
<style>

/* Dashboard cards */
.dashboard-card {
    position: relative;
    min-height: 190px;
    padding: 22px 18px;
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.8);
    background: rgba(255, 255, 255, 0.88);
    box-shadow: 0 8px 24px rgba(45, 55, 100, 0.08);
    transition: transform 0.25s ease,
                box-shadow 0.25s ease;
    animation: fadeIn 0.6s ease-out;
    margin-bottom: 12px;
}

.dashboard-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 14px 30px rgba(45, 55, 100, 0.15);
}

.dashboard-icon {
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 15px;
    font-size: 26px;
    margin-bottom: 15px;
}

.dashboard-card h3 {
    font-size: 20px;
    margin: 0 0 8px 0;
    color: #243b80;
}

.dashboard-card p {
    color: #64748b;
    font-size: 14px;
    line-height: 1.5;
    min-height: 42px;
    margin-bottom: 0;
}

.admission-card {
    background: linear-gradient(145deg, #fff7ed, #ffffff);
}
.admission-card .dashboard-icon {
    background: #ffedd5;
}

.courses-card {
    background: linear-gradient(145deg, #eff6ff, #ffffff);
}
.courses-card .dashboard-icon {
    background: #dbeafe;
}

.fees-card {
    background: linear-gradient(145deg, #ecfdf5, #ffffff);
}
.fees-card .dashboard-icon {
    background: #d1fae5;
}

.internship-card {
    background: linear-gradient(145deg, #f5f3ff, #ffffff);
}
.internship-card .dashboard-icon {
    background: #ede9fe;
}

.placement-card {
    background: linear-gradient(145deg, #fdf2f8, #ffffff);
}
.placement-card .dashboard-icon {
    background: #fce7f3;
}

@media (max-width: 640px) {
    .dashboard-card {
        min-height: 165px;
        padding: 16px;
    }
}

</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🎓 Student Helpdesk")
    st.write("Your virtual college assistant")

    st.markdown("### Available Topics")
    st.write("🎓 Admissions")
    st.write("📚 Courses")
    st.write("💰 Fees")
    st.write("💼 Internships")
    st.write("🏢 Placements")

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Chat cleared! 👋 What would you like to know?"
                )
            }
        ]
        st.rerun()

    st.caption("Student Helpdesk AI | Minor Project")

# ---------------- MAIN INTERFACE ----------------

st.markdown(
    '<div class="main-title">'
    '🎓 Student Helpdesk AI ✨'
    '</div>',
    unsafe_allow_html=True
)


st.markdown(
    '<div class="subtitle">'
    'Your assistant for college-related questions'
    '</div>',
    unsafe_allow_html=True
)


st.markdown("## ✨ Explore Student Services")
st.caption(
    "Choose a topic below to get help from your virtual college assistant."
)

# Dashboard card layout
card_data = [
    {
        "title": "Admissions",
        "icon": "🎓",
        "description": "Application process, eligibility and documents.",
        "css": "admission-card",
        "question": "How can I apply for admission?"
    },
    {
        "title": "Courses",
        "icon": "📚",
        "description": "Explore engineering branches and programs.",
        "css": "courses-card",
        "question": "Which courses are available?"
    },
    {
        "title": "Fees & Scholarships",
        "icon": "💰",
        "description": "Fee details, payment guidance and scholarships.",
        "css": "fees-card",
        "question": "Are scholarships available?"
    },
    {
        "title": "Internships",
        "icon": "💼",
        "description": "Discover skills, resume tips and internship advice.",
        "css": "internship-card",
        "question": "How can I get an internship?"
    },
    {
        "title": "Placements",
        "icon": "🚀",
        "description": "Prepare for aptitude tests and interviews.",
        "css": "placement-card",
        "question": "How can I prepare for placements?"
    }
]

# Three cards on the first row, two on the second
for start in range(0, len(card_data), 3):
    cards = st.columns(3)

    for col, item in zip(cards, card_data[start:start + 3]):
        with col:
            st.markdown(
                f"""
                <div class="dashboard-card {item['css']}">
                    <div class="dashboard-icon">{item['icon']}</div>
                    <h3>{item['title']}</h3>
                    <p>{item['description']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button(
                f"Explore {item['title']} →",
                key=f"dashboard_{item['title']}",
                use_container_width=True
            ):
                st.session_state.pending_question = item["question"]
                st.rerun()

st.divider()
st.markdown("### 💬 Ask your question")


# Suggested questions
st.write("**Try asking:**")

col1, col2 = st.columns(2)

with col1:
    if st.button("🎓 Admission process", use_container_width=True):
        st.session_state.pending_question = (
            "How can I apply for admission?"
        )

    if st.button("📚 Available courses", use_container_width=True):
        st.session_state.pending_question = (
            "Which courses are available?"
        )

    if st.button("💰 Fee information", use_container_width=True):
        st.session_state.pending_question = (
            "What is the college fee?"
        )

with col2:
    if st.button("💼 Internship guidance", use_container_width=True):
        st.session_state.pending_question = (
            "How can I get an internship?"
        )

    if st.button("🏢 Placement preparation", use_container_width=True):
        st.session_state.pending_question = (
            "How can I prepare for placements?"
        )

    if st.button("🎯 Scholarship information", use_container_width=True):
        st.session_state.pending_question = (
            "Are scholarships available?"
        )

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept typed questions or suggested questions
typed_question = st.chat_input(
    "Type your question here..."
)

pending_question = st.session_state.pop(
    "pending_question", None
)

user_question = pending_question or typed_question

if user_question:
    st.session_state.messages.append(
        {"role": "user", "content": user_question}
    )

    with st.chat_message("user"):
        st.markdown(user_question)

    answer = get_response(user_question)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )

    with st.chat_message("assistant"):
        st.markdown(answer)

st.divider()

st.caption(
    "Note: This is an educational demo. "
    "Verify admission, fee, scholarship, and placement details "
    "with your college before making decisions."
)