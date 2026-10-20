import type { ReactNode } from 'react'
import { cn } from '../lib/cn'

function inline(text: string): ReactNode[] {
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
    part.startsWith('**') && part.endsWith('**') ? (
      <strong key={i} className="font-semibold text-ink">
        {part.slice(2, -2)}
      </strong>
    ) : (
      part
    ),
  )
}

/** Renders the small markdown subset the copilot uses: paragraphs, bullet and
 * numbered lists, and **bold**. Builds React elements, never raw HTML. */
export function RichText({ text, className }: { text: string; className?: string }) {
  const blocks: ReactNode[] = []
  let list: { ordered: boolean; items: string[] } | null = null

  const flush = () => {
    if (!list) return
    const Tag = list.ordered ? 'ol' : 'ul'
    blocks.push(
      <Tag key={blocks.length} className={cn('my-1.5 space-y-1 pl-5', list.ordered ? 'list-decimal' : 'list-disc')}>
        {list.items.map((it, i) => (
          <li key={i}>{inline(it)}</li>
        ))}
      </Tag>,
    )
    list = null
  }

  for (const raw of text.split('\n')) {
    const line = raw.trim()
    const bullet = line.match(/^[-*•]\s+(.*)$/)
    const numbered = line.match(/^\d+[.)]\s+(.*)$/)
    if (bullet || numbered) {
      const ordered = !!numbered
      if (!list || list.ordered !== ordered) {
        flush()
        list = { ordered, items: [] }
      }
      list.items.push((bullet ?? numbered)![1])
      continue
    }
    flush()
    if (line) {
      blocks.push(
        <p key={blocks.length} className="my-1">
          {inline(line.replace(/^#+\s*/, ''))}
        </p>,
      )
    }
  }
  flush()
  return <div className={cn('text-sm leading-relaxed text-ink', className)}>{blocks}</div>
}

export function plainText(text: string): string {
  return text.replace(/\*\*/g, '').replace(/^\s*([-*•]|\d+[.)])\s+/gm, '').replace(/^#+\s*/gm, '')
}
