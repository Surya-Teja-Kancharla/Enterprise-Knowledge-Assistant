"""
Enterprise Knowledge Assistant
Conversation Memory Test

Tests:

1. Session creation
2. Adding conversation turns
3. Formatting history
4. Memory trimming
5. Session clearing
6. Session manager

Author: Surya Teja
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from memory.manager import ConversationManager


def print_separator(title: str) -> None:

    print()

    print("=" * 80)

    print(title)

    print("=" * 80)


def test_session_creation(manager: ConversationManager) -> str:
    """
    Test session creation.
    """

    print_separator("SESSION CREATION")

    session_id = manager.create_session()

    print(f"Session ID : {session_id}")

    assert manager.exists(session_id)

    print("[PASS] Session successfully created.")

    return session_id


def test_add_turns(manager: ConversationManager, session_id: str) -> None:
    """
    Test storing conversation turns.
    """

    print_separator("ADDING CONVERSATION TURNS")

    memory = manager.get_session(session_id)

    memory.add(
        question="What is GDPR?",
        answer="GDPR is a European data protection regulation.",
        sources=["GDPR Policy.pdf"],
    )

    memory.add(
        question="Who does it apply to?",
        answer="It applies to organizations processing EU personal data.",
        sources=["GDPR Policy.pdf"],
    )

    memory.add(
        question="What are the penalties?",
        answer="Organizations may face significant fines.",
        sources=["GDPR Policy.pdf"],
    )

    print(f"Conversation Size : {len(memory.history())}")

    assert len(memory.history()) == 3

    print("[PASS] Conversation turns stored successfully.")


def test_history_format(manager: ConversationManager, session_id: str) -> None:
    """
    Test prompt history formatting.
    """

    print_separator("FORMATTED HISTORY")

    memory = manager.get_session(session_id)

    history = memory.format_history()

    print(history)

    assert "User:" in history

    assert "Assistant:" in history

    print()

    print("[PASS] History formatting successful.")


def test_memory_trim(manager: ConversationManager, session_id: str) -> None:
    """
    Test automatic trimming.
    """

    print_separator("MEMORY TRIMMING")

    memory = manager.get_session(session_id)

    max_turns = 5

    for i in range(10):

        memory.add(

            question=f"Question {i}",

            answer=f"Answer {i}",

        )

    history = memory.history()

    print(f"Turns After Trim : {len(history)}")

    assert len(history) <= max_turns

    print("[PASS] Memory trimming works correctly.")


def test_clear_session(manager: ConversationManager, session_id: str) -> None:
    """
    Test clearing memory.
    """

    print_separator("CLEAR SESSION")

    memory = manager.get_session(session_id)

    memory.clear()

    assert memory.history() == []

    print("[PASS] Session cleared successfully.")


def test_remove_session(manager: ConversationManager, session_id: str) -> None:
    """
    Test deleting a session.
    """

    print_separator("REMOVE SESSION")

    removed = manager.remove_session(session_id)

    assert removed

    assert not manager.exists(session_id)

    print("[PASS] Session removed successfully.")


def main() -> None:

    print()

    print("=" * 80)

    print("ENTERPRISE KNOWLEDGE ASSISTANT")

    print("CONVERSATION MEMORY TEST")

    print("=" * 80)

    manager = ConversationManager()

    session_id = test_session_creation(manager)

    test_add_turns(manager, session_id)

    test_history_format(manager, session_id)

    test_memory_trim(manager, session_id)

    test_clear_session(manager, session_id)

    test_remove_session(manager, session_id)

    print()

    print("=" * 80)

    print("ALL MEMORY TESTS PASSED")

    print("=" * 80)


if __name__ == "__main__":
    main()