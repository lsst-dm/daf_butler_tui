"""Module for AppBase class and related methods.
"""
from __future__ import annotations

import logging
from typing import Any, Callable, List, Optional, Tuple, Type

import urwid
from .ui import UIHints, UIPopUp, UIPopUpLauncher, UIPopUpMessageBox


# default palette for all apps
_palette: List[Tuple[str, ...]] = [
    ('body', 'light gray', 'dark blue'),
    ('selected', 'white', 'dark green'),

    ('title', 'white', 'dark green', 'bold,standout'),

    ('hint', 'black', 'dark green'),
    ('hint-high', 'white', 'dark green'),

    ('status', 'black', 'dark green', 'bold,standout'),
    ('status-high', 'yellow', 'dark green', 'bold,standout'),

    ('list-colhead', 'light cyan', 'dark blue', 'bold'),
    ('list-item', 'light gray', 'dark blue'),
    ('list-selected', 'black', 'dark cyan', 'standout'),

    ('menu', 'white', 'black'),
    ('menu-focus', 'black', 'white', 'standout'),

    ('messagebox', 'black', 'white'),
    ('messagebox-focus', 'white', 'dark gray', 'standout'),

    ('help', 'black', 'dark cyan'),

    ('messagebox-error', 'white', 'dark red'),
    ('messagebox-error-focus', 'dark red', 'white', 'standout'),

    ('editbox', 'black', 'white'),
    ('editbox-focus', 'white', 'dark gray', 'standout'),
    ('editbox-field', 'white', 'black'),

    ('progressbar', 'white', 'dark blue'),
    ('progressbar-incomplete', 'yellow', 'black'),
    ('progressbar-complete', 'black', 'yellow'),
]

_log = logging.getLogger(__name__)


class FailedExit(UIPopUpMessageBox):

    def __init__(self, message: str, callback: Callable):
        buttons = [('Exit', 'exit')]
        self.__super.__init__('Application failure', message, buttons, callback,
                              escape_value='exit', attr='messagebox-error')

#------------------------
# Exported definitions --
#------------------------


class AppBase(urwid.WidgetWrap):
    """Class representing top-level widget for the whole application.

    It implements general application behavior such as input handling,
    status line and hint display, panel stack, and common palette.
    Specific application sub-classes will have to re-implement few
    methods to add application panels.
    """

    _selectable = True

    palette = _palette

    #----------------
    #  Constructor --
    #----------------
    def __init__(self) -> None:
        self._hint = UIHints()
        self._status = urwid.Text("", wrap='clip', align='right')
        footer = urwid.Columns([self._hint, urwid.AttrMap(self._status, 'status')])
        root = urwid.LineBox(urwid.SolidFill(), '')
        title = self.title()
        header = urwid.AttrMap(urwid.Text(title, wrap='clip'), 'title') if title else None
        self._frame = urwid.Frame(urwid.AttrMap(root, 'body'),
                                  header=header,
                                  footer=urwid.AttrMap(footer, 'hint'))
        self._pop_up_launcher = UIPopUpLauncher(self._frame)
        super().__init__(self._pop_up_launcher)

        urwid.connect_signal(self._pop_up_launcher, 'popup_closed', self.popup_closed)

        self._widgetStack: List[urwid.Widget] = []

        # make a main loop and arrange it to call app.start() when alive
        self._main_loop = urwid.MainLoop(self, self.palette, pop_ups=True)
        self._main_loop.set_alarm_in(0, self.start)

    def title(self) -> Optional[str]:
        """Return string displayed as application title at the top
        of the window.

        If None or empty string is returned then nothing is displayed.
        """
        return None

    def make_pop_up(self, popup: UIPopUp) -> None:
        """Show pop-up widget.

        Panels should call this method if they need to display popup widgets.

        Parameters
        ----------
        pop_up : `UIPopUp`
        """
        self._pop_up_launcher.make_pop_up(popup)
        self._hint.set_hints(popup.hints())

    def popup_closed(self, widget: urwid.Widget) -> None:
        widget = self._widgetStack[-1]
        self._hint.set_hints(widget.hints(self.hints()))
        # have to refresh
        self._main_loop.draw_screen()

    def run(self) -> None:
        """Starts the whole shebang.
        """
        self._main_loop.run()

    def start(self, loop: urwid.MainLoop, user_data: Any) -> None:
        """Will be called once event loop starts (e.g. via timer or signal).

        This method has to be overriden by sub-class to instantiate whatever
        first panel it needs.
        """
        raise NotImplementedError()

    def makePanel(self, PanelClass: Type[urwid.Widget], *args: Any, **kwargs: Any) -> Optional[urwid.Widget]:
        """Create panel widget from given panel class and additional arguments.

        This is the factory method that should be used by sub-classes to
        instantiate panel widgets.
        """
        try:
            widget = PanelClass(self, *args, **kwargs)
        except Exception as exc:
            _log.error("Exception in panel constructor", exc_info=True)
            buttons = [('Close', 'close')]
            self.make_pop_up(UIPopUpMessageBox("Exception", str(exc), buttons=buttons,
                                               escape_value="close", cols=72, attr='messagebox-error'))
            widget = None
        if widget:
            self.setCentralWidget(widget)
        return widget

    def setCentralWidget(self, widget: urwid.Widget) -> None:
        """Display given widget in the central area with line box around it
        """
        root = urwid.LineBox(widget, widget.title())
        self._frame.contents['body'] = (urwid.AttrMap(root, 'body'), None)
        self._widgetStack.append(widget)
        self._status.set_text(widget.status())
        self._hint.set_hints(widget.hints(self.hints()))

    def goBack(self) -> None:
        """Return to previous panel.
        """
        if len(self._widgetStack) > 1:
            del self._widgetStack[-1]
            widget = self._widgetStack[-1]
            root = urwid.LineBox(widget, widget.title())
            self._frame.contents['body'] = (urwid.AttrMap(root, 'body'), None)
            self._hint.set_hints(widget.hints(self.hints()))
            self._status.set_text(widget.status())

    def hints(self) -> List[Tuple[str, str]]:
        """Return global hints for this application
        """
        hints = [('^X', "Exit")]
        if len(self._widgetStack) > 1:
            hints += [('Esc/BS', "Back")]
        return hints

    def keypress(self, size: Tuple[int, int], key: str) -> Optional[str]:
        """Handle keyboard input.
        """
        _log.debug("received key: %s", key)

        # update window size for pup-ups
        self._pop_up_launcher.set_parent_size(size)

        child = self._frame.contents['body'][0]
        if child.selectable():
            _log.debug("forward key to child: %s", key)
            size = (size[0], size[1] - 2)
            try:
                key = child.keypress(size, key)
            except Exception as exc:
                _log.error("Application failure", exc_info=True)
                msg = "Exception: " + str(exc)
                self.make_pop_up(FailedExit(msg, self._exitOnFail))
                return None
            # update status line
            self._status.set_text(self._widgetStack[-1].status())
        if key == 'ctrl x':
            raise urwid.ExitMainLoop()
        if key in ('esc', 'backspace'):
            # handle "go back" key
            self.goBack()
            return None

        if self._pop_up_launcher.popup:
            self._hint.set_hints(self._pop_up_launcher.popup.hints())
        elif self._widgetStack:
            widget = self._widgetStack[-1]
            self._hint.set_hints(widget.hints(self.hints()))

        return key

    def _exitOnFail(self, widget: urwid.Widget, button: urwid.Button) -> None:
        raise urwid.ExitMainLoop()
