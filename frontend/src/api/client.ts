const BASE = '/api'

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export interface DDLMeta {
  name: string
  tags: string[]
  created_at: string
  table_count: number
}

export interface DDLDetail {
  name: string
  content: string
  meta: DDLMeta
}

export interface Conversation {
  id: string
  ddl_name: string
  target_db: string
  created_at: string
  updated_at: string
  message_count: number
  messages?: Message[]
}

export interface Message {
  role: string
  content: string
}

export interface AskResult {
  sql: string
  raw_response: string
  explanation: string
  valid: boolean
  messages: Message[]
}

export interface ConfigDisplay {
  provider: string
  base_url: string
  api_key: string
  model: string
}

// DDL APIs
export const ddlApi = {
  list: () => request<DDLMeta[]>('/ddls'),
  get: (name: string) => request<DDLDetail>(`/ddls/${encodeURIComponent(name)}`),
  create: (data: { name: string; text: string; tags?: string[]; force?: boolean }) =>
    request<{ status: string; name: string }>('/ddls', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  delete: (name: string) =>
    request<{ status: string; name: string }>(`/ddls/${encodeURIComponent(name)}`, {
      method: 'DELETE',
    }),
}

// Conversation APIs
export const chatApi = {
  create: (data: { ddl_name: string; target_db: string }) =>
    request<Conversation>('/conversations', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  ask: (convId: string, question: string) =>
    request<AskResult>(`/conversations/${encodeURIComponent(convId)}/ask`, {
      method: 'POST',
      body: JSON.stringify({ question }),
    }),
  list: () => request<Conversation[]>('/conversations'),
  get: (convId: string) => request<Conversation>(`/conversations/${encodeURIComponent(convId)}`),
  delete: (convId: string) =>
    request<{ status: string; id: string }>(`/conversations/${encodeURIComponent(convId)}`, {
      method: 'DELETE',
    }),
}

// Config APIs
export const configApi = {
  get: () => request<ConfigDisplay>('/config'),
  update: (key: string, value: string) =>
    request<{ status: string }>('/config', {
      method: 'PUT',
      body: JSON.stringify({ key, value }),
    }),
  init: (data: { base_url: string; api_key: string; model: string }) =>
    request<{ status: string }>('/config/init', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  status: () => request<{ exists: boolean }>('/config/status'),
}
