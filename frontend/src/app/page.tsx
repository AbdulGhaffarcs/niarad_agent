'use client'
import { useState, useEffect, useCallback } from 'react'
import { MessageSquare, GraduationCap, FolderOpen, FileDown } from 'lucide-react'
import ChatView from '@/components/ChatView'
import StudyView from '@/components/StudyView'
import VaultView from '@/components/VaultView'
import FilesView from '@/components/FilesView'
import ChatSidebar from '@/components/ChatSidebar'
import { api } from '@/lib/api'
import { saveChat, getChat, getAllChats, generateChatId, saveVaultFile } from '@/lib/storage'
import type { Message } from '@/lib/storage'

type Tab = 'chat' | 'study' | 'vault' | 'files'

export default function Home() {
  const [tab, setTab] = useState<Tab>('chat')
  const [vault, setVault] = useState({ has_docs: false, doc_count: 0 })
  const [dueCount, setDueCount] = useState(0)
  const [filesKey, setFilesKey] = useState(0)
  const [currentChatId, setCurrentChatId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [chatRefreshKey, setChatRefreshKey] = useState(0)

  const refreshVault = useCallback(() => { api.vaultStatus().then(setVault).catch(() => {}) }, [])
  const refreshDue = useCallback(() => { api.stats().then(s => setDueCount(s.due_now)).catch(() => {}) }, [])

  useEffect(() => { refreshVault(); refreshDue() }, [refreshVault, refreshDue])
  useEffect(() => { const t = setInterval(refreshDue, 15000); return () => clearInterval(t) }, [refreshDue])

  const handleNewChat = useCallback(async () => {
    const id = generateChatId()
    setCurrentChatId(id)
    setMessages([])
  }, [])

  const handleSelectChat = useCallback(async (id: string) => {
    const chat = await getChat(id)
    if (chat) {
      setCurrentChatId(id)
      setMessages(chat.messages)
    }
  }, [])

  const handleFileGenerated = useCallback(() => {
    setFilesKey(k => k + 1)
  }, [])

  const handleDeleteChat = useCallback((id: string) => {
    if (id === currentChatId) {
      setCurrentChatId(null)
      setMessages([])
    }
  }, [currentChatId])

  useEffect(() => {
    if (currentChatId || messages.length === 0) return
    const id = generateChatId()
    setCurrentChatId(id)
  }, [currentChatId, messages.length])

  useEffect(() => {
    if (!currentChatId || messages.length === 0) return
    const chatId = currentChatId
    const msgs = messages
    const t = setTimeout(async () => {
      try {
        const existingChats = await getAllChats()
        const existing = existingChats.find(c => c.id === chatId)
        const title = existing?.title || (msgs[0].role === 'user' ? msgs[0].content.slice(0, 60) : '')
        await saveChat(chatId, title, msgs)
        setChatRefreshKey(k => k + 1)
      } catch (e) {
        console.error('Failed to save chat:', e)
      }
    }, 800)
    return () => clearTimeout(t)
  }, [messages, currentChatId])

  useEffect(() => {
    if (vault.has_docs) {
      api.files().then(d => {
        d.files.forEach(f => {
          saveVaultFile({
            id: f.name,
            name: f.name,
            type: f.name.split('.').pop() || '',
            size: 0,
            indexedAt: Date.now(),
            skipped: false,
          })
        })
      }).catch(() => {})
    }
  }, [vault.has_docs])

  return (
    <div className="shell">
      <aside className={`rail ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <div className="brand">
          <h1>NIARAD</h1>
          <span className="tag">v0.1</span>
        </div>
        <nav className="nav">
          <button className={`nav-item ${tab === 'chat' ? 'active' : ''}`} onClick={() => setTab('chat')}>
            <MessageSquare size={16} />
            <span>Chat</span>
          </button>
          <button className={`nav-item ${tab === 'study' ? 'active' : ''}`} onClick={() => setTab('study')}>
            <GraduationCap size={16} />
            <span>Study</span>
            {dueCount > 0 && <span className="count">{dueCount}</span>}
          </button>
          <button className={`nav-item ${tab === 'vault' ? 'active' : ''}`} onClick={() => setTab('vault')}>
            <FolderOpen size={16} />
            <span>Vault</span>
            {vault.has_docs && <span className="count">{vault.doc_count}</span>}
          </button>
          <button className={`nav-item ${tab === 'files' ? 'active' : ''}`} onClick={() => setTab('files')}>
            <FileDown size={16} />
            <span>Files</span>
          </button>
        </nav>
        <div className="rail-foot">
          <div className="vault-chip">
            <span className={`dot ${vault.has_docs ? 'on' : 'off'}`} />
            <span>{vault.has_docs ? `${vault.doc_count} chunks` : 'Empty'}</span>
          </div>
        </div>
        <ChatSidebar
          currentChatId={currentChatId}
          onSelectChat={handleSelectChat}
          onNewChat={handleNewChat}
          onDeleteChat={handleDeleteChat}
          collapsed={sidebarCollapsed}
          onToggleCollapse={() => setSidebarCollapsed(false)}
          refreshKey={chatRefreshKey}
        />
      </aside>

      <main className="main">
        {tab === 'chat' && (
          <ChatView
            messages={messages}
            setMessages={setMessages}
            currentChatId={currentChatId}
            onFileGenerated={handleFileGenerated}
            onToggleSidebar={() => setSidebarCollapsed(!sidebarCollapsed)}
            sidebarCollapsed={sidebarCollapsed}
          />
        )}
        {tab === 'study' && <StudyView vaultReady={vault.has_docs} />}
        {tab === 'vault' && <VaultView docCount={vault.doc_count} onChange={refreshVault} />}
        {tab === 'files' && <FilesView refreshKey={filesKey} />}
      </main>
    </div>
  )
}