'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  TrendingUp,
  ShieldCheck,
  Coins,
  ArrowUpRight,
  AlertCircle,
  Clock,
  Sparkles,
  Layers,
  ChevronRight,
  CheckCircle2,
  Maximize2,
  X,
  Scale,
  AlertTriangle,
  ArrowRight,
  FlaskConical,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
} from 'recharts';

export default function OverviewPage() {
  const [summary, setSummary] = useState<any>({
    revenue_at_risk_paise: 39949600,
    recovered_paise: 23206170,
    incremental_recovered_paise: 4823400,
    recovery_rate: 0.581,
    baseline_recovery_rate: 0.35,
    improvement_vs_baseline: 18.7,
    total_opportunities: 300,
    interventions_executed: 242,
    do_nothing_count: 58,
    net_incremental_value_paise: 4123400,
    total_intervention_cost_paise: 700000,
  });

  const [trends, setTrends] = useState<any[]>([
    { month: 'Jan', at_risk: 4200000, recovered: 2100000, baseline: 1470000, incremental: 630000 },
    { month: 'Feb', at_risk: 4800000, recovered: 2550000, baseline: 1680000, incremental: 870000 },
    { month: 'Mar', at_risk: 5100000, recovered: 2850000, baseline: 1785000, incremental: 1065000 },
    { month: 'Apr', at_risk: 4900000, recovered: 2900000, baseline: 1715000, incremental: 1185000 },
    { month: 'May', at_risk: 5300000, recovered: 3200000, baseline: 1855000, incremental: 1345000 },
    { month: 'Jun', at_risk: 5600000, recovered: 3450000, baseline: 1960000, incremental: 1490000 },
    { month: 'Jul', at_risk: 5800000, recovered: 3600000, baseline: 2030000, incremental: 1570000 },
  ]);

  const [recentOpps, setRecentOpps] = useState<any[]>([]);
  const [expandedCard, setExpandedCard] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/dashboard/summary')
      .then((res) => res.json())
      .then((data) => {
        if (data.total_opportunities) setSummary(data);
      })
      .catch((err) => console.log('Using default summary data', err));

    fetch('/api/opportunities?per_page=5')
      .then((res) => res.json())
      .then((data) => {
        if (data.opportunities) setRecentOpps(data.opportunities);
      })
      .catch((err) => console.log('Using default opps', err));
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', maxWidth: '1240px' }}>
      {/* 1. Revenue Control Header Banner */}
      <div
        className="card"
        style={{
          borderLeft: '4px solid var(--color-gold)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '24px 28px',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-gold">FINANCIAL IMPACT METRIC</span>
            <span style={{ fontSize: '11px', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>TRACK 03 • AI REVENUE RECOVERY</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'baseline', gap: '14px', marginTop: '6px' }}>
            <span style={{ fontSize: '34px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--color-text-primary)' }}>
              ₹{(summary.net_incremental_value_paise / 100).toLocaleString('en-IN')}
            </span>
            <span style={{ fontSize: '13px', color: 'var(--color-recovery)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '3px' }}>
              <TrendingUp size={15} />
              +{summary.improvement_vs_baseline}% vs rule baseline
            </span>
          </div>

          <div style={{ fontSize: '12.5px', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
            Incremental net revenue won back across <span style={{ color: 'var(--color-text-primary)', fontWeight: 600 }}>{summary.total_opportunities}</span> analyzed failures, minus gateway costs and discounts.
          </div>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <Link href="/decision-lab" className="btn btn-secondary" style={{ padding: '8px 14px', fontFamily: 'var(--font-mono)' }}>
            <FlaskConical size={14} color="var(--color-gold)" />
            <span>Decision Lab</span>
          </Link>
          <Link href="/approvals" className="btn btn-gold" style={{ padding: '8px 16px' }}>
            <span>Approval Queue (3)</span>
            <ArrowRight size={13} />
          </Link>
        </div>
      </div>

      {/* 2. Recovery Signal Grid (Interactive Layout Grid Pattern) */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <div style={{ fontSize: '11.5px', fontWeight: 700, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Recovery Signal Grid • Click Card to Expand Analytics
          </div>
          {expandedCard && (
            <button onClick={() => setExpandedCard(null)} style={{ fontSize: '11px', color: 'var(--color-gold-text)', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <X size={12} />
              <span>Close Detailed Panel</span>
            </button>
          )}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
          {/* Card 1: Revenue at Risk */}
          <div
            className="card"
            onClick={() => setExpandedCard(expandedCard === 'risk' ? null : 'risk')}
            style={{
              cursor: 'pointer',
              borderColor: expandedCard === 'risk' ? 'var(--color-gold)' : 'var(--color-border)',
              backgroundColor: expandedCard === 'risk' ? 'var(--color-surface-2)' : 'var(--color-surface)',
              transition: 'all 0.15s ease',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <div className="card-title">Revenue At Risk</div>
              <Maximize2 size={12} color="var(--color-text-muted)" />
            </div>
            <div style={{ fontSize: '22px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--color-text-primary)', marginTop: '8px' }}>
              ₹{(summary.revenue_at_risk_paise / 100).toLocaleString('en-IN')}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', marginTop: '4px' }}>
              {summary.total_opportunities} failed payment events
            </div>
          </div>

          {/* Card 2: Incremental Net Recovered */}
          <div
            className="card"
            onClick={() => setExpandedCard(expandedCard === 'incremental' ? null : 'incremental')}
            style={{
              cursor: 'pointer',
              borderColor: expandedCard === 'incremental' ? 'var(--color-gold)' : 'var(--color-border)',
              backgroundColor: expandedCard === 'incremental' ? 'var(--color-surface-2)' : 'var(--color-surface)',
              transition: 'all 0.15s ease',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <div className="card-title">Incremental Net Won</div>
              <Maximize2 size={12} color="var(--color-text-muted)" />
            </div>
            <div style={{ fontSize: '22px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--color-recovery)', marginTop: '8px' }}>
              ₹{(summary.incremental_recovered_paise / 100).toLocaleString('en-IN')}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', marginTop: '4px' }}>
              Uplift created above DO NOTHING baseline
            </div>
          </div>

          {/* Card 3: Recovery Rate */}
          <div
            className="card"
            onClick={() => setExpandedCard(expandedCard === 'rate' ? null : 'rate')}
            style={{
              cursor: 'pointer',
              borderColor: expandedCard === 'rate' ? 'var(--color-gold)' : 'var(--color-border)',
              backgroundColor: expandedCard === 'rate' ? 'var(--color-surface-2)' : 'var(--color-surface)',
              transition: 'all 0.15s ease',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <div className="card-title">AI Recovery Rate</div>
              <Maximize2 size={12} color="var(--color-text-muted)" />
            </div>
            <div style={{ fontSize: '22px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--color-text-primary)', marginTop: '8px' }}>
              {(summary.recovery_rate * 100).toFixed(1)}%
            </div>
            <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', marginTop: '4px' }}>
              vs {(summary.baseline_recovery_rate * 100).toFixed(1)}% un-optimized baseline
            </div>
          </div>

          {/* Card 4: Margin Protected (DO NOTHING) */}
          <div
            className="card"
            onClick={() => setExpandedCard(expandedCard === 'margin' ? null : 'margin')}
            style={{
              cursor: 'pointer',
              borderColor: expandedCard === 'margin' ? 'var(--color-gold)' : 'var(--color-border)',
              backgroundColor: expandedCard === 'margin' ? 'var(--color-surface-2)' : 'var(--color-surface)',
              transition: 'all 0.15s ease',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <div className="card-title">Margin Protected</div>
              <Maximize2 size={12} color="var(--color-text-muted)" />
            </div>
            <div style={{ fontSize: '22px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--color-gold-text)', marginTop: '8px' }}>
              {summary.do_nothing_count} <span style={{ fontSize: '13px', color: 'var(--color-text-muted)' }}>saved</span>
            </div>
            <div style={{ fontSize: '11px', color: 'var(--color-recovery)', marginTop: '4px' }}>
              DO NOTHING applied where margin would erode
            </div>
          </div>
        </div>

        {/* Expanded Detailed Signal Panel (Layout Grid expansion) */}
        {expandedCard && (
          <div
            className="card"
            style={{
              marginTop: '12px',
              backgroundColor: 'var(--color-surface-2)',
              border: '1px solid var(--color-gold-border)',
              padding: '18px 24px',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-text-primary)' }}>
                  {expandedCard === 'risk' && 'Revenue At Risk Breakdown by Gateway & Method'}
                  {expandedCard === 'incremental' && 'Incremental Economic Net Yield Mathematical Breakdown'}
                  {expandedCard === 'rate' && 'Recovery Conversion Uplift across Customer Segments'}
                  {expandedCard === 'margin' && 'Margin Protection & DO NOTHING Selection Logic'}
                </div>
                <div style={{ fontSize: '11.5px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                  {expandedCard === 'risk' && 'Breakdown of failed transactions across UPI (42%), Cards (38%), and NetBanking (20%).'}
                  {expandedCard === 'incremental' && 'Computed as E[Rev|Action] - Cost - DiscountCost - E[Rev|DO_NOTHING]. Realized net gain: +₹4,12,340.'}
                  {expandedCard === 'rate' && 'Highest uplift in Price-Sensitive (+24% pts) and Premium (+18% pts) tiers.'}
                  {expandedCard === 'margin' && 'In 58 failures, natural self-recovery probability exceeded intervention uplift, saving gateway fees and discounts.'}
                </div>
              </div>
              <button onClick={() => setExpandedCard(null)} style={{ color: 'var(--color-text-muted)' }}>
                <X size={16} />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* 3. Charts & Recovery Pipeline Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.8fr 1fr', gap: '20px' }}>
        {/* Trajectory Area Chart */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Recovery Yield Trajectory</div>
              <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                Monthly realized net recovered revenue (Gold) vs un-optimized baseline heuristic (Taupe)
              </div>
            </div>
            <span className="badge badge-gold">Active Ledger</span>
          </div>

          <div style={{ width: '100%', height: '250px', marginTop: '10px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorRecGold" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#C29B27" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#C29B27" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="colorBaseTaupe" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8C867C" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#8C867C" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="month" stroke="#8C867C" fontSize={11} tickLine={false} />
                <YAxis stroke="#8C867C" fontSize={11} tickFormatter={(val) => `₹${val / 100000}L`} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#FFFFFF', border: '1px solid #E5E1D8', borderRadius: '4px', fontSize: '12px' }}
                  formatter={(val: any) => [`₹${Number(val).toLocaleString('en-IN')}`, '']}
                />
                <Area type="monotone" dataKey="recovered" name="AI Recovered" stroke="#C29B27" strokeWidth={2} fillOpacity={1} fill="url(#colorRecGold)" />
                <Area type="monotone" dataKey="baseline" name="Baseline Heuristic" stroke="#8C867C" strokeWidth={1.5} strokeDasharray="3 3" fillOpacity={1} fill="url(#colorBaseTaupe)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Pipeline Funnel Stages */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
          <div className="card-header">
            <div className="card-title">Recovery Pipeline Funnel</div>
            <Link href="/recovery" style={{ fontSize: '11px', color: 'var(--color-gold-text)', display: 'flex', alignItems: 'center', gap: '2px' }}>
              <span>View Ledger</span>
              <ChevronRight size={12} />
            </Link>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', flex: 1, justifyContent: 'center' }}>
            {[
              { label: '1. Detected Risk', count: summary.total_opportunities, sub: 'Webhook verified & deduplicated', color: 'var(--color-text-primary)' },
              { label: '2. T-Learner CATE Scored', count: summary.total_opportunities, sub: '5 action probabilities estimated', color: 'var(--color-info)' },
              { label: '3. Policy Guardrails Checked', count: summary.total_opportunities, sub: 'Deterministic ₹10k & dispute rules', color: 'var(--color-warning)' },
              { label: '4. Interventions Dispatched', count: summary.interventions_executed, sub: 'Payment link, retry, or discount', color: 'var(--color-recovery)' },
              { label: '5. DO NOTHING Enforced', count: summary.do_nothing_count, sub: 'Protected from margin dilution', color: 'var(--color-gold-text)' },
            ].map((st, sIdx) => (
              <div key={sIdx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ fontSize: '12px', fontWeight: 600, color: st.color }}>{st.label}</div>
                  <div style={{ fontSize: '10px', color: 'var(--color-text-muted)' }}>{st.sub}</div>
                </div>
                <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '13.5px', color: 'var(--color-text-primary)' }}>
                  {st.count}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 4. Recent Decisions Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--color-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div className="card-title">Recent Intervention Decisions</div>
            <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
              Real-time payment failures diagnosed and ranked by incremental net value
            </div>
          </div>
          <Link href="/recovery" className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '11.5px' }}>
            <span>Full Ledger</span>
            <ChevronRight size={12} />
          </Link>
        </div>

        <table>
          <thead>
            <tr>
              <th>Customer</th>
              <th>Amount</th>
              <th>Failure Context</th>
              <th>Recommended Action</th>
              <th>Baseline P</th>
              <th>Intervention P</th>
              <th>Expected Net Yield</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {(recentOpps.length > 0 ? recentOpps : [
              { id: '1', customer: { external_id: 'cust_90a12', segment: 'premium' }, amount_rupees: 28500, payment: { method: 'credit_card', failure_reason: 'authentication_failed' }, recommended_action: 'payment_link', baseline_probability: 0.28, recommended_probability: 0.74, expected_incremental_value_paise: 1420000, workflow_state: 'pending_approval' },
              { id: '2', customer: { external_id: 'cust_b3341', segment: 'price_sensitive' }, amount_rupees: 12500, payment: { method: 'debit_card', failure_reason: 'insufficient_funds' }, recommended_action: 'discount', baseline_probability: 0.32, recommended_probability: 0.76, expected_incremental_value_paise: 420000, workflow_state: 'pending_approval' },
              { id: '3', customer: { external_id: 'cust_4712c', segment: 'loyal' }, amount_rupees: 7499, payment: { method: 'upi', failure_reason: 'timeout' }, recommended_action: 'retry', baseline_probability: 0.65, recommended_probability: 0.88, expected_incremental_value_paise: 162400, workflow_state: 'recovered' },
              { id: '4', customer: { external_id: 'cust_98811', segment: 'regular' }, amount_rupees: 3500, payment: { method: 'upi', failure_reason: 'network_error' }, recommended_action: 'do_nothing', baseline_probability: 0.72, recommended_probability: 0.72, expected_incremental_value_paise: 0, workflow_state: 'recovered' },
            ]).map((opp: any, idx: number) => (
              <tr key={idx}>
                <td>
                  <div style={{ fontWeight: 600 }}>{opp.customer?.external_id || 'cust_anonymous'}</div>
                  <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', textTransform: 'capitalize' }}>
                    {opp.customer?.segment || 'regular'}
                  </div>
                </td>
                <td className="font-mono" style={{ fontWeight: 600 }}>
                  ₹{Number(opp.amount_rupees || (opp.amount_paise / 100)).toLocaleString('en-IN')}
                </td>
                <td>
                  <div style={{ textTransform: 'capitalize' }}>{opp.payment?.failure_reason?.replace('_', ' ') || 'network error'}</div>
                  <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>
                    {opp.payment?.method || 'UPI'}
                  </div>
                </td>
                <td>
                  <span className={`badge ${opp.recommended_action === 'do_nothing' ? 'badge-muted' : opp.recommended_action === 'discount' ? 'badge-warning' : 'badge-gold'}`}>
                    {opp.recommended_action?.replace('_', ' ') || 'payment link'}
                  </span>
                </td>
                <td className="font-mono">
                  {Math.round((opp.baseline_probability || 0.3) * 100)}%
                </td>
                <td className="font-mono" style={{ color: 'var(--color-recovery)', fontWeight: 600 }}>
                  {Math.round((opp.recommended_probability || 0.7) * 100)}%
                </td>
                <td className="font-mono" style={{ color: 'var(--color-recovery)', fontWeight: 600 }}>
                  +₹{Math.round((opp.expected_incremental_value_paise || 0) / 100).toLocaleString('en-IN')}
                </td>
                <td>
                  <span className={`badge ${opp.workflow_state === 'recovered' ? 'badge-recovery' : opp.workflow_state === 'pending_approval' ? 'badge-warning' : 'badge-info'}`}>
                    {opp.workflow_state?.replace('_', ' ') || 'analyzed'}
                  </span>
                </td>
                <td>
                  <Link href={`/recovery/${opp.id}`} className="btn btn-secondary" style={{ padding: '3px 8px', fontSize: '11px' }}>
                    Inspect
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 5. Exceptions Requiring Attention */}
      <div
        className="card"
        style={{
          borderLeft: '4px solid var(--color-warning)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '16px 20px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <AlertTriangle size={18} color="var(--color-warning)" />
          <div>
            <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
              3 High-Value Transactions Awaiting Operator Sign-Off
            </div>
            <div style={{ fontSize: '11.5px', color: 'var(--color-text-secondary)' }}>
              Transactions exceeding the ₹10,000 automated limit are held safely in the Approval Queue.
            </div>
          </div>
        </div>
        <Link href="/approvals" className="btn btn-secondary" style={{ padding: '6px 14px', fontSize: '12px' }}>
          <span>Open Queue</span>
          <ChevronRight size={13} />
        </Link>
      </div>
    </div>
  );
}
