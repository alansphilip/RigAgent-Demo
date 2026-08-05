"""
Agent tools for the RIG Query Agent.
Each tool handles a specific query category.
"""
import os
from typing import Optional, List
from sqlalchemy.orm import Session
from database import WorkPack, Procedure, Shift, Checklist, ChecklistItem, get_db
from rag import retrieve
from pdf_generator import generate_checklist_pdf


# ─────────────────────────────────────────────────────────────
# TOOL 1: Equipment Knowledge (RAG)
# ─────────────────────────────────────────────────────────────

def tool_equipment_knowledge(query: str) -> dict:
    """
    Uses RAG to answer equipment-related questions.
    Retrieves relevant chunks from the FAISS index.
    """
    results = retrieve(query, top_k=4)
    
    if not results:
        return {
            "tool": "equipment_knowledge",
            "context": "No equipment documentation found for this query.",
            "sources": [],
        }
    
    context_parts = []
    sources = []
    for r in results:
        context_parts.append(f"[{r['equipment']}]\n{r['text']}")
        if r["equipment"] not in sources:
            sources.append(r["equipment"])
    
    context = "\n\n---\n\n".join(context_parts)
    
    return {
        "tool": "equipment_knowledge",
        "context": context,
        "sources": sources,
    }


# ─────────────────────────────────────────────────────────────
# TOOL 2: Work Pack SQL Tool
# ─────────────────────────────────────────────────────────────

def tool_work_pack_query(query: str, db: Session) -> dict:
    """
    Queries the SQLite database for work pack information.
    """
    query_lower = query.lower()
    
    # Determine filter
    status_filter = None
    if any(w in query_lower for w in ["active"]):
        status_filter = "Active"
    elif any(w in query_lower for w in ["in progress", "inprogress"]):
        status_filter = "In Progress"
    elif any(w in query_lower for w in ["completed", "complete", "done", "finished"]):
        status_filter = "Completed"
    elif any(w in query_lower for w in ["pending", "not started"]):
        status_filter = "Pending"
    
    # Check if looking for a specific work pack
    work_packs = db.query(WorkPack).all()
    matching_wp = None
    for wp in work_packs:
        if wp.code.lower() in query_lower or wp.name.lower() in query_lower:
            matching_wp = wp
            break
    
    if matching_wp:
        # Return specific work pack detail
        procs = db.query(Procedure).filter(Procedure.work_pack_id == matching_wp.id).all()
        data = {
            "work_pack": {
                "code": matching_wp.code,
                "name": matching_wp.name,
                "status": matching_wp.status,
                "priority": matching_wp.priority,
                "description": matching_wp.description,
                "procedures": [{"code": p.code, "name": p.name, "status": p.status} for p in procs]
            }
        }
    elif status_filter:
        filtered = db.query(WorkPack).filter(WorkPack.status == status_filter).all()
        data = {
            "status_filter": status_filter,
            "count": len(filtered),
            "work_packs": [{"code": wp.code, "name": wp.name, "priority": wp.priority} for wp in filtered]
        }
    else:
        # Return summary
        all_wps = db.query(WorkPack).all()
        from collections import Counter
        status_counts = Counter(wp.status for wp in all_wps)
        data = {
            "total": len(all_wps),
            "by_status": dict(status_counts),
            "work_packs": [{"code": wp.code, "name": wp.name, "status": wp.status, "priority": wp.priority} for wp in all_wps]
        }
    
    return {"tool": "work_pack_query", "data": data}


# ─────────────────────────────────────────────────────────────
# TOOL 3: Shift SQL Tool
# ─────────────────────────────────────────────────────────────

def tool_shift_query(query: str, db: Session) -> dict:
    """
    Queries shift information from the database.
    """
    query_lower = query.lower()
    
    if any(w in query_lower for w in ["current", "active", "now", "on duty"]):
        shifts = db.query(Shift).filter(Shift.status == "Active").all()
        label = "current"
    elif any(w in query_lower for w in ["previous", "last", "before", "yesterday", "prior"]):
        shifts = db.query(Shift).filter(Shift.status == "Completed").order_by(Shift.id.desc()).limit(3).all()
        label = "previous"
    elif any(w in query_lower for w in ["morning"]):
        shifts = db.query(Shift).filter(Shift.shift_type == "Morning").order_by(Shift.id.desc()).limit(5).all()
        label = "morning"
    elif any(w in query_lower for w in ["night", "overnight"]):
        shifts = db.query(Shift).filter(Shift.shift_type == "Night").order_by(Shift.id.desc()).limit(5).all()
        label = "night"
    else:
        shifts = db.query(Shift).order_by(Shift.id.desc()).limit(5).all()
        label = "recent"
    
    data = {
        "label": label,
        "shifts": [
            {
                "operator": s.operator_name,
                "shift_type": s.shift_type,
                "login_time": s.login_time,
                "logout_time": s.logout_time or "Still on shift",
                "status": s.status,
                "date": s.date,
            }
            for s in shifts
        ]
    }
    
    return {"tool": "shift_query", "data": data}


# ─────────────────────────────────────────────────────────────
# TOOL 4: Procedure SQL Tool
# ─────────────────────────────────────────────────────────────

def tool_procedure_query(query: str, db: Session) -> dict:
    """
    Queries procedure information from the database.
    """
    query_lower = query.lower()
    
    # Specific procedure by code
    import re
    proc_code_match = re.search(r'p0*(\d+)', query_lower)
    if proc_code_match:
        code = f"P{proc_code_match.group(1).zfill(3)}"
        proc = db.query(Procedure).filter(Procedure.code == code).first()
        if proc:
            from database import Operation
            ops = db.query(Operation).filter(Operation.procedure_id == proc.id).all()
            return {
                "tool": "procedure_query",
                "data": {
                    "procedure": {
                        "code": proc.code,
                        "name": proc.name,
                        "status": proc.status,
                        "assigned_to": proc.assigned_to,
                        "operations": [{"step": op.step_order, "name": op.name, "status": op.status} for op in ops]
                    }
                }
            }
    
    # Status filter
    status_filter = None
    if any(w in query_lower for w in ["completed", "complete", "done", "finished"]):
        status_filter = "Completed"
    elif any(w in query_lower for w in ["pending", "not started", "upcoming"]):
        status_filter = "Pending"
    elif any(w in query_lower for w in ["in progress", "ongoing", "active"]):
        status_filter = "In Progress"
    
    if status_filter:
        procs = db.query(Procedure).filter(Procedure.status == status_filter).all()
    else:
        procs = db.query(Procedure).all()
    
    from collections import Counter
    all_procs = db.query(Procedure).all()
    status_counts = Counter(p.status for p in all_procs)
    
    return {
        "tool": "procedure_query",
        "data": {
            "filter": status_filter or "all",
            "count": len(procs),
            "summary": dict(status_counts),
            "procedures": [
                {"code": p.code, "name": p.name, "status": p.status, "assigned_to": p.assigned_to}
                for p in procs[:20]  # Limit to 20
            ]
        }
    }


# ─────────────────────────────────────────────────────────────
# TOOL 5: Checklist Search Tool
# ─────────────────────────────────────────────────────────────

def tool_checklist_search(query: str, db: Session) -> dict:
    """
    Searches for checklists matching the query.
    """
    checklists = db.query(Checklist).all()
    query_lower = query.lower()
    
    # Find matching checklist
    matched = None
    for cl in checklists:
        if (cl.equipment.lower() in query_lower or
            any(word in cl.name.lower() for word in query_lower.split() if len(word) > 3)):
            matched = cl
            break
    
    if not matched and checklists:
        # Default to first pump checklist
        for cl in checklists:
            if "pump" in cl.equipment.lower():
                matched = cl
                break
        if not matched:
            matched = checklists[0]
    
    if matched:
        items = db.query(ChecklistItem).filter(ChecklistItem.checklist_id == matched.id).all()
        return {
            "tool": "checklist_search",
            "data": {
                "found": True,
                "checklist": {
                    "id": matched.id,
                    "name": matched.name,
                    "equipment": matched.equipment,
                    "items": [
                        {"step_number": i.step_number, "description": i.description, "is_required": i.is_required}
                        for i in sorted(items, key=lambda x: x.step_number)
                    ]
                }
            }
        }
    
    return {"tool": "checklist_search", "data": {"found": False, "message": "No matching checklist found."}}


# ─────────────────────────────────────────────────────────────
# TOOL 6: Checklist PDF Generator
# ─────────────────────────────────────────────────────────────

def tool_generate_checklist_pdf(query: str, db: Session) -> dict:
    """
    Generates a downloadable PDF checklist.
    First searches for the relevant checklist, then generates PDF.
    """
    # Find checklist
    search_result = tool_checklist_search(query, db)
    
    if not search_result["data"].get("found"):
        return {
            "tool": "checklist_pdf",
            "data": {"success": False, "message": "No matching checklist found for PDF generation."}
        }
    
    cl_data = search_result["data"]["checklist"]
    
    # Get work pack code
    cl_obj = db.query(Checklist).filter(Checklist.id == cl_data["id"]).first()
    wp_code = ""
    if cl_obj and cl_obj.work_pack_id:
        wp = db.query(WorkPack).filter(WorkPack.id == cl_obj.work_pack_id).first()
        if wp:
            wp_code = wp.code
    
    try:
        filename = generate_checklist_pdf(
            checklist_name=cl_data["name"],
            equipment=cl_data["equipment"],
            procedure="Standard Inspection Procedure",
            items=cl_data["items"],
            inspector="Field Operator",
            work_pack_code=wp_code,
        )
        
        return {
            "tool": "checklist_pdf",
            "data": {
                "success": True,
                "filename": filename,
                "checklist_name": cl_data["name"],
                "equipment": cl_data["equipment"],
                "item_count": len(cl_data["items"]),
            }
        }
    except Exception as e:
        return {
            "tool": "checklist_pdf",
            "data": {"success": False, "message": f"PDF generation error: {str(e)}"}
        }
