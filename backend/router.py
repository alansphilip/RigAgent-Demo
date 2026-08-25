"""
Query intent routing for the RIG Query Agent.
Soft routing: always tries to be helpful. Routes to specific tools when
confident, falls back to general LLM+RAG for everything else.
"""
import re

# ─────────────────────────────────────────────────────────────
# Greeting — checked FIRST
# ─────────────────────────────────────────────────────────────
GREETING_WORDS = {"hi", "hello", "hey", "hola", "yo", "howdy", "greetings", "sup", "morning", "evening"}

GREETING_PHRASES = [
    r"^(good\s*(morning|afternoon|evening|day))",
    r"^who are you",
    r"^what can you do",
    r"^what are you",
    r"how can you help",
    r"what is this (app|tool|system|agent)",
    r"^help$",
    r"^start$",
    r"^menu$",
]

# ─────────────────────────────────────────────────────────────
# Specific tool intent patterns
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
        r"\bchecklist\b",
    ],
    "shift": [
        r"current shift",
        r"who is.*shift",
        r"who worked",
        r"shift.*operator",
        r"previous shift",
        r"last shift",
        r"night shift",
        r"morning shift",
        r"afternoon shift",
        r"who.*on duty",
        r"on duty",
        r"\bshift\b",
        r"how many.*work(ing|ers?)?",
        r"how many.*on duty",
        r"who.*work(ing)?",
        r"currently working",
        r"at work",
        r"who.*logged in",
        r"operators? (on|at|working)",
        r"active operator",
        r"how many people",
        r"how many staff",
        r"whos? working",
        r"who.*active",
        r"current worker",
        r"\bworker[s]?\b",
        r"\bpersonnel\b",
        r"\bstaff\b",
        r"how many.*employ",
        r"number of.*worker",
        r"number of.*operator",
        r"current.*staff",
        r"current.*worker",
        r"current.*operator",
        r"current.*personnel",
        r"logged.*in",
        r"active.*shift",
        r"today.*shift",
        r"today.*worker",
        r"on the rig",
        r"on rig today",
    ],
    "procedure": [
        r"\bprocedure[s]?\b",
        r"\bp\d{3}\b",
        r"pending.*procedure",
        r"completed.*procedure",
        r"procedure.*status",
        r"show.*procedure",
    ],
    "work_pack": [
        r"work\s*pack[s]?",
        r"\bwp\d+\b",
        r"active.*pack",
        r"pack.*active",
        r"how many.*pack",
        r"list.*pack",
        r"pack.*status",
    ],
    "equipment": [
        r"\bmud pump\b", r"\bblowout preventer\b", r"\bbop\b",
        r"\btop drive\b", r"\brotary table\b", r"\bdrill pipe\b",
        r"\bchoke manifold\b", r"\bmud motor\b", r"\bdraw works\b",
        r"\bkelly\b", r"\bswivel\b", r"\baccumulator\b",
        r"\bshale shaker\b", r"\bdegasser\b", r"\bdesander\b",
        r"\bdesilter\b", r"\bstandpipe\b", r"\bheave compensator\b",
        r"\biron roughneck\b", r"\briser\b", r"\bcatwalk\b",
        r"\bcementing\b", r"\bwireline\b", r"\bwellhead\b",
        r"\bchristmas tree\b", r"\bsubsea\b", r"\bmux pod\b",
        r"\bdynamic positioning\b", r"\bmpd\b", r"\bmanaged pressure\b",
    ],
}

# Keywords that indicate a general knowledge/question query → route to LLM+RAG
GENERAL_QUESTION_SIGNALS = [
    r"\bwhat is\b", r"\bwhat are\b", r"\bwhat does\b", r"\bhow does\b",
    r"\bhow do\b", r"\bwhy\b", r"\bwhen\b", r"\bexplain\b", r"\bdescribe\b",
    r"\btell me\b", r"\bcan you\b", r"\bshould i\b", r"\badvise\b",
    r"\brecommend\b", r"\bhelp me\b", r"\bwhat happens\b", r"\bhow to\b",
]


def route_query(user_query: str) -> str:
    """
    Determine the intent of the user query.

    Returns one of:
        'checklist_pdf', 'checklist_search', 'shift', 'procedure',
        'work_pack', 'equipment', 'greeting', 'general'

    'general' now means: use LLM + RAG context to answer ANY question.
    """
    query_lower = user_query.lower().strip()
    words = set(query_lower.split())

    # ── 1. Greeting check first ───────────────────────────────
    if words & GREETING_WORDS and len(words) <= 4:
        return "greeting"
    for pattern in GREETING_PHRASES:
        if re.search(pattern, query_lower):
            return "greeting"

    # ── 2. Score specific tool intents ────────────────────────
    scores = {intent: 0 for intent in INTENT_PATTERNS}
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, query_lower):
                scores[intent] += 1

    priority_order = [
        "checklist_pdf", "checklist_search",
        "shift", "procedure", "work_pack", "equipment",
    ]
    best_intent = max(priority_order, key=lambda i: scores[i])

    # ── 3. High-confidence specific tool match ────────────────
    if scores[best_intent] >= 1:
        return best_intent

    # ── 4. Everything else → general (LLM + RAG handles it) ──
    return "general"
