import unidecode

# Map Umlauts and 'ß' to private use codepoints
# see: https://unicode-table.com/en/blocks/private-use-area/
GERMAN_MAP = {
    "\u0364": "\u0308",  # uppercase e to trema, keeps the length of the word identical
    "æ": "ä",
    "ꝛ": "r",
    "ſ": "s",
    "/": ",",  # / is often replaced by comma in modern version
}

ESCAPE = {
    "Ä": "\ue000",
    "Ö": "\ue001",
    "Ü": "\ue002",
    "ä": "\ue003",
    "ö": "\ue004",
    "ü": "\ue005",
    "ß": "\ue006",
    "\u0308": "\ue007",
}

UNESCAPE = {
    "\ue000": "Ä",
    "\ue001": "Ö",
    "\ue002": "Ü",
    "\ue003": "ä",
    "\ue004": "ö",
    "\ue005": "ü",
    "\ue006": "ß",
    "\ue007": "\u0308",
}


def escape(token: str) -> str:
    return "".join([ESCAPE[s] if s in ESCAPE else s for s in token])


def unescape(token: str) -> str:
    return "".join([UNESCAPE[s] if s in UNESCAPE else s for s in token])


def german_map(token: str) -> str:
    for combi, repl in GERMAN_MAP.items():
        if combi in token:
            token = token.replace(combi, repl)
    return token


def unidecode_ger(s: str):
    """Simple transliteration of characters, preserving Umlauts and ß"""
    s = german_map(s)
    s = unescape(unidecode.unidecode(escape(s), errors="preserve"))
    return s
