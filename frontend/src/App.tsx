import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import ChatPage from './pages/ChatPage'
import SystemStatusPage from './pages/SystemStatusPage'
import RigDataPage from './pages/RigDataPage'
import ModelConfigPage from './pages/ModelConfigPage'
import RecentQueriesPage from './pages/RecentQueriesPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<ChatPage />} />
          <Route path="system-status" element={<SystemStatusPage />} />
          <Route path="rig-data" element={<RigDataPage />} />
          <Route path="model-config" element={<ModelConfigPage />} />
          <Route path="recent-queries" element={<RecentQueriesPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
