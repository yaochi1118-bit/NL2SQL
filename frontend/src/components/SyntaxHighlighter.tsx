import { useMemo, useState } from 'react'
import hljs from 'highlight.js/lib/core'
import sql from 'highlight.js/lib/languages/sql'
import 'highlight.js/styles/github-dark.css'

hljs.registerLanguage('sql', sql)

interface Props {
  code: string
}

export default function SyntaxHighlighter({ code }: Props) {
  const [copied, setCopied] = useState(false)
  const highlighted = useMemo(() => {
    const result = hljs.highlight(code, { language: 'sql' })
    return result.value
  }, [code])

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div style={{
      position: 'relative',
      background: '#1e1e2e',
      borderRadius: 8,
      overflow: 'hidden',
      border: '1px solid var(--border)',
    }}>
      <div style={{
        display: 'flex', justifyContent: 'flex-end', padding: '4px 8px',
        background: 'var(--bg-tertiary)', borderBottom: '1px solid var(--border)',
      }}>
        <button
          onClick={handleCopy}
          style={{
            background: 'transparent', color: copied ? 'var(--success)' : 'var(--text-muted)',
            padding: '2px 8px', fontSize: 12, border: '1px solid var(--border)',
            borderRadius: 4,
          }}
        >
          {copied ? '已复制' : '复制'}
        </button>
      </div>
      <pre style={{ padding: '12px 16px', overflow: 'auto', margin: 0, fontSize: 13, lineHeight: 1.6 }}>
        <code style={{ fontFamily: "'JetBrains Mono', 'Fira Code', monospace" }}
          dangerouslySetInnerHTML={{ __html: highlighted }} />
      </pre>
    </div>
  )
}
