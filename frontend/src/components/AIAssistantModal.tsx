'use client';

import React, { useState } from 'react';
import { X, Sparkles, Send, ShieldCheck, Database, ArrowRight } from 'lucide-react';

interface AIAssistantModalProps {
  onClose: () => void;
}

export default function AIAssistantModal({ onClose }: AIAssistantModalProps) {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<Array<{ sender: 'user' | 'ai'; text: string; evidence?: any[] }>>([
    {
      sender: 'ai',
      text: 'Hello. I am your Revenue Operations Analytical Assistant. Every number and insight I provide is strictly grounded in your active database records, ML uplift models, and financial policies. No hallucinations.',
      evidence: [
        { metric: 'Grounding Mode', value: 'Active PostgreSQL Metrics' },
        { metric: 'Authority', value: 'Read-only Advisory (Policies control execution)' },
      ],
    },
  ]);
  const [loading, setLoading] = useState(false);

  const suggestedQuestions = [
    'Why did the system choose DO NOTHING?',
    'Which interventions are wasting margin?',
    'How much incremental net revenue has been recovered?',
    'Which failure reason has the highest recoverability?',
  ];

  const handleSend = async (questionText?: string) => {
    const textToSend = questionText || query;
    if (!textToSend.trim()) return;

    setMessages((prev) => [...prev, { sender: 'user', text: textToSend }]);
    setQuery('');
    setLoading(true);

    try {
      const res = await fetch('/api/assistant/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: textToSend }),
      });
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        {
          sender: 'ai',
          text: data.response || 'No response data received.',
          evidence: data.evidence || [],
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'ai',
          text: 'Unable to reach backend operations API. Ensure backend service is running on port 8000.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        backdropFilter: 'blur(4px)',
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px',
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: '680px',
          maxWidth: '100%',
          height: '620px',
          backgroundColor: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: '10px',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: 'var(--shadow-lg)',
          overflow: 'hidden',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div
          style={{
            padding: '16px 20px',
            borderBottom: '1px solid var(--color-border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            backgroundColor: 'var(--color-surface-2)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                width: '28px',
                height: '28px',
                borderRadius: '6px',
                backgroundColor: 'var(--color-positive-bg)',
                border: '1px solid var(--color-positive-border)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Sparkles size={16} color="var(--color-positive)" />
            </div>
            <div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                AI Revenue Analytics & Investigation
              </div>
              <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Database size={11} color="var(--color-positive)" />
                <span>Grounded in active ledger & model predictions</span>
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              padding: '6px',
              borderRadius: '4px',
              color: 'var(--color-text-secondary)',
              cursor: 'pointer',
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Chat Stream */}
        <div style={{ flex: 1, padding: '20px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {messages.map((m, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: m.sender === 'user' ? 'flex-end' : 'flex-start',
              }}
            >
              <div
                style={{
                  maxWidth: '85%',
                  padding: '12px 16px',
                  borderRadius: '8px',
                  fontSize: '13px',
                  lineHeight: 1.6,
                  backgroundColor: m.sender === 'user' ? 'var(--color-surface-2)' : 'var(--color-bg)',
                  border: `1px solid ${m.sender === 'user' ? 'var(--color-border)' : 'var(--color-border-subtle)'}`,
                  color: 'var(--color-text-primary)',
                }}
              >
                {m.text}

                {/* Evidence Metrics Table */}
                {m.evidence && m.evidence.length > 0 && (
                  <div
                    style={{
                      marginTop: '12px',
                      padding: '10px',
                      borderRadius: '6px',
                      backgroundColor: 'var(--color-surface)',
                      border: '1px solid var(--color-border)',
                      fontSize: '11px',
                    }}
                  >
                    <div style={{ fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '6px' }}>
                      Verified Grounded Evidence
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      {m.evidence.map((ev, eIdx) => (
                        <div key={eIdx} style={{ display: 'flex', justifyContent: 'space-between' }}>
                          <span style={{ color: 'var(--color-text-secondary)' }}>{ev.metric}</span>
                          <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-positive)', fontWeight: 600 }}>
                            {ev.value}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-text-secondary)', fontSize: '12px' }}>
              <Sparkles size={14} color="var(--color-positive)" />
              <span>Querying live ledger & uplift estimators...</span>
            </div>
          )}
        </div>

        {/* Suggested Queries */}
        <div style={{ padding: '8px 20px', display: 'flex', gap: '6px', overflowX: 'auto', borderTop: '1px solid var(--color-border-subtle)' }}>
          {suggestedQuestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(q)}
              style={{
                whiteSpace: 'nowrap',
                fontSize: '11px',
                padding: '4px 10px',
                borderRadius: '12px',
                backgroundColor: 'var(--color-surface-2)',
                border: '1px solid var(--color-border)',
                color: 'var(--color-text-secondary)',
                cursor: 'pointer',
              }}
            >
              {q}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div style={{ padding: '14px 20px', borderTop: '1px solid var(--color-border)', display: 'flex', gap: '10px' }}>
          <input
            type="text"
            placeholder="Ask about margin waste, DO NOTHING rationale, or uplift..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            style={{ flex: 1 }}
          />
          <button
            onClick={() => handleSend()}
            className="btn btn-primary"
            style={{ padding: '8px 16px' }}
            disabled={loading}
          >
            <Send size={15} />
          </button>
        </div>
      </div>
    </div>
  );
}
