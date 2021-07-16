"""Module for AppPanel class and related methods.
"""
from __future__ import annotations

from typing import List, Optional, Tuple


class AppPanel:
    """Interface definition for application panels.
    """

    def title(self) -> Optional[str]:
        """Return string displayed as a panel title"""
        raise NotImplementedError()

    def hints(self) -> List[Tuple[str, str]]:
        """Return list of hints.

        Each hint is a tuple of two strings, first string is the name of
        a key and second is the name of the action, e.g. ("^E", "Menu").
        Default implementation returns empty list.
        """
        return []

    def status(self) -> str:
        """Return status string.

        Default implementation returns empty string.
        """
        return ""
