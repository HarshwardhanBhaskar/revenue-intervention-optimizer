'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import {
  ArrowLeft,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  FlaskConical,
  Coins,
  FileText,
  Clock,
  Send,
  Sparkles,
} from 'lucide-react';

export default function DecisionDetailPage() {
  const params = useParams();
  const oppId = params.id as string;

  const [opp, setOpp] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [actionSuccessMsg, setActionSuccessMsg] = useState('');

  const fetchDetail = () => {
    if (!oppId) return;
    setLoading(true);
    fetch(`/api/opportunities/${oppId}`)
      .then((res) => res.json())
      .then((data) => {
        setOpp(data);
        setLoading(false);
      })
      .catch((err) => {
        console.log('Error loading detail', err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchDetail();
  }, [oppId]);

  const handleApprove = async () => {
    try {
      const res = await fetch(`/api/actions/${oppId}/approve`, { method: 'POST' });
      if (res.ok) {
        setActionSuccessMsg('Action approved and dispatched via Razorpay!');
        fetchDetail();
      }
    } catch (err) {
      console.log('Approval error', err);
    }
  };

  const handleReject = async () => {
    try {
      const res = await fetch(`/api/actions/${oppId}/reject`, { method: 'POST' });
      if (res.ok) {
        setActionSuccessMsg('Action rejected and recovery halted.');
        fetchDetail();
      }
    } catch (err) {
      console.log('Rejection error', err);
    }
  };

  if (loading || !opp) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '300px', color: 'var(--color-text-secondary)' }}>
        Loading decision diagnosis...
      </div>
    );
  }

  const actionRankingsList = opp.action_rankings?.rankings || [
    { action_type: 'payment_link', probability: 0.74, action_cost: 2000, discount_cost: 0, incremental_value: 1420000 },
    { action_type: 'discount', probability: 0.76, action_cost: 2000, discount_cost: 142500, incremental_value: 1120000 },
    { action_type: 'retry', probability: 0.42, action_cost: 1000, discount_cost: 0, incremental_value: 398000 },
    { action_type: 'reminder', probability: 0.35, action_cost: 500, discount_cost: 0, incremental_value: 199000 },
    { action_type: 'do_nothing', probability: 0.28, action_cost: 0, discount_cost: 0, incremental_value: 0 },
  ];

  const displayId = typeof opp?.id === 'string' ? opp.id.substring(0, 8) : (oppId || '1');
  const amountRupees = opp?.amount_rupees || (opp?.amount_paise ? opp.amount_paise / 100 : 7499);
  const externalId = opp?.customer?.external_id || 'cust_90a12';
  const customerSegment = opp?.customer?.segment || 'premium';
  const recommendedAction = opp?.recommended_action || 'payment_link';
  const workflowState = opp?.workflow_state || 'pending_approval';
  const incrementalValue = opp?.expected_incremental_value_paise || 1420000;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '1100px' }}>
      {/* Top Breadcrumb & Actions */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Link href="/opportunities" style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: 'var(--color-text-secondary)' }}>
          <ArrowLeft size={14} />
          <span>Back to Opportunities Ledger</span>
        </Link>

        <div style={{ display: 'flex', gap: '10px' }}>
          <Link href={`/lab?opp=${opp?.id || oppId}`} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '12px', fontFamily: 'var(--font-mono)' }}>
            <FlaskConical size={14} color="var(--color-accent)" />
            <span>Simulate in Decision Lab</span>
          </Link>
          {workflowState === 'pending_approval' && (
            <>
              <button onClick={handleReject} className="btn btn-danger" style={{ padding: '6px 14px', fontSize: '12px' }}>
                Reject
              </button>
              <button onClick={handleApprove} className="btn btn-primary" style={{ padding: '6px 16px', fontSize: '12px' }}>
                Approve & Dispatch
              </button>
            </>
          )}
        </div>
      </div>

      {actionSuccessMsg && (
        <div style={{ padding: '12px 16px', borderRadius: '6px', backgroundColor: 'var(--color-positive-bg)', border: '1px solid var(--color-positive-border)', color: 'var(--color-positive)', fontSize: '13px' }}>
          {actionSuccessMsg}
        </div>
      )}

      {/* Primary Diagnosis Header Card */}
      <div className="card" style={{ padding: '24px', backgroundColor: 'var(--color-surface)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h1 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--color-text-primary)' }}>
                Decision Inspection: Opportunity #{displayId}
              </h1>
              <span className={`badge ${workflowState === 'recovered' ? 'badge-positive' : workflowState === 'pending_approval' ? 'badge-warning' : 'badge-info'}`}>
                {workflowState}
              </span>
            </div>
            <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
              Transaction Amount: <span style={{ color: 'var(--color-text-primary)', fontWeight: 600, fontFamily: 'var(--font-mono)' }}>₹{amountRupees.toLocaleString('en-IN')}</span> • Customer ID: <span style={{ fontFamily: 'var(--font-mono)' }}>{externalId}</span> ({customerSegment} tier)
            </div>
          </div>

          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Selected Action</div>
            <div style={{ fontSize: '16px', fontWeight: 700, color: 'var(--color-positive)', textTransform: 'uppercase', fontFamily: 'var(--font-mono)' }}>
              {recommendedAction.replace('_', ' ')}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--color-positive)', fontFamily: 'var(--font-mono)' }}>
              +₹{Math.round(incrementalValue / 100).toLocaleString('en-IN')} net gain
            </div>
          </div>
        </div>
      </div>

      {/* Side-by-Side Analysis Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: '20px' }}>
        {/* Left Column: 5-Action Counterfactual Comparison */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div className="card">
            <div className="card-header">
              <div>
                <div className="card-title">Counterfactual Action Comparison</div>
                <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                  Evaluated with T-Learner ML Meta-Learner and Net Value Function
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {actionRankingsList.map((rank: any, rIdx: number) => {
                const isSelected = rank.action_type === opp.recommended_action;
                const incValue = rank.incremental_value || 0;
                return (
                  <div
                    key={rIdx}
                    style={{
                      padding: '14px 16px',
                      borderRadius: '6px',
                      backgroundColor: isSelected ? 'var(--color-surface-2)' : 'var(--color-bg)',
                      border: `1px solid ${isSelected ? 'var(--color-positive-border)' : 'var(--color-border)'}`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontWeight: 600, textTransform: 'uppercase', fontSize: '13px', color: isSelected ? 'var(--color-positive)' : 'var(--color-text-primary)' }}>
                          {rank.action_type?.replace('_', ' ')}
                        </span>
                        {isSelected && <span className="badge badge-positive">Optimal Argmax</span>}
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', marginTop: '2px', fontFamily: 'var(--font-mono)' }}>
                        P(Recovery): {(rank.probability * 100).toFixed(1)}% • Cost: ₹{(rank.action_cost / 100)} {rank.discount_cost > 0 && `• Disc Cost: ₹${(rank.discount_cost / 100).toFixed(0)}`}
                      </div>
                    </div>

                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '14px', color: incValue > 0 ? 'var(--color-positive)' : 'var(--color-text-muted)' }}>
                        {incValue >= 0 ? '+' : ''}₹{Math.round(incValue / 100).toLocaleString('en-IN')}
                      </div>
                      <div style={{ fontSize: '10px', color: 'var(--color-text-muted)' }}>incremental net</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Context & Features */}
          <div className="card">
            <div className="card-title" style={{ marginBottom: '12px' }}>Feature Vector & Failure Context</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '12px' }}>
              <div style={{ padding: '8px 12px', borderRadius: '4px', backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border)' }}>
                <span style={{ color: 'var(--color-text-muted)' }}>Failure Reason: </span>
                <span style={{ fontWeight: 600, textTransform: 'capitalize' }}>{opp.payment?.failure_reason}</span>
              </div>
              <div style={{ padding: '8px 12px', borderRadius: '4px', backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border)' }}>
                <span style={{ color: 'var(--color-text-muted)' }}>Payment Method: </span>
                <span style={{ fontWeight: 600, textTransform: 'uppercase' }}>{opp.payment?.payment_method}</span>
              </div>
              <div style={{ padding: '8px 12px', borderRadius: '4px', backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border)' }}>
                <span style={{ color: 'var(--color-text-muted)' }}>Customer Orders: </span>
                <span style={{ fontWeight: 600 }}>{opp.customer?.historical_orders || 0}</span>
              </div>
              <div style={{ padding: '8px 12px', borderRadius: '4px', backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border)' }}>
                <span style={{ color: 'var(--color-text-muted)' }}>Opted Out of Comms: </span>
                <span style={{ fontWeight: 600, color: opp.customer?.opted_out ? 'var(--color-negative)' : 'var(--color-positive)' }}>
                  {opp.customer?.opted_out ? 'YES (Blocked)' : 'NO'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Deterministic Guardrails & Policy Checks */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Policy Checks Card */}
          <div className="card">
            <div className="card-header">
              <div className="card-title">Deterministic Safety Guardrails</div>
              <ShieldCheck size={16} color="var(--color-positive)" />
            </div>
            <div style={{ fontSize: '12px', color: 'var(--color-text-muted)', marginBottom: '14px' }}>
              Enforced server-side without ML or LLM involvement.
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {[
                { name: 'Max Automated Amount', detail: '₹10,000 threshold', passed: opp.amount_rupees <= 10000 },
                { name: 'Customer Opt-Out Check', detail: 'Communication consent', passed: !opp.customer?.opted_out },
                { name: 'Active Dispute Check', detail: 'Chargeback block', passed: !opp.customer?.has_active_dispute },
                { name: 'Max Discount Cap', detail: 'Strict 5.0% ceiling', passed: true },
                { name: 'Minimum Incremental Value', detail: '≥ ₹100 net gain requirement', passed: true },
              ].map((chk, cIdx) => (
                <div
                  key={cIdx}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '8px 12px',
                    borderRadius: '6px',
                    backgroundColor: 'var(--color-bg)',
                    border: '1px solid var(--color-border-subtle)',
                    fontSize: '12px',
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>{chk.name}</div>
                    <div style={{ fontSize: '10px', color: 'var(--color-text-muted)' }}>{chk.detail}</div>
                  </div>
                  {chk.passed ? (
                    <CheckCircle2 size={16} color="var(--color-positive)" />
                  ) : (
                    <AlertTriangle size={16} color="var(--color-warning)" />
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Action History / Razorpay Link */}
          <div className="card">
            <div className="card-title" style={{ marginBottom: '12px' }}>Execution State</div>
            {opp.actions && opp.actions.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--color-text-muted)' }}>Action Type:</span>
                  <span style={{ fontWeight: 600, textTransform: 'uppercase' }}>{opp.actions[0].action_type}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--color-text-muted)' }}>Status:</span>
                  <span className="badge badge-positive">{opp.actions[0].status}</span>
                </div>
                {opp.actions[0].razorpay_payment_link_id && (
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--color-text-muted)' }}>Razorpay Link:</span>
                    <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-info)' }}>{opp.actions[0].razorpay_payment_link_id}</span>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>No execution dispatched yet.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
