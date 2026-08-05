import { useState } from 'react'
import { Save, Cpu, Key, Globe, Sliders } from 'lucide-react'

export default function ModelConfigPage() {
  const [config, setConfig] = useState({
    provider: 'openai',
    model: 'gpt-4o-mini',
    apiKey: '',
    baseUrl: 'https://api.openai.com/v1',
    temperature: '0.3',
    maxTokens: '1024',
  })
  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="flex flex-col h-full overflow-y-auto bg-rig-bg">
      <div className="max-w-2xl mx-auto w-full p-6 space-y-6">
        <div>
          <div className="text-rig-amber font-mono text-sm font-medium mb-1">Configuration</div>
          <h1 className="text-2xl font-bold text-rig-text">Model Config</h1>
          <p className="text-sm text-rig-muted mt-1">Configure the LLM provider and parameters for the AI agent.</p>
        </div>

        {/* Provider */}
        <div className="rig-card space-y-4">
          <div className="flex items-center gap-2 mb-2">
            <Cpu size={16} className="text-rig-amber" />
            <h2 className="font-semibold text-rig-text">Provider Settings</h2>
          </div>

          <div>
            <label className="rig-label block mb-2">LLM Provider</label>
            <select
              value={config.provider}
              onChange={e => setConfig(c => ({ ...c, provider: e.target.value }))}
              className="w-full bg-rig-card border border-rig-border rounded-lg px-3 py-2.5 text-sm text-rig-text focus:outline-none focus:border-rig-amber transition-colors font-mono"
            >
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="groq">Groq</option>
              <option value="ollama">Ollama (Local)</option>
              <option value="custom">Custom OpenAI-compatible</option>
            </select>
          </div>

          <div>
            <label className="rig-label block mb-2">Model</label>
            <select
              value={config.model}
              onChange={e => setConfig(c => ({ ...c, model: e.target.value }))}
              className="w-full bg-rig-card border border-rig-border rounded-lg px-3 py-2.5 text-sm text-rig-text focus:outline-none focus:border-rig-amber transition-colors font-mono"
            >
              <option value="gpt-4o-mini">gpt-4o-mini</option>
              <option value="gpt-4o">gpt-4o</option>
              <option value="gpt-3.5-turbo">gpt-3.5-turbo</option>
              <option value="claude-3-haiku-20240307">claude-3-haiku</option>
              <option value="llama3-70b-8192">llama3-70b (Groq)</option>
            </select>
          </div>
        </div>

        {/* API Config */}
        <div className="rig-card space-y-4">
          <div className="flex items-center gap-2 mb-2">
            <Key size={16} className="text-rig-amber" />
            <h2 className="font-semibold text-rig-text">API Configuration</h2>
          </div>

          <div>
            <label className="rig-label block mb-2">API Key</label>
            <input
              type="password"
              value={config.apiKey}
              onChange={e => setConfig(c => ({ ...c, apiKey: e.target.value }))}
              placeholder="sk-...  (set in backend .env)"
              className="w-full bg-rig-card border border-rig-border rounded-lg px-3 py-2.5 text-sm text-rig-text placeholder:text-rig-muted focus:outline-none focus:border-rig-amber transition-colors font-mono"
            />
            <p className="text-xs text-rig-muted mt-1">Set <code className="text-rig-amber">OPENAI_API_KEY</code> in backend <code className="text-rig-amber">.env</code> file.</p>
          </div>

          <div>
            <label className="rig-label block mb-2">Base URL</label>
            <div className="flex items-center gap-2">
              <Globe size={14} className="text-rig-muted flex-shrink-0" />
              <input
                type="text"
                value={config.baseUrl}
                onChange={e => setConfig(c => ({ ...c, baseUrl: e.target.value }))}
                className="flex-1 bg-rig-card border border-rig-border rounded-lg px-3 py-2.5 text-sm text-rig-text focus:outline-none focus:border-rig-amber transition-colors font-mono"
              />
            </div>
          </div>
        </div>

        {/* Parameters */}
        <div className="rig-card space-y-4">
          <div className="flex items-center gap-2 mb-2">
            <Sliders size={16} className="text-rig-amber" />
            <h2 className="font-semibold text-rig-text">Generation Parameters</h2>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="rig-label block mb-2">Temperature</label>
              <input
                type="number"
                min="0" max="2" step="0.1"
                value={config.temperature}
                onChange={e => setConfig(c => ({ ...c, temperature: e.target.value }))}
                className="w-full bg-rig-card border border-rig-border rounded-lg px-3 py-2.5 text-sm text-rig-text focus:outline-none focus:border-rig-amber transition-colors font-mono"
              />
            </div>
            <div>
              <label className="rig-label block mb-2">Max Tokens</label>
              <input
                type="number"
                min="256" max="4096" step="256"
                value={config.maxTokens}
                onChange={e => setConfig(c => ({ ...c, maxTokens: e.target.value }))}
                className="w-full bg-rig-card border border-rig-border rounded-lg px-3 py-2.5 text-sm text-rig-text focus:outline-none focus:border-rig-amber transition-colors font-mono"
              />
            </div>
          </div>
        </div>

        <button
          onClick={handleSave}
          className={`w-full flex items-center justify-center gap-2 py-3 rounded-lg font-semibold text-sm transition-all duration-200 ${
            saved
              ? 'bg-green-500 text-white'
              : 'bg-rig-amber text-black hover:bg-rig-amber-light active:scale-95'
          }`}
        >
          <Save size={16} />
          {saved ? 'Saved!' : 'Save Configuration'}
        </button>

        <div className="rig-card">
          <div className="rig-label mb-3">Current Status</div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-rig-muted">Backend URL</span>
              <span className="font-mono text-rig-text text-xs">{import.meta.env.VITE_API_URL || 'http://localhost:8000'}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-rig-muted">RAG Status</span>
              <span className="badge-online">Active</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-rig-muted">Agent Version</span>
              <span className="font-mono text-rig-text text-xs">V-1.0.4</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
