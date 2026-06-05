import { NavLink } from 'react-router-dom'
import { useTheme } from '../theme/ThemeContext'

const links = [
  { to: '/chat', label: '对话', icon: 'M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z', badge: 'new' },
  { to: '/ddls', label: 'Schema', icon: 'M3 3h7v7H3zm11 0h7v7h-7zm0 11h7v7h-7zM3 14h7v7H3z' },
  { to: '/history', label: '历史', icon: 'M12 2C6.486 2 2 6.486 2 12s4.486 10 10 10 10-4.486 10-10S17.514 2 12 2zm0 18c-4.411 0-8-3.589-8-8s3.589-8 8-8 8 3.589 8 8-3.589 8-8 8zm1-13h-2v6l5.25 3.15.75-1.23-4-2.37z' },
  { to: '/settings', label: '设置', icon: 'M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72 1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42' },
]

export default function Sidebar() {
  const { theme, toggle } = useTheme()
  return (
    <aside className="sidebar" style={{
      width: 'var(--sidebar-w)',
      minHeight: '100vh',
      background: 'var(--sidebar-bg)',
      borderRight: '1px solid var(--border-subtle)',
      display: 'flex',
      flexDirection: 'column',
      position: 'fixed',
      left: 0, top: 0, bottom: 0,
      zIndex: 10,
      backdropFilter: 'blur(12px)',
    }}>
      {/* Logo */}
      <div style={{
        padding: '32px 24px 28px',
        borderBottom: '1px solid var(--border-subtle)',
        position: 'relative',
      }}>
        <div style={{
          position: 'absolute',
          bottom: -1, left: 24,
          width: 40, height: 1,
          background: 'var(--accent-gold)',
        }} />
        <div style={{
          fontFamily: "'Syne', sans-serif",
          fontWeight: 800,
          fontSize: '1.3rem',
          letterSpacing: '-0.02em',
          display: 'flex',
          alignItems: 'center',
          gap: 10,
        }}>
          <div style={{
            width: 28, height: 28,
            border: '1.5px solid var(--accent-gold)',
            borderRadius: 6,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 13,
            color: 'var(--accent-gold)',
            fontFamily: "'JetBrains Mono', monospace",
            fontWeight: 600,
            flexShrink: 0,
          }}>D</div>
          <span><span style={{color:'var(--accent-gold)'}}>DDL</span><span style={{color:'var(--accent-teal)'}}>→SQL</span></span>
        </div>
        <div style={{
          fontSize: 10,
          textTransform: 'uppercase',
          letterSpacing: 4,
          color: 'var(--text-muted)',
          marginTop: 6,
          fontWeight: 300,
        }}>
          Schema Intelligence
        </div>
      </div>

      {/* Navigation */}
      <nav style={{
        flex: 1,
        padding: '16px 12px',
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
      }}>
        {links.map(link => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.to === '/chat'}
            style={{ textDecoration: 'none', display: 'block' }}
          >
            {({ isActive }: { isActive: boolean }) => (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                padding: '10px 14px',
                borderRadius: 'var(--radius-sm)',
                color: isActive ? 'var(--accent-gold)' : 'var(--text-muted)',
                background: isActive ? 'var(--accent-gold-subtle)' : 'transparent',
                fontSize: 14,
                fontWeight: isActive ? 500 : 400,
                transition: 'all 0.25s ease',
                position: 'relative',
                fontFamily: "'Outfit', sans-serif",
                cursor: 'pointer',
              }}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"
                  style={{ width: 18, height: 18, opacity: isActive ? 1 : 0.5, flexShrink: 0 }}
                >
                  <path d={link.icon} />
                </svg>
                {link.label}
                {link.badge && (
                  <span style={{
                    marginLeft: 'auto',
                    background: 'rgba(45, 212, 191, 0.1)',
                    color: 'var(--accent-teal)',
                    fontSize: 10,
                    padding: '2px 7px',
                    borderRadius: 100,
                    fontWeight: 500,
                    border: '1px solid rgba(45, 212, 191, 0.08)',
                  }}>{link.badge}</span>
                )}
                {isActive && (
                  <div style={{
                    position: 'absolute',
                    left: 0, top: '25%', bottom: '25%',
                    width: 2,
                    background: 'var(--accent-gold)',
                    borderRadius: 1,
                  }} />
                )}
              </div>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div style={{
        padding: '20px 24px',
        borderTop: '1px solid var(--border-subtle)',
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: 8,
        }}>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', letterSpacing: 1 }}>
            v0.2.0 · Nightly
          </div>
          <button
            onClick={toggle}
            title={theme === 'dark' ? '切换到明亮模式' : '切换到暗黑模式'}
            style={{
              background: 'transparent',
              border: '1px solid var(--border-subtle)',
              borderRadius: 6,
              width: 28, height: 28,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              color: 'var(--text-muted)',
              transition: 'all 0.25s ease',
              fontSize: 13,
              padding: 0,
              lineHeight: 1,
            }}
            onMouseEnter={e => {
              e.currentTarget.style.color = 'var(--accent-gold)'
              e.currentTarget.style.borderColor = 'rgba(212, 160, 71, 0.3)'
            }}
            onMouseLeave={e => {
              e.currentTarget.style.color = 'var(--text-muted)'
              e.currentTarget.style.borderColor = 'var(--border-subtle)'
            }}
          >
            {theme === 'dark' ? '☀' : '☾'}
          </button>
        </div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          fontSize: 12,
          color: 'var(--accent-teal)',
        }}>
          <span style={{
            width: 5, height: 5,
            borderRadius: '50%',
            background: 'var(--accent-teal)',
            animation: 'pulse-dot 2s ease-in-out infinite',
            display: 'inline-block',
          }} />
          系统就绪
        </div>
      </div>
    </aside>
  )
}
