"""
删字规则：Windows 系常见文件茎、名称表内区域关键词、cmap 粗判（CJK/拉丁/谚文/阿文）。

说明：与 Windows 同名的非系统拷贝无法 100% 识别；名称表为 Microsoft 的整族倾向删除。
"""

from __future__ import annotations

import re
from pathlib import Path

# 小写、按长度降序，仅用 stem.lower().startswith
_WIN_PX: tuple[str, ...] = tuple(
    sorted(
        {
            "arial",
            "ariblk",
            "bahn",
            "baskvill",
            "bookos",
            "bradhitc",
            "calibri",
            "cambri",
            "candara",
            "cascadi",
            "century",
            "chiller",
            "comic",
            "consola",
            "constan",
            "corbel",
            "courb",
            "courbi",
            "couri",
            "cour",
            "coor",
            "dengl",
            "dengb",
            "ebrima",
            "fradmit",
            "gabriol",
            "gadugi",
            "gungsuh",
            "himalaya",
            "impact",
            "latha",
            "leelaw",
            "lucon",
            "malgun",
            "mangal",
            "meiryo",
            "msjh",
            "msuigoth",
            "msyi",
            "msyh",
            "nirmal",
            "ntailu",
            "pala",
            "phagsp",
            "raavi",
            "sakkal",
            "segoe",
            "simsun",
            "simsb",
            "nsimsun",
            "simfang",
            "simkai",
            "simli",
            "sylfaen",
            "tahoma",
            "times",
            "trebuc",
            "verdan",
            "cambriab",
            "cambriaz",
            "cambriai",
            "cambri",
            "gili",
            "gilsan",
            "gisha",
            "refspc",
            "refsan",
            "segmdl2",
            "seguibl",
            "leelawu",
            "georgia",
            "segui",
            "frabk",
            "fradm",
            "fradmcn",
            "pertibd",
            "pertili",
            "javatext",
            "bernhc",
            "centaur",
            "deng",
            "msuighur",
            "seguisym",
        },
        key=len,
        reverse=True,
    )
)

_BAD_SUB: tuple[str, ...] = (
    "naskh arabic",
    "arabic ui",
    " hebrew",
    "devanagari",
    "bengali",
    "gujarati",
    "gurmukhi",
    "kannada",
    "malayalam",
    "oriya",
    " sinhala",
    " telugu",
    "tamil",
    "tibetan",
    "khmer",
    "myanmar",
    "yi baiti",
    "mongolian b",
    "hanguel",
    "noto sans ar",
    "noto naskh",
    "mishafi",
    "malgun gothic",
    "batang",
    "gulim",
    "gungsu",
    "dotum",
    "hiragino",
    "kozuka gothic",
)

_RE_JK = re.compile(
    r"(\bnoto\s+.*(sans|serif|mono).*\b(jp|kr|kore)\b|"
    r"[\(（]\s*jp\s*[\)）]|[\(（]\s*kr\s*[\)）])",
    re.I,
)

_RE_KEEP = re.compile(
    r"(source\s*han|noto\s*.*\bcjk\b|"
    r"harmony|oppo|vivo|alibaba|misan|hanyi|fangz|"
    r"简|繁|臺|台|中黑|中宋|港|澳|體|书)",
    re.I,
)


def names_lower(ttf) -> str:
    o: list[str] = []
    try:
        for r in ttf["name"].names:
            try:
                o.append(str(r).lower())
            except Exception:
                pass
    except Exception:
        pass
    return " ".join(o)


def is_win_stem(stem: str) -> bool:
    s = stem.lower()
    for p in _WIN_PX:
        if s.startswith(p):
            return True
    return False


def bad_name(n: str) -> bool:
    if _RE_KEEP.search(n):
        return False
    low = n.lower()
    for x in _BAD_SUB:
        if x in low:
            return True
    if _RE_JK.search(low):
        return True
    return False


def cm(ttf) -> tuple[int, int, int, int]:
    a = b = c = d = 0
    try:
        for u in (ttf.getBestCmap() or {}):
            if 0x4E00 <= u <= 0x9FFF:
                a += 1
            if 0x20 <= u <= 0x7E:
                b += 1
            if 0x0600 <= u <= 0x06FF:
                c += 1
            if 0xAC00 <= u <= 0xD7A3:
                d += 1
    except Exception:
        pass
    return a, b, c, d


def should_remove(_path: Path, ttf, stem: str, nlow: str) -> tuple[bool, str]:
    if is_win_stem(stem):
        return True, "win"
    if bad_name(nlow):
        return True, "name"
    cj, la, ar, ha = cm(ttf)
    if cj >= 1:
        return False, ""
    if la >= 50:
        return False, ""
    if ha > 900 and cj < 3 and la < 60:
        return True, "cmap"
    if ar > 300 and cj < 1 and la < 50:
        return True, "cmap"
    if cj < 1 and la < 30:
        return True, "cmap"
    return False, ""
