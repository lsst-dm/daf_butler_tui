"""Helper methods and classes for UI part.
"""
from __future__ import annotations

__all__ = ["UIHints"]


#--------------------------------
#  Imports of standard modules --
#--------------------------------
import logging
from typing import List, Tuple, Union

#-----------------------------
# Imports for other modules --
#-----------------------------
import urwid

#----------------------------------
# Local non-exported definitions --
#----------------------------------

_log = logging.getLogger(__name__)

#------------------------
# Exported definitions --
#------------------------


class UIHints(urwid.WidgetWrap):
    """This is a line of text which displays "hints" which are typically
    keyboard shortcuts
    """

    def __init__(self, attr: str = "hint", attr_high: str = "hint-hight"):
        self._attr = attr
        self._attr_high = attr_high
        self._hints = urwid.Text("", wrap='clip')
        super().__init__(urwid.AttrMap(self._hints, self._attr))

        self._hint_stack: List[Union[str, List]] = []

    def push_hints(self, hints: List[Tuple[str, str]]) -> None:
        """Pushes one more level of hints.
        """
        _log.debug("UIHints: push_hints: _hint_stack=%s", self._hint_stack)
        _log.debug("UIHints: push_hints: hints=%s", hints)
        self._hint_stack.append("")
        self.set_hints(hints)

    def set_hints(self, hints: List[Tuple[str, str]]) -> None:
        """Sets hint string (e.g. "^Q: Exit")
        """
        message = []
        for key, action in hints:
            message += [' ', ('hint-high', key), ':' + action]
        _log.debug("UIHints: set_hints: message=%s", message)
        if self._hint_stack:
            self._hint_stack[-1] = message
            _log.debug("UIHints: set_hints: _hint_stack=%s", self._hint_stack)
        self._hints.set_text(message or "")

    def pop_hints(self) -> None:
        """Restores previous level of hints"""
        _log.debug("UIHints: pop_hints: _hint_stack=%s", self._hint_stack)
        if self._hint_stack:
            del self._hint_stack[-1]
        message = self._hint_stack[-1] if self._hint_stack else ""
        _log.debug("UIHints: pop_hints: message=%s", message)
        self._hints.set_text(message)
