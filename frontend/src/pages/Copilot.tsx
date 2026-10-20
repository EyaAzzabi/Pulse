import { useQuery } from '@tanstack/react-query'
import { Bot, Mic, MicOff, Plus, Send, User, Volume2, VolumeX } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { useAuth } from '../contexts/AuthContext'
import { useCopilotChat } from '../hooks/useCopilotChat'
import { useVoice } from '../hooks/useVoice'
import { api } from '../lib/api'
import { formatDateTime } from '../lib/format'
import type { ConversationOut } from '../types'

const STARTER_PROMPTS = [
  'What is my biggest financial risk?',
  'Explain my cash runway.',
  'How can I avoid a cash shortage?',
  'Prepare reminders for my overdue invoices.',
]

export function Copilot() {
  const { currentOrg } = useAuth()
  const orgId = currentOrg?.organization_id
  const chat = useCopilotChat(orgId)
  const voice = useVoice()
  const [input, setInput] = useState('')
  const listRef = useRef<HTMLDivElement>(null)

  const historyQuery = useQuery({
    queryKey: ['copilot-conversations', orgId],
    queryFn: async () => (await api.get<ConversationOut[]>(`/copilot/conversations?organization_id=${orgId}`)).data,
    enabled: !!orgId,
  })

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' })
  }, [chat.messages, chat.isSending])

  function send(message: string) {
    setInput('')
    chat.send(message)
  }

  function handleMic() {
    if (voice.isListening) {
      voice.stopListening()
    } else {
      voice.startListening((transcript) => send(transcript))
    }
  }

  return (
    <div className="flex h-screen">
      <aside className="hidden w-64 shrink-0 flex-col border-r border-slate-200 bg-white p-4 md:flex">
        <Button variant="secondary" size="sm" onClick={chat.startNew} className="mb-4 w-full justify-start">
          <Plus className="h-4 w-4" /> New conversation
        </Button>
        <p className="mb-2 px-1 text-[11px] font-medium uppercase tracking-wider text-slate">History</p>
        <div className="flex-1 space-y-1 overflow-y-auto scrollbar-thin">
          {(historyQuery.data ?? []).map((c) => (
            <button
              key={c.id}
              onClick={() => chat.loadConversation(c)}
              className={`block w-full truncate rounded-lg px-2.5 py-2 text-left text-xs ${
                chat.conversationId === c.id ? 'bg-brand/10 text-brand' : 'text-slate hover:bg-slate-50 hover:text-ink'
              }`}
            >
              <span className="block truncate font-medium">{c.title}</span>
              <span className="block text-[10px] text-slate">{formatDateTime(c.created_at)}</span>
            </button>
          ))}
          {historyQuery.data?.length === 0 && (
            <p className="px-2 text-xs text-slate">No past conversations yet.</p>
          )}
        </div>
      </aside>

      <div className="mx-auto flex max-w-3xl flex-1 flex-col p-8">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-ink">AI Copilot</h1>
            <p className="text-sm text-slate">Grounded in your real financial data. Nothing is invented.</p>
          </div>
          {chat.llmAvailable !== null && (
            <Badge tone={chat.llmAvailable ? 'info' : 'neutral'}>
              {chat.llmAvailable ? 'LLM phrasing enabled' : 'Offline deterministic mode'}
            </Badge>
          )}
        </div>

        <div ref={listRef} className="flex-1 space-y-4 overflow-y-auto scrollbar-thin pb-4">
          {chat.messages.length === 0 && (
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              {STARTER_PROMPTS.map((p) => (
                <button
                  key={p}
                  onClick={() => send(p)}
                  className="rounded-xl border border-slate-200 bg-white p-3 text-left text-sm text-slate hover:border-brand/30 hover:text-ink"
                >
                  {p}
                </button>
              ))}
            </div>
          )}

          {chat.messages.map((m, i) => (
            <div key={i} className={`flex gap-3 ${m.role === 'user' ? 'justify-end' : ''}`}>
              {m.role === 'assistant' && (
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand/15">
                  <Bot className="h-4 w-4 text-brand" />
                </div>
              )}
              <div className={`max-w-[80%] ${m.role === 'user' ? 'order-first' : ''}`}>
                <Card className={m.role === 'user' ? 'bg-brand/5' : undefined}>
                  <div className="px-4 py-3">
                    <p className="whitespace-pre-line text-sm text-ink">{m.content}</p>
                    <div className="mt-2 flex items-center gap-2">
                      {m.aiGenerated !== undefined && (
                        <p className="text-[11px] text-slate">
                          {m.aiGenerated ? 'Phrased by LLM, grounded in computed data' : 'Deterministic answer (no LLM)'}
                        </p>
                      )}
                      {m.role === 'assistant' && voice.synthSupported && (
                        <button
                          onClick={() => (voice.isSpeaking ? voice.stopSpeaking() : voice.speak(m.content))}
                          className="ml-auto flex items-center gap-1 text-[11px] text-slate hover:text-brand"
                          title="Listen"
                        >
                          {voice.isSpeaking ? <VolumeX className="h-3 w-3" /> : <Volume2 className="h-3 w-3" />}
                          Listen
                        </button>
                      )}
                    </div>
                  </div>
                </Card>
                {m.followUps && m.followUps.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {m.followUps.map((f) => (
                      <button
                        key={f}
                        onClick={() => send(f)}
                        className="rounded-full border border-slate-200 px-3 py-1 text-xs text-slate hover:border-brand/30 hover:text-ink"
                      >
                        {f}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              {m.role === 'user' && (
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-100">
                  <User className="h-4 w-4 text-ink" />
                </div>
              )}
            </div>
          ))}
          {chat.isSending && <p className="text-sm text-slate">PULSE is analyzing your data…</p>}
          {chat.error && <p className="text-sm text-risk">{chat.error}</p>}
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault()
            send(input)
          }}
          className="flex gap-2 border-t border-slate-200 pt-4"
        >
          {voice.recognitionSupported && (
            <Button
              type="button"
              variant={voice.isListening ? 'danger' : 'secondary'}
              onClick={handleMic}
              title={voice.isListening ? 'Stop listening' : 'Ask by voice'}
            >
              {voice.isListening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
            </Button>
          )}
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={voice.isListening ? 'Listening…' : 'Ask about your cash flow, risks, or a scenario…'}
            className="flex-1 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-ink outline-none focus:border-brand/50"
          />
          <Button type="submit" disabled={chat.isSending}>
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </div>
  )
}
