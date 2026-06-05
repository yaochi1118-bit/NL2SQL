export default function LoadingSpinner({ text = '加载中...' }: { text?: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: 24, color: 'var(--text-muted)' }}>
      <div style={{
        width: 20, height: 20, border: '2px solid var(--border-card)',
        borderTopColor: 'var(--accent-gold)', borderRadius: '50%',
        animation: 'spin 0.8s linear infinite',
      }} />
      <span style={{ fontSize: 13, fontWeight: 300 }}>{text}</span>
    </div>
  )
}
