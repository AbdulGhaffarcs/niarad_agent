'use client'
import { useState, useEffect, useCallback } from 'react'
import { Plus, MessageSquare, Trash2, ChevronLeft, ChevronRight } from 'lucide-react'
import { getAllChats, deleteChat } from '@/lib/storage'

interface ChatSidebarProps {
  currentChatId: string | null
  onSelectChat: (id: string) => void
  onNewChat: () => void
  onDeleteChat: (id: string) => void
  collapsed?: boolean
  onToggleCollapse?: () => void
  refreshKey?: number
}

export default function ChatSidebar({
  currentChatId,
  onSelectChat,
  onNewChat,
  onDeleteChat,
  collapsed = false,
  onToggleCollapse,
  refreshKey = 0,
}: ChatSidebarProps) {
  const [chats, setChats] = useState<Array<{ id: string; title: string; updatedAt: number }>>([])

  const loadChats = useCallback(async () => {
    const all = await getAllChats()
    setChats(all)
  }, [])

  useEffect(() => { loadChats() }, [loadChats, refreshKey])

  if (collapsed) {
    return (
      <button
        className="sidebar-toggle"
        onClick={onToggleCollapse}
        aria-label="Expand chat history"
        style={{ marginTop: 'auto', marginBottom: 8 }}
      >
        <ChevronRight size={18} />
      </button>
    )
  }

  return (
    <div className="sidebar-chats">
      <div className="sidebar-chats-header">
        <h3>Chats</h3>
        <button className="btn-icon" onClick={onNewChat} title="New chat">
          <Plus size={16} />
        </button>
      </div>
      <div className="chats-list">
        {chats.length === 0 ? (
          <div className="no-chats">No chats yet</div>
        ) : chats.map(chat => (
          <button
            key={chat.id}
            className={`chat-item ${chat.id === currentChatId ? 'active' : ''}`}
            onClick={() => onSelectChat(chat.id)}
          >
            <MessageSquare size={14} />
            <span className="chat-title" title={chat.title}>{chat.title}</span>
            <button
              className="btn-icon delete-chat"
              onClick={e => { e.stopPropagation(); deleteChat(chat.id); onDeleteChat(chat.id); loadChats() }}
              title="Delete"
            >
              <Trash2 size={12} />
            </button>
          </button>
        ))}
      </div>
    </div>
  )
}