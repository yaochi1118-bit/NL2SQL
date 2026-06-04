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
      <h1 style={{ marginBottom: 24 }}>设置</h1>

      <div style={{
        background: 'var(--bg-secondary)', borderRadius: 8, padding: 24,
        border: '1px solid var(--border)', maxWidth: 480,
      }}>
        {error && <div style={{ color: 'var(--danger)', marginBottom: 12, fontSize: 14 }}>{error}</div>}
        {success && <div style={{ color: 'var(--success)', marginBottom: 12, fontSize: 14 }}>{success}</div>}

        {exists && config && (
          <div style={{
            background: 'var(--bg-tertiary)', borderRadius: 6, padding: 12, marginBottom: 20,
            fontSize: 13, color: 'var(--text-secondary)',
          }}>
            <div>当前配置: {config.provider} / {config.model}</div>
            <div>API Key: {config.api_key}</div>
          </div>
        )}

        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 13, color: 'var(--text-secondary)' }}>
            Base URL
          </label>
          <input value={baseUrl} onChange={e => setBaseUrl(e.target.value)} placeholder="https://api.openai.com/v1" />
        </div>

        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 13, color: 'var(--text-secondary)' }}>
            API Key {exists && '(留空则不修改)'}
          </label>
          <input
            type="password"
            value={apiKey}
            onChange={e => setApiKey(e.target.value)}
            placeholder={exists ? '输入新 Key 以修改' : 'sk-...'}
          />
        </div>

        <div style={{ marginBottom: 24 }}>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 13, color: 'var(--text-secondary)' }}>
            Model
          </label>
          <input value={model} onChange={e => setModel(e.target.value)} placeholder="gpt-4o" />
        </div>

        <button className="btn-primary" onClick={handleSave} disabled={saving}>
          {saving ? '保存中...' : '保存'}
        </button>
      </div>
    </div>
  )
}
