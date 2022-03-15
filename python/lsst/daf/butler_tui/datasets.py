from __future__ import annotations

import logging
from typing import Iterable, List, Tuple, TYPE_CHECKING

import urwid
from .app_panel import AppPanel
from .ui import UIListBoxWithHeader, UIColumns, UISelectableText

if TYPE_CHECKING:
    from .butler_tui import ButlerTui
    from lsst.daf.butler import Butler, DatasetRef, DatasetType


_log = logging.getLogger(__name__)


class DatasetList(UIListBoxWithHeader, AppPanel):
    """Widget class containing list of collections.

    Parameters
    ----------
    app : `ButlerTui`
    db : `Butler`
    """

    _selectable = True

    signals = ['selected']

    def __init__(self, app: ButlerTui, butler: Butler, collection: str, dataset_type: DatasetType):

        self._butler = butler
        self._collection = collection
        self._known_storage = True

        dim_names = list(dataset_type.dimensions.names)

        def _sort_key(ref):
            return tuple(ref.dataId[name] for name in dim_names)

        refs: Iterable[DatasetRef] = set(
            butler.registry.queryDatasets(datasetType=dataset_type, collections=collection)
        )

        refs = sorted(refs, key=_sort_key)
        self._total_count = len(refs)

        id_len = min(max([2] + [len(str(ref.id)) for ref in refs]), 64)
        dim_lengths = [len(name) for name in dim_names]
        for ref in refs:
            for i, name in enumerate(dim_names):
                dim_lengths[i] = max(dim_lengths[i], len(str(ref.dataId[name])))

        col_width = [id_len] + dim_lengths
        header = UIColumns(["ID"] + dim_names,
                           col_width, 1)

        items = []
        for ref in refs:
            cols: List = [UISelectableText(str(ref.id))]
            cols += [str(ref.dataId[name]) for name in dim_names]
            item = UIColumns(cols, col_width, 1)
            if self._known_storage:
                urwid.connect_signal(item, 'activated', self._itemActivated, user_args=[ref])
            item = urwid.AttrMap(item, "list-item", "list-selected")
            items.append(item)

        self._walker = urwid.SimpleFocusListWalker(items)
        UIListBoxWithHeader.__init__(self, self._walker, header=header)

    def title(self) -> str:
        return "Dataset List"

    def hints(self, global_hints: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        hints = global_hints
        if self._known_storage:
            hints += [('Enter', "Select")]
        return hints

    def status(self) -> str:
        if self._walker.focus is not None:
            position = self._walker.focus + 1
            return f"Dataset {position} out of {self._total_count}"
        else:
            return ""

    def _itemActivated(self, ref: DatasetRef, item: UIColumns) -> None:
        _log.debug("emitting signal 'selected': %r", ref)
        self._emit('selected', ref)
