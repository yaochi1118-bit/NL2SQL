import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import DDLList from './pages/DDLList'
import DDLDetail from './pages/DDLDetail'
import Chat from './pages/Chat'
import History from './pages/History'
import Settings from './pages/Settings'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Navigate to="/ddls" replace />} />
          <Route path="/ddls" element={<DDLList />} />
          <Route path="/ddls/:name" element={<DDLDetail />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/chat/:convId" element={<Chat />} />
          <Route path="/history" element={<History />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/ddls" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
