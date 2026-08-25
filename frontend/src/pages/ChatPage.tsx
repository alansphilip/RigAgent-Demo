import { useState, useRef, useEffect } from 'react'
import { Send, Download, Plus, Loader2, User, Zap } from 'lucide-react'
import { useLocation } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { ChatMessage, QueryResponse, QueryHistoryItem } from '../types'

const API_URL = import.meta.env.VITE_API_URL || ''

function saveRecentQuery(queryText: string, tool: string) {
  try {
    const existingRaw = localStorage.getItem('rig_recent_queries')
    let list: QueryHistoryItem[] = existingRaw ? JSON.parse(existingRaw) : []
    const now = new Date()
    const timeStr = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }) + ' UTC'
    
    const newItem: QueryHistoryItem = {
      id: crypto.randomUUID(),
      query: queryText,
      tool: tool || 'general',
      time: timeStr,
      date: 'Today',
      timestamp: Date.now()
    }

    list = [newItem, ...list.filter(q => q.query.toLowerCase() !== queryText.toLowerCase())].slice(0, 50)
    localStorage.setItem('rig_recent_queries', JSON.stringify(list))
  } catch (e) {
    console.error('Error saving recent query:', e)
  }
}

function formatTime(date: Date) {
  return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
}

function TypingIndicator() {
  return (
    <div className="flex items-start gap-3 animate-fade-in">
      <div className="w-8 h-8 rounded-full bg-rig-amber/20 border border-rig-amber/30 flex items-center justify-center flex-shrink-0 mt-0.5">
        <Zap size={14} className="text-rig-amber" />
      </div>
      <div className="bg-rig-card border border-rig-border rounded-lg px-4 py-3">
        <div className="flex gap-1 items-center">
          {[0, 1, 2].map(i => (
            <div
              key={i}
              className="w-1.5 h-1.5 bg-rig-amber rounded-full animate-typing"
              style={{ animationDelay: `${i * 0.2}s` }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user'
  const apiBase = import.meta.env.VITE_API_URL || ''

  if (isUser) {
    return (
      <div className="flex items-start gap-3 justify-end animate-fade-in">
        <div className="max-w-[75%]">
          <div className="bg-rig-border/60 border border-rig-border-light rounded-lg px-4 py-3 text-sm text-rig-text">
            {message.content}
          </div>
          <div className="text-right mt-1">
            <span className="text-xs text-rig-muted font-mono">{formatTime(message.timestamp)}</span>
          </div>
        </div>
        <div className="w-8 h-8 rounded-full bg-rig-border border border-rig-border-light flex items-center justify-center flex-shrink-0 mt-0.5">
          <User size={14} className="text-rig-muted-light" />
        </div>
      </div>
    )
  }

  return (
    <div className="flex items-start gap-3 animate-fade-in">
      <div className="w-8 h-8 rounded-full bg-rig-amber/20 border border-rig-amber/30 flex items-center justify-center flex-shrink-0 mt-0.5">
        <Zap size={14} className="text-rig-amber" />
      </div>
      <div className="max-w-[85%] min-w-0">
        {/* Analysis complete header */}
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xs font-mono font-medium text-rig-amber tracking-wider">
            ✦ ANALYSIS COMPLETE
          </span>
        </div>

        <div className="bg-rig-card border border-rig-border rounded-lg overflow-hidden">
          <div className="px-4 py-3">
            <div className="prose prose-invert prose-sm max-w-none text-rig-text text-sm leading-relaxed
              [&_strong]:text-rig-text [&_strong]:font-semibold
              [&_code]:text-rig-amber [&_code]:bg-rig-border/50 [&_code]:px-1.5 [&_code]:py-0.5 [&_code]:rounded [&_code]:font-mono [&_code]:text-xs
              [&_pre]:bg-rig-border/40 [&_pre]:border [&_pre]:border-rig-border [&_pre]:rounded [&_pre]:p-3 [&_pre]:font-mono [&_pre]:text-xs
              [&_ul]:space-y-1 [&_li]:text-rig-text-dim
              [&_table]:text-xs [&_th]:text-rig-muted [&_th]:font-mono [&_th]:font-medium [&_td]:text-rig-text-dim
              [&_blockquote]:border-l-2 [&_blockquote]:border-rig-amber [&_blockquote]:pl-3 [&_blockquote]:text-rig-muted-light
            ">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
          </div>

          {/* PDF Download */}
          {message.pdfUrl && (
            <div className="px-4 py-3 border-t border-rig-border bg-rig-panel/50">
              <a
                href={`${apiBase}${message.pdfUrl}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 bg-rig-amber text-black font-semibold text-sm px-4 py-2 rounded-lg hover:bg-rig-amber-light transition-all duration-200 active:scale-95"
              >
                <Download size={14} />
                Download Checklist PDF
              </a>
            </div>
          )}

          {/* Sources/tags */}
          {message.sources && message.sources.length > 0 && (
            <div className="px-4 py-2.5 border-t border-rig-border flex flex-wrap gap-2">
              {message.sources.map(src => (
                <span key={src} className="text-xs font-mono px-2 py-0.5 bg-rig-border/60 border border-rig-border-light rounded text-rig-muted-light">
                  {src.toUpperCase()}
                </span>
              ))}
            </div>
          )}

          {message.toolUsed && (
            <div className="px-4 py-2 border-t border-rig-border">
              <span className="text-xs font-mono text-rig-muted">TOOL: {message.toolUsed.toUpperCase().replace(/_/g, ' ')}</span>
            </div>
          )}
        </div>

        <div className="mt-1">
          <span className="text-xs text-rig-muted font-mono">{formatTime(message.timestamp)}</span>
        </div>
      </div>
    </div>
  )
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const location = useLocation()
  const [sessionTime] = useState(() => {
    const now = new Date()
    return now.toISOString().replace('T', ' ').substring(0, 16) + ' UTC'
  })
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isLoading])

  // Handle re-running query from Recent Queries navigation
  useEffect(() => {
    const navQuery = (location.state as { query?: string })?.query
    if (navQuery) {
      sendMessage(navQuery)
      window.history.replaceState({}, document.title)
    }
  }, [location.state])

  const sendMessage = async (query: string) => {
    if (!query.trim() || isLoading) return

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: query.trim(),
      timestamp: new Date(),
    }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setIsLoading(true)

    const assistantId = crypto.randomUUID()
    let fullText = ''
    let pdfUrl: string | undefined
    let toolUsed: string | undefined
    let streamStarted = false

    try {
      const apiUrl = import.meta.env.VITE_API_URL || ''
      const encodedMsg = encodeURIComponent(query.trim())

      // Try streaming first (SSE)
      const res = await fetch(`${apiUrl}/query/stream?message=${encodedMsg}`)
      if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`)

      const reader = res.body.getReader()
      const decoder = new TextDecoder()

      // Add empty assistant message immediately so user sees it start
      setMessages(prev => [...prev, {
        id: assistantId,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
      }])
      setIsLoading(false)
      streamStarted = true

      let buffer = ''
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const parsed = JSON.parse(line.slice(6))
            if (parsed.pdf_url) pdfUrl = parsed.pdf_url
            if (parsed.tool_used) toolUsed = parsed.tool_used
            if (parsed.token) {
              fullText += parsed.token
              setMessages(prev => prev.map(m =>
                m.id === assistantId
                  ? { ...m, content: fullText, pdfUrl, toolUsed }
                  : m
              ))
            }
            if (parsed.done) {
              if (parsed.tool_used) toolUsed = parsed.tool_used
              setMessages(prev => prev.map(m =>
                m.id === assistantId
                  ? { ...m, content: fullText.trim(), pdfUrl, toolUsed }
                  : m
              ))
            }
          } catch { /* skip malformed SSE line */ }
        }
      }

      saveRecentQuery(query.trim(), toolUsed || 'general')

    } catch (err) {
      if (streamStarted) {
        // Already showing partial — show error appended
        setMessages(prev => prev.map(m =>
          m.id === assistantId
            ? { ...m, content: fullText || '**Connection lost during streaming.**' }
            : m
        ))
      } else {
        setIsLoading(false)
        const errorMsg: ChatMessage = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: `**Connection Error**\n\nUnable to reach the RIG Query Agent backend at \`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}\`.`,
          timestamp: new Date(),
        }
        setMessages(prev => [...prev, errorMsg])
      }
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    sendMessage(input)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(input)
    }
  }

  const handleNewChat = () => {
    setMessages([])
    setInput('')
  }

  return (
    <div className="flex flex-col h-full bg-rig-bg">
      {/* Session header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-rig-border bg-rig-panel">
        <div className="font-mono text-xs text-rig-muted tracking-wider">
          SESSION INITIATED: {sessionTime}
        </div>
        <button
          onClick={handleNewChat}
          className="flex items-center gap-1.5 text-xs font-mono text-rig-muted hover:text-rig-amber transition-colors px-2 py-1 rounded hover:bg-rig-border/50"
        >
          <Plus size={12} />
          NEW SESSION
        </button>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-5">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full space-y-8 py-12">
            {/* Clean Professional Empty State */}
            <div className="text-center space-y-4 max-w-md">
              <div className="w-16 h-16 rounded-2xl bg-rig-amber/10 border border-rig-amber/30 flex items-center justify-center mx-auto shadow-lg shadow-rig-amber/5">
                <Zap size={30} className="text-rig-amber" />
              </div>
              <div className="space-y-1.5">
                <h2 className="text-2xl font-bold tracking-tight text-rig-text font-mono">RIG OPERATIONAL INTELLIGENCE</h2>
                <div className="inline-block px-3 py-1 bg-rig-amber/10 border border-rig-amber/30 rounded-full text-xs font-mono text-rig-amber">
                  AI ASSISTANT · SYSTEM ONLINE
                </div>
              </div>
              <p className="text-xs font-mono text-rig-muted leading-relaxed max-w-sm mx-auto">
                Ready for operational queries. Ask about equipment specifications, active work packs, shift rosters, maintenance procedures, or generate checklist PDFs.
              </p>
              
              <div className="pt-4 flex flex-wrap justify-center gap-2 font-mono text-[10px]">
                <span className="px-2.5 py-1 bg-rig-card border border-rig-border text-rig-muted rounded">EQUIPMENT MANUALS</span>
                <span className="px-2.5 py-1 bg-rig-card border border-rig-border text-rig-muted rounded">WORK PACK STATUS</span>
                <span className="px-2.5 py-1 bg-rig-card border border-rig-border text-rig-muted rounded">SHIFT LOGS</span>
                <span className="px-2.5 py-1 bg-rig-card border border-rig-border text-rig-muted rounded">PDF CHECKLISTS</span>
              </div>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {isLoading && <TypingIndicator />}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="px-4 py-3 border-t border-rig-border bg-rig-panel">
        <form onSubmit={handleSubmit} className="flex items-center gap-3">
          <button
            type="button"
            className="w-9 h-9 rounded-full border border-rig-border flex items-center justify-center text-rig-muted hover:text-rig-amber hover:border-rig-amber transition-all duration-200 flex-shrink-0"
          >
            <Plus size={16} />
          </button>
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Enter command or query rig data..."
            disabled={isLoading}
            className="flex-1 bg-rig-card border border-rig-border rounded-lg px-4 py-2.5 text-sm text-rig-text placeholder:text-rig-muted focus:outline-none focus:border-rig-amber transition-colors disabled:opacity-50 font-mono"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="w-10 h-10 rounded-lg bg-rig-amber flex items-center justify-center text-black hover:bg-rig-amber-light transition-all duration-200 active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed flex-shrink-0"
          >
            {isLoading ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <Send size={16} />
            )}
          </button>
        </form>
      </div>
    </div>
  )
}
