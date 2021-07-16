"""Helper methods and classes for UI part.
"""
from __future__ import annotations

__all__ = ["UIKeysInput", "UIPopUpKeysInput", "UIPopUpKeysInputHelp"]

#--------------------------------
#  Imports of standard modules --
#--------------------------------
import logging
from typing import List, Optional, Tuple, Type

#-----------------------------
# Imports for other modules --
#-----------------------------
import urwid
from .messagebox import UIPopUpMessageBox
from .popup import UIPopUp
from . import time_edit

#----------------------------------
# Local non-exported definitions --
#----------------------------------

_log = logging.getLogger(__name__)

#------------------------
# Exported definitions --
#------------------------


class UIKeyInputRunlb(urwid.WidgetWrap):
    second_caption = "LBN"
    signals = ['activated']

    _stored_values = {"since": (0, 0), "until": (0, 0)}

    def __init__(self, kind: str, attr: str = 'editbox'):
        self.kind = kind
        run, lbn = self._stored_values[kind]
        self.run_edit = urwid.IntEdit((attr, "Run"), run)
        self.lbn_edit = urwid.IntEdit((attr, self.second_caption), lbn)
        columns = urwid.Columns([(10, self.run_edit), (10, self.lbn_edit)], 1)
        super().__init__(urwid.AttrMap(columns, attr + "-field"))

    def value(self) -> int:
        run = self.run_edit.value()
        lbn = self.lbn_edit.value()
        self._stored_values[self.kind] = (run, lbn)
        return (run << 32) + (lbn & 0xFFFFFFFF)

    def keypress(self, size: Tuple, key: str) -> Optional[str]:
        if key == 'enter':
            self._emit("activated")
            return None
        return super().keypress(size, key)

    @classmethod
    def combine(cls, since: int, until: int) -> Tuple[int, int]:
        return since, until


class UIKeyInput_runevt(UIKeyInputRunlb):
    second_caption = "Event"

    _stored_values = {"since": (0, 0), "until": (0, 0)}


class UIKeyInputTime(urwid.WidgetWrap):
    signals = ['activated']

    _stored_values = {"since": "now - 1d", "until": "now"}

    def __init__(self, kind: str, attr: str = 'editbox'):

        self.kind = kind
        time_str = self._stored_values[kind]
        self.edit = urwid.Edit("", time_str)
        super().__init__(urwid.AttrMap(self.edit, attr + "-field"))

    def value(self) -> str:
        value = self.edit.get_edit_text()
        self._stored_values[self.kind] = value
        return value

    def keypress(self, size: Tuple, key: str) -> Optional[str]:
        if key == 'enter':
            self._emit("activated")
            return None
        return super().keypress(size, key)

    @classmethod
    def combine(cls, since: str, until: str) -> Tuple[int, int]:
        return time_edit.combine(since, until)


class UIKeyInput_unknown(urwid.WidgetWrap):
    signals = ['activated']

    _stored_values = {"since": 0, "until": 0}

    def __init__(self, kind: str, attr: str = 'editbox'):
        self.kind = kind
        init_value = self._stored_values[kind]
        self.edit = urwid.IntEdit("", init_value)
        super().__init__(urwid.AttrMap(self.edit, attr + "-field"))

    def value(self) -> int:
        value = self.edit.value()
        self._stored_values[self.kind] = value
        return value

    def keypress(self, size: Tuple, key: str) -> Optional[str]:
        if key == 'enter':
            self._emit("activated")
            return None
        return super().keypress(size, key)

    @classmethod
    def combine(cls, since: int, until: int) -> Tuple[int, int]:
        return since, until


def UIKeyInputClass(iov_type: str) -> Type:
    if iov_type == "run-lumi":
        return UIKeyInputRunlb
    elif iov_type == "run-event":
        return UIKeyInput_runevt
    elif iov_type == "time":
        return UIKeyInputTime
    else:
        return UIKeyInput_unknown


class UIKeysInput(urwid.WidgetWrap):

    signals = ['selected', 'cancelled', 'help']

    def __init__(self, title: str, message: str, iov_type: str, attr: str = 'editbox'):
        """
        @param title:    Menu title
        @param message:  Message string
        @param iov_type: Folder IOV type, one of CoolDB.IOV_* constants
        """
        self.iov_type = iov_type
        self.KeyInputClass = UIKeyInputClass(iov_type)
        stretch = urwid.Text(' ' * 132, wrap='clip')  # stretch space to the left of the buttons
        buttons = []
        button = urwid.Button("Cancel")
        urwid.connect_signal(button, 'click', self._cancelled)
        buttons.append((10, urwid.AttrMap(button, None, attr + '-focus')))
        button = urwid.Button("OK")
        urwid.connect_signal(button, 'click', self._callback)
        buttons.append((6, urwid.AttrMap(button, None, attr + '-focus')))
        buttons += [stretch]
        button = urwid.Button("Help")
        urwid.connect_signal(button, 'click', self._help)
        buttons.append((8, urwid.AttrMap(button, None, attr + '-focus')))
        button_row = urwid.Columns(buttons, 2)

        stretch = urwid.Text(' ' * 132, wrap='clip')
        self.since = self.KeyInputClass("since", attr)
        since = urwid.Columns([(6, urwid.Text("Since:")), ('weight', 2, self.since), stretch], 1, 1)
        self.until = self.KeyInputClass("until", attr)
        until = urwid.Columns([(6, urwid.Text("Until:")), ('weight', 2, self.until), stretch], 1, 1)
        pile = urwid.Pile([urwid.Text(message), since, until, urwid.Divider(u'\u2500'), button_row])
        filler = urwid.Filler(pile, height='flow')     # need to wrap it into a box widget
        linebox = urwid.LineBox(filler, title)         # wrap it all into linebox with title

        urwid.connect_signal(self.since, 'activated', self._callback)
        urwid.connect_signal(self.until, 'activated', self._callback)

        super().__init__(urwid.AttrMap(linebox, attr))

    def _cancelled(self, button: Optional[urwid.Button]) -> None:
        self._emit("cancelled")

    def _help(self, button: Optional[urwid.Button]) -> None:
        _log.debug("UIKeysInput: emitting help")
        self._emit("help")

    def _callback(self, button: Optional[urwid.Button]) -> None:
        since = self.since.value()
        until = self.until.value()
        since, until = self.KeyInputClass.combine(since, until)
        self._emit("selected", since, until)

    def keypress(self, size: Tuple, key: str) -> Optional[str]:
        _log.debug("UIKeysInput: received key: %s", key)
        if key == 'esc':
            self._cancelled(None)
            return None
        if key == 'f1':
            self._help(None)
            return None
        return super().keypress(size, key)


class UIPopUpKeysInput(UIPopUp):
    """Pop-up showing a keys input box.

    Parameters
    ----------
    title, options, escape_value : same as for `UIMenu` class
    callback : `method`, optional
        Method to call when any buton is activated.
    cols : `int`
        Width of a pop-up window
    """

    signals = ["selected", "help"]

    def __init__(self, title: str, message: str, iov_type: str, attr: str = 'editbox', cols: int = 48):

        mbox = UIKeysInput(title, message, iov_type, attr)
        # NOTE: the order of callbacks is important
        urwid.connect_signal(mbox, 'selected', self.close)
        urwid.connect_signal(mbox, 'selected', self._callback)
        urwid.connect_signal(mbox, 'help', self.close)
        urwid.connect_signal(mbox, 'help', self._help)
        urwid.connect_signal(mbox, 'cancelled', self.close)

        rows = urwid.Text(message).rows((cols,))
        pop_up_size = (cols + 2, rows + 6)

        super().__init__(mbox, pop_up_size)

    def _callback(self, widget: urwid.Widget, since: int, until: int) -> None:
        self._emit("selected", since, until)

    def _help(self, widget: urwid.Widget) -> None:
        _log.debug("UIPopUpKeysInput: emitting help")
        self._emit("help")

    def hints(self) -> List[Tuple[str, str]]:
        return [("Esc", "Cancel"), ("Enter", "OK"), ("F1", "Help")]


_help = """
IOV selection dialog allows you to select a range of IOVs to display on the \
next panel. Depending on the type of folder IOV can be specified as a pair of:
  - timestamp
  - run number and LB number
  - run number and event number (rare)
  - a 64-bit integer (for folders of unknown type)

Timestamp input dialog accepts time expressions which include a combination \
of absolute and relative time. Absolute time is expressed in UTC time zone \
and can have one of the formats:
  - special constant "now", "today", "tomorrow", or "yesterday"
  - date expressed in ISO format, e.g. "2020-01-01"
  - time expressed in ISO format, seconds are optional, e.g. "2020-01-01 10:21"

Relative time can be specified as number of years, months, days, hours, \
minutes, or seconds. The format is a plus/minus sign followed by the \
combination of numbers and units, e.g "- 5 days", "+1h30m", "-1y6mo". \
Units can be one of the "years", "months", "days", "hours", "minutes", or \
"seconds". Units can be abbreviated, either by dropping "s" at the end, or \
to the first letter of unit (except for months that can only be shortened \
to "mo" to avoid collision with minutes). If multiple units are specified \
their order must be from coarser to finer, e.g. "1d12h" is OK, while "12h1d" \
is not.

Combination of absolute and relative time can look like "now - 30d", \
"today - 6 months", "2020-01-01 + 1 year", etc. If one of the two timestamps \
is missing an absolute part then another timestamp is used as an absolute \
part. If both timestamps are missing absolute part then they assumed to be \
relative to "now", but at least one of the two must have relative time.
"""


class UIPopUpKeysInputHelp(UIPopUpMessageBox):

    def __init__(self, message: str = _help):
        buttons = [('OK', 'ok')]
        super().__init__('You asked, we answered', message, buttons,
                         escape_value='ok', attr="help", cols=80)
