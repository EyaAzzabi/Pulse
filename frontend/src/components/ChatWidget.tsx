import { Bot, Maximize2, Mic, MicOff, Send, Volume2, VolumeX, X } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useCopilotChat } from '../hooks/useCopilotChat'
import { useVoice } from '../hooks/useVoice'
import { ActionCards, AgentTrace } from './AgentTrace'
import { Logo } from './Logo'
import { RichText, plainText } from './RichText'

/** Floating assistant available beside every authenticated page. Keeps its own
 * short-lived conversation (separate from the full /copilot page's history),
 * so it's always one click away without leaving what you're doing. */
export function ChatWidget() {
  const { currentOrg } = useAuth()
  const orgId = currentOrg?.organization_id
  const chat = useCopilotChat(orgId)
  const voice = useVoice()
  const [open, setOpen] = useState(false)
  const [input, setInput] = useState('')
  const listRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' })
  }, [chat.messages, chat.isSending, open])

  function send(message: string) {
    setInput('')
    chat.send(message)
  }

  function handleMic() {
    if (voice.isListening) voice.stopListening()
    else voice.startListening((t) => send(t))
  }

  if (!orgId) return null

  return (
    <>
      {open && (
        <div className="fixed bottom-20 right-5 z-40 flex h-[460px] w-80 flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl sm:right-6">
          <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
            <div className="flex items-center gap-2">
              <Logo size={24} />
              <div>
                <p className="text-xs font-semibold text-ink">Ask PULSE</p>
                <p className="text-[10px] text-slate">Quick assistant, any page</p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <Link to="/copilot" title="Open full copilot" className="rounded p-1 text-slate hover:bg-slate-50 hover:text-ink">
                <Maximize2 className="h-3.5 w-3.5" />
              </Link>
              <button onClick={() => setOpen(false)} className="rounded p-1 text-slate hover:bg-slate-50 hover:text-ink">
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>

          <div ref={listRef} className="flex-1 space-y-3 overflow-y-auto scrollbar-thin p-3">
            {chat.messages.length === 0 && (
              <p className="px-1 text-xs text-slate">
                Ask a quick question about your cash flow, risks or a scenario. Answers are grounded in your real
                data.
              </p>
            )}
            {chat.messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[85%] rounded-xl px-3 py-2 text-xs ${
                    m.role === 'user' ? 'bg-brand text-white' : 'border border-slate-200 bg-slate-50 text-ink'
                  }`}
                >
                  {m.role === 'assistant' ? (
                    <RichText text={m.content} className="text-xs" />
                  ) : (
                    <p className="whitespace-pre-line">{m.content}</p>
                  )}
                  {m.actions && <ActionCards actions={m.actions} />}
                  {m.trace && <AgentTrace steps={m.trace} compact />}
                  {m.role === 'assistant' && voice.synthSupported && (
                    <button
                      onClick={() => (voice.isSpeaking ? voice.stopSpeaking() : voice.speak(plainText(m.content)))}
                      className="mt-1 flex items-center gap-1 text-[10px] text-slate hover:text-brand"
                    >
                      {voice.isSpeaking ? <VolumeX className="h-2.5 w-2.5" /> : <Volume2 className="h-2.5 w-2.5" />}
                      Listen
                    </button>
                  )}
                </div>
              </div>
            ))}
            {chat.isSending && <p className="text-xs text-slate">Thinking…</p>}
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault()
              send(input)
            }}
            className="flex gap-1.5 border-t border-slate-100 p-2.5"
          >
            {voice.recognitionSupported && (
              <button
                type="button"
                onClick={handleMic}
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${
                  voice.isListening ? 'bg-risk/15 text-risk' : 'bg-slate-50 text-slate hover:text-ink'
                }`}
              >
                {voice.isListening ? <MicOff className="h-3.5 w-3.5" /> : <Mic className="h-3.5 w-3.5" />}
              </button>
            )}
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything…"
              className="flex-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs text-ink outline-none focus:border-brand/50"
            />
            <button
              type="submit"
              disabled={chat.isSending}
              className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-brand text-white disabled:opacity-50"
            >
              <Send className="h-3.5 w-3.5" />
            </button>
          </form>
        </div>
      )}

      <button
        onClick={() => setOpen((v) => !v)}
        className="fixed bottom-5 right-5 z-40 flex h-12 w-12 items-center justify-center rounded-full bg-brand text-white shadow-lg transition-transform hover:scale-105 sm:right-6"
        title="Ask PULSE"
      >
        {open ? <X className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
      </button>
    </>
  )
}
