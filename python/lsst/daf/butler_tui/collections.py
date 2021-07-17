from __future__ import annotations

import logging
from typing import List, Tuple, TYPE_CHECKING

import urwid
from lsst.daf.butler import CollectionType
from .app_panel import AppPanel
from .ui import UIListBoxWithHeader, UIColumns, UISelectableText

if TYPE_CHECKING:
    from .butler_tui import ButlerTui
    from lsst.daf.butler import Butler


_log = logging.getLogger(__name__)


class CollectionList(UIListBoxWithHeader, AppPanel):
    """Widget class containing list of collections.

    Parameters
    ----------
    app : `ButlerTui`
    db : `Butler`
    """

    _selectable = True

    signals = ['selected', 'show-chain']

    def __init__(self, app: ButlerTui, butler: Butler, collection=None):

        if collection is None:
            collections = sorted(butler.registry.queryCollections())
        else:
            collections = sorted(butler.registry.queryCollections(collection, flattenChains=True))
        max_len = min(max(len(coll_name) for coll_name in collections), 64)

        col_width = [max_len, 12]
        header = UIColumns(["Name",
                            "Type"],
                           col_width, 1)

        items = []
        for coll_name in collections:
            coll_type = butler.registry.getCollectionType(coll_name)
            item = UIColumns([UISelectableText(coll_name),
                              coll_type.name],
                             col_width, 1)
            urwid.connect_signal(item, 'activated', self._itemActivated, user_args=[coll_name, coll_type])
            item = urwid.AttrMap(item, "list-item", "list-selected")
            item.user_data = coll_name, coll_type
            items.append(item)

        self._walker = urwid.SimpleFocusListWalker(items)
        UIListBoxWithHeader.__init__(self, self._walker, header=header)

    def title(self) -> str:
        return "Collections List"

    def hints(self) -> List[Tuple[str, str]]:
        hints = []
        item = self._walker.get_focus()[0]
        coll_type = item.user_data[1]
        if coll_type != CollectionType.CALIBRATION:
            hints = [('Enter', "Select")]
        if coll_type == CollectionType.CHAINED:
            hints += [("->", "Show Chain")]
        return hints

    def keypress(self, size: Tuple[int, int], key: str) -> Optional[str]:

        # handle '^E'
        if key == 'right':
            self._show_chain()
            return None

        # send it to base class
        key = self.__super.keypress(size, key)
        return key

    def status(self) -> str:
        return "Collections"

    def _itemActivated(self, coll_name: str, coll_type: CollectionType, item: UIColumns) -> None:
        if coll_type != CollectionType.CALIBRATION:
            _log.debug("emitting signal 'selected': %r", coll_name)
            self._emit('selected', coll_name)

    def _show_chain(self) -> None:
        # figure out which collection is selected
        item = self._walker.get_focus()[0]
        coll_name, coll_type = item.user_data
        if coll_type == CollectionType.CHAINED:
            _log.debug("emitting signal 'show-chain': %r", coll_name)
            self._emit('show-chain', coll_name)
