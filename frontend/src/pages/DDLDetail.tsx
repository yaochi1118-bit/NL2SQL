import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ddlApi, DDLDetail as DDLDetailType } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'
import SyntaxHighlighter from '../components/SyntaxHighlighter'

export default function DDLDetail() {
  const { name } = useParams<{ name: string }>()
  const navigate = useNavigate()
  const [data, setData] = useState<DDLDetailType | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!name) return
    setLoading(true)
    ddlApi.get(decodeURIComponent(name))
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [name])

  if (loading) return <LoadingSpinner text="加载中..." />
  if (error) return <div style={{ color: 'var(--danger)' }}>{error}</div>
  if (!data) return null

  return (
    <div>
      <button className="btn-secondary" onClick={() => navigate('/ddls')} style={{ marginBottom: 16 }}>
        ← 返回列表
      </button>

      <div style={{
        background: 'var(--bg-secondary)', borderRadius: 8, padding: 20,
        border: '1px solid var(--border)', marginBottom: 20,
      }}>
        <h1 style={{ marginBottom: 8 }}>{data.meta.name}</h1>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', fontSize: 14, color: 'var(--text-secondary)' }}>
          <span>{data.meta.table_count} 张表</span>
          <span>·</span>
          <span>{new Date(data.meta.created_at).toLocaleString('zh-CN')}</span>
          {data.meta.tags.map(tag => (
            <span key={tag} style={{
              background: 'var(--bg-tertiary)', padding: '2px 8px', borderRadius: 4,
              fontSize: 12, color: 'var(--accent)',
            }}>{tag}</span>
          ))}
        </div>
      </div>

      <h3 style={{ marginBottom: 12 }}>DDL 内容</h3>
      <SyntaxHighlighter code={data.content} />
    </div>
  )
}
