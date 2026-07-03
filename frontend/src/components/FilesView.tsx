'use client'
import { useEffect, useState } from 'react'
import { Download, FileText, FileOutput } from 'lucide-react'
import { api, API, type GenFile } from '@/lib/api'

export default function FilesView({ refreshKey }: { refreshKey: number }) {
  const [files, setFiles] = useState<GenFile[]>([])
  useEffect(() => { api.files().then(d => setFiles(d.files)).catch(() => {}) }, [refreshKey])

  return (
    <div className="main">
      <div className="topbar"><h2>Files</h2><span className="sub">Reports the agent generated for you.</span></div>
      <div className="scroll pad">
        {files.length === 0 ? (
          <div className="card-panel" style={{ color: 'var(--muted)', fontSize: 14 }}>
            No files yet. Ask in chat for a “PDF summary” or “Word report” and it’ll show up here.
          </div>
        ) : files.map(f => (
          <a key={f.name} href={API + f.url} target="_blank" rel="noreferrer" download className="file-row">
            {f.name.endsWith('.pdf') ? <FileText size={16} color="var(--weak)" /> : <FileOutput size={16} color="var(--violet)" />}
            <span style={{ flex: 1 }}>{f.name}</span>
            <Download size={15} color="var(--muted)" />
          </a>
        ))}
      </div>
    </div>
  )
}
