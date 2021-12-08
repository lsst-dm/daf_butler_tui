"""Helper methods and classes for UI part.
"""
from __future__ import annotations

__all__ = ["UIMenu", "UIPopUpMenu"]

#--------------------------------
#  Imports of standard modules --
#--------------------------------
import logging
from typing import Any, Callable, List, Optional, Tuple

#-----------------------------
# Imports for other modules --
#-----------------------------
import urwid
from .popup import UIPopUp

#----------------------------------
# Local non-exported definitions --
#----------------------------------

_log = logging.getLogger(__name__)

#------------------------
# Exported definitions --
#------------------------


class UIMenu(urwid.WidgetWrap):
    """
    Widget implementing simple menu.

    Consists of a ListBox with a bunch of buttons, when button
    is clicked this widget generates 'selected' signal with a value
    which corresponds to that particular button. Optionally Escape
    key can be configured to also generate 'selected' signal with
    specified value.
    """

    signals = ['selected']

    def __init__(self, title: str, options: List[Tuple[str, Any]], escape_value: Any = None):
        """
        @param title:    Menu title
        @param options:  List of tuples (string, value)
        @param escape_value:  if not None then escape key will generate
                         'selected' signal with this value
        """

        items = []
        for name, value in options:
            button = urwid.Button(name)
            urwid.connect_signal(button, 'click', self._callback, user_args=[value])
            items.append(urwid.AttrMap(button, None, 'menu-focus'))
        listbox = urwid.ListBox(urwid.SimpleFocusListWalker(items))
        linebox = urwid.LineBox(listbox, title)
        self.__super.__init__(urwid.AttrMap(linebox, 'menu'))

        self.escape_value = escape_value

    def _callback(self, value: Any, button: urwid.Button) -> None:
        self._emit('selected', value)

    def keypress(self, size: Tuple, key: str) -> Optional[str]:
        _log.debug("UIMenu: received key: %s", key)
        if self.escape_value is not None and key == 'esc':
            _log.debug("UIMenu: escape key: %s", self.escape_value)
            self._emit('selected', self.escape_value)
            return None
        return self.__super.keypress(size, key)


class UIPopUpMenu(UIPopUp):
    """Pop-up showing a menu.

    Parameters
    ----------
    title, message, buttons, escape_value, attr :
        same as for `UIMessageBox` class
    callback : `method`
        Method to call when menu item is selected.
    cols : `int`
        Width of a pop-up window
    """
    def __init__(self, title: str, options: List[Tuple[str, Any]], callback: Callable,
                 escape_value: Any = None, cols: int = 24):

        menu = UIMenu(title, options, 'cancel')
        # NOTE: the order of callbacks is important
        urwid.connect_signal(menu, 'selected', self.close)
        urwid.connect_signal(menu, 'selected', callback)

        pop_up_size = (cols, len(options) + 2)

        self.__super.__init__(menu, pop_up_size)

    def hints(self) -> List[Tuple[str, str]]:
        return [("Esc", "Cancel"), ("Enter", "Select")]
