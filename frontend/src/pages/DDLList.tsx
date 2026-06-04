import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ddlApi, DDLMeta } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'
import ConfirmDialog from '../components/ConfirmDialog'
import DDLUploadModal from './DDLUploadModal'

export default function DDLList() {
  const [ddls, setDdls] = useState<DDLMeta[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showUpload, setShowUpload] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null)
  const navigate = useNavigate()

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await ddlApi.list()
      setDdls(data)
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
      await ddlApi.delete(deleteTarget)
      setDeleteTarget(null)
      load()
    } catch (e: any) {
      setError(e.message)
    }
  }

  const formatDate = (s: string) => new Date(s).toLocaleString('zh-CN')

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1>DDL 管理</h1>
        <button className="btn-primary" onClick={() => setShowUpload(true)}>+ 添加 DDL</button>
      </div>

      {error && <div style={{ color: 'var(--danger)', marginBottom: 16 }}>{error}</div>}

      {loading ? <LoadingSpinner text="加载中..." /> : ddls.length === 0 ? (
        <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
          <p style={{ fontSize: 16, marginBottom: 8 }}>暂无 DDL</p>
          <p style={{ fontSize: 14 }}>点击「添加 DDL」按钮上传你的第一个数据库 Schema</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: 12 }}>
          {ddls.map(ddl => (
            <div
              key={ddl.name}
              style={{
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border)',
                borderRadius: 8,
                padding: '16px 20px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                cursor: 'pointer',
                transition: 'border-color 0.2s',
              }}
              onClick={() => navigate(`/ddls/${encodeURIComponent(ddl.name)}`)}
              onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--accent)'}
              onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
            >
              <div>
                <div style={{ fontWeight: 600, fontSize: 16, marginBottom: 4 }}>{ddl.name}</div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center', fontSize: 13, color: 'var(--text-secondary)' }}>
                  <span>{ddl.table_count} 张表</span>
                  <span>·</span>
                  <span>{formatDate(ddl.created_at)}</span>
                  {ddl.tags.map(tag => (
                    <span key={tag} style={{
                      background: 'var(--bg-tertiary)', padding: '2px 8px', borderRadius: 4,
                      fontSize: 12, color: 'var(--accent)',
                    }}>{tag}</span>
                  ))}
                </div>
              </div>
              <button
                className="btn-danger"
                onClick={e => { e.stopPropagation(); setDeleteTarget(ddl.name) }}
                style={{ fontSize: 13, padding: '4px 12px' }}
              >
                删除
              </button>
            </div>
          ))}
        </div>
      )}

      <DDLUploadModal open={showUpload} onClose={() => setShowUpload(false)} onCreated={load} />
      <ConfirmDialog
        open={!!deleteTarget}
        title="确认删除"
        message={`确定要删除 DDL「${deleteTarget}」吗？此操作不可撤销。`}
        confirmLabel="删除"
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  )
}
