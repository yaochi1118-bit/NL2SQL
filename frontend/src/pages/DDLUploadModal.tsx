import { useState } from 'react'
import { ddlApi } from '../api/client'

interface Props {
  open: boolean
  onClose: () => void
  onCreated: () => void
  editData?: { name: string; text: string; tags: string }
}

export default function DDLUploadModal({ open, onClose, onCreated, editData }: Props) {
  const isEdit = !!editData
  const [name, setName] = useState(editData?.name ?? '')
  const [text, setText] = useState(editData?.text ?? '')
  const [tags, setTags] = useState(editData?.tags ?? '')
  const [force, setForce] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (!open) return null

  const handleSubmit = async () => {
    setError('')
    if (!editData?.name && !name.trim()) { setError('请输入名称'); return }
    if (!text.trim()) { setError('请输入 DDL 内容'); return }
    setLoading(true)
    try {
      const tagList = tags.split(',').map(t => t.trim()).filter(Boolean)
      if (isEdit && editData) {
        await ddlApi.update(editData.name, { text: text.trim(), tags: tagList })
      } else {
        await ddlApi.create({ name: name.trim(), text: text.trim(), tags: tagList, force })
      }
      onCreated()
      onClose()
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <h2 className="modal-title">{isEdit ? '编辑 DDL' : '添加 DDL'}</h2>

        {error && <div style={{ color: 'var(--danger)', marginBottom: 12, fontSize: 14 }}>{error}</div>}

        <div className="form-group">
          <label className="form-label">名称</label>
          <input
            className="form-input"
            defaultValue={editData?.name ?? ''}
            readOnly={isEdit}
            style={isEdit ? { opacity: 0.6, cursor: 'not-allowed' } : {}}
            placeholder="例如：电商系统"
            onChange={e => { if (!isEdit) setName(e.target.value) }}
          />
        </div>

        <div className="form-group">
          <label className="form-label">DDL 内容</label>
          <textarea
            className="form-textarea"
            value={text}
            onChange={e => setText(e.target.value)}
            placeholder="CREATE TABLE users ( ... );"
            rows={10}
          />
        </div>

        <div className="form-group">
          <label className="form-label">标签（逗号分隔）</label>
          <input className="form-input" value={tags} onChange={e => setTags(e.target.value)} placeholder="MySQL, 生产" />
        </div>

        {!isEdit && (
          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
              <input type="checkbox" checked={force} onChange={e => setForce(e.target.checked)} style={{ width: 'auto', accentColor: 'var(--accent-gold)' }} />
              <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>覆盖已存在的 DDL</span>
            </label>
          </div>
        )}

        <div className="modal-actions">
          <button className="btn btn-ghost" onClick={onClose}>取消</button>
          <button className="btn btn-primary" onClick={handleSubmit} disabled={loading}>
            {loading ? '提交中...' : (isEdit ? '保存' : '添加')}
          </button>
        </div>
      </div>
    </div>
  )
}
