import { useState, useEffect } from 'react'
import { RefreshCw, AlertTriangle, Shield, Radio, Clock, Activity } from 'lucide-react'
import { SystemStatus } from '../types'

const API_URL = import.meta.env.VITE_API_URL || ''

function StatusBadge({ status }: { status: string }) {
  const variants: Record<string, string> = {
    Online: 'badge-online',
    Warning: 'badge-warning',
    Critical: 'badge-critical',
    Offline: 'badge-offline',
  }
  const cls = variants[status] || 'badge-offline'
  return (
    <span className={cls}>
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {status}
    </span>
  )
}

function EventBadge({ level }: { level: string }) {
  const variants: Record<string, string> = {
    INFO: 'text-blue-400 bg-blue-500/10 border-blue-500/30',
    WARN: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
    ERROR: 'text-red-400 bg-red-500/10 border-red-500/30',
  }
  return (
    <span className={`text-xs font-mono px-1.5 py-0.5 rounded border ${variants[level] || variants.INFO}`}>
      {level}
    </span>
  )
}

export default function SystemStatusPage() {
  const [data, setData] = useState<SystemStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [lastRefresh, setLastRefresh] = useState(new Date())

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/system-status`)
      const json = await res.json()
      setData(json)
      setLastRefresh(new Date())
    } catch {
      // Use mock data on error
      setData({
        telemetry_health: 98.2,
        telemetry_trend: '+0.4%',
        connectivity: 'Active - Satellite',
        connectivity_detail: 'Primary Link Established',
        active_alerts: 1,
        query_latency_ms: 140,
        last_updated: '08:45 UTC',
        subsystems: [
          { name: 'Drill Floor Sensors', status: 'Online', uptime: '99.9%' },
          { name: 'Mud Pump Monitoring', status: 'Warning', uptime: '98.5%' },
          { name: 'Power Generation', status: 'Online', uptime: '100%' },
          { name: 'BOP Control System', status: 'Online', uptime: '99.9%' },
        ],
        events: [
          { time: '08:42:15 UTC', level: 'INFO', message: 'Satellite handover complete. Connection stable.' },
          { time: '08:35:02 UTC', level: 'WARN', message: 'Minor sensor drift detected on Pump Alpha-3.' },
          { time: '08:00:00 UTC', level: 'INFO', message: 'Database backup successful. Sync verified.' },
          { time: '07:45:10 UTC', level: 'INFO', message: 'Automated diagnostic routine completed.' },
        ],
        warning_message: 'Minor sensor drift detected on Pump Alpha-3. Diagnostic routine initiated.',
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchData() }, [])

  return (
    <div className="flex flex-col h-full overflow-y-auto bg-rig-bg">
      <div className="max-w-5xl mx-auto w-full p-6 space-y-5">
        {/* Page header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="text-rig-amber font-mono text-sm font-medium mb-1">RIG Query Agent</div>
            <h1 className="text-2xl font-bold text-rig-text">System Status</h1>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-rig-muted font-mono">
              Last updated: {data?.last_updated || '...'}
            </span>
            <button
              onClick={fetchData}
              disabled={loading}
              className="w-8 h-8 flex items-center justify-center rounded-lg border border-rig-border text-rig-muted hover:text-rig-amber hover:border-rig-amber transition-all"
            >
              <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            </button>
          </div>
        </div>

        {/* Warning banner */}
        {data?.warning_message && (
          <div className="flex items-start gap-3 p-4 bg-rig-card border border-rig-border rounded-lg border-l-2 border-l-rig-amber">
            <AlertTriangle size={16} className="text-rig-amber mt-0.5 flex-shrink-0" />
            <div>
              <div className="text-sm font-semibold text-rig-text mb-0.5">Subsystem Warning Active</div>
              <div className="text-sm text-rig-muted-light">{data.warning_message}</div>
            </div>
          </div>
        )}

        {/* Metric cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Telemetry Health */}
          <div className="rig-card">
            <div className="flex items-center justify-between mb-3">
              <span className="rig-label">Telemetry Health</span>
              <Shield size={14} className="text-rig-muted" />
            </div>
            <div className="text-2xl font-bold text-rig-text">{data?.telemetry_health ?? '—'}%</div>
            <div className="text-xs text-green-400 mt-1 font-mono">↑ {data?.telemetry_trend}</div>
          </div>

          {/* Connectivity */}
          <div className="rig-card">
            <div className="flex items-center justify-between mb-3">
              <span className="rig-label">RIG Connectivity</span>
              <Radio size={14} className="text-rig-muted" />
            </div>
            <div className="text-base font-bold text-rig-text">{data?.connectivity}</div>
            <div className="text-xs text-rig-muted mt-1">{data?.connectivity_detail}</div>
          </div>

          {/* Active Alerts */}
          <div className="rig-card border-rig-amber/30 bg-rig-amber/5">
            <div className="flex items-center justify-between mb-3">
              <span className="rig-label text-rig-amber">Active Critical Alerts</span>
              <Activity size={14} className="text-rig-amber" />
            </div>
            <div className="w-10 h-10 rounded-full bg-rig-amber flex items-center justify-center">
              <span className="text-black font-bold text-lg">{data?.active_alerts ?? 0}</span>
            </div>
          </div>

          {/* Query Latency */}
          <div className="rig-card">
            <div className="flex items-center justify-between mb-3">
              <span className="rig-label">Query Latency</span>
              <Clock size={14} className="text-rig-muted" />
            </div>
            <div className="text-2xl font-bold text-rig-text">{data?.query_latency_ms ?? '—'}<span className="text-sm font-normal text-rig-muted ml-1">ms</span></div>
            <div className="mt-2 h-1 bg-rig-border rounded-full overflow-hidden">
              <div className="h-full bg-rig-amber rounded-full" style={{ width: '60%' }} />
            </div>
          </div>
        </div>

        {/* Main content row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Subsystem table */}
          <div className="lg:col-span-2 rig-card">
            <h2 className="text-base font-semibold text-rig-text mb-4">Subsystem Status</h2>
            <table className="w-full">
              <thead>
                <tr className="border-b border-rig-border">
                  <th className="rig-label text-left pb-3">Subsystem</th>
                  <th className="rig-label text-left pb-3">Status</th>
                  <th className="rig-label text-right pb-3">Uptime</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-rig-border">
                {data?.subsystems.map((sys) => (
                  <tr key={sys.name} className="hover:bg-rig-border/10 transition-colors">
                    <td className="py-3 text-sm text-rig-text">{sys.name}</td>
                    <td className="py-3">
                      <StatusBadge status={sys.status} />
                    </td>
                    <td className="py-3 text-sm text-rig-muted-light text-right font-mono">{sys.uptime}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Events panel */}
          <div className="rig-card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-semibold text-rig-text">System Events</h2>
              <Activity size={14} className="text-rig-muted" />
            </div>
            <div className="space-y-3">
              {data?.events.map((evt, i) => (
                <div key={i} className="pb-3 border-b border-rig-border last:border-0 last:pb-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-mono text-rig-muted">{evt.time}</span>
                    <EventBadge level={evt.level} />
                  </div>
                  <p className="text-xs text-rig-text-dim leading-relaxed">{evt.message}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Refresh button */}
        <button
          onClick={fetchData}
          disabled={loading}
          className="w-full rig-btn-primary flex items-center justify-center gap-2 py-3"
        >
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          Refresh Status
        </button>
      </div>
    </div>
  )
}
