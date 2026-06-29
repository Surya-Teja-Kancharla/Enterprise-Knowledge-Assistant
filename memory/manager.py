"""
Conversation Session Manager.

Responsible for:

- Creating conversation sessions
- Retrieving existing sessions
- Removing sessions
- Clearing sessions
- Managing multiple concurrent users

Author: Surya Teja
"""

from __future__ import annotations

import uuid
from typing import Dict, List

from app.core.logger import get_logger
from memory.conversation import ConversationMemory


logger = get_logger(__name__)


class ConversationManager:
    """
    Manages multiple conversation sessions.

    Each session owns its own ConversationMemory.
    """

    def __init__(self) -> None:

        self._sessions: Dict[str, ConversationMemory] = {}

        logger.info(
            "Conversation manager initialized."
        )

    # --------------------------------------------------------
    # Session Creation
    # --------------------------------------------------------

    def create_session(
        self,
    ) -> str:
        """
        Create a new conversation session.

        Returns
        -------
        str
            Generated session ID.
        """

        session_id = str(uuid.uuid4())

        self._sessions[session_id] = ConversationMemory(
            session_id=session_id
        )

        logger.info(
            "Created session %s",
            session_id,
        )

        return session_id

    # --------------------------------------------------------
    # Session Retrieval
    # --------------------------------------------------------

    def get_session(
        self,
        session_id: str,
    ) -> ConversationMemory:
        """
        Retrieve an existing session.

        If the session does not exist,
        it will be created automatically.
        """

        if session_id not in self._sessions:

            logger.info(
                "Session %s not found. Creating new session.",
                session_id,
            )

            self._sessions[session_id] = ConversationMemory(
                session_id=session_id
            )

        return self._sessions[session_id]

    # --------------------------------------------------------
    # Session Removal
    # --------------------------------------------------------

    def remove_session(
        self,
        session_id: str,
    ) -> bool:
        """
        Delete a conversation session.

        Returns
        -------
        bool
            True if removed.
        """

        if session_id not in self._sessions:
            return False

        del self._sessions[session_id]

        logger.info(
            "Removed session %s",
            session_id,
        )

        return True

    # --------------------------------------------------------
    # Session Maintenance
    # --------------------------------------------------------

    def clear_session(
        self,
        session_id: str,
    ) -> bool:
        """
        Clear conversation history while
        preserving the session.
        """

        if session_id not in self._sessions:
            return False

        self._sessions[session_id].clear()

        logger.info(
            "Cleared session %s",
            session_id,
        )

        return True

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    def session_count(
        self,
    ) -> int:
        """
        Number of active sessions.
        """

        return len(self._sessions)

    def active_sessions(
        self,
    ) -> List[str]:
        """
        Return all active session IDs.
        """

        return list(self._sessions.keys())

    # --------------------------------------------------------
    # Utility
    # --------------------------------------------------------

    def exists(
        self,
        session_id: str,
    ) -> bool:
        """
        Check whether a session exists.
        """

        return session_id in self._sessions
