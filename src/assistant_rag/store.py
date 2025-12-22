from __future__ import annotations

from collections import defaultdict
from typing import DefaultDict, Dict, List


class ConversationStore:
    def __init__(self, max_history_messages: int) -> None:
        self._messages: DefaultDict[str, List[Dict[str, str]]] = defaultdict(list)
        self._max_history_messages = max_history_messages

    def append(self, conversation_id: str, role: str, content: str) -> None:
        history = self._messages[conversation_id]
        history.append({"role": role, "content": content})
        if len(history) > self._max_history_messages:
            self._messages[conversation_id] = history[-self._max_history_messages :]

    def history(self, conversation_id: str) -> List[Dict[str, str]]:
        return list(self._messages.get(conversation_id, []))
