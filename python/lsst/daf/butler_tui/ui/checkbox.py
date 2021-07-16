"""Helper methods and classes for UI part.
"""
from __future__ import annotations

__all__ = ["SlimCheckBox"]

#--------------------------------
#  Imports of standard modules --
#--------------------------------
import logging
from typing import Dict, Optional

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


def _keymap_for_checkbox() -> Dict[str, Optional[str]]:
    # Do not use enter for toggle, only space and insert
    command_map: Dict[str, Optional[str]] = urwid.command_map.copy()
    command_map['enter'] = None
    command_map['insert'] = 'activate'
    return command_map


class SlimCheckBox(urwid.CheckBox):
    """
    CheckBox which is one character wide.
    """

    states = {
        True: urwid.SelectableIcon(('selected', "X")),
        False: urwid.SelectableIcon(" "),
        'mixed': urwid.SelectableIcon("#")}
    reserve_columns = 1

    _command_map = _keymap_for_checkbox()
