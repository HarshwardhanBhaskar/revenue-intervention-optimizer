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
  Scale,
  RotateCcw,
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

  // Simulation Controls State
  const [amount, setAmount] = useState<number>(7499);
  const [baseProb, setBaseProb] = useState<number>(31);
  const [discountPct, setDiscountPct] = useState<number>(5.0);
  const [minIncrementalRupees, setMinIncrementalRupees] = useState<number>(100);
  const [humanApprovalThreshold, setHumanApprovalThreshold] = useState<number>(10000);
  const [objective, setObjective] = useState<'net_value' | 'gross_recovery'>('net_value');

  // Compute live economics
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
  const sortedSimulations = [...simulationResults].sort((a, b) => {
    if (objective === 'gross_recovery') {
      return b.expectedRevenue - a.expectedRevenue;
    }
    return b.incrementalNet - a.incrementalNet;
  });

  // Apply minimum incremental value policy
  let optimalAction = sortedSimulations[0];
  let policyEnforced = false;
  if (optimalAction.actionKey !== 'do_nothing' && optimalAction.incrementalNet < minIncrementalRupees) {
    optimalAction = simulationResults.find((s) => s.actionKey === 'do_nothing') || sortedSimulations[0];
    policyEnforced = true;
  }

  const requiresHumanApproval = amount > humanApprovalThreshold;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', maxWidth: '1240px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="badge badge-gold">SIGNATURE FEATURE</span>
            <h1 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--color-text-primary)' }}>
              Counterfactual Decision Lab
            </h1>
          </div>
          <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
            Interactive financial simulator: test what-if parameters, discount sensitivity curves, and policy threshold impacts in real-time.
          </p>
        </div>

        <button
          onClick={() => {
            setAmount(7499);
            setBaseProb(31);
            setDiscountPct(5.0);
            setMinIncrementalRupees(100);
            setHumanApprovalThreshold(10000);
          }}
          className="btn btn-secondary"
          style={{ padding: '6px 12px', fontSize: '12px' }}
        >
          <RotateCcw size={13} />
          <span>Reset Parameters</span>
        </button>
      </div>

      {/* Interactive Controls Bar */}
      <div className="card" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', backgroundColor: 'var(--color-surface-2)' }}>
        {/* Transaction Amount */}
        <div>
          <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Failed Order Amount
          </label>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '6px' }}>
            <span style={{ fontSize: '16px', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>₹</span>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(Math.max(100, Number(e.target.value)))}
              style={{ fontSize: '15px', fontWeight: 700, fontFamily: 'var(--font-mono)', width: '100%' }}
            />
          </div>
          <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', marginTop: '4px' }}>
            {requiresHumanApproval ? '⚠️ Exceeds ₹10k human sign-off threshold' : 'Within automated execution threshold'}
          </div>
        </div>

        {/* Baseline Recovery Probability */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
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
            style={{ width: '100%', marginTop: '10px', accentColor: 'var(--color-gold)' }}
          />
          <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', marginTop: '4px' }}>
            High baseline (&gt;65%) naturally shifts decision to DO NOTHING
          </div>
        </div>

        {/* Discount Sensitivity Slider */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
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
            style={{ width: '100%', marginTop: '10px', accentColor: 'var(--color-warning)' }}
          />
          <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', marginTop: '4px' }}>
            Higher discount dilutes margin on large transactions
          </div>
        </div>

        {/* Minimum Incremental Yield Policy */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Min Incremental Margin Policy
            </label>
            <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--color-text-primary)' }}>₹{minIncrementalRupees}</span>
          </div>
          <input
            type="number"
            value={minIncrementalRupees}
            onChange={(e) => setMinIncrementalRupees(Math.max(0, Number(e.target.value)))}
            style={{ width: '100%', marginTop: '6px' }}
          />
          <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', marginTop: '4px' }}>
            Enforces DO NOTHING if net yield is below this floor
          </div>
        </div>
      </div>

      {/* Argmax Optimal Recommendation Banner */}
      <div
        className="card"
        style={{
          borderLeft: '4px solid var(--color-gold)',
          backgroundColor: 'var(--color-gold-bg)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '18px 24px',
        }}
      >
        <div>
          <div style={{ fontSize: '10.5px', fontWeight: 700, color: 'var(--color-gold-text)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Mathematical Optimization Result (Argmax Incremental Net Value)
          </div>
          <div style={{ fontSize: '22px', fontWeight: 700, color: 'var(--color-text-primary)', marginTop: '2px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ textTransform: 'uppercase' }}>{optimalAction.label}</span>
            <span className="badge badge-recovery">+₹{Math.round(optimalAction.incrementalNet).toLocaleString('en-IN')} net gain</span>
            {requiresHumanApproval && <span className="badge badge-warning">Requires Human Sign-off</span>}
          </div>
        </div>

        <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', textAlign: 'right', maxWidth: '400px' }}>
          Expected recovery probability lifted from <span style={{ color: 'var(--color-text-primary)', fontWeight: 600 }}>{baseProb}%</span> to <span style={{ color: 'var(--color-recovery)', fontWeight: 600 }}>{Math.round(optimalAction.probability * 100)}%</span> after factoring ₹{optimalAction.actionCost + Math.round(optimalAction.discountCost)} total intervention & margin costs.
        </div>
      </div>

      {/* Side-by-Side Simulation Breakdown & Yield Comparison */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '20px' }}>
        {/* Ranked Action Economics Cards */}
        <div className="card">
          <div className="card-title" style={{ marginBottom: '14px' }}>Counterfactual Breakdown Across All 5 Interventions</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {sortedSimulations.map((sim, sIdx) => {
              const isOptimal = sim.actionKey === optimalAction.actionKey;
              return (
                <div
                  key={sIdx}
                  style={{
                    padding: '14px 16px',
                    borderRadius: '4px',
                    backgroundColor: isOptimal ? 'var(--color-gold-bg)' : 'var(--color-surface-2)',
                    border: `1px solid ${isOptimal ? 'var(--color-gold-border)' : 'var(--color-border)'}`,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontWeight: 600, fontSize: '13px', color: isOptimal ? 'var(--color-gold-text)' : 'var(--color-text-primary)' }}>
                        {sim.label}
                      </span>
                      {isOptimal && <span className="badge badge-gold">Recommended</span>}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>
                      P: {Math.round(sim.probability * 100)}% • Cost: ₹{sim.actionCost} {sim.discountCost > 0 && `• Discount: ₹${Math.round(sim.discountCost)}`}
                    </div>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '13.5px', color: sim.incrementalNet > 0 ? 'var(--color-recovery)' : 'var(--color-text-muted)' }}>
                      {sim.incrementalNet >= 0 ? '+' : ''}₹{Math.round(sim.incrementalNet).toLocaleString('en-IN')}
                    </div>
                    <div style={{ fontSize: '10px', color: 'var(--color-text-muted)' }}>incremental net</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Incremental Yield Bar Chart */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
          <div className="card-title" style={{ marginBottom: '10px' }}>Incremental Yield Comparison</div>
          <div style={{ width: '100%', height: '240px', flex: 1 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sortedSimulations} layout="vertical" margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
                <XAxis type="number" stroke="#8C867C" fontSize={10} tickFormatter={(v) => `₹${v}`} />
                <YAxis type="category" dataKey="actionKey" stroke="#8C867C" fontSize={11} width={80} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#FFFFFF', border: '1px solid #E5E1D8', borderRadius: '4px', fontSize: '12px' }}
                  formatter={(val: any) => [`₹${Math.round(Number(val)).toLocaleString('en-IN')}`, 'Net Incremental']}
                />
                <Bar dataKey="incrementalNet" radius={[0, 3, 3, 0]}>
                  {sortedSimulations.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.actionKey === optimalAction.actionKey ? '#C29B27' : entry.incrementalNet > 0 ? '#2980B9' : '#8C867C'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div style={{ padding: '10px 12px', borderRadius: '4px', backgroundColor: 'var(--color-surface-2)', border: '1px solid var(--color-border)', fontSize: '11px', color: 'var(--color-text-secondary)', marginTop: '10px' }}>
            <div style={{ fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: '2px' }}>Economic Net Value Function:</div>
            <code>IncrementalNet = [P(Recovery|Action) × Amount - Cost - DiscountCost] - [P(Recovery|DO_NOTHING) × Amount]</code>
          </div>
        </div>
      </div>
    </div>
  );
}
