'use client'
import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { UploadCloud, FileCheck2, Trash2, AlertCircle, Loader2 } from 'lucide-react'
import { api } from '@/lib/api'

type UploadLog = {
  id: string
  name: string
  status: 'uploading' | 'ok' | 'skip' | 'err'
  detail: string
}

export default function VaultView({ docCount, onChange }: { docCount: number; onChange: () => void }) {
  const [logs, setLogs] = useState<UploadLog[]>([])
  const [isUploading, setIsUploading] = useState(false)

  const onDrop = useCallback(async (files: File[]) => {
    if (files.length === 0) return

    const queued = files.map((file, index) => ({
      id: `${file.name}-${file.size}-${Date.now()}-${index}`,
      name: file.name,
      status: 'uploading' as const,
      detail: 'Uploading and indexing...',
    }))

    setIsUploading(true)
    setLogs(previous => [...queued, ...previous])

    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      const id = queued[i].id

      try {
        const data = await api.upload(file)
        setLogs(previous => previous.map(log => log.id === id
          ? {
              ...log,
              status: data.skipped ? 'skip' : 'ok',
              detail: data.skipped ? 'Already indexed' : `Indexed ${data.chunks ?? 0} chunks`,
            }
          : log))
      } catch (error) {
        setLogs(previous => previous.map(log => log.id === id
          ? { ...log, status: 'err', detail: error instanceof Error ? error.message : 'Upload failed' }
          : log))
      }
    }

    setIsUploading(false)
    onChange()
  }, [onChange])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: true,
    disabled: isUploading,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/csv': ['.csv'],
    },
  })

  const clear = async () => {
    if (isUploading) return
    await api.clearVault()
    setLogs([])
    onChange()
  }

  return (
    <div className="main">
      <div className="topbar"><h2>Vault</h2><span className="sub">Your study material indexed locally, searched by the agent and used to build cards.</span></div>
      <div className="scroll pad">
        <div {...getRootProps()} className={'dropzone' + (isDragActive ? ' active' : '') + (isUploading ? ' uploading' : '')}>
          <input {...getInputProps()} />
          {isUploading
            ? <Loader2 className="spin" size={30} color="var(--gold)" style={{ marginBottom: 12 }} />
            : <UploadCloud size={30} color="var(--gold)" style={{ marginBottom: 12 }} />}
          <div style={{ fontWeight: 600, fontSize: 15 }}>
            {isUploading ? 'Uploading and indexing files' : isDragActive ? 'Drop to index' : 'Drag files here, or click to browse'}
          </div>
          <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 11, color: 'var(--dim)', marginTop: 6 }}>
            {isUploading ? 'This may take a moment for large files' : 'PDF - DOCX - PPTX - XLSX - CSV'}
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', margin: '22px 0 12px' }}>
          <span className="eyebrow">{docCount} chunks indexed</span>
          {docCount > 0 && <button className="btn btn-ghost" onClick={clear} disabled={isUploading}><Trash2 size={14} /> Clear vault</button>}
        </div>

        {logs.map(log => (
          <div key={log.id} className="file-row">
            {log.status === 'uploading'
              ? <Loader2 className="spin" size={16} color="var(--gold)" />
              : log.status === 'err'
                ? <AlertCircle size={16} color="var(--weak)" />
                : <FileCheck2 size={16} color={log.status === 'skip' ? 'var(--muted)' : 'var(--strong)'} />}
            <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{log.name}</span>
            <span style={{
              fontFamily: "'JetBrains Mono',monospace",
              fontSize: 11,
              color: log.status === 'err' ? 'var(--weak)' : log.status === 'uploading' ? 'var(--gold)' : 'var(--muted)',
              whiteSpace: 'nowrap',
            }}>{log.detail}</span>
          </div>
        ))}

        {logs.length === 0 && docCount === 0 && (
          <div className="card-panel" style={{ color: 'var(--muted)', fontSize: 14 }}>
            Nothing indexed yet. Upload a lecture PDF or your notes to get started, then head to Study to turn them into flashcards.
          </div>
        )}
      </div>
    </div>
  )
}
