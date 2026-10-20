import { useState } from 'react'
import { api } from '../lib/api'
import type { AgentStep, ChatResponse, ConversationOut } from '../types'

export interface DisplayMessage {
  role: 'user' | 'assistant'
  content: string
  aiGenerated?: boolean
  evidence?: string[]
  followUps?: string[]
  trace?: AgentStep[]
  chartPoints?: ChatResponse['chart_points']
  actions?: ChatResponse['actions']
}

export function useCopilotChat(orgId: string | undefined) {
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [messages, setMessages] = useState<DisplayMessage[]>([])
  const [llmAvailable, setLlmAvailable] = useState<boolean | null>(null)
  const [isSending, setIsSending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function send(message: string) {
    if (!message.trim() || !orgId || isSending) return
    setError(null)
    setMessages((prev) => [...prev, { role: 'user', content: message }])
    setIsSending(true)
    try {
      const res = await api.post<ChatResponse>(`/copilot/chat?organization_id=${orgId}`, {
        message,
        conversation_id: conversationId,
      })
      setConversationId(res.data.conversation_id)
      setLlmAvailable(res.data.llm_available)
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: res.data.message,
          aiGenerated: res.data.ai_generated,
          evidence: res.data.evidence,
          followUps: res.data.suggested_follow_ups,
          trace: res.data.agent_trace,
          chartPoints: res.data.chart_points,
          actions: res.data.actions,
        },
      ])
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setIsSending(false)
    }
  }

  function loadConversation(conversation: ConversationOut) {
    setConversationId(conversation.id)
    setMessages(conversation.messages.map((m) => ({ role: m.role, content: m.content, trace: m.agent_trace })))
  }

  function startNew() {
    setConversationId(null)
    setMessages([])
    setError(null)
  }

  return { conversationId, messages, llmAvailable, isSending, error, send, loadConversation, startNew }
}
