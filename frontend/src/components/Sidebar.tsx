'use client'
import { MessageSquare, GraduationCap, FolderOpen, FileDown } from 'lucide-react'

export type Tab = 'chat' | 'study' | 'vault' | 'files'

const ITEMS: { id: Tab; label: string; Icon: typeof MessageSquare }[] = [
  { id: 'chat',  label: 'Ask',   Icon: MessageSquare },
  { id: 'study', label: 'Study', Icon: GraduationCap },
  { id: 'vault', label: 'Vault', Icon: FolderOpen },
  { id: 'files', label: 'Files', Icon: FileDown },
]

export default function Sidebar({ tab, setTab, dueCount, vaultReady, docCount }:
  { tab: Tab; setTab: (t: Tab) => void; dueCount: number; vaultReady: boolean; docCount: number }) {
  return (
    <aside className="rail">
      <div className="brand">
        <h1>NIARAD</h1>
        <span className="tag">study agent</span>
      </div>

      <nav className="nav">
        {ITEMS.map(({ id, label, Icon }) => (
          <button key={id} className={'nav-item' + (tab === id ? ' active' : '')} onClick={() => setTab(id)}>
            <Icon size={18} />
            <span>{label}</span>
            {id === 'study' && dueCount > 0 && <span className="count">{dueCount}</span>}
          </button>
        ))}
      </nav>

      <div className="rail-foot">
        <div className="vault-chip">
          <span className={'dot ' + (vaultReady ? 'on' : 'off')} />
          <span>{vaultReady ? `${docCount} chunks indexed` : 'Vault empty'}</span>
        </div>
      </div>
    </aside>
  )
}
