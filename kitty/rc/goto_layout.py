#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2020, Kovid Goyal <kovid at kovidgoyal.net>

from typing import TYPE_CHECKING, Optional

from .base import (
    MATCH_TAB_OPTION, ArgsType, Boss, PayloadGetType, PayloadType, RCOptions,
    RemoteCommand, ResponseType, UnknownLayout, Window
)

if TYPE_CHECKING:
    from kitty.cli_stub import GotoLayoutRCOptions as CLIOptions


class GotoLayout(RemoteCommand):

    '''
    layout+: The new layout name
    match: Which tab to change the layout of
    '''

    short_desc = 'Set the window layout'
    desc = (
        'Set the window layout in the specified tab (or the active tab if not specified).'
        ' You can use special match value :italic:`all` to set the layout in all tabs.'
    )
    options_spec = MATCH_TAB_OPTION
    argspec = 'LAYOUT_NAME'

    def message_to_kitty(self, global_opts: RCOptions, opts: 'CLIOptions', args: ArgsType) -> PayloadType:
        try:
            return {'layout': args[0], 'match': opts.match}
        except IndexError:
            raise self.fatal('No layout specified')

    def response_from_kitty(self, boss: Boss, window: Optional[Window], payload_get: PayloadGetType) -> ResponseType:
        tabs = self.tabs_for_match_payload(boss, window, payload_get)
        for tab in tabs:
            if tab:
                try:
                    tab.goto_layout(payload_get('layout'), raise_exception=True)
                except ValueError:
                    raise UnknownLayout('The layout {} is unknown or disabled'.format(payload_get('layout')))


goto_layout = GotoLayout()
