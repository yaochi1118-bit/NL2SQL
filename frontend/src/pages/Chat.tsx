import { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { chatApi, ddlApi, Conversation, DDLMeta } from '../api/client'

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
    setCreating(true)
    try {
      const c = await chatApi.create({
        ...(selectedDDL ? { ddl_name: selectedDDL } : {}),
        target_db: targetDB,
      })
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
      <div style={{ animation: 'fade-slide-up 0.5s ease-out' }}>
        <div className="page-header" style={{ borderBottom: 'none', paddingBottom: 0, marginBottom: 32 }}>
          <div className="page-header-left">
            <div className="page-header-sup">New Session</div>
            <h1>新<span className="gold" style={{color:'var(--accent-gold)'}}>对话</span></h1>
            <div className="page-header-desc">选择一个 Schema 开始生成 SQL</div>
          </div>
        </div>

        <div className="new-conv-card" style={{
          background: 'var(--bg-card)', border: '1px solid var(--border-card)',
          borderRadius: 'var(--radius)', padding: 28, maxWidth: 460,
          animation: 'card-enter 0.5s ease-out',
        }}>
          <h2 style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, fontSize: '1.1rem', marginBottom: 20 }}>
            配置对话
          </h2>

          <div className="form-group">
            <label className="form-label">
              选择 DDL <span style={{ color: 'var(--text-muted)', fontWeight: 300 }}>（可选，不选则自动匹配）</span>
            </label>
            <select className="form-select" value={selectedDDL} onChange={e => setSelectedDDL(e.target.value)}>
              <option value="">-- 自动匹配 --</option>
              {ddlList.map(d => <option key={d.name} value={d.name}>{d.name}</option>)}
            </select>
          </div>

          <div className="form-group" style={{ marginBottom: 24 }}>
            <label className="form-label">目标数据库</label>
            <input className="form-input" value={targetDB} onChange={e => setTargetDB(e.target.value)} placeholder="PostgreSQL" />
          </div>

          <button className="btn btn-primary" onClick={handleCreate} disabled={creating}>
            {creating ? '创建中...' : '开始对话'}
          </button>
        </div>
      </div>
    )
  }

  // Chat interface
  return (
    <div className="chat-layout">
      {/* Chat Header */}
      <div className="chat-header-bar">
        <div className="chat-header-info">
          <span className="chat-header-dot"></span>
          <span className="chat-header-label">
            <strong style={{ color: 'var(--accent-gold)', fontWeight: 500 }}>
              {conv.ddl_name || '自动匹配 DDL'}
            </strong>
            <span style={{ color: 'var(--text-muted)', margin: '0 6px' }}>→</span>
            {conv.target_db}
          </span>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <button className="btn btn-ghost btn-sm" onClick={() => { setConv(null); setMessages([]); navigate('/chat', { replace: true }) }}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 5v14M5 12h14"/></svg>
            新对话
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`chat-msg ${msg.role}`}>
            <div className="chat-msg-bubble" style={msg.role === 'assistant' && msg.content.startsWith('错误') ? { borderColor: 'rgba(239,68,68,0.2)', color: 'var(--danger)' } : undefined}>
              {msg.content}
            </div>
            {msg.sql && (
              <div className="chat-msg-sql">
                <div className="sql-header">
                  <span>SQL</span>
                  <button className="code-block-header-btn" onClick={() => {
                    navigator.clipboard.writeText(msg.sql || '')
                  }}>复制</button>
                </div>
                <div className="sql-body">{msg.sql}</div>
              </div>
            )}
          </div>
        ))}
        {sending && (
          <div className="chat-msg assistant" style={{ opacity: 0.5 }}>
            <div className="chat-msg-bubble" style={{ padding: '12px 16px' }}>
              <div className="typing-dots">
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="chat-input-area">
        <div className="chat-input-wrap">
          <textarea
            className="chat-input"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入问题... 用自然语言描述你想要的查询"
            rows={1}
          />
          <div className="chat-input-hint">Enter 发送 · Shift+Enter 换行</div>
        </div>
        <button
          className="chat-send-btn"
          onClick={handleSend}
          disabled={sending || !input.trim()}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path d="M22 2 11 13M22 2l-7 20-4-9-9-4 20-7z"/>
          </svg>
        </button>
      </div>
    </div>
  )
}
