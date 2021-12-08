"""Helper methods and classes for UI part.
"""
from __future__ import annotations

__all__ = ["UIColumns"]

#--------------------------------
#  Imports of standard modules --
#--------------------------------
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

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


class UIColumns(urwid.Columns):
    """
    Convenience wrapper for Columns widget
    """

    signals = ['activated']

    def __init__(self, widget_list: List[urwid.Widget], width_list: Optional[List[int]] = None,
                 dividechars: int = 0, focus_column: Optional[int] = None, min_width: int = 1,
                 box_columns: Optional[List[int]] = None, wrap: str = 'clip'):
        """
        @param widget_list: List of items, each item can be either widget or an
                    object, if it is non-widget it is converted to string and
                    wrapped into UISelectableText widget
        @param width_list:  List of widget widths, if given must have the same
                    length as widget_list. Items in the list are either
                    positive numbers for absolute width, negative numbers for
                    negative weight, or string 'pack' to calculate actual size
                    of the widget.
        @param wrap: Wrapping method for text widgets created from strings in
                    widget_list.

        Other parameters are the same as in call to urwid.Columns constructor.
        """

        def widget_factory(w: Any) -> urwid.Widget:
            if not isinstance(w, urwid.Widget):
                w = urwid.Text(str(w), wrap=wrap)
            return w

        def width_tuple_factory(w: urwid.Widget, width: Union[int, float, str]) -> Tuple:
            if isinstance(width, (int, float)):
                if width < 0:
                    return ('weight', -width, w)
                else:
                    return (width, w)
            elif width == 'pack':
                return ('pack', w)
            else:
                return ('weight', 1, w)

        # make widget list
        widget_list = [widget_factory(w) for w in widget_list]

        # zip with widths
        if width_list:
            widget_list = [width_tuple_factory(w, width) for w, width in zip(widget_list, width_list)]

        urwid.Columns.__init__(self, widget_list, dividechars, focus_column, min_width, box_columns)

        # we want to have a focus in a single column only
        command_map: Dict[str, str] = self._command_map.copy()  # type: ignore
        del command_map['left']
        del command_map['right']
        self._command_map = command_map

    def keypress(self, size: Tuple, key: str) -> Optional[str]:

        _log.debug("UIColumns: received key: %s", key)

        # see if any child is interested in this key
        key = urwid.Columns.keypress(self, size, key)

        # if no one grabs a key then process it here
        if self._command_map[key] == urwid.ACTIVATE:
            self._emit('activated')
            return None

        return key
