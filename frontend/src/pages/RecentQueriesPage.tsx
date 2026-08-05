import { useState, useEffect } from 'react'
import { Clock, Search, Trash2, MessageSquare } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { QueryHistoryItem } from '../types'

const DEFAULT_SAMPLE_QUERIES: QueryHistoryItem[] = [
  { id: '1', query: 'What is a Blowout Preventer?', tool: 'equipment', time: '08:42 UTC', date: 'Today', timestamp: Date.now() - 3600000 },
  { id: '2', query: 'How many active work packs?', tool: 'work_pack', time: '08:35 UTC', date: 'Today', timestamp: Date.now() - 4000000 },
  { id: '3', query: 'Who is in the current shift?', tool: 'shift', time: '08:15 UTC', date: 'Today', timestamp: Date.now() - 5000000 },
  { id: '4', query: 'Show completed procedures.', tool: 'procedure', time: '07:52 UTC', date: 'Today', timestamp: Date.now() - 6000000 },
  { id: '5', query: 'Download Mud Pump checklist.', tool: 'checklist_pdf', time: '07:30 UTC', date: 'Today', timestamp: Date.now() - 7000000 },
  { id: '6', query: 'Explain Iron Roughneck system.', tool: 'equipment', time: '16:22 UTC', date: 'Yesterday', timestamp: Date.now() - 86400000 },
  { id: '7', query: 'What is Managed Pressure Drilling?', tool: 'equipment', time: '14:10 UTC', date: 'Yesterday', timestamp: Date.now() - 95000000 },
]

const TOOL_LABELS: Record<string, { label: string; color: string }> = {
  equipment: { label: 'EQUIPMENT', color: 'text-blue-400 bg-blue-500/10 border-blue-500/20' },
  equipment_knowledge: { label: 'EQUIPMENT', color: 'text-blue-400 bg-blue-500/10 border-blue-500/20' },
  work_pack: { label: 'WORK PACK', color: 'text-green-400 bg-green-500/10 border-green-500/20' },
  work_pack_query: { label: 'WORK PACK', color: 'text-green-400 bg-green-500/10 border-green-500/20' },
  shift: { label: 'SHIFT', color: 'text-purple-400 bg-purple-500/10 border-purple-500/20' },
  shift_query: { label: 'SHIFT', color: 'text-purple-400 bg-purple-500/10 border-purple-500/20' },
  procedure: { label: 'PROCEDURE', color: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20' },
  procedure_query: { label: 'PROCEDURE', color: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20' },
  checklist_search: { label: 'CHECKLIST', color: 'text-amber-400 bg-amber-500/10 border-amber-500/20' },
  checklist_pdf: { label: 'CHECKLIST PDF', color: 'text-amber-400 bg-amber-500/10 border-amber-500/20' },
  greeting: { label: 'GREETING', color: 'text-rig-amber bg-rig-amber/10 border-rig-amber/20' },
  general: { label: 'GENERAL', color: 'text-rig-muted bg-rig-border/50 border-rig-border' },
}

export default function RecentQueriesPage() {
  const [search, setSearch] = useState('')
  const [queriesList, setQueriesList] = useState<QueryHistoryItem[]>([])
  const navigate = useNavigate()

  useEffect(() => {
    try {
      const raw = localStorage.getItem('rig_recent_queries')
      if (raw) {
        const parsed = JSON.parse(raw)
        if (Array.isArray(parsed) && parsed.length > 0) {
          setQueriesList(parsed)
          return
        }
      }
    } catch (e) {}
    setQueriesList(DEFAULT_SAMPLE_QUERIES)
  }, [])

  const handleClearAll = () => {
    localStorage.removeItem('rig_recent_queries')
    setQueriesList([])
  }

  const handleDeleteItem = (e: React.MouseEvent, id: string) => {
    e.stopPropagation()
    const updated = queriesList.filter(q => q.id !== id)
    setQueriesList(updated)
    localStorage.setItem('rig_recent_queries', JSON.stringify(updated))
  }

  const filtered = queriesList.filter(q =>
    q.query.toLowerCase().includes(search.toLowerCase())
  )

  const grouped = filtered.reduce((acc, q) => {
    const groupKey = q.date || 'Today'
    if (!acc[groupKey]) acc[groupKey] = []
    acc[groupKey].push(q)
    return acc
  }, {} as Record<string, QueryHistoryItem[]>)

  const handleRerun = (query: string) => {
    navigate('/', { state: { query } })
  }

  return (
    <div className="flex flex-col h-full overflow-y-auto bg-rig-bg">
      <div className="max-w-2xl mx-auto w-full p-6 space-y-5">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-rig-amber font-mono text-sm font-medium mb-1">History</div>
            <h1 className="text-2xl font-bold text-rig-text">Recent Queries</h1>
          </div>
          {queriesList.length > 0 && (
            <button
              onClick={handleClearAll}
              className="flex items-center gap-1.5 text-xs font-mono text-rig-muted hover:text-red-400 transition-colors px-2.5 py-1.5 rounded border border-rig-border hover:border-red-400/40"
            >
              <Trash2 size={12} />
              CLEAR HISTORY
            </button>
          )}
        </div>

        {/* Search */}
        <div className="relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-rig-muted" />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search recent queries..."
            className="w-full bg-rig-card border border-rig-border rounded-lg pl-9 pr-4 py-2.5 text-sm text-rig-text placeholder:text-rig-muted focus:outline-none focus:border-rig-amber transition-colors font-mono"
          />
        </div>

        {/* Groups */}
        {Object.entries(grouped).map(([date, queries]) => (
          <div key={date}>
            <div className="rig-label mb-3">{date}</div>
            <div className="space-y-2">
              {queries.map(q => {
                const toolInfo = TOOL_LABELS[q.tool] || { label: q.tool.toUpperCase(), color: 'text-rig-muted bg-rig-border/50 border-rig-border' }
                return (
                  <div key={q.id} className="rig-card hover:border-rig-amber/30 cursor-pointer group flex items-center justify-between" onClick={() => handleRerun(q.query)}>
                    <div className="flex items-start gap-3 flex-1 min-w-0 pr-3">
                      <MessageSquare size={14} className="text-rig-muted mt-0.5 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-rig-text group-hover:text-rig-amber transition-colors truncate font-mono">{q.query}</p>
                        <div className="flex items-center gap-2 mt-1.5">
                          <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${toolInfo.color}`}>{toolInfo.label}</span>
                          <span className="text-xs text-rig-muted font-mono">{q.time}</span>
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={(e) => handleDeleteItem(e, q.id)}
                      className="opacity-0 group-hover:opacity-100 p-1.5 text-rig-muted hover:text-red-400 transition-all rounded hover:bg-rig-border/40 flex-shrink-0"
                      title="Delete query"
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                )
              })}
            </div>
          </div>
        ))}

        {filtered.length === 0 && (
          <div className="text-center py-12">
            <Clock size={32} className="text-rig-muted mx-auto mb-3" />
            <p className="text-rig-muted text-sm font-mono">No recent queries found.</p>
          </div>
        )}
      </div>
    </div>
  )
}
