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

  const [editData, setEditData] = useState<{ name: string; text: string; tags: string } | null>(null)
  const [loadingEdit, setLoadingEdit] = useState(false)

  const handleEditClick = async (ddlName: string) => {
    setLoadingEdit(true)
    try {
      const detail = await ddlApi.get(ddlName)
      setEditData({
        name: detail.meta.name,
        text: detail.content,
        tags: detail.meta.tags.join(', '),
      })
    } catch {
      setEditData(null)
    } finally {
      setLoadingEdit(false)
    }
  }

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
      {/* Page Header */}
      <header className="page-header">
        <div className="page-header-left">
          <div className="page-header-sup">Schema Registry</div>
          <h1>DDL <span className="gold" style={{color:'var(--accent-gold)'}}>管理</span></h1>
          <div className="page-header-desc">
            共 <strong style={{color:'var(--text-secondary)'}}>{ddls.length}</strong> 个数据库 Schema
          </div>
        </div>
        <div className="page-header-actions">
          <button className="btn btn-primary" onClick={() => setShowUpload(true)}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M12 5v14M5 12h14"/></svg>
            新建 Schema
          </button>
        </div>
      </header>

      {error && <div style={{ color: 'var(--danger)', marginBottom: 16, fontSize: 14 }}>{error}</div>}

      {loading ? (
        <LoadingSpinner text="加载中..." />
      ) : ddls.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">⊞</div>
          <div className="empty-title">暂无 DDL</div>
          <div className="empty-desc">点击「新建 Schema」上传你的第一个数据库 Schema 定义</div>
          <button className="btn btn-primary" onClick={() => setShowUpload(true)}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M12 5v14M5 12h14"/></svg>
            新建 Schema
          </button>
        </div>
      ) : (
        <div className="card-list">
          {ddls.map((ddl, idx) => (
            <div
              key={ddl.name}
              className="card-list-item"
              style={{ animationDelay: `${0.05 + idx * 0.07}s` }}
              onClick={() => navigate(`/ddls/${encodeURIComponent(ddl.name)}`)}
              onMouseMove={e => {
                const rect = e.currentTarget.getBoundingClientRect()
                const x = ((e.clientX - rect.left) / rect.width) * 100
                const y = ((e.clientY - rect.top) / rect.height) * 100
                e.currentTarget.style.setProperty('--mouse-x', x + '%')
                e.currentTarget.style.setProperty('--mouse-y', y + '%')
              }}
            >
              <div className="card-left">
                <div className="card-name">{ddl.name}</div>
                <div className="card-meta">
                  <span className="card-meta-item">⊞ {ddl.table_count} 张表</span>
                  <span className="card-meta-item">◷ {formatDate(ddl.created_at)}</span>
                  <div className="card-tags">
                    {ddl.tags.map(tag => (
                      <span key={tag} className={`tag ${tag.match(/mysql|postgres|sqlite/i) ? 'gold' : ''}`}>{tag}</span>
                    ))}
                  </div>
                </div>
              </div>
              <div className="card-actions">
                <button
                  className="card-action-btn edit"
                  onClick={e => { e.stopPropagation(); handleEditClick(ddl.name) }}
                >
                  编辑
                </button>
                <button
                  className="card-action-btn delete"
                  onClick={e => { e.stopPropagation(); setDeleteTarget(ddl.name) }}
                >
                  删除
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <DDLUploadModal open={showUpload} onClose={() => setShowUpload(false)} onCreated={load} />
      {editData && (
        <DDLUploadModal
          open={true}
          onClose={() => setEditData(null)}
          onCreated={() => { setEditData(null); load() }}
          editData={editData}
        />
      )}
      {loadingEdit && <LoadingSpinner text="加载中..." />}
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
