import { useState } from 'react'
import { ddlApi } from '../api/client'

interface Props {
  open: boolean
  onClose: () => void
  onCreated: () => void
}

export default function DDLUploadModal({ open, onClose, onCreated }: Props) {
  const [name, setName] = useState('')
  const [text, setText] = useState('')
  const [tags, setTags] = useState('')
  const [force, setForce] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (!open) return null

  const handleSubmit = async () => {
    setError('')
    if (!name.trim()) { setError('请输入名称'); return }
    if (!text.trim()) { setError('请输入 DDL 内容'); return }
    setLoading(true)
    try {
      const tagList = tags.split(',').map(t => t.trim()).filter(Boolean)
      await ddlApi.create({ name: name.trim(), text: text.trim(), tags: tagList, force })
      onCreated()
      onClose()
      setName('')
      setText('')
      setTags('')
      setForce(false)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
    }} onClick={onClose}>
      <div style={{
        background: 'var(--bg-secondary)', borderRadius: 12, padding: 24, minWidth: 480,
        border: '1px solid var(--border)', maxHeight: '80vh', overflow: 'auto',
      }} onClick={e => e.stopPropagation()}>
        <h2 style={{ marginBottom: 20 }}>添加 DDL</h2>

        {error && <div style={{ color: 'var(--danger)', marginBottom: 12, fontSize: 14 }}>{error}</div>}

        <div style={{ marginBottom: 12 }}>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 13, color: 'var(--text-secondary)' }}>名称</label>
          <input value={name} onChange={e => setName(e.target.value)} placeholder="例如：电商系统" />
        </div>

        <div style={{ marginBottom: 12 }}>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 13, color: 'var(--text-secondary)' }}>DDL 内容</label>
          <textarea
            value={text}
            onChange={e => setText(e.target.value)}
            placeholder="CREATE TABLE users ( ... );"
            rows={10}
            style={{ fontFamily: 'monospace', resize: 'vertical' }}
          />
        </div>

        <div style={{ marginBottom: 12 }}>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 13, color: 'var(--text-secondary)' }}>标签（逗号分隔）</label>
          <input value={tags} onChange={e => setTags(e.target.value)} placeholder="MySQL, 生产" />
        </div>

        <div style={{ marginBottom: 20 }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
            <input type="checkbox" checked={force} onChange={e => setForce(e.target.checked)} style={{ width: 'auto' }} />
            <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>覆盖已存在的 DDL</span>
          </label>
        </div>

        <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
          <button className="btn-secondary" onClick={onClose}>取消</button>
          <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
            {loading ? '提交中...' : '添加'}
          </button>
        </div>
      </div>
    </div>
  )
}
