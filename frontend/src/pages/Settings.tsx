import { useEffect, useState } from 'react'
import { configApi, ConfigDisplay } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Settings() {
  const [config, setConfig] = useState<ConfigDisplay | null>(null)
  const [exists, setExists] = useState(false)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Init form state
  const [baseUrl, setBaseUrl] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [model, setModel] = useState('gpt-4o')

  const load = async () => {
    setLoading(true)
    try {
      const status = await configApi.status()
      setExists(status.exists)
      if (status.exists) {
        const c = await configApi.get()
        setConfig(c)
        setBaseUrl(c.base_url)
        setModel(c.model)
      }
    } catch {
      // Config may not exist
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleSave = async () => {
    setError('')
    setSuccess('')
    setSaving(true)
    try {
      if (exists) {
        if (baseUrl !== config?.base_url) await configApi.update('base_url', baseUrl)
        if (apiKey) await configApi.update('api_key', apiKey)
        if (model !== config?.model) await configApi.update('model', model)
      } else {
        await configApi.init({ base_url: baseUrl, api_key: apiKey, model })
      }
      setSuccess('配置已保存')
      load()
    } catch (e: any) {
      setError(e.message)
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <LoadingSpinner text="加载中..." />

  return (
    <div>
      {/* Page Header */}
      <header className="page-header">
        <div className="page-header-left">
          <div className="page-header-sup">Configuration</div>
          <h1>系统 <span className="gold" style={{color:'var(--accent-gold)'}}>设置</span></h1>
          <div className="page-header-desc">管理 API 连接与模型参数</div>
        </div>
      </header>

      {error && <div style={{ color: 'var(--danger)', marginBottom: 16, fontSize: 14 }}>{error}</div>}

      {/* API Config Section */}
      <div className="settings-section" style={{ animation: 'fade-slide-up 0.5s ease-out' }}>
        <div className="settings-section-title">
          <span style={{color:'var(--accent-teal)'}}>◈</span> API 配置
        </div>
        <div className="settings-card">
          {exists && config && (
            <div className="settings-current">
              <div className="settings-current-row">
                <span className="settings-current-label">Provider</span>
                <span className="settings-current-value">{config.provider}</span>
              </div>
              <div className="settings-current-row">
                <span className="settings-current-label">Model</span>
                <span className="settings-current-value">{config.model}</span>
              </div>
              <div className="settings-current-row">
                <span className="settings-current-label">API Key</span>
                <span className="settings-current-value" style={{
                  color: 'var(--accent-gold)',
                  filter: 'blur(4px)',
                  cursor: 'pointer',
                  transition: 'filter 0.3s',
                }}
                  onMouseEnter={e => (e.target as HTMLElement).style.filter = 'blur(0)'}
                  onMouseLeave={e => (e.target as HTMLElement).style.filter = 'blur(4px)'}
                >
                  {config.api_key}
                </span>
              </div>
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Base URL</label>
            <input className="form-input" value={baseUrl} onChange={e => setBaseUrl(e.target.value)} placeholder="https://api.openai.com/v1" />
          </div>

          <div className="form-group">
            <label className="form-label">
              API Key {exists && <span style={{ color: 'var(--text-muted)', fontWeight: 300, fontSize: 11 }}>（留空则不修改）</span>}
            </label>
            <input
              className="form-input"
              type="password"
              value={apiKey}
              onChange={e => setApiKey(e.target.value)}
              placeholder={exists ? '输入新 Key 以修改' : 'sk-...'}
            />
          </div>

          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Model</label>
            <input className="form-input" value={model} onChange={e => setModel(e.target.value)} placeholder="gpt-4o, claude-3-opus, ..." />
          </div>

          <div className="settings-save-bar">
            <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
              {saving ? '保存中...' : '保存配置'}
            </button>
            {success && <span className="settings-success-msg">✓ {success}</span>}
          </div>
        </div>
      </div>

      {/* Conversation Settings Section */}
      <div className="settings-section" style={{ animation: 'fade-slide-up 0.5s ease-out 0.15s both' }}>
        <div className="settings-section-title">
          <span style={{color:'var(--accent-gold)'}}>◈</span> 对话设置
        </div>
        <div className="settings-card">
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <input type="checkbox" defaultChecked style={{ width: 16, height: 16, accentColor: 'var(--accent-gold)' }} />
              <span>启用自动 DDL 匹配</span>
            </label>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4, marginLeft: 24 }}>
              不指定 DDL 时自动在所有 Schema 中匹配最合适的
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
