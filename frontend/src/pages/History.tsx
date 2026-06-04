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
      <h1 style={{ marginBottom: 24 }}>历史对话</h1>

      {error && <div style={{ color: 'var(--danger)', marginBottom: 16 }}>{error}</div>}

      {loading ? <LoadingSpinner text="加载中..." /> : convs.length === 0 ? (
        <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
          <p style={{ fontSize: 16 }}>暂无历史对话</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: 12 }}>
          {convs.map(conv => (
            <div
              key={conv.id}
              style={{
                background: 'var(--bg-secondary)', border: '1px solid var(--border)',
                borderRadius: 8, padding: '16px 20px',
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                cursor: 'pointer', transition: 'border-color 0.2s',
              }}
              onClick={() => navigate(`/chat/${conv.id}`)}
              onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--accent)'}
              onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
            >
              <div>
                <div style={{ fontWeight: 600, fontSize: 15, marginBottom: 4 }}>
                  {conv.ddl_name}
                  <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}> → {conv.target_db}</span>
                </div>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                  {conv.message_count} 条消息 · {formatDate(conv.created_at)}
                </div>
              </div>
              <button
                className="btn-danger"
                onClick={e => { e.stopPropagation(); setDeleteTarget(conv.id) }}
                style={{ fontSize: 13, padding: '4px 12px' }}
              >
                删除
              </button>
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
