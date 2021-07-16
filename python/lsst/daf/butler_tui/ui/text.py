"""Helper methods and classes for UI part.
"""
from __future__ import annotations

__all__ = ["UISelectableText"]


#--------------------------------
#  Imports of standard modules --
#--------------------------------
import logging
from typing import Any, Optional, Tuple

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


class UISelectableText(urwid.Text):

    _selectable = True

    def __init__(self, markup: Any, align: str = 'left', wrap: str = 'space',
                 layout: Optional[urwid.TextLayout] = None):
        """
        @param markup: Text Markup: content of text widget
        @param align (text alignment mode) - typically 'left', 'center' or 'right'
        @param wrap (text wrapping mode) - typically 'space', 'any' or 'clip'
        @param layout (text layout instance) - defaults to a shared StandardTextLayout instance
        """
        urwid.Text.__init__(self, markup, align, wrap, layout)

    def keypress(self, size: Tuple, key: str) -> Optional[str]:
        return key
