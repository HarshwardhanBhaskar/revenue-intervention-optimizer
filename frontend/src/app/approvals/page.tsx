'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { ShieldCheck, CheckCircle2, XCircle, AlertTriangle, Eye, RefreshCw } from 'lucide-react';

export default function ApprovalsPage() {
  const [pending, setPending] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  const fetchPending = () => {
    setLoading(true);
    fetch('/api/actions/pending')
      .then((res) => res.json())
      .then((data) => {
        setPending(data.pending_actions || []);
        setLoading(false);
      })
      .catch((err) => {
        console.log('Error loading pending', err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchPending();
  }, []);

  const handleApprove = async (oppId: string) => {
    try {
      const res = await fetch(`/api/actions/${oppId}/approve`, { method: 'POST' });
      if (res.ok) {
        setMessage(`Opportunity #${oppId.substring(0, 8)} approved and recovery action dispatched!`);
        fetchPending();
      }
    } catch (err) {
      console.log('Error approving', err);
    }
  };

  const handleReject = async (oppId: string) => {
    try {
      const res = await fetch(`/api/actions/${oppId}/reject`, { method: 'POST' });
      if (res.ok) {
        setMessage(`Opportunity #${oppId.substring(0, 8)} rejected. Recovery halted.`);
        fetchPending();
      }
    } catch (err) {
      console.log('Error rejecting', err);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '1100px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="badge badge-warning">Operator Sign-off Required</span>
            <h1 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--color-text-primary)' }}>
              Human Approval Queue
            </h1>
          </div>
          <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
            High-value transactions exceeding policy threshold (&gt;₹10,000) or flagged for operator review.
          </p>
        </div>

        <button onClick={fetchPending} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '12px' }}>
          <RefreshCw size={13} />
          <span>Refresh</span>
        </button>
      </div>

      {message && (
        <div style={{ padding: '12px 16px', borderRadius: '6px', backgroundColor: 'var(--color-positive-bg)', border: '1px solid var(--color-positive-border)', color: 'var(--color-positive)', fontSize: '13px' }}>
          {message}
        </div>
      )}

      {/* Pending Items List */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {pending.length === 0 ? (
          <div style={{ padding: '40px 20px', textAlign: 'center', color: 'var(--color-text-secondary)' }}>
            <CheckCircle2 size={32} color="var(--color-positive)" style={{ margin: '0 auto 10px' }} />
            <div style={{ fontWeight: 600, fontSize: '15px', color: 'var(--color-text-primary)' }}>Approval Queue Clear</div>
            <div style={{ fontSize: '12px', color: 'var(--color-text-muted)', marginTop: '4px' }}>
              All high-value transactions have been reviewed and resolved.
            </div>
          </div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Customer</th>
                <th>Transaction Amount</th>
                <th>Failure Reason</th>
                <th>AI Recommendation</th>
                <th>Baseline → Rec</th>
                <th>Incremental Net Gain</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {pending.map((item, idx) => (
                <tr key={idx}>
                  <td>
                    <div style={{ fontWeight: 600 }}>{item.customer?.external_id}</div>
                    <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', textTransform: 'capitalize' }}>
                      {item.customer?.segment} tier
                    </div>
                  </td>
                  <td className="font-mono" style={{ fontWeight: 700, fontSize: '14px', color: 'var(--color-text-primary)' }}>
                    ₹{item.amount_rupees.toLocaleString('en-IN')}
                  </td>
                  <td>
                    <div style={{ textTransform: 'capitalize' }}>{item.payment?.failure_reason?.replace('_', ' ')}</div>
                    <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>{item.payment?.method}</div>
                  </td>
                  <td>
                    <span className={`badge ${item.recommended_action === 'discount' ? 'badge-warning' : 'badge-positive'}`}>
                      {item.recommended_action?.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="font-mono">
                    {Math.round((item.baseline_probability || 0.3) * 100)}% → <span style={{ color: 'var(--color-positive)', fontWeight: 600 }}>{Math.round((item.recommended_probability || 0.7) * 100)}%</span>
                  </td>
                  <td className="font-mono" style={{ color: 'var(--color-positive)', fontWeight: 600 }}>
                    +₹{Math.round((item.expected_incremental_value_paise || 0) / 100).toLocaleString('en-IN')}
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <Link href={`/opportunities/${item.opportunity_id}`} className="btn btn-secondary" style={{ padding: '4px 8px', fontSize: '11px' }}>
                        <Eye size={12} />
                      </Link>
                      <button onClick={() => handleReject(item.opportunity_id)} className="btn btn-danger" style={{ padding: '4px 10px', fontSize: '11px' }}>
                        Reject
                      </button>
                      <button onClick={() => handleApprove(item.opportunity_id)} className="btn btn-primary" style={{ padding: '4px 12px', fontSize: '11px' }}>
                        Approve
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
