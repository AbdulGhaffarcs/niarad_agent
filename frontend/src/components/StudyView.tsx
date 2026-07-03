'use client'
import { useState, useEffect, useCallback } from 'react'
import { Sparkles, Loader2, Play, RefreshCw, AlertTriangle, Check } from 'lucide-react'
import { api, type Card, type Stats } from '@/lib/api'
import Flashcard from './Flashcard'
import MasteryRing from './MasteryRing'

// SM-2 "next interval" preview text, mirrors the backend grades.
const GRADES = [
  { g: 1, label: 'Again', when: '<1d', cls: 'again' },
  { g: 3, label: 'Hard',  when: '1d',  cls: 'hard' },
  { g: 4, label: 'Good',  when: '6d+', cls: 'good' },
  { g: 5, label: 'Easy',  when: 'long', cls: 'easy' },
]

export default function StudyView({ vaultReady }: { vaultReady: boolean }) {
  const [stats, setStats] = useState<Stats | null>(null)
  const [topic, setTopic] = useState('')
  const [count, setCount] = useState(8)
  const [genMsg, setGenMsg] = useState<string | null>(null)
  const [generating, setGenerating] = useState(false)

  const [queue, setQueue] = useState<Card[]>([])
  const [pos, setPos] = useState(0)
  const [sessionDone, setSessionDone] = useState(false)

  const loadStats = useCallback(() => { api.stats().then(setStats).catch(() => {}) }, [])
  useEffect(() => { loadStats() }, [loadStats])

  const generate = async () => {
    if (!topic.trim()) return
    setGenerating(true); setGenMsg(null)
    try {
      const r = await api.generate(topic.trim(), count)
      setGenMsg(r.ok ? `Added ${r.added} cards on “${topic.trim()}”.` : (r.error || 'Generation failed.'))
      if (r.ok) { setTopic(''); loadStats() }
    } catch (e) { setGenMsg(String(e)) }
    setGenerating(false)
  }

  const startSession = async (weakOnly: boolean) => {
    const { cards } = weakOnly ? await api.quizWeak(12) : await api.due(20)
    setQueue(cards); setPos(0); setSessionDone(cards.length === 0)
  }

  const grade = async (g: number) => {
    const card = queue[pos]
    await api.review(card.id, g)
    if (pos + 1 < queue.length) setPos(pos + 1)
    else { setSessionDone(true); setQueue([]); loadStats() }
  }

  const inSession = queue.length > 0 && !sessionDone
  const weak = stats?.topics.filter(t => t.weak) ?? []

  // ── review session ──
  if (inSession) {
    const card = queue[pos]
    return (
      <div className="main">
        <div className="topbar"><h2>Review</h2><span className="sub">Grade honestly — that’s what tunes your schedule.</span></div>
        <div className="scroll pad">
          <div className="deck">
            <Flashcard card={card} index={pos} total={queue.length} />
            <div className="grade-row">
              {GRADES.map(b => (
                <button key={b.g} className={'grade-btn ' + b.cls} onClick={() => grade(b.g)}>
                  <span className="g-label">{b.label}</span>
                  <span className="g-when">{b.when}</span>
                </button>
              ))}
            </div>
            <button className="btn btn-ghost" onClick={() => { setQueue([]); setSessionDone(false) }}>End session</button>
          </div>
        </div>
      </div>
    )
  }

  // ── dashboard ──
  return (
    <div className="main">
      <div className="topbar"><h2>Study</h2><span className="sub">Your decks, your weak spots, and what’s due now.</span></div>
      <div className="scroll pad">

        <div className="stat-strip">
          <div className="stat-box"><div className="num" style={{ color: 'var(--gold)' }}>{stats?.due_now ?? 0}</div><div className="lbl">Due now</div></div>
          <div className="stat-box"><div className="num">{stats?.total_cards ?? 0}</div><div className="lbl">Total cards</div></div>
          <div className="stat-box"><div className="num">{stats?.total_reviews ?? 0}</div><div className="lbl">Reviews done</div></div>
          <div className="stat-box"><div className="num" style={{ color: weak.length ? 'var(--weak)' : 'var(--strong)' }}>{weak.length}</div><div className="lbl">Weak topics</div></div>
        </div>

        <div style={{ display: 'flex', gap: 10, marginBottom: 24, flexWrap: 'wrap' }}>
          <button className="btn btn-accent" disabled={!stats?.due_now} onClick={() => startSession(false)}>
            <Play size={15} /> Review due ({stats?.due_now ?? 0})
          </button>
          <button className="btn" disabled={!weak.length} onClick={() => startSession(true)}>
            <AlertTriangle size={15} /> Drill weak spots
          </button>
          <button className="btn btn-ghost" onClick={loadStats}><RefreshCw size={14} /> Refresh</button>
        </div>

        {/* generate */}
        <div className="card-panel" style={{ marginBottom: 24 }}>
          <div className="eyebrow" style={{ marginBottom: 12 }}>Make cards from your vault</div>
          {!vaultReady && <div className="io" style={{ color: 'var(--learning)', marginBottom: 10, fontSize: 13 }}>Upload documents in the Vault tab first — cards are built from what you’ve indexed.</div>}
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            <input className="input" style={{ flex: 1, minWidth: 200 }} value={topic}
              placeholder="Topic, e.g. “photosynthesis” or “dynamic programming”"
              onChange={e => setTopic(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && generate()} />
            <select className="input" style={{ width: 90 }} value={count} onChange={e => setCount(+e.target.value)}>
              {[5, 8, 12, 20].map(n => <option key={n} value={n}>{n}</option>)}
            </select>
            <button className="btn btn-accent" onClick={generate} disabled={generating || !topic.trim() || !vaultReady}>
              {generating ? <Loader2 size={15} className="spin" /> : <Sparkles size={15} />} Generate
            </button>
          </div>
          {genMsg && <div className="io" style={{ marginTop: 10, color: 'var(--strong)', display: 'flex', gap: 6, alignItems: 'center' }}><Check size={14} /> {genMsg}</div>}
        </div>

        {/* topics */}
        <div className="eyebrow" style={{ marginBottom: 12 }}>Mastery by topic</div>
        {(!stats || stats.topics.length === 0) ? (
          <div className="card-panel" style={{ color: 'var(--muted)', fontSize: 14 }}>
            No cards yet. Generate some above, then review them — mastery appears here as you grade.
          </div>
        ) : (
          <div className="topic-grid">
            {stats.topics.map(t => (
              <div key={t.topic} className="topic-tile">
                <MasteryRing value={t.mastery} />
                <div className="meta">
                  <div className="name">{t.topic}</div>
                  <div className="stat">{t.cards} cards · {t.due} due</div>
                  <div className="stat">{t.reviews} reviews{t.avg_grade != null ? ` · avg ${t.avg_grade}` : ''}</div>
                  {t.weak && <span className="weak-pill">needs work</span>}
                </div>
              </div>
            ))}
          </div>
        )}

        {sessionDone && queue.length === 0 && (
          <div className="card-panel" style={{ marginTop: 20, display: 'flex', gap: 8, alignItems: 'center', color: 'var(--strong)' }}>
            <Check size={16} /> Session complete — nothing left in the queue. Come back when more cards are due.
          </div>
        )}
      </div>
    </div>
  )
}
