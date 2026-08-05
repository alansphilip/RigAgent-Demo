"""
Query intent routing for the RIG Query Agent.
Determines which tool to invoke based on the user's query.
"""
import re


# ─────────────────────────────────────────────────────────────
# Explicit greeting words checked FIRST before anything else
# ─────────────────────────────────────────────────────────────
GREETING_WORDS = {"hi", "hello", "hey", "hola", "yo", "howdy", "greetings", "sup"}

GREETING_PHRASES = [
    r"^(good\s*(morning|afternoon|evening|day))",
    r"who are you",
    r"what can you do",
    r"what are you",
    r"how can you help",
    r"what is this (app|tool|system|agent)",
    r"^help$",       # only standalone "help"
    r"^start$",
    r"^menu$",
]

# ─────────────────────────────────────────────────────────────
# Intent patterns (order matters — specific before generic)
# ─────────────────────────────────────────────────────────────
INTENT_PATTERNS = {
    "checklist_pdf": [
        r"download",
        r"generate.*checklist",
        r"checklist.*pdf",
        r"pdf.*checklist",
        r"print.*checklist",
        r"export.*checklist",
        r"get.*checklist",
    ],
    "checklist_search": [
        r"show.*checklist",
        r"checklist.*for",
        r"view.*checklist",
        r"list.*checklist",
        r"checklist",
    ],
    "shift": [
        r"current shift",
        r"who is.*shift",
        r"who worked",
        r"shift.*operator",
        r"shift.*timing",
        r"previous shift",
        r"last shift",
        r"night shift",
        r"morning shift",
        r"afternoon shift",
        r"who.*on duty",
        r"operator.*shift",
        r"\bshift\b",
    ],
    "procedure": [
        r"procedure[s]?",
        r"\bp\d{3}\b",
        r"pending.*procedure",
        r"completed.*procedure",
        r"procedure.*status",
        r"show.*procedure",
        r"in progress.*procedure",
    ],
    "work_pack": [
        r"work\s*pack[s]?",
        r"\bwp\d+\b",
        r"active.*pack",
        r"pack.*active",
        r"how many.*pack",
        r"list.*pack",
        r"pack.*status",
        r"maintenance.*pack",
    ],
    "equipment": [
        r"\bwhat is\b",
        r"\bexplain\b",
        r"\bhow does\b",
        r"\bhow do\b",
        r"\bwhat does\b",
        r"\bdescribe\b",
        r"\btell me about\b",
        r"\bpurpose of\b",
        r"\bspecification[s]?\b",
        r"\bspecs?\b",
        r"\boperate[s]?\b",
        r"\boperation of\b",
        r"\bmanual\b",
        r"\bmud pump\b",
        r"\bblowout preventer\b",
        r"\bbop\b",
        r"\btop drive\b",
        r"\brotary table\b",
        r"\bdrill pipe\b",
        r"\bchoke manifold\b",
        r"\bmud motor\b",
        r"\bdraw works\b",
        r"\bkelly\b",
        r"\bhook\b",
        r"\bswivel\b",
        r"\baccumulator\b",
        r"\bshale shaker\b",
        r"\bdegasser\b",
        r"\bdesander\b",
        r"\bdesilter\b",
        r"\bstandpipe\b",
        r"\bheave compensator\b",
        r"\biron roughneck\b",
        r"\briser\b",
        r"\bcatwalk\b",
        r"\bcementing\b",
        r"\bwireline\b",
        r"\bwellhead\b",
        r"\bchristmas tree\b",
        r"\bsubsea\b",
        r"\bmux pod\b",
        r"\bdynamic positioning\b",
        r"\b\bdp system\b",
        r"\bmpd\b",
        r"\bmanaged pressure\b",
        r"\bequipment\b",
    ],
}


def route_query(user_query: str) -> str:
    """
    Determine the intent of the user query and return the appropriate tool name.

    Returns one of:
        'checklist_pdf', 'checklist_search', 'shift', 'procedure',
        'work_pack', 'equipment', 'greeting', 'general'
    """
    query_lower = user_query.lower().strip()
    words = set(query_lower.split())

    # ── 1. Greeting — check FIRST before any other matching ──────────────
    # Direct single/few word greeting
    if words & GREETING_WORDS and len(words) <= 4:
        return "greeting"

    # Greeting phrases
    for pattern in GREETING_PHRASES:
        if re.search(pattern, query_lower):
            return "greeting"

    # ── 2. Score remaining intents ────────────────────────────────────────
    scores = {intent: 0 for intent in INTENT_PATTERNS}

    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, query_lower):
                scores[intent] += 1

    # Priority order for tie-breaking
    priority_order = [
        "checklist_pdf",
        "checklist_search",
        "shift",
        "procedure",
        "work_pack",
        "equipment",
    ]

    best_intent = max(priority_order, key=lambda i: scores[i])

    # ── 3. No intent matched → general ────────────────────────────────────
    if scores[best_intent] == 0:
        return "general"

    return best_intent
