from __future__ import annotations

import logging
import os
from typing import Callable, List, Optional, Tuple, TYPE_CHECKING

import urwid
from .app_panel import AppPanel

if TYPE_CHECKING:
    from .butler_tui import ButlerTui


_log = logging.getLogger(__name__)


class Pager(urwid.Frame, AppPanel):
    """Widget class containing list of possible options in main menu.

    Parameters
    ----------
    app : `BuitlerTui`
    """

    _selectable = True

    signals = ['finished']

    def __init__(self, app: ButlerTui, main_loop: urwid.MainLoop, factory: Callable,
                 header: Optional[str] = None):
        self._app = app
        self._title = header

        path = factory()

        pager = os.environ.get("PAGER", "/usr/bin/less")
        command = [pager, path]

        if header:
            header = urwid.AttrMap(urwid.Text(header), 'list-colhead')
        term = urwid.Terminal(command, main_loop=main_loop, escape_sequence="ctrl s")
        urwid.connect_signal(term, "closed", self._terminalFinished, user_args=[path])
        term.keygrab = True

        urwid.Frame.__init__(self, term)

    def title(self) -> Optional[str]:
        return self._title

    def hints(self, global_hints: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        return []

    def status(self) -> str:
        return "Use usual $PAGER/less keys to exit"

    def _terminalFinished(self, path: str, term: urwid.Terminal) -> None:
        _log.debug("removing temp file: %r", path)
        try:
            os.remove(path)
        except OSError:
            # do not try too hard
            pass
        _log.debug("emitting signal 'finished': %s")
        self._emit('finished')
