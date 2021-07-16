"""Sphinx configuration file for an LSST stack package.

This configuration only affects single-package Sphinx documentation builds.
"""

from documenteer.sphinxconfig.stackconf import build_package_configs
import lsst.daf.butler_tui


_g = globals()
_g.update(build_package_configs(
    project_name='daf_butler_tui',
    version=lsst.daf.butler_tui.version.__version__))
