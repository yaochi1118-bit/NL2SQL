import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'

export default function Layout() {
  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Background decorations */}
      <div className="bg-grid" />
      <div className="glow-orb gold" />
      <div className="glow-orb teal" />
      <div className="accent-bar" />

      <Sidebar />
      <main style={{
        flex: 1,
        marginLeft: 'var(--sidebar-w)',
        padding: '40px 40px 80px',
        maxWidth: 1120,
        position: 'relative',
        zIndex: 1,
        minHeight: '100vh',
      }}>
        <Outlet />
      </main>
    </div>
  )
}
