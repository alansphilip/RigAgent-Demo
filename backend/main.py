"""
RIG Query Agent - FastAPI Backend
Main application entry point.
"""
import os
import json
import time
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

from database import get_db, create_tables
from models import QueryRequest, QueryResponse, SystemStatusResponse, RigDataResponse
from router import route_query
from agent_tools import (
    tool_equipment_knowledge,
    tool_work_pack_query,
    tool_shift_query,
    tool_procedure_query,
    tool_checklist_search,
    tool_generate_checklist_pdf,
)

# Initialize app
app = FastAPI(
    title="RIG Query Agent API",
    description="AI-powered query agent for offshore oil rig operations",
    version="1.0.4",
)

# CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins + ["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PDF output directory
PDF_OUTPUT_DIR = os.getenv("PDF_OUTPUT_DIR", "./generated_pdfs")
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)

# Mount static files for PDFs
app.mount("/pdfs", StaticFiles(directory=PDF_OUTPUT_DIR), name="pdfs")


# ─────────────────────────────────────────────────────────────
# LLM Client (abstracted for easy provider swap)
# ─────────────────────────────────────────────────────────────

class LLMClient:
    """Abstracted LLM client - swap provider by changing env vars."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = None
        
        if self.api_key and self.api_key != "your_openai_api_key_here":
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            except Exception as e:
                print(f"LLM client init warning: {e}")
    
    def generate(self, system_prompt: str, user_message: str, context: str = "") -> str:
        """Generate a response using the configured LLM."""
        if not self.client:
            return self._fallback_response(context, user_message)
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
            ]
            if context:
                messages.append({"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_message}"})
            else:
                messages.append({"role": "user", "content": user_message})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=1024,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM generation error: {e}")
            return self._fallback_response(context, user_message)
    
    def _fallback_response(self, context: str, query: str) -> str:
        """Return structured context when LLM is unavailable."""
        if context:
            return context
        return f"I received your query: *{query}*"


llm = LLMClient()

# System prompt for the rig assistant
SYSTEM_PROMPT = """You are RIG Query Agent, a professional AI assistant for offshore oil rig operations.
You help rig operators, engineers, and supervisors by answering questions about equipment, 
work packs, procedures, shift schedules, and maintenance checklists.

Guidelines:
- Respond like a knowledgeable field engineer who is precise and professional
- Format responses clearly using markdown (bold, bullet points, tables where appropriate)
- For equipment questions, explain function, specifications, and operational context
- For database queries (work packs, shifts, procedures), present the data clearly and summarize
- Use technical terminology appropriate for the oil & gas industry
- Keep responses concise but complete
- Always prioritize safety-critical information

Response format example for data queries:
**Current Active Work Packs** — 8 total
• WP001 – Pump Maintenance *(High Priority)*
• WP004 – Valve Inspection *(High Priority)*
"""


# ─────────────────────────────────────────────────────────────
# SMART RESPONSE FORMATTERS (used when no LLM key is configured)
# These produce professional markdown without needing an API call.
# ─────────────────────────────────────────────────────────────

def format_equipment_response(query: str, context: str, sources: list) -> str:
    """Format RAG equipment knowledge into clean markdown."""
    if not context:
        return "No equipment documentation found for that query. Try asking about: Mud Pump, BOP, Top Drive, Rotary Table, Drill Pipe, Choke Manifold, Mud Motor, Draw Works, Kelly, or Hook."

    # Extract the most relevant section (first chunk is highest score)
    sections = context.split("\n\n---\n\n")
    primary = sections[0].strip()

    src_list = " · ".join(f"**{s}**" for s in sources) if sources else ""
    source_line = f"\n\n---\n*Source: {src_list}*" if src_list else ""

    return f"{primary}{source_line}"


def format_work_pack_response(data: dict) -> str:
    """Format work pack SQL data into readable markdown."""
    # Single work pack detail
    if "work_pack" in data:
        wp = data["work_pack"]
        procs = wp.get("procedures", [])
        status_icon = {"Active": "🟢", "In Progress": "🟡", "Completed": "✅", "Pending": "⏳"}.get(wp["status"], "•")
        priority_icon = {"High": "🔴", "Medium": "🟠", "Low": "🟢"}.get(wp.get("priority", ""), "")

        lines = [
            f"## {wp['code']} — {wp['name']}",
            f"",
            f"| Field | Value |",
            f"|-------|-------|",
            f"| **Status** | {status_icon} {wp['status']} |",
            f"| **Priority** | {priority_icon} {wp.get('priority', 'N/A')} |",
            f"| **Description** | {wp.get('description', 'N/A')} |",
        ]
        if procs:
            lines += ["", "**Procedures:**", ""]
            for p in procs:
                icon = {"Completed": "✅", "In Progress": "🔄", "Pending": "⏳"}.get(p["status"], "•")
                lines.append(f"- {icon} `{p['code']}` — {p['name']} *({p['status']})*")
        return "\n".join(lines)

    # Filtered list (e.g. "show active work packs")
    if "status_filter" in data:
        status = data["status_filter"]
        wps = data.get("work_packs", [])
        count = data.get("count", len(wps))
        status_icon = {"Active": "🟢", "In Progress": "🟡", "Completed": "✅", "Pending": "⏳"}.get(status, "•")

        lines = [f"**{status_icon} {status} Work Packs** — {count} total", ""]
        for wp in wps:
            pri = {"High": "🔴", "Medium": "🟠", "Low": "🟢"}.get(wp.get("priority", ""), "")
            lines.append(f"- `{wp['code']}` — **{wp['name']}** {pri}")
        if not wps:
            lines.append("*No work packs found with that status.*")
        return "\n".join(lines)

    # Summary overview
    total = data.get("total", 0)
    by_status = data.get("by_status", {})
    wps = data.get("work_packs", [])

    lines = [f"**Work Pack Summary** — {total} total", ""]
    for status, count in by_status.items():
        icon = {"Active": "🟢", "In Progress": "🟡", "Completed": "✅", "Pending": "⏳"}.get(status, "•")
        lines.append(f"- {icon} **{status}**: {count}")
    lines += ["", "**All Work Packs:**", ""]
    for wp in wps[:15]:
        icon = {"Active": "🟢", "In Progress": "🟡", "Completed": "✅", "Pending": "⏳"}.get(wp["status"], "•")
        lines.append(f"- {icon} `{wp['code']}` — {wp['name']} *({wp['status']})*")
    return "\n".join(lines)


def format_shift_response(data: dict) -> str:
    """Format shift SQL data into readable markdown."""
    label = data.get("label", "recent")
    shifts = data.get("shifts", [])

    label_map = {
        "current": "🟢 Current Active Shift",
        "previous": "🕐 Previous Shifts",
        "morning": "🌅 Morning Shifts",
        "night": "🌙 Night Shifts",
        "recent": "📋 Recent Shifts",
    }
    heading = label_map.get(label, f"Shifts — {label}")

    if not shifts:
        return f"**{heading}**\n\nNo shift records found."

    lines = [f"**{heading}**", ""]

    for s in shifts:
        status_icon = "🟢 Active" if s["status"] == "Active" else "✅ Completed"
        shift_icon = {"Morning": "🌅", "Afternoon": "☀️", "Night": "🌙"}.get(s["shift_type"], "🔄")
        lines += [
            f"### {shift_icon} {s['operator']} — {s['shift_type']} Shift",
            f"",
            f"| Field | Value |",
            f"|-------|-------|",
            f"| **Status** | {status_icon} |",
            f"| **Date** | {s.get('date', 'N/A')} |",
            f"| **Login** | {s['login_time']} |",
            f"| **Logout** | {s['logout_time']} |",
            f"",
        ]
    return "\n".join(lines).strip()


def format_procedure_response(data: dict) -> str:
    """Format procedure SQL data into readable markdown."""
    # Single procedure detail
    if "procedure" in data:
        proc = data["procedure"]
        ops = proc.get("operations", [])
        status_icon = {"Completed": "✅", "In Progress": "🔄", "Pending": "⏳"}.get(proc["status"], "•")

        lines = [
            f"## `{proc['code']}` — {proc['name']}",
            f"",
            f"| Field | Value |",
            f"|-------|-------|",
            f"| **Status** | {status_icon} {proc['status']} |",
            f"| **Assigned To** | {proc.get('assigned_to', 'Unassigned')} |",
        ]
        if ops:
            lines += ["", "**Operations:**", ""]
            for op in ops:
                icon = {"Completed": "✅", "In Progress": "🔄", "Pending": "⏳"}.get(op["status"], "•")
                lines.append(f"{op['step']}. {icon} {op['name']}")
        return "\n".join(lines)

    # Filtered or full list
    filter_val = data.get("filter", "all")
    procs = data.get("procedures", [])
    count = data.get("count", len(procs))
    summary = data.get("summary", {})

    icon_map = {"Completed": "✅", "In Progress": "🔄", "Pending": "⏳"}
    filter_label = f"**{icon_map.get(filter_val, '📋')} {filter_val.title()} Procedures** — {count} total"

    lines = [filter_label, ""]
    if filter_val == "all" and summary:
        for st, cnt in summary.items():
            lines.append(f"- {icon_map.get(st, '•')} **{st}**: {cnt}")
        lines.append("")

    for p in procs:
        icon = icon_map.get(p["status"], "•")
        assigned = f" *(assigned: {p['assigned_to']})*" if p.get("assigned_to") else ""
        lines.append(f"- {icon} `{p['code']}` — **{p['name']}**{assigned}")

    if not procs:
        lines.append("*No procedures found.*")
    return "\n".join(lines)


def format_checklist_response(data: dict) -> str:
    """Format checklist data into readable markdown."""
    if not data.get("found"):
        return "No matching checklist found. Try: *Mud Pump checklist*, *BOP checklist*, *Top Drive checklist*."

    cl = data["checklist"]
    items = cl.get("items", [])
    required = [i for i in items if i.get("is_required")]
    optional = [i for i in items if not i.get("is_required")]

    lines = [
        f"## 📋 {cl['name']}",
        f"**Equipment:** {cl['equipment']}  |  **{len(items)} items** ({len(required)} required)",
        "",
        "### Required Checks",
        "",
    ]
    for item in required:
        lines.append(f"- ☐ **Step {item['step_number']}:** {item['description']}")

    if optional:
        lines += ["", "### Optional Checks", ""]
        for item in optional:
            lines.append(f"- ☐ *(Optional)* {item['description']}")

    lines += ["", "---", "*Use the **Download PDF** button to get a printable checklist.*"]
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# MAIN QUERY ENDPOINT
# ─────────────────────────────────────────────────────────────

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, db: Session = Depends(get_db)):
    """
    Main agent endpoint. Routes query to appropriate tool and generates response.
    """
    user_query = request.message.strip()
    if not user_query:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Step 1: Route the query to appropriate tool
    intent = route_query(user_query)
    
    pdf_url = None
    sources = []
    tool_result = {}
    
    # Step 2: Execute the appropriate tool and format the response
    if intent == "equipment":
        tool_result = tool_equipment_knowledge(user_query)
        raw_context = tool_result.get("context", "")
        sources = tool_result.get("sources", [])
        if llm.client:
            answer = llm.generate(SYSTEM_PROMPT, user_query, raw_context)
        else:
            answer = format_equipment_response(user_query, raw_context, sources)

    elif intent == "work_pack":
        tool_result = tool_work_pack_query(user_query, db)
        if llm.client:
            answer = llm.generate(SYSTEM_PROMPT, user_query,
                                  f"Work Pack Database Results:\n{json.dumps(tool_result['data'], indent=2)}")
        else:
            answer = format_work_pack_response(tool_result["data"])

    elif intent == "shift":
        tool_result = tool_shift_query(user_query, db)
        if llm.client:
            answer = llm.generate(SYSTEM_PROMPT, user_query,
                                  f"Shift Database Results:\n{json.dumps(tool_result['data'], indent=2)}")
        else:
            answer = format_shift_response(tool_result["data"])

    elif intent == "procedure":
        tool_result = tool_procedure_query(user_query, db)
        if llm.client:
            answer = llm.generate(SYSTEM_PROMPT, user_query,
                                  f"Procedure Database Results:\n{json.dumps(tool_result['data'], indent=2)}")
        else:
            answer = format_procedure_response(tool_result["data"])

    elif intent == "checklist_search":
        tool_result = tool_checklist_search(user_query, db)
        if llm.client:
            answer = llm.generate(SYSTEM_PROMPT, user_query,
                                  f"Checklist Database Results:\n{json.dumps(tool_result['data'], indent=2)}")
        else:
            answer = format_checklist_response(tool_result["data"])

    elif intent == "checklist_pdf":
        tool_result = tool_generate_checklist_pdf(user_query, db)
        data = tool_result["data"]
        if data.get("success"):
            filename = data["filename"]
            pdf_url = f"/checklist/{filename}"
            answer = (
                f"**Checklist Generated Successfully** ✓\n\n"
                f"| Field | Value |\n"
                f"|-------|-------|\n"
                f"| **Checklist** | {data['checklist_name']} |\n"
                f"| **Equipment** | {data['equipment']} |\n"
                f"| **Items** | {data['item_count']} inspection points |\n\n"
                f"Your PDF checklist is ready for download."
            )
        else:
            answer = f"Could not generate checklist PDF: {data.get('message', 'Unknown error')}"

    elif intent == "greeting":
        if llm.client:
            answer = llm.generate(SYSTEM_PROMPT, user_query, "The user greeted you. Respond warmly as RIG Query Agent and summarize what you can help with.")
        else:
            answer = (
                "Hello! I am the **RIG Query Agent**, your AI-powered assistant for offshore rig operations. ⚡\n\n"
                "I am online and ready to assist you with:\n\n"
                "- 🛠️ **Equipment Knowledge** — *e.g., \"What is a Blowout Preventer?\", \"Explain Top Drive specifications\"*\n"
                "- 📋 **Work Pack Status** — *e.g., \"Show active work packs\", \"Details for WP001\"*\n"
                "- 👨‍🔧 **Shift Roster & Operators** — *e.g., \"Who is in the current shift?\", \"Show previous night shifts\"*\n"
                "- ⚙️ **Standard Operating Procedures** — *e.g., \"Show completed procedures\", \"Status of procedure P002\"*\n"
                "- 📄 **Checklist PDFs** — *e.g., \"Download Mud Pump checklist\", \"BOP Ram checklist\"*\n\n"
                "How can I assist your operations today?"
            )

    else:
        if llm.client:
            answer = llm.generate(SYSTEM_PROMPT, user_query)
        else:
            answer = (
                "I am specialized in offshore rig operational data and equipment knowledge.\n\n"
                "Here are some examples of queries I can answer accurately:\n\n"
                "1. **Equipment Knowledge:** *\"What is a Mud Pump?\"*, *\"Explain Iron Roughneck\"*\n"
                "2. **Work Pack Tracking:** *\"Show active work packs\"*, *\"What is WP002 status?\"*\n"
                "3. **Shift Logs:** *\"Who is on duty in the current shift?\"*\n"
                "4. **Procedures:** *\"List all completed procedures\"*\n"
                "5. **PDF Checklists:** *\"Generate Mud Pump inspection checklist PDF\"*"
            )

    return QueryResponse(
        answer=answer,
        pdf_url=pdf_url,
        tool_used=intent,
        sources=sources if sources else None,
    )


# ─────────────────────────────────────────────────────────────
# CHECKLIST PDF DOWNLOAD
# ─────────────────────────────────────────────────────────────

@app.get("/checklist/{filename}")
async def get_checklist_pdf(filename: str):
    """
    Serve a generated PDF checklist file.
    """
    filepath = os.path.join(PDF_OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Checklist PDF not found")
    
    # Security: ensure file is within PDF directory
    if not os.path.abspath(filepath).startswith(os.path.abspath(PDF_OUTPUT_DIR)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=filename,
    )


# ─────────────────────────────────────────────────────────────
# SYSTEM STATUS
# ─────────────────────────────────────────────────────────────

@app.get("/system-status")
async def get_system_status():
    """Return mock system status for the rig."""
    return {
        "telemetry_health": 98.2,
        "telemetry_trend": "+0.4%",
        "connectivity": "Active - Satellite",
        "connectivity_detail": "Primary Link Established",
        "active_alerts": 1,
        "query_latency_ms": 140,
        "last_updated": "08:45 UTC",
        "subsystems": [
            {"name": "Drill Floor Sensors", "status": "Online", "uptime": "99.9%"},
            {"name": "Mud Pump Monitoring", "status": "Warning", "uptime": "98.5%"},
            {"name": "Power Generation", "status": "Online", "uptime": "100%"},
            {"name": "BOP Control System", "status": "Online", "uptime": "99.9%"},
        ],
        "events": [
            {
                "time": "08:42:15 UTC",
                "level": "INFO",
                "message": "Satellite handover complete. Connection stable."
            },
            {
                "time": "08:35:02 UTC",
                "level": "WARN",
                "message": "Minor sensor drift detected on Pump Alpha-3."
            },
            {
                "time": "08:00:00 UTC",
                "level": "INFO",
                "message": "Database backup successful. Sync verified."
            },
            {
                "time": "07:45:10 UTC",
                "level": "INFO",
                "message": "Automated diagnostic routine completed."
            },
        ],
        "warning_message": "Minor sensor drift detected on Pump Alpha-3. Diagnostic routine initiated."
    }


# ─────────────────────────────────────────────────────────────
# RIG DATA / TELEMETRY
# ─────────────────────────────────────────────────────────────

@app.get("/rig-data")
async def get_rig_data():
    """Return mock rig telemetry data for Mud Pump MP-04."""
    import math, random
    random.seed(42)  # Consistent data
    
    # Generate 24h trend data (vibration increasing over time)
    trend_data = []
    for i in range(25):  # 24 hours + now
        hour = i - 24  # T-24h to Now
        base = 1.2 + (i * 0.08)  # Gradual increase
        noise = random.uniform(-0.1, 0.15)
        value = round(base + noise, 2)
        trend_data.append({"hour": hour, "value": value, "label": f"T{hour}h" if hour < 0 else "Now"})
    
    return {
        "pump_id": "MP-04",
        "pump_name": "Mud Pump MP-04",
        "status": "WARNING",
        "last_inspection": "2023-10-24 08:30Z",
        "primary_op": "J. HENDERSON",
        "alert_message": "Elevated bearing vibration detected on Drive End bearing.",
        "intake_pressure_psi": 2450,
        "temperature_f": 185,
        "vibration_mms": 4.2,
        "vibration_trend": "+15% vs baseline",
        "vibration_status": "WARNING",
        "flow_rate_gpm": 850,
        "trend_data": trend_data,
        "maintenance_logs": [
            {
                "time": "10:42Z",
                "author": "AUTOMATED DIAG",
                "message": "Bearing wear detected beyond optimal threshold (Axial: 4.2mm/s).",
                "level": "warning"
            },
            {
                "time": "08:15Z",
                "author": "SYSTEM",
                "message": "Lubrication cycle initiated automatically.",
                "level": "info"
            },
            {
                "time": "06:00Z",
                "author": "J. HENDERSON",
                "message": "Shift start manual inspection completed. No visual anomalies.",
                "level": "info"
            },
            {
                "time": "YESTERDAY",
                "author": "SYSTEM",
                "message": "Scheduled calibration of pressure transducers completed.",
                "level": "info"
            },
        ]
    }


# ─────────────────────────────────────────────────────────────
# STARTUP
# ─────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """Initialize database and RAG index on startup."""
    print("RIG Query Agent starting up...")
    create_tables()
    
    # Check if DB has data, if not seed it
    from database import SessionLocal, WorkPack
    db = SessionLocal()
    try:
        count = db.query(WorkPack).count()
        if count == 0:
            print("No data found. Running database seeder...")
            import subprocess
            import sys
            subprocess.run([sys.executable, "setup_db.py"], check=True)
    finally:
        db.close()
    
    # Build RAG index if not exists
    from rag import load_index, build_rag_from_db
    import os
    index_file = os.path.join(os.getenv("FAISS_INDEX_PATH", "./faiss_index"), "equipment.index")
    if not os.path.exists(index_file):
        print("Building FAISS RAG index...")
        try:
            build_rag_from_db()
        except Exception as e:
            print(f"RAG index build warning: {e}")
    
    print("RIG Query Agent ready!")


@app.get("/")
async def root():
    return {"status": "operational", "version": "1.0.4", "service": "RIG Query Agent API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
