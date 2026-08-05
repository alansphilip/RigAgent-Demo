export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  pdfUrl?: string
  toolUsed?: string
  sources?: string[]
}

export interface QueryResponse {
  answer: string
  pdf_url?: string
  tool_used?: string
  sources?: string[]
}

export interface QueryHistoryItem {
  id: string
  query: string
  tool: string
  time: string
  date: string
  timestamp: number
}

export interface SystemStatus {
  telemetry_health: number
  telemetry_trend: string
  connectivity: string
  connectivity_detail: string
  active_alerts: number
  query_latency_ms: number
  last_updated: string
  subsystems: Array<{
    name: string
    status: string
    uptime: string
  }>
  events: Array<{
    time: string
    level: string
    message: string
  }>
  warning_message: string
}

export interface RigData {
  pump_id: string
  pump_name: string
  status: string
  last_inspection: string
  primary_op: string
  alert_message: string
  intake_pressure_psi: number
  temperature_f: number
  vibration_mms: number
  vibration_trend: string
  vibration_status: string
  flow_rate_gpm: number
  trend_data: Array<{ hour: number; value: number; label: string }>
  maintenance_logs: Array<{
    time: string
    author: string
    message: string
    level: string
  }>
}
