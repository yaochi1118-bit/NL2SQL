import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { chatApi, Conversation } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'
import ConfirmDialog from '../components/ConfirmDialog'

export default function History() {
  const [convs, setConvs] = useState<Conversation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null)
  const navigate = useNavigate()

  const load = async () => {
    setLoading(true)
    try {
      setConvs(await chatApi.list())
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleDelete = async () => {
    if (!deleteTarget) return
    try {
      await chatApi.delete(deleteTarget)
      setDeleteTarget(null)
      load()
    } catch (e: any) {
      setError(e.message)
    }
  }

  const formatDate = (s: string) => new Date(s).toLocaleString('zh-CN')

  return (
    <div>
      {/* Page Header */}
      <header className="page-header">
        <div className="page-header-left">
          <div className="page-header-sup">Conversation Log</div>
          <h1>历史 <span className="teal" style={{color:'var(--accent-teal)'}}>对话</span></h1>
          <div className="page-header-desc">
            共 <strong style={{color:'var(--text-secondary)'}}>{convs.length}</strong> 次对话记录
          </div>
        </div>
      </header>

      {error && <div style={{ color: 'var(--danger)', marginBottom: 16, fontSize: 14 }}>{error}</div>}

      {loading ? (
        <LoadingSpinner text="加载中..." />
      ) : convs.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🕐</div>
          <div className="empty-title">暂无历史对话</div>
          <div className="empty-desc">开始一个新的对话，记录会显示在这里</div>
          <button className="btn btn-primary" onClick={() => navigate('/chat')}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M12 5v14M5 12h14"/></svg>
            新对话
          </button>
        </div>
      ) : (
        <div className="card-list">
          {convs.map((conv, idx) => (
            <div
              key={conv.id}
              className="card-list-item"
              style={{ animationDelay: `${0.05 + idx * 0.07}s` }}
              onClick={() => navigate(`/chat/${conv.id}`)}
              onMouseMove={e => {
                const rect = e.currentTarget.getBoundingClientRect()
                const x = ((e.clientX - rect.left) / rect.width) * 100
                const y = ((e.clientY - rect.top) / rect.height) * 100
                e.currentTarget.style.setProperty('--mouse-x', x + '%')
                e.currentTarget.style.setProperty('--mouse-y', y + '%')
              }}
            >
              <div className="card-left">
                <div className="card-name">
                  {conv.ddl_name || '自动匹配 DDL'}
                  <span style={{ fontWeight: 300, color: 'var(--text-muted)', fontFamily: "'Outfit', sans-serif", fontSize: 13 }}>
                    {' '}→ {conv.target_db}
                  </span>
                </div>
                <div className="card-meta">
                  <span className="card-meta-item">💬 {conv.message_count} 条消息</span>
                  <span className="card-meta-item">◷ {formatDate(conv.created_at)}</span>
                </div>
              </div>
              <div className="card-actions">
                <button
                  className="card-action-btn edit"
                  onClick={e => { e.stopPropagation(); navigate(`/chat/${conv.id}`) }}
                >
                  继续
                </button>
                <button
                  className="card-action-btn delete"
                  onClick={e => { e.stopPropagation(); setDeleteTarget(conv.id) }}
                >
                  删除
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <ConfirmDialog
        open={!!deleteTarget}
        title="确认删除"
        message="确定要删除此对话吗？此操作不可撤销。"
        confirmLabel="删除"
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  )
}
