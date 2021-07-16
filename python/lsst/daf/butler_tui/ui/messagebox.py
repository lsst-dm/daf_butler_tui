"""Helper methods and classes for UI part.
"""
from __future__ import annotations

__all__ = ["UIMessageBox", "UIPopUpMessageBox"]

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


class UIMessageBox(urwid.WidgetWrap):
    """
    Widget implementing simple message box.

    Consists of a text widget with a message and few buttons. When
    button is clicked this widget generates 'selected' signal with a
    value which corresponds to that particular button. Optionally Escape
    key can be configured to also generate 'selected' signal with
    specified value.

    """

    signals = ['selected']

    def __init__(self, title: str, message: str, buttons: List[Tuple[str, Any]],
                 escape_value: Any = None, attr: str = 'messagebox'):
        """
        @param title:    Menu title
        @param message:  Message string
        @param buttons:  List of ('button_text', value) tuples, value is used for
                         'selected' signal when corresponding button is clicked
        @param escape_value:  if not None then escape key will generate
                         'selected' signal with this value
        """

        stretch = urwid.Text(' ' * 132, wrap='clip')  # stretch space to the left of the buttons
        items = [stretch]
        for name, value in buttons:
            button = urwid.Button(name)
            urwid.connect_signal(button, 'click', self._callback, user_args=[value])
            size = len(name) + 4
            items.append((size, urwid.AttrMap(button, None, attr + '-focus')))
        items += [stretch]
        button_row = urwid.Columns(items, 2)
        text = urwid.Text(message)
        pile = urwid.Pile([text, urwid.Divider(u'\u2500'), button_row])
        filler = urwid.Filler(pile, height='flow')     # need to wrap it into a box widget
        linebox = urwid.LineBox(filler, title)         # wrap it all into linebox with title
        super().__init__(urwid.AttrMap(linebox, attr))

        self.escape_value = escape_value

    def _callback(self, value: Any, button: urwid.Button) -> None:
        self._emit('selected', value)

    def keypress(self, size: Tuple, key: str) -> Optional[str]:
        _log.debug("UIMenu: received key: %s", key)
        if self.escape_value is not None and key == 'esc':
            _log.debug("UIMenu: escape key: %s", self.escape_value)
            self._emit('selected', self.escape_value)
            return None
        return super().keypress(size, key)


class UIPopUpMessageBox(UIPopUp):
    """Pop-up showing a message box.

    Parameters
    ----------
    title, options, escape_value : same as for `UIMenu` class
    callback : `method`, optional
        Method to call when any buton is activated.
    cols : `int`
        Width of a pop-up window
    """
    def __init__(self, title: str, message: str, buttons: List[urwid.Button],
                 callback: Optional[Callable] = None, escape_value: Any = None,
                 attr: str = 'messagebox', cols: int = 48):

        mbox = UIMessageBox(title, message, buttons, escape_value, attr)
        # NOTE: the order of callbacks is important
        urwid.connect_signal(mbox, 'selected', self.close)
        if callback is not None:
            urwid.connect_signal(mbox, 'selected', callback)

        rows = urwid.Text(message).rows((cols,))
        pop_up_size = (cols + 2, rows + 4)

        super().__init__(mbox, pop_up_size)

    def hints(self) -> List[Tuple[str, str]]:
        return [("Esc", "Cancel")]
