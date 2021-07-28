from __future__ import annotations

import logging
from typing import List, Optional, Tuple, TYPE_CHECKING

import urwid
from .app_panel import AppPanel
from .ui import UIListBoxWithHeader, UIColumns, UISelectableText, UIPopUpMessageBox

if TYPE_CHECKING:
    from .butler_tui import ButlerTui
    from lsst.daf.butler import Butler


_log = logging.getLogger(__name__)



class DimensionRecordList(UIListBoxWithHeader, AppPanel):
    """Widget class containing list of dimension records.

    Parameters
    ----------
    app : `ButlerTui`
    db : `Butler`
    """

    _selectable = True

    signals = ['selected']

    def __init__(self, app: ButlerTui, butler: Butler, element: DimensionElement):

        self._butler = butler

        records = list(butler.registry.queryDimensionRecords(element, check=False))

        if records:
            keys = records[0].fields.names
        else:
            keys = []
        records.sort(key=lambda r: r.dataId)
        self._total_count = len(records)

        key_lengths = [len(key) for key in keys]
        for rec in records:
            for i, key in enumerate(keys):
                key_lengths[i] = max(key_lengths[i], len(str(getattr(rec, key, ""))))

        header = UIColumns(keys, key_lengths, 1)

        items = []
        for rec in records:
            fields = [str(getattr(rec, key, "")) for key in keys]
            fields[0] = UISelectableText(fields[0])
            item = UIColumns(fields, key_lengths, 1)
            item = urwid.AttrMap(item, "list-item", "list-selected")
            items.append(item)

        self._walker = urwid.SimpleFocusListWalker(items)
        UIListBoxWithHeader.__init__(self, self._walker, header=header)

    def title(self) -> str:
        return "Dimension Records List"

    def status(self) -> str:
        if self._walker.focus is not None:
            position = self._walker.focus + 1
            return f"Record {position} out of {self._total_count}"
        else:
            return ""