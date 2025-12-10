"""Helper methods and classes for UI part.
"""
from __future__ import annotations

__all__ = ["UIProgressBar", "UIPopUpProgress"]

#--------------------------------
#  Imports of standard modules --
#--------------------------------
import logging
import time
from typing import Callable, Optional, Tuple

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


class _LoopProgressBar(urwid.ProgressBar):
    """Customized progress bar with loop effect.
    """
    def __init__(self, normal: str, complete: str, current: int = 0, done: int = 100,
                 satt: Optional[str] = None):
        self._loop = False
        if done <= 0:
            self._loop = True
            self._loop_start_time = time.time()
            done = 100
        urwid.ProgressBar.__init__(self, normal, complete, current, done, satt)

    def get_text(self) -> str:
        if self._loop:
            return "working"
        else:
            return urwid.ProgressBar.get_text(self)

    def set_completion(self, value: float) -> None:
        if self._loop:
            # in loop mode we progress as 10% per second
            now = time.time()
            value = (now - self._loop_start_time) * 10.
            if value >= 100:
                value = 0
                self._loop_start_time = now
        urwid.ProgressBar.set_completion(self, value)


class UIProgressBar(urwid.WidgetWrap):
    """Widget implementing box with progress bar, title and a button.

    When button is clicked this widget generates 'cancelled' signal.
    Optionally Escape key can be configured to also generate 'cancelled'
    signal.

    Parameters
    ----------
    title : `str`
    cancel_button : `bool`, optional
        If True then show a Cancel button.
    escape_signal : `bool`, optional
        If True then Escape key generates "cancelled" signal.
    attr : `str`
        Attributes for widget area
    """

    signals = ['cancelled']

    def __init__(self, title: str, current: int = 0, done: int = 100,
                 cancel_button: bool = False, escape_signal: bool = False, attr: str = 'progressbar'):
        self.progress_bar = _LoopProgressBar(attr + "-incomplete", attr + "-complete", current, done)
        if cancel_button:
            stretch = urwid.Text(' ' * 132, wrap='clip')  # stretch space to the left of the buttons
            buttons = [stretch]
            button = urwid.Button("Cancel")
            urwid.connect_signal(button, 'click', self._cancel)
            buttons += [(10, urwid.AttrMap(button, None, attr + '-focus'))]
            buttons += [stretch]
            inner = urwid.Pile([self.progress_bar, urwid.Divider(u'\u2500'), urwid.Columns(buttons, 2)])
        else:
            inner = self.progress_bar
        filler = urwid.Filler(inner, height='flow')     # need to wrap it into a box widget
        linebox = urwid.LineBox(filler, title)         # wrap it all into linebox with title
        super().__init__(urwid.AttrMap(linebox, attr))

        self._escape_signal = escape_signal

    def _cancel(self, button: urwid.Button) -> None:
        self._emit('cancelled', button)

    def keypress(self, size: Tuple, key: str) -> Optional[str]:
        if self._escape_signal is not None and key == 'esc':
            self._emit('cancelled')
            return None
        return super().keypress(size, key)


class UIPopUpProgress(UIPopUp):
    """Pop-up showing a progress bar.
    """
    def __init__(self, title: str, current: int = 0, done: int = 100, callback: Optional[Callable] = None,
                 cols: int = 36, cancel_button: bool = False, escape_signal: bool = False,
                 attr: str = 'progressbar'):
        self.pbar = UIProgressBar(title, current, done, cancel_button, escape_signal, attr)
        urwid.connect_signal(self.pbar, 'cancelled', self._cancel)
        if callback is not None:
            urwid.connect_signal(self.pbar, 'cancelled', callback)

        pop_up_size = (cols, 5 if cancel_button else 3)
        super().__init__(self.pbar, pop_up_size)

        self._cancelled = False

    def _cancel(self) -> None:
        self._cancelled = True

    def set_done(self, value: float) -> None:
        """Set progress done value.
        """
        progressbar = self.pbar.progress_bar
        progressbar.done = value

    def set_completion(self, value: float) -> None:
        """Set progress current value.
        """
        progressbar = self.pbar.progress_bar
        progressbar.set_completion(value)

    def set_percent(self, percent: float) -> None:
        """Set progress current value as a percentage.
        """
        progressbar = self.pbar.progress_bar
        value = progressbar.done / 100. * percent
        progressbar.set_completion(value)

    def cancelled(self) -> bool:
        """Return True if Cancel button was activated.
        """
        return self._cancelled
