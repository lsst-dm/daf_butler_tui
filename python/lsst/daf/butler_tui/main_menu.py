from __future__ import annotations

import logging
from typing import List, Tuple, TYPE_CHECKING

import urwid
from .app_panel import AppPanel
from .ui import UIListBoxWithHeader, UIColumns, UISelectableText

if TYPE_CHECKING:
    from .butler_tui import ButlerTui


_log = logging.getLogger(__name__)


class ButlerMainMenu(UIListBoxWithHeader, AppPanel):
    """Widget class containing list of possible options in main menu.

    Parameters
    ----------
    app : `BuitlerTui`
    """

    _selectable = True

    signals = ['selected']

    def __init__(self, app: ButlerTui):
        self._app = app

        menu = [
            ("Dimensions", "dimensions"),
            ("Dataset Types", "dataset_types"),
            ("Collections chains", "collections"),
        ]

        col_width = [30]
        header = UIColumns(['Data selection'], col_width, 2)

        items = []
        for selection, value in menu:
            item = UIColumns([UISelectableText(selection)], col_width, 2, 0)
            urwid.connect_signal(item, 'activated', self._itemActivated, user_args=[value])
            items.append(item)

        UIListBoxWithHeader.__init__(self, items, header=header)

    def title(self) -> str:
        return 'Types of butler data'

    def hints(self, global_hints: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        return global_hints + [('Enter', "Select")]

    def status(self) -> str:
        return ""

    def _itemActivated(self, value: str, item: UIColumns) -> None:
        _log.debug("emitting signal 'selected': %r", value)
        self._emit('selected', value)
