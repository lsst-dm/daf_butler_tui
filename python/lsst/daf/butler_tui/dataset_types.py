from __future__ import annotations

import logging
from typing import List, Optional, Tuple, TYPE_CHECKING

import urwid
from .app_panel import AppPanel
from .ui import UIListBoxWithHeader, UIColumns, UISelectableText

if TYPE_CHECKING:
    from .butler_tui import ButlerTui
    from lsst.daf.butler import Butler


_log = logging.getLogger(__name__)


class DatasetTypeList(UIListBoxWithHeader, AppPanel):
    """Widget class containing list of collections.

    Parameters
    ----------
    app : `ButlerTui`
    db : `Butler`
    """

    _selectable = True

    signals = ['selected']

    def __init__(self, app: ButlerTui, butler: Butler, collection: Optional[str] = None):

        self._collection = collection

        if collection:
            coll_summary = butler.registry.getCollectionSummary(collection)
            dataset_types = sorted(coll_summary.datasetTypes, key=lambda dst: dst.name)
        else:
            dataset_types = sorted(butler.registry.queryDatasetTypes(components=True), key=lambda dst: dst.name)

        name_len = min(max([4] + [len(dst.name) for dst in dataset_types]), 64)
        # dst.storageClass.name can crash
        stc_len = min(max([13] + [len(dst._storageClassName) for dst in dataset_types]), 64)

        col_width = [name_len, stc_len, 16]
        header = UIColumns(["Name",
                            "Storage class",
                            "Dimensions"],
                           col_width, 1)

        items = []
        for dst in dataset_types:
            storageClass = dst._storageClassName
            dimensions = "\n".join(dst.dimensions.names)
            item = UIColumns([UISelectableText(dst.name),
                              storageClass,
                              dimensions],
                             col_width, 1)
            urwid.connect_signal(item, 'activated', self._itemActivated, user_args=[collection, dst])
            items.append(item)

        UIListBoxWithHeader.__init__(self, items, header=header)

    def title(self) -> str:
        return "Dataset Type List"

    def status(self) -> str:
        return "Dataset types"

    def hints(self) -> List[Tuple[str, str]]:
        hints = []
        if self._collection:
            hints += [('Enter', "Select")]
        return hints

    def _itemActivated(self, coll_name: str, dataset_type: DatasetType, item: UIColumns) -> None:
        _log.debug("emitting signal 'selected': %r %r", coll_name, dataset_type)
        self._emit('selected', coll_name, dataset_type)
