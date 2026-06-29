"""
Conversation memory implementation.

Maintains a conversation buffer that stores previous
question-answer pairs for contextual conversations.

Author: Surya Teja
"""

from __future__ import annotations

import uuid
from typing import List

from app.core.config import settings
from memory.models import ConversationSession, ConversationTurn


class ConversationMemory:
    """
    Stores conversation history for one session.
    """

    def __init__(self, session_id: str | None = None):
        self.session = ConversationSession(
            session_id=session_id or str(uuid.uuid4())
        )

    @property
    def session_id(self) -> str:
        """
        Return session ID.
        """
        return self.session.session_id

    def add(
        self,
        question: str,
        answer: str,
        sources: List[str] | None = None,
    ) -> None:
        """
        Store a completed conversation turn.
        """

        turn = ConversationTurn(
            question=question,
            answer=answer,
            sources=sources or [],
        )

        self.session.add_turn(turn)

        self._trim_history()

    def history(self) -> List[ConversationTurn]:
        """
        Return all stored conversation turns.
        """
        return self.session.turns

    def last_turn(self) -> ConversationTurn | None:
        """
        Return the most recent conversation turn.
        """
        if not self.session.turns:
            return None

        return self.session.turns[-1]

    def clear(self) -> None:
        """
        Clear conversation history.
        """
        self.session.clear()

    def format_history(self) -> str:
        """
        Convert conversation history into text suitable
        for an LLM prompt.
        """

        if not self.session.turns:
            return ""

        lines = []

        for turn in self.session.turns:
            lines.append(f"User: {turn.question}")
            lines.append(f"Assistant: {turn.answer}")
            lines.append("")

        return "\n".join(lines).strip()

    def _trim_history(self) -> None:
        """
        Keep only the most recent conversation turns.
        """

        max_turns = settings.MEMORY_MAX_HISTORY

        if len(self.session.turns) <= max_turns:
            return

        self.session.turns = self.session.turns[-max_turns:]
