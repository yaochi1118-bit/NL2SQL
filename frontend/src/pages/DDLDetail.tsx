import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ddlApi, DDLDetail as DDLDetailType } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'
import SyntaxHighlighter from '../components/SyntaxHighlighter'
import DDLUploadModal from './DDLUploadModal'

export default function DDLDetail() {
  const { name } = useParams<{ name: string }>()
  const navigate = useNavigate()
  const [data, setData] = useState<DDLDetailType | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showEdit, setShowEdit] = useState(false)

  const load = () => {
    if (!name) return
    setLoading(true)
    ddlApi.get(decodeURIComponent(name))
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [name])

  const handleUpdated = () => {
    setShowEdit(false)
    load()
  }

  if (loading) return <LoadingSpinner text="加载中..." />
  if (error) return <div style={{ color: 'var(--danger)', marginBottom: 16, fontSize: 14 }}>{error}</div>
  if (!data) return null

  return (
    <div>
      {/* Top bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <button className="btn btn-ghost btn-sm" onClick={() => navigate('/ddls')}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
          返回列表
        </button>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn btn-ghost btn-sm" onClick={() => setShowEdit(true)}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20 14.66V20a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h5.34"/><polygon points="18 2 22 6 12 16 8 16 8 12 18 2"/></svg>
            编辑
          </button>
        </div>
      </div>

      {/* Detail card */}
      <div className="detail-card" style={{ animation: 'fade-slide-up 0.5s ease-out' }}>
        <div className="detail-card-title">
          <span style={{color:'var(--accent-gold)'}}>{data.meta.name}</span>
          {data.meta.tags.slice(0, 2).map(tag => (
            <span key={tag} className={`tag ${tag.match(/mysql|postgres|sqlite/i) ? 'gold' : ''}`}
              style={{fontSize:10}}>{tag}</span>
          ))}
        </div>
        <div className="detail-meta">
          <span>⊞ {data.meta.table_count} 张表</span>
          <span>◷ {new Date(data.meta.created_at).toLocaleString('zh-CN')}</span>
          <div className="card-tags">
            {data.meta.tags.map(tag => (
              <span key={tag} className={`tag ${tag.match(/mysql|postgres|sqlite/i) ? 'gold' : ''}`}>{tag}</span>
            ))}
          </div>
        </div>
      </div>

      {/* DDL Content */}
      <div className="section-title" style={{ animation: 'fade-slide-up 0.5s ease-out 0.1s both' }}>
        <span style={{color:'var(--accent-gold)'}}>DDL</span> 内容
        <span style={{fontWeight:300,fontSize:12,color:'var(--text-muted)',fontFamily:"'Outfit',sans-serif"}}>
          — 完整的数据库 Schema 定义
        </span>
      </div>
      <div style={{ animation: 'fade-slide-up 0.5s ease-out 0.15s both' }}>
        <SyntaxHighlighter code={data.content} />
      </div>

      {showEdit && (
        <DDLUploadModal
          open={true}
          onClose={() => setShowEdit(false)}
          onCreated={handleUpdated}
          editData={{
            name: data.meta.name,
            text: data.content,
            tags: data.meta.tags.join(', '),
          }}
        />
      )}
    </div>
  )
}
