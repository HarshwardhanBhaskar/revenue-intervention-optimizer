'use client';

import React, { useState } from 'react';
import { Bot, Sparkles, Send, Database, ShieldCheck, HelpCircle, ArrowRight } from 'lucide-react';

export default function AIAnalystPage() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<Array<{ sender: 'user' | 'ai'; text: string; evidence?: any[] }>>([
    {
      sender: 'ai',
      text: 'Welcome to the Grounded AI Revenue Analyst. I assist revenue operations teams in diagnosing recovery patterns, margin preservation, and counterfactual economics. Every observation is strictly cited from active PostgreSQL ledger records and trained T-Learner uplift estimators with zero hallucination.',
      evidence: [
        { metric: 'Authority Mode', value: 'Advisory Only (Deterministic policies control execution)' },
        { metric: 'Grounding Source', value: 'Live PostgreSQL Database + ML Registry' },
      ],
    },
  ]);
  const [loading, setLoading] = useState(false);

  const suggestedQuestions = [
    'Why did the system choose DO NOTHING on 58 transactions?',
    'Which interventions are diluting merchant margin?',
    'How much incremental net revenue has been recovered vs baseline?',
    'Which payment failure reason has the highest recoverability?',
    'What is the average recovery uplift on UPI vs Credit Cards?',
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
          text: data.response || 'Analysis complete.',
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
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '1000px', height: 'calc(100vh - 120px)' }}>
      {/* Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="badge badge-gold">BOUNDED INTELLIGENCE</span>
          <h1 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--color-text-primary)' }}>
            AI Revenue Analyst
          </h1>
        </div>
        <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
          Grounded conversational investigation over historical transactions, uplift predictions, and margin safety.
        </p>
      </div>

      {/* Main Chat Container */}
      <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 0, overflow: 'hidden' }}>
        {/* Messages Stream */}
        <div style={{ flex: 1, padding: '24px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
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
                  padding: '14px 18px',
                  borderRadius: '4px',
                  fontSize: '13px',
                  lineHeight: 1.6,
                  backgroundColor: m.sender === 'user' ? 'var(--color-surface-2)' : 'var(--color-surface)',
                  border: `1px solid ${m.sender === 'user' ? 'var(--color-border)' : 'var(--color-border-subtle)'}`,
                  boxShadow: m.sender === 'ai' ? 'var(--shadow-subtle)' : 'none',
                  color: 'var(--color-text-primary)',
                }}
              >
                {m.text}

                {/* Evidence Metrics Table */}
                {m.evidence && m.evidence.length > 0 && (
                  <div
                    style={{
                      marginTop: '12px',
                      padding: '10px 14px',
                      borderRadius: '4px',
                      backgroundColor: 'var(--color-surface-2)',
                      border: '1px solid var(--color-border)',
                      fontSize: '11px',
                    }}
                  >
                    <div style={{ fontWeight: 700, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '6px' }}>
                      Verified Grounded Evidence
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      {m.evidence.map((ev, eIdx) => (
                        <div key={eIdx} style={{ display: 'flex', justifyContent: 'space-between' }}>
                          <span style={{ color: 'var(--color-text-secondary)' }}>{ev.metric}</span>
                          <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-recovery)', fontWeight: 600 }}>
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
              <Sparkles size={14} color="var(--color-gold)" />
              <span>Querying ledger statistics and uplift estimators...</span>
            </div>
          )}
        </div>

        {/* Suggested Queries */}
        <div style={{ padding: '10px 20px', display: 'flex', gap: '8px', overflowX: 'auto', borderTop: '1px solid var(--color-border-subtle)', backgroundColor: 'var(--color-surface-2)' }}>
          {suggestedQuestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(q)}
              style={{
                whiteSpace: 'nowrap',
                fontSize: '11.5px',
                padding: '4px 10px',
                borderRadius: '12px',
                backgroundColor: 'var(--color-surface)',
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
        <div style={{ padding: '16px 20px', borderTop: '1px solid var(--color-border)', display: 'flex', gap: '10px', backgroundColor: 'var(--color-surface)' }}>
          <input
            type="text"
            placeholder="Ask about margin waste, DO NOTHING selection rationale, or recovery uplift..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            style={{ flex: 1 }}
          />
          <button
            onClick={() => handleSend()}
            className="btn btn-gold"
            style={{ padding: '8px 18px' }}
            disabled={loading}
          >
            <Send size={14} />
          </button>
        </div>
      </div>
    </div>
  );
}
