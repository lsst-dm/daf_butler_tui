"""Helper methods and classes for UI part.
"""
from __future__ import annotations

__all__ = ["UIListBox", "UIListBoxWithHeader"]

#--------------------------------
#  Imports of standard modules --
#--------------------------------
import logging
from typing import Any, Dict, Optional, Tuple

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


class UIListBox(urwid.ListBox):
    """
    This is an extension of the ListBox with few additional niceties.

    Constructor takes the same arguments as urwid.ListBox.
    """

    def __init__(self, *args: Any):
        urwid.ListBox.__init__(self, *args)

        # remap home/end keys
        command_map: Dict[str, str] = self._command_map.copy()  # type: ignore
        command_map['home'] = 'cursor top'
        command_map['end'] = 'cursor bottom'
        self._command_map = command_map

    def keypress(self, size: Tuple, key: str) -> Optional[str]:
        """
        Define reaction to some special keys like begin/end
        """

        # see if any child wants to handle
        key = urwid.ListBox.keypress(self, size, key)

        command = self._command_map[key]
        _log.debug("UIListBox: received key: %s -> %s", key, command)

        if command in ["cursor top", "cursor bottom"]:
            # only support it if walker has positions() method
            positions_fn = getattr(self.body, 'positions', None)
            if positions_fn is not None:
                try:
                    if command == "cursor top":
                        positions = positions_fn(False)
                        self.change_focus(size, positions[0], 0, 'below')
                        _log.debug("change focus to: %s", positions[0])
                    else:
                        positions = positions_fn(True)
                        self.change_focus(size, positions[0], 0, 'above')
                        _log.debug("change focus to: %s", positions[0])
                except Exception as exc:
                    _log.error('exception: %s', exc, exc_info=True)
                return None

        return key


class UIListBoxWithHeader(urwid.Frame):
    """
    Combination of listbox and headers/footers.
    """

    def __init__(self, body: urwid.ListWalker, header: Optional[urwid.Widget] = None,
                 footer: Optional[urwid.Widget] = None, focus_part: str = 'body'):
        """
        @param body:  walker instance passed to ListBox constructor or a list of
                      items, each item will be wrapped into AttrMap.

        Other parameters are passed to Frame constructor
        """

        if getattr(body, 'get_focus', None) is None:
            # wrap into SimpleFocusListWalker
            body = [urwid.AttrMap(item, "list-item", "list-selected") for item in body]
            body = urwid.SimpleFocusListWalker(body)

        listbox = UIListBox(body)
        if header:
            header = urwid.AttrMap(header, 'list-colhead')
        if footer:
            footer = urwid.AttrMap(footer, 'list-colhead')
        body = urwid.AttrMap(listbox, 'body')
        urwid.Frame.__init__(self, body, header=header, footer=footer, focus_part=focus_part)
