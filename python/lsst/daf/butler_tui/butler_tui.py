from __future__ import annotations

__all__ = ["ButlerTui"]

import logging
import os
import tempfile
from typing import Any

import urwid

from lsst.daf.butler import Butler, DatasetRef, DatasetType, DimensionElement
from .app_base import AppBase
from .collections import CollectionList
from .datasets import DatasetList
from .dataset_types import DatasetTypeList
from .dimensions import DimensionsList
from .dimension_records import DimensionRecordList
from .main_menu import ButlerMainMenu
from .pager import Pager


_log = logging.getLogger(__name__)


class ButlerTui(AppBase):
    """Class representing top-level widget for the whole application.

    Parameters
    ----------
    conn_str : `str`
        CORAL connection string for mda database
    readonly : `str`
        boolean, if True then use read-only mode for database
    """

    #----------------
    #  Constructor --
    #----------------
    def __init__(self, butler_uri: str, readonly: bool):
        AppBase.__init__(self)
        self.butler = Butler(butler_uri, writeable=not readonly)

    def title(self) -> str:
        return ' = Butler explorer = '

    def start(self, loop: urwid.MainLoop, user_data: Any) -> None:
        """Make initial panel
        """
        mainMenu = self.makePanel(ButlerMainMenu)
        if mainMenu is None:
            return
        urwid.connect_signal(mainMenu, 'selected', self.mainMenuSelected)

    def mainMenuSelected(self, widget: urwid.Widget, mainMenuItem: str) -> None:
        _log.debug("selected item: %r", mainMenuItem)

        if mainMenuItem == 'dimensions':
            widget = self.makePanel(DimensionsList, self.butler)
            urwid.connect_signal(widget, 'selected', self.dimensionSelected)
            pass
        elif mainMenuItem == 'collections':
            widget = self.makePanel(CollectionList, self.butler)
            if widget is not None:
                urwid.connect_signal(widget, 'selected', self.collectionSelected)
                urwid.connect_signal(widget, 'show-chain', self.collectionChains)
            pass
        elif mainMenuItem == 'dataset_types':
            widget = self.makePanel(DatasetTypeList, self.butler)
            # if widget is not None:
            #     urwid.connect_signal(widget, 'selected',
            #                          self.partitionSelected)
            pass

    def dimensionSelected(self, widget: urwid.Widget, element: DimensionElement) -> None:
        self.makePanel(DimensionRecordList, self.butler, element)

    def collectionSelected(self, widget: urwid.Widget, collName: str) -> None:
        widget = self.makePanel(DatasetTypeList, self.butler, collName)
        if widget is not None:
            urwid.connect_signal(widget, 'selected', self.collectionDatasetSelected)

    def collectionDatasetSelected(self, widget: urwid.Widget, collName: str, dst: DatasetType) -> None:
        widget = self.makePanel(DatasetList, self.butler, collName, dst)
        if widget is not None:
            urwid.connect_signal(widget, 'selected', self.datasetSelected)

    def collectionChains(self, widget: urwid.Widget, collName: str) -> None:
        widget = self.makePanel(CollectionList, self.butler, collName)
        if widget is not None:
            urwid.connect_signal(widget, 'selected', self.collectionSelected)
            urwid.connect_signal(widget, 'show-chain', self.collectionChains)

    def datasetSelected(self, widget: urwid.Widget, ref: DatasetRef) -> None:

        def factory():
            data = self.butler.getDirect(ref)
            fd, path = tempfile.mkstemp()
            os.write(fd, str(data).encode())
            os.close(fd)
            _log.debug("dumped data to: %r", path)
            return path

        header = str(ref)
        widget = self.makePanel(Pager, self._main_loop, factory, header)
        if widget is not None:
            urwid.connect_signal(widget, 'finished', self.pagerFinished)

    def pagerFinished(self, widget: urwid.Widget) -> None:
        self.goBack()
