// src/lib/api.ts — typed client for the NIARAD backend.

export const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export type Step = { tool: string; input: string; output: string }
export type Intent = { category: string; reason: string; via: string }
export type ChatResponse = { response: string; mode: string; steps: Step[]; intent?: Intent }
export type ChatMessage = { role: 'user' | 'assistant'; content: string }

export type Card = {
  id: number; front: string; back: string; topic: string; source: string
  ease_factor: number; interval: number; repetitions: number; lapses: number
  due_date: string
}
export type TopicReport = {
  topic: string; cards: number; due: number; reviews: number
  avg_grade: number | null; lapse_rate: number; mastery: number; weak: boolean
}
export type Stats = { total_cards: number; due_now: number; total_reviews: number; topics: TopicReport[] }
export type VaultStatus = { has_docs: boolean; doc_count: number }
export type GenFile = { name: string; url: string }

async function j<T>(p: Promise<Response>): Promise<T> {
  const r = await p
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || r.statusText)
  return r.json()
}
const post = (path: string, body: unknown) =>
  fetch(API + path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })

export const api = {
  chat: (message: string, history: ChatMessage[] = []) =>
    j<ChatResponse>(post('/chat', { message, history })),

  vaultStatus: () => j<VaultStatus>(fetch(API + '/vault/status')),
  clearVault: () => j(fetch(API + '/vault/clear', { method: 'DELETE' })),
  upload: (file: File) => {
    const form = new FormData(); form.append('file', file)
    return j<{ success: boolean; chunks?: number; skipped?: boolean }>(
      fetch(API + '/vault/upload', { method: 'POST', body: form }))
  },

  files: () => j<{ files: GenFile[] }>(fetch(API + '/files/list')),

  // spaced-repetition loop
  generate: (topic: string, count: number, text?: string) =>
    j<{ ok: boolean; generated?: number; added?: number; error?: string; sources?: string[] }>(
      post('/cards/generate', { topic, count, text })),
  due: (limit = 20, topic?: string) =>
    j<{ cards: Card[] }>(fetch(API + `/cards/due?limit=${limit}${topic ? `&topic=${encodeURIComponent(topic)}` : ''}`)),
  quizWeak: (count = 12) => j<{ cards: Card[]; weak_topics: string[] }>(post('/cards/quiz_weak', { count })),
  review: (card_id: number, grade: number) =>
    j<{ interval_days: number; next_due: string; lapsed: boolean }>(post('/cards/review', { card_id, grade })),
  stats: () => j<Stats>(fetch(API + `/cards/stats`)),
}

export const masteryColor = (m: number) =>
  m >= 75 ? 'var(--strong)' : m >= 45 ? 'var(--learning)' : 'var(--weak)'
