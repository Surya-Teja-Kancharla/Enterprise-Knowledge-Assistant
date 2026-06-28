"""
Enterprise Knowledge Assistant
Prompt Templates

Defines the system prompt used by the RAG pipeline.

The prompt is intentionally strict to:

1. Prevent hallucinations.
2. Force answers from retrieved context only.
3. Admit when information is unavailable.
4. Always cite document sources.
"""

from __future__ import annotations

from typing import List

from langchain_core.documents import Document


# ---------------------------------------------------------------------
# Fixed fallback response (assignment requirement)
# ---------------------------------------------------------------------

NO_INFORMATION_RESPONSE = (
    "I could not find this information in the provided knowledge base."
)


# ---------------------------------------------------------------------
# System Prompt
# ---------------------------------------------------------------------

SYSTEM_PROMPT = f"""
You are an Enterprise Knowledge Assistant.

Your job is to answer employee questions ONLY using the retrieved context.

Rules:

1. Use ONLY the provided context.
2. Do NOT use outside knowledge.
3. Do NOT guess.
4. Do NOT fabricate information.
5. If the answer cannot be found in the context,
   respond EXACTLY:

"{NO_INFORMATION_RESPONSE}"

6. Keep answers concise and professional.
7. Always include source citations.
8. If multiple documents support the answer,
   cite all relevant documents.
""".strip()


# ---------------------------------------------------------------------
# User Prompt Template
# ---------------------------------------------------------------------

USER_PROMPT_TEMPLATE = """
Question:
{question}

Retrieved Context:
{context}

Answer:
""".strip()

# ---------------------------------------------------------------------
# Context Formatter
# ---------------------------------------------------------------------

def format_context(documents: List[Document]) -> str:
    """
    Converts retrieved LangChain Documents
    into a formatted prompt context.

    Each chunk contains metadata that will later
    become citations.
    """

    if not documents:
        return ""

    sections = []

    for i, doc in enumerate(documents, start=1):

        metadata = doc.metadata

        source = metadata.get("source", "Unknown")

        page = metadata.get("page", "?")

        category = metadata.get("category", "general")

        section = (
            f"[Document {i}]\n"
            f"Source: {source}\n"
            f"Category: {category}\n"
            f"Page: {page}\n\n"
            f"{doc.page_content.strip()}"
        )

        sections.append(section)

    return "\n\n----------------------------------------\n\n".join(sections)

# ---------------------------------------------------------------------
# Prompt Builder
# ---------------------------------------------------------------------

def build_prompt(
    question: str,
    documents: List[Document],
) -> str:
    """
    Builds the final prompt supplied to the LLM.
    """

    context = format_context(documents)

    return USER_PROMPT_TEMPLATE.format(
        question=question,
        context=context,
    )

# ---------------------------------------------------------------------
# Citation Formatter
# ---------------------------------------------------------------------

def format_citations(
    documents: List[Document],
) -> str:
    """
    Creates a readable citation section.
    """

    if not documents:
        return ""

    citations = []

    seen = set()

    for doc in documents:

        source = doc.metadata.get("source", "Unknown")

        page = doc.metadata.get("page", "?")

        citation = f"{source} (Page {page})"

        if citation not in seen:
            seen.add(citation)
            citations.append(citation)

    return "\n".join(f"- {item}" for item in citations)

__all__ = [
    "SYSTEM_PROMPT",
    "USER_PROMPT_TEMPLATE",
    "NO_INFORMATION_RESPONSE",
    "format_context",
    "build_prompt",
    "format_citations",
]

