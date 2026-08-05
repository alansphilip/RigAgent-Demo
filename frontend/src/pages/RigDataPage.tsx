import { useState, useEffect } from 'react'
import { AlertTriangle, Activity, Gauge, Thermometer, Droplets, ChevronUp } from 'lucide-react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine
} from 'recharts'
import { RigData } from '../types'

const API_URL = import.meta.env.VITE_API_URL || ''

const TIME_RANGES = ['1H', '6H', '24H']

interface TelemetryCardProps {
  label: string
  value: string | number
  unit: string
  icon: React.ReactNode
  progress?: number
  progressColor?: string
  highlighted?: boolean
  trend?: string
  status?: string
}

function TelemetryCard({ label, value, unit, icon, progress, progressColor = 'bg-blue-500', highlighted, trend, status }: TelemetryCardProps) {
  return (
    <div className={`rig-card ${
      highlighted
        ? 'border-rig-amber/40 bg-rig-amber/5'
        : ''
    }`}>
      <div className="flex items-center justify-between mb-3">
        <span className={`rig-label ${highlighted ? 'text-rig-amber' : ''}`}>{label}</span>
        <div className="flex items-center gap-2">
          {status && (
            <span className="text-xs font-mono px-2 py-0.5 bg-rig-amber text-black font-bold rounded">
              {status}
            </span>
          )}
          <span className={highlighted ? 'text-rig-amber' : 'text-rig-muted'}>{icon}</span>
        </div>
      </div>
      <div className={`text-3xl font-bold ${highlighted ? 'text-rig-amber' : 'text-rig-text'}`}>
        {value} <span className="text-sm font-normal text-rig-muted">{unit}</span>
      </div>
      {trend && (
        <div className="flex items-center gap-1 mt-1">
          <ChevronUp size={12} className="text-rig-amber" />
          <span className="text-xs text-rig-amber font-mono">{trend}</span>
        </div>
      )}
      {progress !== undefined && (
        <div className="mt-3 h-1 bg-rig-border rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${progressColor}`}
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
    </div>
  )
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-rig-panel border border-rig-border rounded-lg px-3 py-2">
        <div className="text-xs font-mono text-rig-muted mb-1">{label}</div>
        <div className="text-sm font-bold text-rig-amber">{payload[0].value} mm/s</div>
      </div>
    )
  }
  return null
}

export default function RigDataPage() {
  const [data, setData] = useState<RigData | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeRange, setActiveRange] = useState('24H')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(`${API_URL}/rig-data`)
        const json = await res.json()
        setData(json)
      } catch {
        // mock fallback
        const trend = Array.from({ length: 25 }, (_, i) => ({
          hour: i - 24,
          value: +(1.2 + i * 0.08 + (Math.random() - 0.5) * 0.2).toFixed(2),
          label: i < 24 ? `T-${24 - i}h` : 'Now',
        }))
        setData({
          pump_id: 'MP-04', pump_name: 'Mud Pump MP-04', status: 'WARNING',
          last_inspection: '2023-10-24 08:30Z', primary_op: 'J. HENDERSON',
          alert_message: 'Elevated bearing vibration detected on Drive End bearing.',
          intake_pressure_psi: 2450, temperature_f: 185, vibration_mms: 4.2,
          vibration_trend: '+15% vs baseline', vibration_status: 'WARNING',
          flow_rate_gpm: 850,
          trend_data: trend,
          maintenance_logs: [
            { time: '10:42Z', author: 'AUTOMATED DIAG', message: 'Bearing wear detected beyond optimal threshold (Axial: 4.2mm/s).', level: 'warning' },
            { time: '08:15Z', author: 'SYSTEM', message: 'Lubrication cycle initiated automatically.', level: 'info' },
            { time: '06:00Z', author: 'J. HENDERSON', message: 'Shift start manual inspection completed. No visual anomalies.', level: 'info' },
            { time: 'YESTERDAY', author: 'SYSTEM', message: 'Scheduled calibration of pressure transducers completed.', level: 'info' },
          ],
        })
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const getChartData = () => {
    if (!data) return []
    const all = data.trend_data
    if (activeRange === '1H') return all.slice(-4)
    if (activeRange === '6H') return all.slice(-7)
    return all
  }

  return (
    <div className="flex flex-col h-full overflow-y-auto bg-rig-bg">
      <div className="max-w-5xl mx-auto w-full p-6 space-y-5">
        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-rig-text">{data?.pump_name || 'Mud Pump MP-04'}</h1>
            <p className="text-rig-muted text-sm mt-1">Subsystem Detail &amp; Telemetry</p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-rig-amber/10 border border-rig-amber/40 rounded-lg">
              <AlertTriangle size={14} className="text-rig-amber" />
              <span className="text-xs font-mono font-bold text-rig-amber">WARNING STATUS</span>
            </div>
            <div className="text-right">
              <div className="rig-label">Last Inspection</div>
              <div className="text-xs text-rig-text font-mono">{data?.last_inspection}</div>
            </div>
            <div className="text-right">
              <div className="rig-label">Primary OP</div>
              <div className="text-xs text-rig-text font-mono font-semibold">{data?.primary_op}</div>
            </div>
          </div>
        </div>

        {/* Alert banner */}
        {data?.alert_message && (
          <div className="flex items-center gap-3 p-3 bg-rig-amber/10 border border-rig-amber/30 rounded-lg">
            <AlertTriangle size={16} className="text-rig-amber flex-shrink-0" />
            <div>
              <span className="text-xs font-mono text-rig-amber font-bold">STATUS ALERT</span>
              <p className="text-sm text-rig-text mt-0.5">{data.alert_message}</p>
            </div>
          </div>
        )}

        {/* Telemetry cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <TelemetryCard
            label="Intake Pressure"
            value={data?.intake_pressure_psi?.toLocaleString() ?? '—'}
            unit="PSI"
            icon={<Gauge size={14} />}
            progress={65}
            progressColor="bg-blue-500"
          />
          <TelemetryCard
            label="Temperature"
            value={data?.temperature_f ?? '—'}
            unit="°F"
            icon={<Thermometer size={14} />}
            progress={74}
            progressColor="bg-orange-500"
          />
          <TelemetryCard
            label="Vibration Level"
            value={data?.vibration_mms ?? '—'}
            unit="mm/s"
            icon={<Activity size={14} />}
            highlighted
            trend={data?.vibration_trend}
            status={data?.vibration_status}
          />
          <TelemetryCard
            label="Flow Rate"
            value={data?.flow_rate_gpm ?? '—'}
            unit="GPM"
            icon={<Droplets size={14} />}
            progress={85}
            progressColor="bg-blue-400"
          />
        </div>

        {/* Chart + Logs row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Vibration chart */}
          <div className="lg:col-span-2 rig-card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-semibold text-rig-text">Vibration Trend (24h)</h2>
              <div className="flex gap-1">
                {TIME_RANGES.map(r => (
                  <button
                    key={r}
                    onClick={() => setActiveRange(r)}
                    className={`text-xs font-mono px-2 py-1 rounded transition-all ${
                      activeRange === r
                        ? 'bg-rig-amber text-black font-bold'
                        : 'text-rig-muted hover:text-rig-text bg-rig-border/50'
                    }`}
                  >
                    {r}
                  </button>
                ))}
              </div>
            </div>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={getChartData()} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
                  <XAxis
                    dataKey="label"
                    tick={{ fontSize: 10, fill: '#6b7280', fontFamily: 'JetBrains Mono' }}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fontSize: 10, fill: '#6b7280', fontFamily: 'JetBrains Mono' }}
                    tickLine={false}
                    axisLine={false}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <ReferenceLine y={3.5} stroke="#f59e0b" strokeDasharray="4 4" strokeWidth={1} />
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke="#f59e0b"
                    strokeWidth={2.5}
                    dot={false}
                    activeDot={{ r: 5, fill: '#f59e0b', stroke: '#1a1a1a', strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-between mt-2">
              <span className="text-xs font-mono text-rig-muted">T-24H</span>
              <span className="text-xs font-mono text-rig-muted">NOW</span>
            </div>
          </div>

          {/* Maintenance logs */}
          <div className="rig-card">
            <div className="flex items-center gap-2 mb-4">
              <Activity size={14} className="text-rig-muted" />
              <h2 className="text-base font-semibold text-rig-text">Maintenance Logs</h2>
            </div>
            <div className="space-y-4">
              {data?.maintenance_logs.map((log, i) => (
                <div key={i} className={`pb-3 border-b border-rig-border last:border-0 last:pb-0 ${
                  log.level === 'warning' ? 'border-l-2 border-l-rig-amber pl-2' : ''
                }`}>
                  <div className="text-xs font-mono text-rig-amber mb-0.5">{log.time} · {log.author}</div>
                  <p className="text-xs text-rig-text-dim leading-relaxed">{log.message}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Action button */}
        <button className="w-full rig-btn-primary flex items-center justify-center gap-2 py-3">
          <Activity size={16} />
          Initiate Diagnostic Routine
        </button>
      </div>
    </div>
  )
}
