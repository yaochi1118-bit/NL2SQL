interface Props {
  open: boolean
  title: string
  message: string
  confirmLabel?: string
  onConfirm: () => void
  onCancel: () => void
}

export default function ConfirmDialog({ open, title, message, confirmLabel = '确认', onConfirm, onCancel }: Props) {
  if (!open) return null
  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal" style={{ minWidth: 360 }} onClick={e => e.stopPropagation()}>
        <h3 className="modal-title">{title}</h3>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 20, fontSize: 14, lineHeight: 1.6 }}>{message}</p>
        <div className="modal-actions">
          <button className="btn btn-ghost" onClick={onCancel}>取消</button>
          <button className="btn btn-danger-ghost" onClick={onConfirm}>{confirmLabel}</button>
        </div>
      </div>
    </div>
  )
}
