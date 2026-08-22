'use client';

import React, { useEffect, useState } from 'react';
import { Sliders, ShieldCheck, CheckCircle2, AlertTriangle, Save } from 'lucide-react';

export default function PoliciesPage() {
  const [policy, setPolicy] = useState<any>({
    max_automated_amount_rupees: 10000,
    max_discount_percentage: 5.0,
    max_retry_attempts: 2,
    min_incremental_value_rupees: 100,
    human_approval_threshold_rupees: 10000,
    min_contact_interval_hours: 24,
    enforce_opt_out: true,
    block_disputed: true,
    block_fraud_signals: true,
  });

  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    fetch('/api/policies')
      .then((res) => res.json())
      .then((data) => {
        if (data.max_discount_percentage) setPolicy(data);
      })
      .catch((err) => console.log('Using default policy', err));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch('/api/policies', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          max_automated_amount_paise: policy.max_automated_amount_rupees * 100,
          max_discount_percentage: Number(policy.max_discount_percentage),
          max_retry_attempts: Number(policy.max_retry_attempts),
          min_incremental_value_paise: policy.min_incremental_value_rupees * 100,
          human_approval_threshold_paise: policy.human_approval_threshold_rupees * 100,
          min_contact_interval_hours: Number(policy.min_contact_interval_hours),
          enforce_opt_out: Boolean(policy.enforce_opt_out),
          block_disputed: Boolean(policy.block_disputed),
          block_fraud_signals: Boolean(policy.block_fraud_signals),
        }),
      });
      if (res.ok) {
        setSavedSuccess(true);
        setTimeout(() => setSavedSuccess(false), 3000);
      }
    } catch (err) {
      console.log('Error saving policy', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', maxWidth: '1000px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="badge badge-positive">Deterministic Safety</span>
            <h1 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--color-text-primary)' }}>
              Merchant Financial Policy Controls
            </h1>
          </div>
          <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
            Server-side deterministic financial rules. All policies are immutable and audited upon change.
          </p>
        </div>

        <button onClick={handleSave} className="btn btn-primary" style={{ padding: '8px 18px' }} disabled={saving}>
          <Save size={15} />
          <span>{saving ? 'Saving...' : 'Save & Audit Policy'}</span>
        </button>
      </div>

      {savedSuccess && (
        <div style={{ padding: '12px 16px', borderRadius: '6px', backgroundColor: 'var(--color-positive-bg)', border: '1px solid var(--color-positive-border)', color: 'var(--color-positive)', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CheckCircle2 size={16} />
          <span>Policy configuration successfully updated and recorded in the append-only audit trail.</span>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Financial Limits */}
        <div className="card">
          <div className="card-title" style={{ marginBottom: '16px' }}>Automated Thresholds & Limits</div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <label style={{ fontSize: '12px', fontWeight: 600 }}>Human Approval Threshold</label>
                <span className="font-mono" style={{ color: 'var(--color-positive)', fontWeight: 600 }}>₹{policy.human_approval_threshold_rupees?.toLocaleString('en-IN')}</span>
              </div>
              <input
                type="number"
                value={policy.human_approval_threshold_rupees || 10000}
                onChange={(e) => setPolicy({ ...policy, human_approval_threshold_rupees: Number(e.target.value) })}
                style={{ width: '100%' }}
              />
              <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', marginTop: '4px' }}>
                Transactions exceeding this amount require manual operator sign-off in the Approval Queue.
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <label style={{ fontSize: '12px', fontWeight: 600 }}>Maximum Discount Percentage Cap</label>
                <span className="font-mono" style={{ color: 'var(--color-warning)', fontWeight: 600 }}>{policy.max_discount_percentage}%</span>
              </div>
              <input
                type="number"
                step="0.5"
                min="0"
                max="20"
                value={policy.max_discount_percentage || 5.0}
                onChange={(e) => setPolicy({ ...policy, max_discount_percentage: Number(e.target.value) })}
                style={{ width: '100%' }}
              />
              <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', marginTop: '4px' }}>
                Hard ceiling. The decision engine cannot offer a discount above this rate.
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <label style={{ fontSize: '12px', fontWeight: 600 }}>Minimum Incremental Net Value</label>
                <span className="font-mono" style={{ color: 'var(--color-text-primary)', fontWeight: 600 }}>₹{policy.min_incremental_value_rupees}</span>
              </div>
              <input
                type="number"
                value={policy.min_incremental_value_rupees || 100}
                onChange={(e) => setPolicy({ ...policy, min_incremental_value_rupees: Number(e.target.value) })}
                style={{ width: '100%' }}
              />
              <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', marginTop: '4px' }}>
                If no action creates at least this incremental margin, DO NOTHING is enforced.
              </div>
            </div>
          </div>
        </div>

        {/* Hard Guardrails & Toggles */}
        <div className="card">
          <div className="card-title" style={{ marginBottom: '16px' }}>Hard Safety Guardrails</div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 12px', borderRadius: '6px', backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border)' }}>
              <div>
                <div style={{ fontWeight: 600, fontSize: '13px' }}>Enforce Customer Communication Opt-Out</div>
                <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Block SMS/WhatsApp for opted-out customers</div>
              </div>
              <input
                type="checkbox"
                checked={policy.enforce_opt_out}
                onChange={(e) => setPolicy({ ...policy, enforce_opt_out: e.target.checked })}
                style={{ width: '18px', height: '18px', cursor: 'pointer', accentColor: 'var(--color-positive)' }}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 12px', borderRadius: '6px', backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border)' }}>
              <div>
                <div style={{ fontWeight: 600, fontSize: '13px' }}>Block Active Disputes / Chargebacks</div>
                <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Halt all recovery when a chargeback is active</div>
              </div>
              <input
                type="checkbox"
                checked={policy.block_disputed}
                onChange={(e) => setPolicy({ ...policy, block_disputed: e.target.checked })}
                style={{ width: '18px', height: '18px', cursor: 'pointer', accentColor: 'var(--color-positive)' }}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 12px', borderRadius: '6px', backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border)' }}>
              <div>
                <div style={{ fontWeight: 600, fontSize: '13px' }}>Block High-Risk Fraud Signals</div>
                <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Instant circuit-breaker on risk flags</div>
              </div>
              <input
                type="checkbox"
                checked={policy.block_fraud_signals}
                onChange={(e) => setPolicy({ ...policy, block_fraud_signals: e.target.checked })}
                style={{ width: '18px', height: '18px', cursor: 'pointer', accentColor: 'var(--color-positive)' }}
              />
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <label style={{ fontSize: '12px', fontWeight: 600 }}>Minimum Contact Interval (Hours)</label>
                <span className="font-mono">{policy.min_contact_interval_hours} hrs</span>
              </div>
              <input
                type="number"
                value={policy.min_contact_interval_hours || 24}
                onChange={(e) => setPolicy({ ...policy, min_contact_interval_hours: Number(e.target.value) })}
                style={{ width: '100%' }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
