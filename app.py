"""
Enterprise Knowledge Assistant-NovaTech
Streamlit Frontend

------
Application setup, layout, sidebar,
custom styling and session state.
"""

from __future__ import annotations

from datetime import datetime
import uuid

import requests
import streamlit as st

from app.core.config import settings


# ======================================================================
# Page Configuration
# ======================================================================

st.set_page_config(
    page_title="Enterprise Knowledge Assistant-NovaTech Solutions",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ======================================================================
# Constants
# ======================================================================

API_BASE_URL = "http://127.0.0.1:8000"

PRIMARY_COLOR = "#3B5BA9"      # muted blue, not neon
TEXT_COLOR = "#1F2937"         # near-black, soft
MUTED_TEXT = "#6B7280"         # gray for captions
SUCCESS_COLOR = "#2F855A"
WARNING_COLOR = "#B7791F"
ERROR_COLOR = "#C53030"
CARD_BG = "#FFFFFF"
PAGE_BG = "#F5F6F8"
BORDER_COLOR = "#E2E5EA"


# ======================================================================
# Session State
# ======================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------------------------------------------
# Conversation Session
# ----------------------------------------------------------

if "session_id" not in st.session_state:

    st.session_state.session_id = str(
        uuid.uuid4()
    )

if "api_status" not in st.session_state:
    st.session_state.api_status = "Unknown"

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = None


# ======================================================================
# Custom CSS
# ======================================================================
# NOTE: Global theme (background/text colors for native widgets) is
# handled entirely by .streamlit/config.toml — that's the only source
# of truth for Streamlit's own components (st.metric, st.info, etc).
# This block ONLY styles the custom HTML elements introduced below
# (.header, .metric-card, .footer). It deliberately does NOT touch
# html/body/section wildcards, because doing so overrides config.toml
# in places it shouldn't and produces inconsistent contrast.

st.markdown(
    f"""
<style>

/* Header ----------------------------------------------------------*/
.header {{
    padding: 24px 28px;
    border-radius: 12px;
    background: {PRIMARY_COLOR};
    color: #FFFFFF;
    margin-bottom: 24px;
}}
.header h1 {{
    color: #FFFFFF;
    margin-bottom: 4px;
}}
.header p {{
    color: #E8ECF7;
    margin: 0;
}}

/* Cards -------------------------------------------------------------*/
.metric-card {{
    padding: 16px 18px;
    border-radius: 10px;
    background: {CARD_BG};
    border: 1px solid {BORDER_COLOR};
    color: {TEXT_COLOR};
    margin-bottom: 12px;
}}
.metric-card h4 {{
    color: {TEXT_COLOR};
    margin: 0;
}}

/* Footer --------------------------------------------------------*/
.footer {{
    text-align: center;
    color: {MUTED_TEXT};
    padding: 20px;
}}

/* Sidebar background — config.toml already sets sidebar text color
   via secondaryBackgroundColor/textColor, so we only add the border
   here rather than re-declaring color on every child element. */
section[data-testid="stSidebar"] {{
    border-right: 1px solid {BORDER_COLOR};
}}

/* Buttons -----------------------------------------------------------*/
button[kind="primary"] {{
    background-color: {PRIMARY_COLOR} !important;
    border-color: {PRIMARY_COLOR} !important;
}}

</style>
""",
    unsafe_allow_html=True,
)


# ======================================================================
# Sidebar
# ======================================================================

with st.sidebar:

    st.title("⚙️ Dashboard")

    st.divider()

    st.subheader("Application")

    st.write(settings.APP_NAME)

    st.caption("Enterprise RAG System")

    st.divider()

    st.subheader("Backend")

    st.write(f"**API** : `{API_BASE_URL}`")

    st.write(f"**LLM** : `{settings.GROQ_MODEL}`")

    st.write(f"**Embeddings** : `{settings.EMBEDDING_MODEL}`")

    st.write(
        f"**Vector DB** : `{settings.VECTOR_COLLECTION_NAME}`"
    )

    st.divider()

    st.subheader("Retrieval")

    st.metric(
        "Top K",
        settings.TOP_K,
    )

    st.metric(
        "Chunk Size",
        settings.CHUNK_SIZE,
    )

    st.metric(
        "Chunk Overlap",
        settings.CHUNK_OVERLAP,
    )

    st.divider()

    st.subheader("Session")

    st.caption(
        f"Session ID\n"
        f"{st.session_state.session_id[:8]}..."
    )

    st.metric(
        "Questions Asked",
        len(st.session_state.messages),
    )

    if st.session_state.api_status == "Online":
        st.success("🟢 API Online")
    elif st.session_state.api_status == "Offline":
        st.error("🔴 API Offline")
    else:
        st.info("⚪ API Unknown")

    if st.session_state.last_refresh:
        st.caption(
            f"Last Request:\n{st.session_state.last_refresh.strftime('%H:%M:%S')}"
        )


# ======================================================================
# Header
# ======================================================================

st.markdown(
    """
<div class="header">

<h1>Enterprise Knowledge Assistant</h1>

<p>
AI-powered Retrieval-Augmented Generation (RAG)
system for querying enterprise knowledge bases.
</p>

</div>
""",
    unsafe_allow_html=True,
)


# ======================================================================
# Welcome Section
# ======================================================================

left, right = st.columns([2, 1])

with left:

    st.markdown(
        """
### Welcome

Ask questions about:

- HR Policies
- Compliance Documents
- Product Documentation
- Technical Guides
- Process Manuals
- Customer FAQs

The assistant retrieves the most relevant
enterprise documents before generating an answer.
"""
    )

with right:

    st.info(
        """
**Current Configuration**

• Groq Llama 3.3

• ChromaDB

• BGE Embeddings

• Top K = 5

• MMR Retrieval
"""
    )


st.divider()


# ======================================================================
# Question Submission
# ======================================================================

st.subheader("Ask a Question")

question = st.text_area(
    label="",
    placeholder="Example: What is the employee leave policy?",
    height=120,
    key="question_input",
)

col1, col2, col3 = st.columns([1, 1, 6])

with col1:
    ask_button = st.button(
        "🚀 Ask",
        use_container_width=True,
        type="primary",
    )

with col2:
    clear_button = st.button(
        "🗑️ Clear",
        use_container_width=True,
    )

# ----------------------------------------------------------------------
# Clear Chat
# ----------------------------------------------------------------------
if clear_button:
    st.session_state.messages = []
    st.session_state.question_input = ""

    # Start a brand-new conversation
    st.session_state.session_id = str(uuid.uuid4())
    st.success("Conversation memory cleared.")
    st.rerun()

# ----------------------------------------------------------------------
# API Request
# ----------------------------------------------------------------------
if ask_button:
    question = question.strip()
    if not question:
        st.warning(
            "Please enter a question."
        )
    else:
        with st.spinner(
            "Searching enterprise knowledge base..."
        ):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/ask",
                    json={
                        "question": question,
                        "session_id": st.session_state.session_id,
                    },
                    timeout=120,
                )

                response.raise_for_status()
                result = response.json()
                st.session_state.messages.append(
                    {
                        "question": question,
                        "response": result,
                    }
                )
                st.session_state.api_status = "Online"
                st.session_state.last_refresh = (
                    datetime.now()
                )
            except requests.exceptions.Timeout:
                st.session_state.api_status = "Offline"
                st.error(
                    "The request timed out."
                )
            except requests.exceptions.ConnectionError:
                st.session_state.api_status = "Offline"
                st.error(
                    "Cannot connect to the FastAPI server.\n\n"
                    "Make sure the backend is running:\n\n"
                    "uvicorn app.api.main:app --reload"
                )
            except requests.exceptions.HTTPError as exc:
                st.session_state.api_status = "Online"
                try:
                    error = response.json()
                    message = error.get(
                        "detail",
                        str(exc),
                    )
                except Exception:
                    message = str(exc)
                st.error(message)
            except Exception as exc:
                st.session_state.api_status = "Unknown"
                st.exception(exc)


# ======================================================================
# Response Rendering
# ======================================================================

if st.session_state.messages:
    st.divider()
    st.header("Response")

    latest = st.session_state.messages[-1]
    response = latest["response"]

    # ----------------------------------------------------------
    # Answer Card
    # ----------------------------------------------------------
    st.markdown(
        """
        <div class="metric-card">
        <h4>💬 Answer</h4>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write(response["answer"])
    st.write("")

    # ----------------------------------------------------------
    # Metrics
    # ----------------------------------------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        confidence = response.get(
            "confidence",
            0.0,
        )
        st.metric(
            "Confidence",
            f"{confidence:.2f}",
        )
        st.progress(
            min(float(confidence), 1.0)
        )

    with col2:
        latency = response.get(
            "latency",
            0.0,
        )
        st.metric(
            "Latency",
            f"{latency:.2f} sec",
        )

    with col3:
        retrieved = response.get(
            "retrieved_documents",
            0,
        )
        st.metric(
            "Retrieved Chunks",
            retrieved,
        )

    st.divider()

    # ----------------------------------------------------------
    # Source Citations
    # ----------------------------------------------------------
    st.subheader("📚 Sources")

    sources = response.get(
        "sources",
        [],
    )

    if not sources:
        st.warning(
            "No supporting sources were returned."
        )
    else:
        for index, source in enumerate(
            sources,
            start=1,
        ):
            title = (
                f"Source {index} • "
                f"{source['document']}"
            )
            with st.expander(title):
                st.write(
                    f"**Document:** "
                    f"{source['document']}"
                )
                st.write(
                    f"**Page:** "
                    f"{source['page']}"
                )
                st.write(
                    f"**Category:** "
                    f"{source['category']}"
                )
                chunk_id = source.get(
                    "chunk_id",
                    "",
                )
                if chunk_id:
                    st.code(
                        chunk_id,
                        language="text",
                    )
                else:
                    st.caption(
                        "Chunk ID unavailable."
                    )

    st.divider()


# ======================================================================
# Backend Health Check
# ======================================================================

def check_backend_health() -> bool:
    """
    Check whether the FastAPI backend is available.
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/health",
            timeout=3,
        )
        return response.status_code == 200
    except Exception:
        return False


backend_online = check_backend_health()


# ======================================================================
# Sidebar Status
# ======================================================================

with st.sidebar:
    st.divider()
    st.subheader("System Status")

    if backend_online:
        st.success("🟢 Backend Online")
    else:
        st.error("🔴 Backend Offline")

    st.metric(
        "Conversation Length",
        len(st.session_state.messages),
    )

    if st.session_state.messages:
        latest = st.session_state.messages[-1]["response"]
        st.metric(
            "Last Confidence",
            f"{latest.get('confidence', 0):.2f}",
        )
        st.metric(
            "Last Latency",
            f"{latest.get('latency', 0):.2f}s",
        )
    else:
        st.metric(
            "Last Confidence",
            "--",
        )
        st.metric(
            "Last Latency",
            "--",
        )


# ======================================================================
# Chat History
# ======================================================================

if st.session_state.messages:
    st.divider()
    st.header("Conversation History")

    for idx, conversation in enumerate(
        reversed(st.session_state.messages),
        start=1,
    ):
        with st.expander(
            f"Question {len(st.session_state.messages)-idx+1}"
        ):
            st.markdown("#### Question")
            st.write(
                conversation["question"]
            )
            st.markdown("#### Answer")
            st.write(
                conversation["response"]["answer"]
            )


# ======================================================================
# Quick Examples
# ======================================================================

st.divider()
st.subheader("Example Questions")
example_cols = st.columns(2)
examples = [
    "What is the password policy?",
    "Explain the leave policy.",
    "How do I onboard a new employee?",
    "What is the software release process?",
    "What are the subscription plans?",
    "How do I reset my password?",
]

for i, example in enumerate(examples):
    with example_cols[i % 2]:
        st.info(example)


# ======================================================================
# Footer
# ======================================================================

st.divider()
st.caption(
    "Enterprise Knowledge Assistant • "
    "FastAPI • Streamlit • ChromaDB • "
    "BGE Embeddings • Groq Llama 3.3"
)
st.caption(
    "Developed as a production-oriented "
    "Retrieval-Augmented Generation (RAG) system."
)
