"""
Pydantic request/response models for the RIG Query Agent API.
"""
from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class QueryRequest(BaseModel):
    message: str


class QueryResponse(BaseModel):
    answer: str
    pdf_url: Optional[str] = None
    tool_used: Optional[str] = None
    sources: Optional[List[str]] = None


class WorkPackModel(BaseModel):
    id: int
    code: str
    name: str
    status: str
    priority: str
    created_date: str

    class Config:
        from_attributes = True


class ProcedureModel(BaseModel):
    id: int
    code: str
    name: str
    status: str
    assigned_to: Optional[str]
    work_pack_code: Optional[str]

    class Config:
        from_attributes = True


class ShiftModel(BaseModel):
    id: int
    operator_name: str
    shift_type: str
    login_time: str
    logout_time: Optional[str]
    status: str

    class Config:
        from_attributes = True


class ChecklistItemModel(BaseModel):
    id: int
    description: str
    is_required: bool
    step_number: int

    class Config:
        from_attributes = True


class ChecklistModel(BaseModel):
    id: int
    name: str
    equipment: str
    items: List[ChecklistItemModel] = []

    class Config:
        from_attributes = True


class SystemStatusResponse(BaseModel):
    telemetry_health: float
    connectivity: str
    active_alerts: int
    query_latency_ms: int
    subsystems: List[dict]
    recent_events: List[dict]


class RigDataResponse(BaseModel):
    pump_id: str
    status: str
    last_inspection: str
    primary_op: str
    intake_pressure_psi: float
    temperature_f: float
    vibration_mms: float
    flow_rate_gpm: float
    trend_data: List[dict]
    maintenance_logs: List[dict]
