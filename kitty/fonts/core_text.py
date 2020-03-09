#!/usr/bin/env python3
# vim:fileencoding=utf-8
# License: GPL v3 Copyright: 2017, Kovid Goyal <kovid at kovidgoyal.net>

import re
from typing import (
    TYPE_CHECKING, Dict, Generator, Iterable, List, Optional, Sequence, Tuple
)

from kitty.fast_data_types import coretext_all_fonts
from kitty.options_stub import Options
from kitty.utils import log_error

from . import ListedFont

if TYPE_CHECKING:
    from kitty.fast_data_types import CoreTextFont
    CoreTextFont


attr_map = {(False, False): 'font_family',
            (True, False): 'bold_font',
            (False, True): 'italic_font',
            (True, True): 'bold_italic_font'}


FontMap = Dict[str, Dict[str, List['CoreTextFont']]]


def create_font_map(all_fonts: Iterable['CoreTextFont']) -> FontMap:
    ans: FontMap = {'family_map': {}, 'ps_map': {}, 'full_map': {}}
    for x in all_fonts:
        f = (x['family'] or '').lower()
        s = (x['style'] or '').lower()
        ps = (x['postscript_name'] or '').lower()
        ans['family_map'].setdefault(f, []).append(x)
        ans['ps_map'].setdefault(ps, []).append(x)
        ans['full_map'].setdefault(f + ' ' + s, []).append(x)
    return ans


def all_fonts_map() -> FontMap:
    ans: Optional[FontMap] = getattr(all_fonts_map, 'ans', None)
    if ans is None:
        ans = create_font_map(coretext_all_fonts())
        setattr(all_fonts_map, 'ans', ans)
    return ans


def list_fonts() -> Generator[ListedFont, None, None]:
    for fd in coretext_all_fonts():
        f = fd['family']
        if f:
            fn = (f + ' ' + (fd['style'] or '')).strip()
            is_mono = bool(fd['monospace'])
            yield {'family': f, 'full_name': fn, 'postscript_name': fd['postscript_name'] or '', 'is_monospace': is_mono}


def bi_match(fonts: Sequence['CoreTextFont'], bold: bool, italic: bool) -> 'CoreTextFont':
    for b, i in ((bold, italic), (False, False)):
        for q in fonts:
            if q['bold'] == b and q['italic'] == i:
                return q
    return fonts[0]


def find_best_match(family: str, bold: bool = False, italic: bool = False) -> 'CoreTextFont':
    q = re.sub(r'\s+', ' ', family.lower())
    font_map = all_fonts_map()

    def score(candidate):
        style_match = 1 if candidate['bold'] == bold and candidate[
            'italic'
        ] == italic else 0
        monospace_match = 1 if candidate['monospace'] else 0
        return style_match, monospace_match

    # First look for an exact match
    for selector in ('ps_map', 'full_map'):
        candidates = font_map[selector].get(q)
        if candidates:
            candidates.sort(key=score)
            return candidates[-1]

    # Let CoreText choose the font if the family exists, otherwise
    # fallback to Menlo
    if q not in font_map['family_map']:
        log_error('The font {} was not found, falling back to Menlo'.format(family))
    return bi_match(font_map['family_map']['menlo'], bold, italic)


def resolve_family(f: str, main_family: str, bold: bool = False, italic: bool = False) -> str:
    if (bold or italic) and f == 'auto':
        f = main_family
    if f.lower() == 'monospace':
        f = 'Menlo'
    return f


def get_font_files(opts: Options) -> Dict[str, 'CoreTextFont']:
    ans: Dict[str, 'CoreTextFont'] = {}
    for (bold, italic), attr in attr_map.items():
        face = find_best_match(resolve_family(getattr(opts, attr), opts.font_family, bold, italic), bold, italic)
        key = {(False, False): 'medium',
               (True, False): 'bold',
               (False, True): 'italic',
               (True, True): 'bi'}[(bold, italic)]
        ans[key] = face
        if key == 'medium':
            setattr(get_font_files, 'medium_family', face['family'])
    return ans


def font_for_family(family: str) -> Tuple['CoreTextFont', bool, bool]:
    ans = find_best_match(resolve_family(family, getattr(get_font_files, 'medium_family')))
    return ans, ans['bold'], ans['italic']
