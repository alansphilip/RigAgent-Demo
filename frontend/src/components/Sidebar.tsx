import { NavLink, useNavigate } from 'react-router-dom'
import {
  MessageSquare, Settings, Activity, Database,
  Clock, Cpu, Plus, X, Zap
} from 'lucide-react'

interface SidebarProps {
  onClose?: () => void
}

const navItems = [
  { path: '/', label: 'Chat', icon: MessageSquare, exact: true },
  { path: '/recent-queries', label: 'Recent Queries', icon: Clock },
  { path: '/model-config', label: 'Model Config', icon: Cpu },
  { path: '/system-status', label: 'System Status', icon: Activity },
  { path: '/rig-data', label: 'Rig Data', icon: Database },
]

export default function Sidebar({ onClose }: SidebarProps) {
  const navigate = useNavigate()

  const handleNewAnalysis = () => {
    navigate('/')
    onClose?.()
  }

  return (
    <div className="w-[220px] h-full bg-rig-panel border-r border-rig-border flex flex-col">
      {/* Logo area */}
      <div className="p-4 border-b border-rig-border">
        <div className="flex items-center gap-3 mb-1">
          {/* Avatar / Logo */}
          <div className="w-9 h-9 rounded-full bg-rig-amber/20 border border-rig-amber/40 flex items-center justify-center flex-shrink-0">
            <Zap size={16} className="text-rig-amber" />
          </div>
          <div className="min-w-0">
            <div className="text-rig-text font-semibold text-sm leading-tight">RIG Query Agent</div>
            <div className="text-rig-muted text-xs font-mono">V-1.0.4 · Operational</div>
          </div>
          {/* Mobile close button */}
          {onClose && (
            <button
              onClick={onClose}
              className="ml-auto lg:hidden text-rig-muted hover:text-rig-amber transition-colors"
            >
              <X size={16} />
            </button>
          )}
        </div>
      </div>

      {/* New Analysis Button */}
      <div className="px-3 py-3">
        <button
          onClick={handleNewAnalysis}
          className="w-full flex items-center justify-center gap-2 bg-rig-amber text-black font-semibold text-sm py-2.5 px-4 rounded-lg hover:bg-rig-amber-light transition-all duration-200 active:scale-95"
        >
          <Plus size={16} />
          New Analysis
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-1 space-y-0.5 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.exact}
            onClick={onClose}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-150 group ${
                isActive
                  ? 'bg-rig-amber/10 text-rig-amber border-l-2 border-rig-amber'
                  : 'text-rig-muted-light hover:text-rig-text hover:bg-rig-border/50 border-l-2 border-transparent'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <item.icon
                  size={16}
                  className={isActive ? 'text-rig-amber' : 'text-rig-muted group-hover:text-rig-text transition-colors'}
                />
                <span className="font-medium">{item.label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Settings at bottom */}
      <div className="p-3 border-t border-rig-border">
        <NavLink
          to="/model-config"
          className={({ isActive }) =>
            `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-150 ${
              isActive ? 'text-rig-amber' : 'text-rig-muted hover:text-rig-text'
            }`
          }
        >
          <Settings size={16} />
          <span>Settings</span>
        </NavLink>
      </div>
    </div>
  )
}
