'use client';

import React, { useEffect, useState } from 'react';
import { Layers, TrendingUp, CheckCircle2, FlaskConical, BarChart3, AlertCircle } from 'lucide-react';

export default function ExperimentsPage() {
  const [benchmark, setBenchmark] = useState<any>({
    sample_size: 538,
    revenue_at_risk: 4238170,
    control_baseline: {
      policy: 'retry_once',
      recovery_rate: 0.552,
      gross_recovered: 2373270,
      total_cost: 5380,
      net_recovered: 2367890,
    },
    treatment_ai: {
      policy: 't_learner_economic_optimization',
      recovery_rate: 0.600,
      gross_recovered: 2771310,
      total_cost: 32598,
      net_recovered: 2738712,
      action_distribution: {
        discount: 155,
        payment_link: 139,
        retry: 126,
        reminder: 90,
        do_nothing: 28,
      },
      do_nothing_rate: 0.052,
    },
    incremental_impact: {
      incremental_gross_revenue: 398040,
      incremental_net_revenue: 370822,
      percentage_uplift: 15.7,
      ci_95_lower: 56019,
      ci_95_upper: 668189,
    },
  });

  useEffect(() => {
    fetch('/api/experiments')
      .then((res) => res.json())
      .then((data) => {
        if (data.test_benchmark) setBenchmark(data.test_benchmark);
      })
      .catch((err) => console.log('Using default experiment data', err));
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', maxWidth: '1100px' }}>
      {/* Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="badge badge-positive">Rigorous Evaluation</span>
          <h1 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--color-text-primary)' }}>
            Scientific Evaluation & A/B Benchmark
          </h1>
        </div>
        <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
          Empirical evaluation on the 100% held-out test set ({benchmark.sample_size} transactions, ₹{benchmark.revenue_at_risk.toLocaleString('en-IN')} at risk) with 1,000 bootstrap iterations.
        </p>
      </div>

      {/* Primary Comparison Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Control Card */}
        <div className="card" style={{ border: '1px solid var(--color-border)', backgroundColor: 'var(--color-surface)' }}>
          <div className="card-header">
            <div>
              <span className="badge badge-muted">Control Group</span>
              <div style={{ fontSize: '15px', fontWeight: 700, color: 'var(--color-text-primary)', marginTop: '4px' }}>
                Rule Baseline (Retry Once)
              </div>
            </div>
            <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>50% Traffic</div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '10px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--color-border-subtle)' }}>
              <span style={{ color: 'var(--color-text-secondary)' }}>Recovery Rate:</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{(benchmark.control_baseline.recovery_rate * 100).toFixed(1)}%</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--color-border-subtle)' }}>
              <span style={{ color: 'var(--color-text-secondary)' }}>Gross Recovered:</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>₹{benchmark.control_baseline.gross_recovered.toLocaleString('en-IN')}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--color-border-subtle)' }}>
              <span style={{ color: 'var(--color-text-secondary)' }}>Intervention Cost:</span>
              <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-warning)' }}>₹{benchmark.control_baseline.total_cost.toLocaleString('en-IN')}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0' }}>
              <span style={{ color: 'var(--color-text-secondary)', fontWeight: 600 }}>Net Revenue Recovered:</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '16px', color: 'var(--color-text-primary)' }}>
                ₹{benchmark.control_baseline.net_recovered.toLocaleString('en-IN')}
              </span>
            </div>
          </div>
        </div>

        {/* Treatment Card */}
        <div className="card" style={{ border: '1px solid var(--color-positive-border)', backgroundColor: 'var(--color-surface)' }}>
          <div className="card-header">
            <div>
              <span className="badge badge-positive">Treatment Group</span>
              <div style={{ fontSize: '15px', fontWeight: 700, color: 'var(--color-positive)', marginTop: '4px' }}>
                AI Intervention Optimizer (T-Learner)
              </div>
            </div>
            <div style={{ fontSize: '11px', color: 'var(--color-positive)', fontFamily: 'var(--font-mono)' }}>50% Traffic</div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '10px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--color-border-subtle)' }}>
              <span style={{ color: 'var(--color-text-secondary)' }}>Recovery Rate:</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--color-positive)' }}>
                {(benchmark.treatment_ai.recovery_rate * 100).toFixed(1)}% (+4.8% pts)
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--color-border-subtle)' }}>
              <span style={{ color: 'var(--color-text-secondary)' }}>Gross Recovered:</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>₹{benchmark.treatment_ai.gross_recovered.toLocaleString('en-IN')}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--color-border-subtle)' }}>
              <span style={{ color: 'var(--color-text-secondary)' }}>Intervention & Discount Cost:</span>
              <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-warning)' }}>₹{benchmark.treatment_ai.total_cost.toLocaleString('en-IN')}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0' }}>
              <span style={{ color: 'var(--color-text-secondary)', fontWeight: 600 }}>Net Revenue Recovered:</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '16px', color: 'var(--color-positive)' }}>
                ₹{benchmark.treatment_ai.net_recovered.toLocaleString('en-IN')}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Incremental Statistical Significance Summary */}
      <div
        className="card"
        style={{
          padding: '20px 24px',
          backgroundColor: 'var(--color-surface-2)',
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '20px',
        }}
      >
        <div>
          <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Incremental Net Gain</div>
          <div style={{ fontSize: '24px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--color-positive)', marginTop: '4px' }}>
            +₹{benchmark.incremental_impact.incremental_net_revenue.toLocaleString('en-IN')}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--color-positive)', marginTop: '2px' }}>
            +{benchmark.incremental_impact.percentage_uplift}% over rule-based baseline
          </div>
        </div>

        <div>
          <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>95% Bootstrap Confidence Interval</div>
          <div style={{ fontSize: '16px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--color-text-primary)', marginTop: '8px' }}>
            [₹{Math.round(benchmark.incremental_impact.ci_95_lower).toLocaleString('en-IN')}, ₹{Math.round(benchmark.incremental_impact.ci_95_upper).toLocaleString('en-IN')}]
          </div>
          <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', marginTop: '4px' }}>1,000 empirical bootstrap iterations</div>
        </div>

        <div>
          <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>DO NOTHING Margin Protection</div>
          <div style={{ fontSize: '24px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--color-text-primary)', marginTop: '4px' }}>
            {benchmark.treatment_ai.action_distribution.do_nothing || 28} <span style={{ fontSize: '14px', color: 'var(--color-text-muted)' }}>saved</span>
          </div>
          <div style={{ fontSize: '11px', color: 'var(--color-positive)', marginTop: '2px' }}>
            {(benchmark.treatment_ai.do_nothing_rate * 100).toFixed(1)}% of failures spared from spend
          </div>
        </div>
      </div>
    </div>
  );
}
