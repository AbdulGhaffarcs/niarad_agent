'use client'
import { useState, useRef, useEffect, useCallback } from 'react'
import ReactMarkdown from 'react-markdown'
import { Send, Search, Code2, FileText, FileOutput, FolderSearch, Sparkles, PanelLeftClose, PanelLeftOpen } from 'lucide-react'
import { api, type Step, type ChatMessage } from '@/lib/api'
import type { Message } from '@/lib/storage'

const TOOL = {
  web_search:    { c: 'var(--cyan)',     Icon: Search },
  vault_search:  { c: 'var(--learning)', Icon: FolderSearch },
  execute_code:  { c: 'var(--strong)',   Icon: Code2 },
  generate_pdf:  { c: 'var(--weak)',     Icon: FileText },
  generate_docx: { c: 'var(--violet)',   Icon: FileOutput },
} as const

const badge = (mode = '') => ({
  AGENT:   { bg: 'var(--gold-soft)', c: 'var(--gold)' },
  NIARAD:  { bg: 'rgba(2,132,199,.08)', c: 'var(--cyan)' },
  BLOCKED: { bg: 'rgba(220,38,38,.1)', c: 'var(--weak)' },
  ERROR:   { bg: 'rgba(220,38,38,.1)', c: 'var(--weak)' },
})[mode.toUpperCase()] || { bg: 'var(--slate-2)', c: 'var(--muted)' }

const SUGGESTION_POOL = [
  'Explain gradient descent with a worked example',
  'Quiz me on what I uploaded',
  'Summarize my notes into a one-page PDF',
  'Compare supervised vs unsupervised learning',
  'Write a Python function for binary search',
  'Explain the Krebs cycle step by step',
  'Help me understand Newton\'s laws of motion',
  'What are the key differences between TCP and UDP?',
  'Explain how a neural network learns',
  'Give me 5 practice problems on integration',
  'What is the difference between AC and DC circuits?',
  'Explain the French Revolution in 5 key events',
  'How does photosynthesis work at the molecular level?',
  'Help me understand Big O notation',
  'Explain supply and demand with real examples',
  'What are the main types of chemical bonds?',
  'Help me write a thesis statement for my essay',
  'Explain how recursion works in programming',
  'What is the Doppler effect and why does it matter?',
  'Give me a study plan for my upcoming exam',
]

const DEFAULT_SUGGESTIONS = SUGGESTION_POOL.slice(0, 3)

interface ChatViewProps {
  messages: Message[]
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>
  currentChatId: string | null
  onFileGenerated: () => void
  onToggleSidebar?: () => void
  sidebarCollapsed?: boolean
}

export default function ChatView({ messages, setMessages, currentChatId, onFileGenerated, onToggleSidebar, sidebarCollapsed }: ChatViewProps) {
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [open, setOpen] = useState<Record<number, boolean>>({})
  const [suggestions, setSuggestions] = useState(DEFAULT_SUGGESTIONS)
  const end = useRef<HTMLDivElement>(null)

  useEffect(() => { end.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, loading])

  useEffect(() => {
    if (messages.length === 0) {
      const shuffled = [...SUGGESTION_POOL].sort(() => Math.random() - 0.5)
      setSuggestions(shuffled.slice(0, 3))
    }
  }, [currentChatId, messages.length])

  const send = useCallback(async (text?: string) => {
    const msg = (text ?? input).trim()
    if (!msg || loading) return
    setInput('')
    const userMsg: Message = { role: 'user', content: msg, timestamp: Date.now() }
    const newMessages = [...messages, userMsg]
    setMessages(newMessages)
    setLoading(true)
    try {
      const history: ChatMessage[] = messages.map(m => ({ role: m.role, content: m.content }))
      const data = await api.chat(msg, history)
      const assistantMsg: Message = {
        role: 'assistant',
        content: data.response,
        mode: data.mode,
        steps: data.steps,
        timestamp: Date.now(),
      }
      setMessages((prev: Message[]) => [...prev, assistantMsg])
      if (data.steps?.some(s => s.tool.includes('generate'))) onFileGenerated()
    } catch {
      const errorMsg: Message = {
        role: 'assistant',
        content: 'Couldn\'t reach the agent. Make sure the backend is running on port 8000.',
        mode: 'ERROR',
        timestamp: Date.now(),
      }
      setMessages((prev: Message[]) => [...prev, errorMsg])
    }
    setLoading(false)
  }, [input, loading, messages, setMessages, onFileGenerated])

  return (
    <div className="main">
      <div className="topbar">
        {onToggleSidebar && (
          <button className="btn-icon" onClick={onToggleSidebar} style={{ marginRight: 4 }}>
            {sidebarCollapsed ? <PanelLeftOpen size={18} /> : <PanelLeftClose size={18} />}
          </button>
        )}
        <h2>Ask</h2>
        <span className="sub">Search, run code, read your docs, or build a report.</span>
      </div>

      <div className="scroll pad" style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
        {messages.length === 0 && (
          <div className="empty">
            <Sparkles size={26} color="var(--gold)" />
            <h3>What are you studying today?</h3>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', justifyContent: 'center', marginTop: 6 }}>
              {suggestions.map(s => (
                <button key={s} className="btn btn-ghost" onClick={() => send(s)}>{s}</button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i}>
            <div className={'msg-row ' + m.role}>
              <div className={'avatar ' + (m.role === 'user' ? 'u' : 'n')}>{m.role === 'user' ? 'You'[0] : 'N'}</div>
              <div style={{ minWidth: 0 }}>
                {m.role === 'assistant' && m.mode && (
                  <div className="badge" style={{ background: badge(m.mode).bg, color: badge(m.mode).c }}>
                    {m.mode === 'AGENT' ? 'Agent' : m.mode === 'NIARAD' ? 'NIARAD' : m.mode}
                  </div>
                )}
                <div className={'bubble ' + m.role}>
                  {m.role === 'assistant'
                    ? <div className="prose"><ReactMarkdown>{m.content}</ReactMarkdown></div>
                    : m.content}
                </div>

                {m.steps && m.steps.length > 0 && (
                  <div>
                    <button className="steps-toggle" onClick={() => setOpen(o => ({ ...o, [i]: !o[i] }))}>
                      {open[i] ? 'Hide' : 'Show'} reasoning · {m.steps.length} step{m.steps.length > 1 ? 's' : ''}
                    </button>
                    {open[i] && m.steps.map((s, j) => {
                      const t = TOOL[s.tool as keyof typeof TOOL] || { c: 'var(--dim)', Icon: Sparkles }
                      const Ic = t.Icon
                      return (
                        <div key={j} className="step" style={{ borderLeftColor: t.c }}>
                          <div className="tool" style={{ color: t.c }}><Ic size={13} /> {s.tool.replace('_', ' ')}</div>
                          <div className="io">{s.input}</div>
                          <div className="io out">{s.output}</div>
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="msg-row">
            <div className="avatar n">N</div>
            <div className="bubble assistant thinking" style={{ color: 'var(--gold)' }}>Thinking through it…</div>
          </div>
        )}
        <div ref={end} />
      </div>

      <div className="composer">
        <input className="input" value={input} disabled={loading}
          placeholder="Ask anything…"
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()} />
        <button className="btn btn-accent" onClick={() => send()} disabled={loading || !input.trim()}>
          <Send size={15} /> Send
        </button>
      </div>
    </div>
  )
}