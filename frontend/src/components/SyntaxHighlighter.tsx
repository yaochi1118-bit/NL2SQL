import { useEffect, useMemo, useState } from 'react'
import hljs from 'highlight.js/lib/core'
import sql from 'highlight.js/lib/languages/sql'
import { useTheme } from '../theme/ThemeContext'

hljs.registerLanguage('sql', sql)

interface Props {
  code: string
}

export default function SyntaxHighlighter({ code }: Props) {
  const [copied, setCopied] = useState(false)
  const { theme } = useTheme()

  // Dynamic theme stylesheet for highlight.js
  useEffect(() => {
    let link = document.querySelector<HTMLLinkElement>('#hljs-theme')
    if (!link) {
      link = document.createElement('link')
      link.id = 'hljs-theme'
      link.rel = 'stylesheet'
      document.head.appendChild(link)
    }
    link.href = theme === 'light'
      ? 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.10.0/styles/github.min.css'
      : 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.10.0/styles/github-dark.min.css'
  }, [theme])
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
    <div className="code-block">
      <div className="code-block-header">
        <span className="code-block-header-lang">SQL</span>
        <button
          className="code-block-header-btn"
          onClick={handleCopy}
          style={{ color: copied ? 'var(--accent-teal)' : undefined, borderColor: copied ? 'rgba(45,212,191,0.3)' : undefined }}
        >
          {copied ? '已复制' : '复制'}
        </button>
      </div>
      <pre className="code-block-body" style={{ margin: 0 }}>
        <code style={{ fontFamily: "'JetBrains Mono', monospace" }}
          dangerouslySetInnerHTML={{ __html: highlighted }} />
      </pre>
    </div>
  )
}
