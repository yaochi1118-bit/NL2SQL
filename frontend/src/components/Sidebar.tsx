import { NavLink } from 'react-router-dom'

const links = [
  { to: '/ddls', label: 'DDL 管理' },
  { to: '/chat', label: '对话' },
  { to: '/history', label: '历史' },
  { to: '/settings', label: '设置' },
]

export default function Sidebar() {
  return (
    <aside style={{
      width: 'var(--sidebar-width)',
      background: 'var(--bg-secondary)',
      borderRight: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      padding: '16px 0',
    }}>
      <div style={{
        padding: '0 20px 16px',
        borderBottom: '1px solid var(--border)',
        marginBottom: 8,
        fontWeight: 700,
        fontSize: 18,
        color: 'var(--accent)',
      }}>
        DDL-to-SQL
      </div>
      <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
        {links.map(link => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.to === '/ddls'}
            style={({ isActive }) => ({
              padding: '10px 20px',
              color: isActive ? 'var(--accent)' : 'var(--text-secondary)',
              background: isActive ? 'var(--bg-tertiary)' : 'transparent',
              borderRight: isActive ? '2px solid var(--accent)' : '2px solid transparent',
              fontWeight: isActive ? 600 : 400,
              fontSize: 14,
            })}
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
      <div style={{ padding: '16px 20px', color: 'var(--text-muted)', fontSize: 12 }}>
        v0.1.0
      </div>
    </aside>
  )
}
