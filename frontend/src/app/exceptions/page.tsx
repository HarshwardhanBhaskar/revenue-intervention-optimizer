'use client';

import React from 'react';
import Link from 'next/link';
import { AlertOctagon, ShieldAlert, AlertTriangle, CheckCircle2, ArrowRight } from 'lucide-react';

export default function ExceptionsPage() {
  const exceptionsList = [
    {
      id: 'exc_01',
      title: 'Customer Communication Opt-Out Enforced',
      type: 'Policy Block',
      details: 'Customer cust_4821a opted out of SMS/Email. Automated Payment Link intervention blocked safely.',
      amount: 4500,
      timestamp: '12 mins ago',
      actionTaken: 'Blocked (DO NOTHING applied)',
    },
    {
      id: 'exc_02',
      title: 'Active Dispute Flagged by Merchant Ledger',
      type: 'Chargeback Circuit Breaker',
      details: 'Active chargeback case open for order_908a2. All recovery actions blocked to prevent dispute escalation.',
      amount: 18200,
      timestamp: '48 mins ago',
      actionTaken: 'Blocked (Dispute protection)',
    },
    {
      id: 'exc_03',
      title: 'High-Value VIP Threshold Exceeded',
      type: 'Operator Escalation',
      details: 'Transaction of ₹28,500 exceeds the automated ₹10,000 threshold. Escalated to Approval Queue.',
      amount: 28500,
      timestamp: '2 hours ago',
      actionTaken: 'Sent to Approval Queue',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '1000px' }}>
      {/* Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="badge badge-negative">Safety & Circuit Breakers</span>
          <h1 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--color-text-primary)' }}>
            Exceptions & Guardrail Blocks
          </h1>
        </div>
        <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
          Real-time record of policy firewall blocks, opt-out enforcement, and risk circuit-breakers.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {exceptionsList.map((exc, idx) => (
          <div
            key={idx}
            className="card"
            style={{
              padding: '18px 20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              borderLeft: '4px solid var(--color-warning)',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="badge badge-warning">{exc.type}</span>
                <span style={{ fontWeight: 600, fontSize: '14px', color: 'var(--color-text-primary)' }}>{exc.title}</span>
              </div>
              <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginTop: '6px', maxWidth: '640px' }}>
                {exc.details}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', marginTop: '4px', fontFamily: 'var(--font-mono)' }}>
                {exc.timestamp} • Amount: ₹{exc.amount.toLocaleString('en-IN')}
              </div>
            </div>

            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Engine Resolution</div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-positive)', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>
                {exc.actionTaken}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
