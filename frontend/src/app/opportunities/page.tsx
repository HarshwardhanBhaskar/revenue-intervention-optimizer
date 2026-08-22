'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { Search, Filter, ArrowUpDown, ChevronRight, Eye, Sparkles, RefreshCw } from 'lucide-react';

export default function OpportunitiesPage() {
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterAction, setFilterAction] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const fetchOpps = () => {
    setLoading(true);
    let url = '/api/opportunities?per_page=50';
    if (filterAction) url += `&action=${filterAction}`;
    if (filterStatus) url += `&status=${filterStatus}`;

    fetch(url)
      .then((res) => res.json())
      .then((data) => {
        if (data.opportunities) setOpportunities(data.opportunities);
        setLoading(false);
      })
      .catch((err) => {
        console.log('Error fetching opps', err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchOpps();
  }, [filterAction, filterStatus]);

  const filteredOpps = opportunities.filter((o) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      o.customer?.external_id?.toLowerCase().includes(q) ||
      o.payment?.failure_reason?.toLowerCase().includes(q) ||
      o.recommended_action?.toLowerCase().includes(q)
    );
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 style={{ fontSize: '20px', fontWeight: 700, letterSpacing: '-0.02em', color: 'var(--color-text-primary)' }}>
            Recovery Opportunities Ledger
          </h1>
          <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
            Full transaction-level financial diagnosis, uplift predictions, and safety policy status.
          </p>
        </div>

        <button onClick={fetchOpps} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '12px' }}>
          <RefreshCw size={13} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filter Controls Bar */}
      <div
        className="card"
        style={{
          padding: '12px 16px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: '12px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1 }}>
          <div style={{ position: 'relative', width: '280px' }}>
            <Search size={14} color="var(--color-text-muted)" style={{ position: 'absolute', left: '10px', top: '11px' }} />
            <input
              type="text"
              placeholder="Search by customer, reason, or action..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ width: '100%', paddingLeft: '32px' }}
            />
          </div>

          {/* Action Filter */}
          <select
            value={filterAction}
            onChange={(e) => setFilterAction(e.target.value)}
            style={{ width: '170px' }}
          >
            <option value="">All Actions</option>
            <option value="do_nothing">DO NOTHING</option>
            <option value="retry">Auto Retry</option>
            <option value="payment_link">Payment Link</option>
            <option value="reminder">Reminder</option>
            <option value="discount">Targeted Discount (5%)</option>
          </select>

          {/* Status Filter */}
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            style={{ width: '170px' }}
          >
            <option value="">All Workflow States</option>
            <option value="pending_approval">Pending Approval</option>
            <option value="executing">Executing / Dispatched</option>
            <option value="recovered">Recovered (Won Back)</option>
            <option value="blocked">Policy Blocked</option>
            <option value="failed">Failed / Expired</option>
          </select>
        </div>

        <div style={{ fontSize: '12px', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
          Showing <span style={{ color: 'var(--color-text-primary)', fontWeight: 600 }}>{filteredOpps.length}</span> failures
        </div>
      </div>

      {/* Opportunities Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table>
          <thead>
            <tr>
              <th>Detected</th>
              <th>Customer</th>
              <th>Order Amount</th>
              <th>Payment Failure</th>
              <th>Recommended Action</th>
              <th>Uplift (Base → Rec)</th>
              <th>Expected Net Yield</th>
              <th>Policy Status</th>
              <th>State</th>
              <th>Inspect</th>
            </tr>
          </thead>
          <tbody>
            {filteredOpps.map((opp, idx) => (
              <tr key={idx}>
                <td style={{ fontSize: '11px', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
                  {opp.detected_at ? new Date(opp.detected_at).toLocaleDateString('en-IN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : 'Recent'}
                </td>
                <td>
                  <div style={{ fontWeight: 600 }}>{opp.customer?.external_id || 'cust_anonymous'}</div>
                  <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', textTransform: 'capitalize' }}>
                    {opp.customer?.segment} • {Math.round((opp.customer?.recovery_rate || 0.3) * 100)}% historical
                  </div>
                </td>
                <td className="font-mono" style={{ fontWeight: 600 }}>
                  ₹{Number(opp.amount_rupees || (opp.amount_paise / 100)).toLocaleString('en-IN')}
                </td>
                <td>
                  <div style={{ textTransform: 'capitalize' }}>{opp.payment?.failure_reason?.replace('_', ' ') || 'Network error'}</div>
                  <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>
                    {opp.payment?.method || 'UPI'}
                  </div>
                </td>
                <td>
                  <span
                    className={`badge ${
                      opp.recommended_action === 'do_nothing'
                        ? 'badge-muted'
                        : opp.recommended_action === 'discount'
                        ? 'badge-warning'
                        : 'badge-positive'
                    }`}
                  >
                    {opp.recommended_action?.replace('_', ' ')}
                  </span>
                </td>
                <td className="font-mono" style={{ fontSize: '12px' }}>
                  <span style={{ color: 'var(--color-text-muted)' }}>{Math.round((opp.baseline_probability || 0.3) * 100)}%</span>
                  <span style={{ color: 'var(--color-text-dim)', margin: '0 4px' }}>→</span>
                  <span style={{ color: 'var(--color-positive)', fontWeight: 600 }}>
                    {Math.round((opp.recommended_probability || 0.7) * 100)}%
                  </span>
                </td>
                <td className="font-mono" style={{ fontWeight: 600, color: (opp.expected_incremental_value_paise || 0) > 0 ? 'var(--color-positive)' : 'var(--color-text-muted)' }}>
                  +₹{Math.round((opp.expected_incremental_value_paise || 0) / 100).toLocaleString('en-IN')}
                </td>
                <td>
                  <span className={`badge ${opp.policy_result === 'requires_human' ? 'badge-warning' : opp.policy_result === 'blocked' ? 'badge-negative' : 'badge-positive'}`}>
                    {opp.policy_result?.replace('_', ' ') || 'approved'}
                  </span>
                </td>
                <td>
                  <span className={`badge ${opp.workflow_state === 'recovered' ? 'badge-positive' : opp.workflow_state === 'pending_approval' ? 'badge-warning' : 'badge-muted'}`}>
                    {opp.workflow_state?.replace('_', ' ')}
                  </span>
                </td>
                <td>
                  <Link href={`/opportunities/${opp.id}`} className="btn btn-secondary" style={{ padding: '4px 8px', fontSize: '11px' }}>
                    <Eye size={12} />
                    <span>Inspect</span>
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
