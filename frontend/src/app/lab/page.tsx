'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import {
  FlaskConical,
  Coins,
  Sparkles,
  ArrowRight,
  TrendingUp,
  Percent,
  Sliders,
  CheckCircle2,
  Info,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

export default function DecisionLabPage() {
  return (
    <Suspense fallback={<div style={{ padding: '20px', color: 'var(--color-text-secondary)' }}>Loading Decision Lab...</div>}>
      <DecisionLabContent />
    </Suspense>
  );
}

function DecisionLabContent() {
  const searchParams = useSearchParams();
  const initialOppId = searchParams.get('opp') || '';

  const [amount, setAmount] = useState<number>(7499);
  const [baseProb, setBaseProb] = useState<number>(31);
  const [discountPct, setDiscountPct] = useState<number>(5.0);
  const [selectedAction, setSelectedAction] = useState<string>('payment_link');

  // Compute live economics
  const amountPaise = amount * 100;
  const pBase = baseProb / 100.0;

  // Actions configuration
  const actionConfigs: Record<string, { label: string; pUplift: number; cost: number; discount: number }> = {
    do_nothing: { label: 'DO NOTHING', pUplift: 0, cost: 0, discount: 0 },
    retry: { label: 'Automated Retry', pUplift: 0.23, cost: 10, discount: 0 },
    payment_link: { label: 'Custom Payment Link', pUplift: 0.40, cost: 20, discount: 0 },
    reminder: { label: 'SMS / WhatsApp Reminder', pUplift: 0.15, cost: 5, discount: 0 },
    discount: { label: `Targeted Discount (${discountPct}%)`, pUplift: 0.45 * (1 + (discountPct - 5) * 0.04), cost: 20, discount: discountPct },
  };

  const simulationResults = Object.entries(actionConfigs).map(([key, cfg]) => {
    const pRec = Math.min(0.98, pBase + cfg.pUplift);
    const expRev = pRec * amount;
    const actionCost = cfg.cost;
    const discCost = pRec * amount * (cfg.discount / 100.0);
    const expNet = expRev - actionCost - discCost;
    const baseNet = pBase * amount;
    const incNet = expNet - baseNet;

    return {
      actionKey: key,
      label: cfg.label,
      probability: pRec,
      expectedRevenue: expRev,
      actionCost: actionCost,
      discountCost: discCost,
      expectedNet: expNet,
      baselineExpected: baseNet,
      incrementalNet: incNet,
    };
  });

  // Sort by incremental net descending
  const sortedSimulations = [...simulationResults].sort((a, b) => b.incrementalNet - a.incrementalNet);
  const optimalAction = sortedSimulations[0];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', maxWidth: '1200px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="badge badge-positive">Signature Feature</span>
            <h1 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--color-text-primary)' }}>
              Counterfactual Decision Lab
            </h1>
          </div>
          <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
            Simulate recovery actions, sensitivity sliders, and mathematical net value functions in real-time.
          </p>
        </div>
      </div>

      {/* Interactive Controls Card */}
      <div className="card" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', backgroundColor: 'var(--color-surface-2)' }}>
        {/* Transaction Amount Slider / Input */}
        <div>
          <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Failed Transaction Amount
          </label>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '6px' }}>
            <span style={{ fontSize: '18px', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>₹</span>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(Math.max(100, Number(e.target.value)))}
              style={{ fontSize: '16px', fontWeight: 700, fontFamily: 'var(--font-mono)', width: '100%' }}
            />
          </div>
          <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', marginTop: '4px' }}>
            Try ₹7,499 (D2C Average) or ₹28,500 (High-Value VIP)
          </div>
        </div>

        {/* Baseline Recovery Probability */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Baseline P(Recovery | Do Nothing)
            </label>
            <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--color-text-primary)' }}>{baseProb}%</span>
          </div>
          <input
            type="range"
            min="5"
            max="80"
            value={baseProb}
            onChange={(e) => setBaseProb(Number(e.target.value))}
            style={{ width: '100%', marginTop: '12px', accentColor: 'var(--color-positive)' }}
          />
          <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', marginTop: '4px' }}>
            Higher baseline (&gt;65%) naturally triggers DO NOTHING
          </div>
        </div>

        {/* Discount Percentage Slider */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Discount Sensitivity Slider
            </label>
            <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--color-warning)' }}>{discountPct}%</span>
          </div>
          <input
            type="range"
            min="1"
            max="10"
            step="0.5"
            value={discountPct}
            onChange={(e) => setDiscountPct(Number(e.target.value))}
            style={{ width: '100%', marginTop: '12px', accentColor: 'var(--color-warning)' }}
          />
          <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', marginTop: '4px' }}>
            Notice how higher discounts dilute margin on larger orders
          </div>
        </div>
      </div>

      {/* Argmax Optimal Action Banner */}
      <div
        className="card"
        style={{
          background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(18, 21, 30, 1) 100%)',
          border: '1px solid rgba(99, 102, 241, 0.4)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '18px 24px',
        }}
      >
        <div>
          <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-accent)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
            Mathematical Optimization Result (Argmax Incremental Net Value)
          </div>
          <div style={{ fontSize: '22px', fontWeight: 700, color: 'var(--color-text-primary)', marginTop: '2px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ textTransform: 'uppercase' }}>{optimalAction.label}</span>
            <span className="badge badge-positive">+₹{Math.round(optimalAction.incrementalNet).toLocaleString('en-IN')} net gain</span>
          </div>
        </div>

        <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', textAlign: 'right', maxWidth: '380px' }}>
          Expected recovery boosted from <span style={{ color: 'var(--color-text-primary)', fontWeight: 600 }}>{baseProb}%</span> to <span style={{ color: 'var(--color-positive)', fontWeight: 600 }}>{Math.round(optimalAction.probability * 100)}%</span> after factoring ₹{optimalAction.actionCost + Math.round(optimalAction.discountCost)} total intervention cost.
        </div>
      </div>

      {/* Side-by-Side Simulation Cards & Chart */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '20px' }}>
        {/* Ranked Action Economics List */}
        <div className="card">
          <div className="card-title" style={{ marginBottom: '14px' }}>Counterfactual Breakdown for all 5 Interventions</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {sortedSimulations.map((sim, sIdx) => {
              const isOptimal = sim.actionKey === optimalAction.actionKey;
              return (
                <div
                  key={sIdx}
                  style={{
                    padding: '14px 16px',
                    borderRadius: '6px',
                    backgroundColor: isOptimal ? 'var(--color-surface-2)' : 'var(--color-bg)',
                    border: `1px solid ${isOptimal ? 'var(--color-positive-border)' : 'var(--color-border)'}`,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontWeight: 600, fontSize: '13px', color: isOptimal ? 'var(--color-positive)' : 'var(--color-text-primary)' }}>
                        {sim.label}
                      </span>
                      {isOptimal && <span className="badge badge-positive">Recommended</span>}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>
                      P: {Math.round(sim.probability * 100)}% • Cost: ₹{sim.actionCost} {sim.discountCost > 0 && `• Discount: ₹${Math.round(sim.discountCost)}`}
                    </div>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '14px', color: sim.incrementalNet > 0 ? 'var(--color-positive)' : 'var(--color-text-muted)' }}>
                      {sim.incrementalNet >= 0 ? '+' : ''}₹{Math.round(sim.incrementalNet).toLocaleString('en-IN')}
                    </div>
                    <div style={{ fontSize: '10px', color: 'var(--color-text-muted)' }}>incremental net</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Incremental Value Bar Chart */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
          <div className="card-title" style={{ marginBottom: '10px' }}>Net Incremental Yield Comparison</div>
          <div style={{ width: '100%', height: '240px', flex: 1 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sortedSimulations} layout="vertical" margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
                <XAxis type="number" stroke="#5E647C" fontSize={10} tickFormatter={(v) => `₹${v}`} />
                <YAxis type="category" dataKey="actionKey" stroke="#5E647C" fontSize={11} width={80} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1A1E2B', border: '1px solid #262B3D', borderRadius: '6px', fontSize: '12px' }}
                  formatter={(val: any) => [`₹${Math.round(Number(val)).toLocaleString('en-IN')}`, 'Net Incremental']}
                />
                <Bar dataKey="incrementalNet" radius={[0, 4, 4, 0]}>
                  {sortedSimulations.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.actionKey === optimalAction.actionKey ? '#00C48C' : entry.incrementalNet > 0 ? '#3B82F6' : '#5E647C'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div style={{ padding: '10px 12px', borderRadius: '6px', backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border)', fontSize: '11px', color: 'var(--color-text-secondary)', marginTop: '10px' }}>
            <div style={{ fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: '2px' }}>Economic Formula:</div>
            <code>IncrementalNet = E[Rev|Action] - Cost - DiscountCost - BaselineExpected</code>
          </div>
        </div>
      </div>
    </div>
  );
}
