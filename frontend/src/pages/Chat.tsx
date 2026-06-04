import { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { chatApi, ddlApi, Conversation, DDLMeta } from '../api/client'
import SyntaxHighlighter from '../components/SyntaxHighlighter'
import LoadingSpinner from '../components/LoadingSpinner'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  sql?: string
}

export default function Chat() {
  const { convId } = useParams<{ convId: string }>()
  const navigate = useNavigate()
  const [conv, setConv] = useState<Conversation | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [ddlList, setDdlList] = useState<DDLMeta[]>([])
  const [selectedDDL, setSelectedDDL] = useState('')
  const [targetDB, setTargetDB] = useState('PostgreSQL')
  const [creating, setCreating] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  useEffect(() => { scrollToBottom() }, [messages])

  // Load DDL list for new conversations
  useEffect(() => {
    ddlApi.list().then(setDdlList)
  }, [])

  // Load existing conversation
  useEffect(() => {
    if (!convId) return
    chatApi.get(convId).then(c => {
      setConv(c)
      setSelectedDDL(c.ddl_name)
      setTargetDB(c.target_db)
      const msgs: ChatMessage[] = []
      for (const m of c.messages || []) {
        if (m.role === 'user') {
          msgs.push({ role: 'user', content: m.content })
        } else if (m.role === 'assistant') {
          const sql = extractSQL(m.content)
          msgs.push({ role: 'assistant', content: m.content, sql })
        }
      }
      setMessages(msgs)
    })
  }, [convId])

  const extractSQL = (text: string): string | undefined => {
    const match = text.match(/```sql\s*([\s\S]*?)\s*```/)
    return match ? match[1].trim() : undefined
  }

  const handleCreate = async () => {
    if (!selectedDDL) return
    setCreating(true)
    try {
      const c = await chatApi.create({ ddl_name: selectedDDL, target_db: targetDB })
      setConv(c)
      setMessages([])
      navigate(`/chat/${c.id}`, { replace: true })
    } catch (e: any) {
      alert(e.message)
    } finally {
      setCreating(false)
    }
  }

  const handleSend = async () => {
    const q = input.trim()
    if (!q || !conv) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: q }])
    setSending(true)
    try {
      const result = await chatApi.ask(conv.id, q)
      const sql = result.valid ? result.sql : undefined
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: result.explanation || result.raw_response,
        sql,
      }])
    } catch (e: any) {
      setMessages(prev => [...prev, { role: 'assistant', content: `错误: ${e.message}` }])
    } finally {
      setSending(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // New conversation selector
  if (!conv) {
    return (
      <div>
        <h1 style={{ marginBottom: 24 }}>新对话</h1>
        <div style={{
          background: 'var(--bg-secondary)', borderRadius: 8, padding: 24,
          border: '1px solid var(--border)', maxWidth: 480,
        }}>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 4, fontSize: 13, color: 'var(--text-secondary)' }}>选择 DDL</label>
            <select value={selectedDDL} onChange={e => setSelectedDDL(e.target.value)}>
              <option value="">-- 请选择 --</option>
              {ddlList.map(d => <option key={d.name} value={d.name}>{d.name}</option>)}
            </select>
          </div>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 4, fontSize: 13, color: 'var(--text-secondary)' }}>目标数据库</label>
            <input value={targetDB} onChange={e => setTargetDB(e.target.value)} placeholder="PostgreSQL" />
          </div>
          <button className="btn-primary" onClick={handleCreate} disabled={creating || !selectedDDL}>
            {creating ? '创建中...' : '开始对话'}
          </button>
        </div>
      </div>
    )
  }

  // Chat interface
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 48px)' }}>
      <div style={{ marginBottom: 16 }}>
        <span style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
          对话: {conv.ddl_name} → {conv.target_db}
        </span>
      </div>

      <div style={{
        flex: 1, overflow: 'auto', marginBottom: 16,
        display: 'flex', flexDirection: 'column', gap: 12,
        padding: '0 4px',
      }}>
        {messages.map((msg, i) => (
          <div key={i} style={{
            maxWidth: '80%',
            alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
          }}>
            <div style={{
              background: msg.role === 'user' ? 'var(--accent)' : 'var(--bg-secondary)',
              color: msg.role === 'user' ? 'var(--bg-primary)' : 'var(--text-primary)',
              borderRadius: 12,
              borderBottomRightRadius: msg.role === 'user' ? 4 : 12,
              borderBottomLeftRadius: msg.role === 'assistant' ? 4 : 12,
              padding: '8px 14px',
              fontSize: 14,
              lineHeight: 1.5,
            }}>
              {msg.content}
            </div>
            {msg.sql && (
              <div style={{ marginTop: 8, width: '100%' }}>
                <SyntaxHighlighter code={msg.sql} />
              </div>
            )}
          </div>
        ))}
        {sending && <LoadingSpinner text="思考中..." />}
        <div ref={messagesEndRef} />
      </div>

      <div style={{ display: 'flex', gap: 8 }}>
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入问题... (Enter 发送, Shift+Enter 换行)"
          rows={2}
          style={{
            flex: 1, resize: 'none', fontFamily: 'inherit',
            background: 'var(--bg-secondary)', border: '1px solid var(--border)',
            borderRadius: 8, padding: '10px 14px', color: 'var(--text-primary)',
            fontSize: 14,
          }}
        />
        <button
          className="btn-primary"
          onClick={handleSend}
          disabled={sending || !input.trim()}
          style={{ alignSelf: 'flex-end', height: 40 }}
        >
          发送
        </button>
      </div>
    </div>
  )
}
