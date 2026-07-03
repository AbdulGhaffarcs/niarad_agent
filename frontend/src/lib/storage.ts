export interface Message {
  role: 'user' | 'assistant'
  content: string
  mode?: string
  steps?: Array<{ tool: string; input: string; output: string }>
  timestamp: number
}

export interface Chat {
  id: string
  title: string
  messages: Message[]
  createdAt: number
  updatedAt: number
}

const CHATS_KEY = 'niarad_chats'
const VAULT_FILES_KEY = 'niarad_vault_files'
const STORAGE_VERSION = 1

function getStore(): Map<string, string> {
  if (typeof window === 'undefined') return new Map()
  try {
    const raw = localStorage.getItem(CHATS_KEY)
    if (!raw) return new Map()
    const parsed = JSON.parse(raw)
    if (parsed.version !== STORAGE_VERSION) return new Map()
    return new Map(Object.entries(parsed.data))
  } catch {
    return new Map()
  }
}

function setStore(store: Map<string, string>) {
  if (typeof window === 'undefined') return
  const obj = Object.fromEntries(store)
  localStorage.setItem(CHATS_KEY, JSON.stringify({ version: STORAGE_VERSION, data: obj }))
}

export function generateChatId(): string {
  return `chat_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`
}

export function generateChatTitle(firstMessage: string): string {
  const words = firstMessage.trim().split(/\s+/).slice(0, 6).join(' ')
  return words || 'New Chat'
}

export async function getAllChats(): Promise<Array<{ id: string; title: string; updatedAt: number }>> {
  const store = getStore()
  const chats: Array<{ id: string; title: string; updatedAt: number }> = []
  for (const [id, data] of store.entries()) {
    try {
      const chat = JSON.parse(data) as Chat
      chats.push({ id: chat.id, title: chat.title, updatedAt: chat.updatedAt })
    } catch {}
  }
  return chats.sort((a, b) => b.updatedAt - a.updatedAt)
}

export async function getChat(id: string): Promise<Chat | null> {
  const store = getStore()
  const data = store.get(id)
  if (!data) return null
  try {
    return JSON.parse(data) as Chat
  } catch {
    return null
  }
}

export async function saveChat(id: string, title: string, messages: Message[]): Promise<void> {
  const store = getStore()
  const existing = store.get(id)
  let createdAt = Date.now()
  if (existing) {
    try { createdAt = JSON.parse(existing).createdAt } catch {}
  }
  const chat: Chat = {
    id,
    title,
    messages,
    createdAt,
    updatedAt: Date.now(),
  }
  store.set(id, JSON.stringify(chat))
  setStore(store)
}

export async function deleteChat(id: string): Promise<void> {
  const store = getStore()
  store.delete(id)
  setStore(store)
}

export async function clearAllChats(): Promise<void> {
  if (typeof window === 'undefined') return
  localStorage.removeItem(CHATS_KEY)
}

// --- Vault files local mirror ---

export interface VaultFile {
  id: string
  name: string
  type: string
  size: number
  indexedAt: number
  skipped: boolean
  chunks?: number
}

function getVaultStore(): Map<string, VaultFile> {
  if (typeof window === 'undefined') return new Map()
  try {
    const raw = localStorage.getItem(VAULT_FILES_KEY)
    if (!raw) return new Map()
    return new Map(Object.entries(JSON.parse(raw)))
  } catch {
    return new Map()
  }
}

function setVaultStore(store: Map<string, VaultFile>) {
  if (typeof window === 'undefined') return
  localStorage.setItem(VAULT_FILES_KEY, JSON.stringify(Object.fromEntries(store)))
}

export function saveVaultFile(file: VaultFile): void {
  const store = getVaultStore()
  store.set(file.id, file)
  setVaultStore(store)
}

export function getVaultFiles(): VaultFile[] {
  const store = getVaultStore()
  return Array.from(store.values()).sort((a, b) => b.indexedAt - a.indexedAt)
}

export function removeVaultFile(id: string): void {
  const store = getVaultStore()
  store.delete(id)
  setVaultStore(store)
}

export function clearVaultFiles(): void {
  if (typeof window === 'undefined') return
  localStorage.removeItem(VAULT_FILES_KEY)
}