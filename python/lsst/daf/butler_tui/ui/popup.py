"""Helper methods and classes for UI part.
"""
from __future__ import annotations

__all__ = ["UIPopUp", "UIPopUpLauncher"]

#--------------------------------
#  Imports of standard modules --
#--------------------------------
import logging
from typing import Any, Dict, List, Optional, Tuple

#-----------------------------
# Imports for other modules --
#-----------------------------
import urwid

#----------------------------------
# Local non-exported definitions --
#----------------------------------

_log = logging.getLogger(__name__)

#------------------------
# Exported definitions --
#------------------------


class UIPopUp(urwid.WidgetWrap):
    """Pop-up widget used with UIPopUpLauncher class below.

    Parameters
    ----------
    widget : `Widget`
        Widget used for pop-up.
    pop_up_size : `tuple`
        (columns, rows) for pop-up widget
    location : `str`
        String with pop-up anchors, can include characters "N", or "S" for
        vertical anchor, and "W" or ""E" for horizontal anchor. Default anchor
        is at the center of parent widget.
    """

    signals = ['closed']

    def __init__(self, widget: urwid.Widget, pop_up_size: Tuple[int, int], location: str = 'C'):
        super().__init__(widget)
        self._pop_up_size = pop_up_size
        self._location = location

    def get_pop_up_parameters(self, parent_size: Tuple[int, int]) -> Dict[str, int]:
        cols, rows = self._pop_up_size
        maxcol, maxrow = parent_size
        _log.debug("UIPopUp: get_pop_up_parameters: %s %s", self._pop_up_size, parent_size)

        if 'N' in self._location:
            top = 0
        elif 'S' in self._location:
            top = maxrow - rows
        else:
            top = (maxrow - rows) // 2
        if 'W' in self._location:
            left = 0
        elif 'E' in self._location:
            left = maxcol - cols
        else:
            left = (maxcol - cols) // 2
        return dict(left=left, top=top, overlay_width=cols, overlay_height=rows)

    def close(self, *args: Any) -> None:
        """Typically this will be a callback for a signal generated by a button.
        """
        self._emit("closed")

    def hints(self) -> List[Tuple[str, str]]:
        """Return list of hints.

        Each hint is a tuple of two strings, first string is the name of
        a key and second is the name of the action, e.g. ("^E", "Menu").
        Default implementation returns empty list.
        """
        return []


class UIPopUpLauncher(urwid.PopUpLauncher):
    """
    PopUpLauncher class with pipml.

    This class is useful for widgets that need to support multiple pop-up
    widget types (e.g. dialog, menu, and error message). It defines
    make_pop_up() method which is used in place open_pop_up() and accepts
    additional context information. This context info is passed to
    create_pop_up() and get_pop_up_parameters() methods in pimpl so that
    they can detect the type of the pop up being instantiated.
    """

    signals = ['popup_closed']

    _parent_size = (0, 0)

    _pop_up: Optional[UIPopUp] = None

    def make_pop_up(self, pop_up: UIPopUp) -> None:
        """Make a pop-up.

        Parameters
        ----------
        pop_up : `UIPopUp`
        """
        self._pop_up = pop_up
        self.open_pop_up()
        urwid.connect_signal(self._pop_up, 'closed', self.close_pop_up)

    @property
    def popup(self) -> Optional[UIPopUp]:
        return self._pop_up

    def create_pop_up(self) -> UIPopUp:
        assert self._pop_up is not None
        return self._pop_up

    def close_pop_up(self, *args: Any) -> Any:
        """Overrides parent class method and accepts any number of parameters.

        This simplifies signal connection for signals that carry extra
        parameters.
        """
        self._emit("popup_closed")
        self._pop_up = None
        return super().close_pop_up()

    def get_pop_up_parameters(self) -> Dict[str, int]:
        assert self._pop_up is not None
        return self._pop_up.get_pop_up_parameters(self._parent_size)

    def set_parent_size(self, size: Tuple[int, int]) -> None:
        self._parent_size = size
