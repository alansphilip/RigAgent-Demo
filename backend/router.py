"""
Query intent routing for the RIG Query Agent.
Determines which tool to invoke based on the user's query.
"""
import re

# Intent keyword mappings
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
        r"who.*on duty",
        r"operator.*shift",
        r"shift",
    ],
    "procedure": [
        r"procedure[s]?",
        r"p\d{3}",
        r"pending.*procedure",
        r"completed.*procedure",
        r"procedure.*status",
        r"show.*procedure",
    ],
    "work_pack": [
        r"work pack[s]?",
        r"wp\d+",
        r"active.*pack",
        r"pack.*active",
        r"how many.*pack",
        r"list.*pack",
        r"pack.*status",
    ],
    "greeting": [
        r"^\s*(hi|hello|hey|greetings|good\s*(morning|afternoon|evening)|hola|yo|howdy)\b",
        r"who are you",
        r"what can you do",
        r"help",
        r"start",
        r"menu",
        r"what is this",
    ],
    "equipment": [
        r"what is",
        r"explain",
        r"how does",
        r"what does",
        r"describe",
        r"tell me about",
        r"mud pump",
        r"blowout preventer",
        r"bop",
        r"top drive",
        r"rotary table",
        r"drill pipe",
        r"choke manifold",
        r"mud motor",
        r"draw works",
        r"kelly",
        r"hook",
        r"swivel",
        r"accumulator",
        r"shale shaker",
        r"degasser",
        r"desander",
        r"desilter",
        r"standpipe",
        r"heave compensator",
        r"iron roughneck",
        r"riser",
        r"catwalk",
        r"cementing",
        r"wireline",
        r"wellhead",
        r"christmas tree",
        r"equipment",
        r"manual",
        r"specification",
        r"specs",
        r"operate",
        r"purpose of",
    ],
}


def route_query(user_query: str) -> str:
    """
    Determine the intent of the user query and return the appropriate tool name.
    
    Returns one of: 'checklist_pdf', 'checklist_search', 'shift',
                    'procedure', 'work_pack', 'equipment', 'greeting', 'general'
    """
    query_lower = user_query.lower().strip()
    
    # Score each intent
    scores = {intent: 0 for intent in INTENT_PATTERNS}
    
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, query_lower):
                scores[intent] += 1
    
    # Check greeting first if explicit greeting match
    if scores["greeting"] > 0 and max(scores.values()) == scores["greeting"]:
        return "greeting"
    
    # Return highest scoring intent (with priority ordering for ties)
    priority_order = ["checklist_pdf", "checklist_search", "shift", "procedure", "work_pack", "equipment", "greeting"]
    
    best_intent = max(priority_order, key=lambda i: scores[i])
    
    # If no specific intent matched:
    if scores[best_intent] == 0:
        # Check if short message looks like a greeting or generic phrase
        if len(query_lower.split()) <= 3 and any(w in query_lower for w in ["hi", "hello", "hey", "help", "who"]):
            return "greeting"
        return "general"
    
    return best_intent
