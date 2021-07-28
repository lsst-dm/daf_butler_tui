from __future__ import annotations

import logging
from typing import List, Tuple, TYPE_CHECKING

import urwid
from .app_panel import AppPanel
from .ui import UIListBoxWithHeader, UIColumns, UISelectableText

if TYPE_CHECKING:
    from .butler_tui import ButlerTui
    from lsst.daf.butler import Butler


_log = logging.getLogger(__name__)


class DimensionsList(UIListBoxWithHeader, AppPanel):
    """Widget class containing list dimensions.

    Parameters
    ----------
    app : `ButlerTui`
    db : `Butler`
    """

    _selectable = True

    signals = ['selected']

    def __init__(self, app: ButlerTui, butler: Butler):

        # read data from database
        universe = butler.registry.dimensions

        col_width = [16, 3, 16, 16, 16, 16]
        header = UIColumns(["Name",
                            urwid.Text('Idx', align='right'),
                            "Governor",
                            "Required",
                            "Implied",
                            "Metadata"],
                           col_width, 1)

        items = []
        for element in universe.getStaticDimensions():
            idx = universe.getElementIndex(element.name)
            governor = element.governor
            required = "\n".join(el.name for el in element.required)
            implied = "\n".join(el.name for el in element.implied)
            metadata = "\n".join(el.name for el in element.metadata)
            item = UIColumns([UISelectableText(element.name),
                              urwid.Text(str(idx), align='right'),
                              governor.name if governor else "",
                              required,
                              implied,
                              metadata],
                             col_width, 1)
            urwid.connect_signal(item, 'activated', self._itemActivated, user_args=[element])
            items.append(item)

        UIListBoxWithHeader.__init__(self, items, header=header)

    def title(self) -> str:
        return "Dimension List"

    def status(self) -> str:
        return "Dimensions"

    def hints(self, global_hints: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        hints = global_hints + [('Enter', "Select")]
        return hints

    def _itemActivated(self, element: DimensionElement, item: UIColumns) -> None:
        _log.debug("emitting signal 'selected': %r", element)
        self._emit('selected', element)
