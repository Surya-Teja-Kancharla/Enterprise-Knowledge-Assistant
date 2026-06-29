"""
Conversation memory data models.

These models represent a single conversation turn and
an entire conversation session.

Author: Surya Teja
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class ConversationTurn:
    """
    Represents one interaction between the user and assistant.
    """

    question: str
    answer: str
    sources: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ConversationSession:
    """
    Stores all conversation turns for one chat session.
    """

    session_id: str
    turns: List[ConversationTurn] = field(default_factory=list)

    def add_turn(self, turn: ConversationTurn) -> None:
        """
        Add a new conversation turn.

        Args:
            turn: ConversationTurn instance.
        """
        self.turns.append(turn)

    def clear(self) -> None:
        """
        Remove all conversation history.
        """
        self.turns.clear()

    def size(self) -> int:
        """
        Number of conversation turns.
        """
        return len(self.turns)
