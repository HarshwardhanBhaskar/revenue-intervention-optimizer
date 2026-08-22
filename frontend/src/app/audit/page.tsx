'use client';

import React, { useEffect, useState } from 'react';
import { ClipboardList, Filter, Search, Terminal, ArrowRight, ShieldCheck, RefreshCw } from 'lucide-react';

export default function AuditPage() {
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState('');
  const [selectedEvent, setSelectedEvent] = useState<any>(null);

  const fetchAudit = () => {
    setLoading(true);
    let url = '/api/audit?per_page=50';
    if (filterType) url += `&event_type=${filterType}`;

    fetch(url)
      .then((res) => res.json())
      .then((data) => {
        if (data.events) setEvents(data.events);
        setLoading(false);
      })
      .catch((err) => {
        console.log('Error loading audit log', err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchAudit();
  }, [filterType]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '1200px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="badge badge-positive">Immutable Ledger</span>
            <h1 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--color-text-primary)' }}>
              Audit & Governance Event Stream
            </h1>
          </div>
          <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
            Append-only record of every workflow state transition, policy check, human approval, and Razorpay execution.
          </p>
        </div>

        <button onClick={fetchAudit} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '12px' }}>
          <RefreshCw size={13} />
          <span>Refresh Log</span>
        </button>
      </div>

      {/* Filter Bar */}
      <div className="card" style={{ padding: '12px 16px', display: 'flex', gap: '12px', alignItems: 'center' }}>
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          style={{ width: '220px' }}
        >
          <option value="">All Event Types</option>
          <option value="recovery.detected">recovery.detected</option>
          <option value="recovery.recommended">recovery.recommended</option>
          <option value="recovery.executed">recovery.executed</option>
          <option value="recovery.completed">recovery.completed</option>
          <option value="recovery.blocked">recovery.blocked</option>
          <option value="policy.updated">policy.updated</option>
        </select>
        <div style={{ fontSize: '12px', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
          Showing {events.length} immutable events
        </div>
      </div>

      {/* Main Audit Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: selectedEvent ? '1.5fr 1fr' : '1fr', gap: '20px' }}>
        {/* Events Table */}
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table>
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Event Type</th>
                <th>Actor</th>
                <th>Workflow ID</th>
                <th>Transition</th>
                <th>Reason</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {events.map((evt, idx) => (
                <tr
                  key={idx}
                  onClick={() => setSelectedEvent(evt)}
                  style={{
                    cursor: 'pointer',
                    backgroundColor: selectedEvent?.id === evt.id ? 'var(--color-surface-hover)' : 'transparent',
                  }}
                >
                  <td style={{ fontSize: '11px', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)', whiteSpace: 'nowrap' }}>
                    {evt.created_at ? new Date(evt.created_at).toLocaleTimeString('en-IN', { hour12: false }) : 'now'}
                  </td>
                  <td>
                    <span className="badge badge-info" style={{ textTransform: 'none' }}>
                      {evt.event_type}
                    </span>
                  </td>
                  <td>
                    <span style={{ fontSize: '11px', color: 'var(--color-text-secondary)', fontFamily: 'var(--font-mono)' }}>
                      {evt.actor}
                    </span>
                  </td>
                  <td style={{ fontSize: '11px', fontFamily: 'var(--font-mono)' }}>
                    {evt.workflow_id ? `#${evt.workflow_id.substring(0, 8)}` : '—'}
                  </td>
                  <td>
                    {evt.new_state ? (
                      <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--color-positive)' }}>
                        {evt.previous_state || 'none'} → {evt.new_state}
                      </span>
                    ) : (
                      '—'
                    )}
                  </td>
                  <td style={{ fontSize: '12px', color: 'var(--color-text-secondary)', maxWidth: '240px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {evt.reason || 'Workflow progress'}
                  </td>
                  <td>
                    <button className="btn btn-secondary" style={{ padding: '2px 6px', fontSize: '10px' }}>
                      JSON
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Selected Event JSON Inspector */}
        {selectedEvent && (
          <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
            <div className="card-header">
              <div className="card-title">Event Payload & Metadata</div>
              <button onClick={() => setSelectedEvent(null)} style={{ color: 'var(--color-text-muted)', fontSize: '12px' }}>
                Close
              </button>
            </div>

            <div style={{ fontSize: '12px', marginBottom: '10px' }}>
              <div style={{ color: 'var(--color-text-muted)' }}>Event ID: <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-text-primary)' }}>{selectedEvent.id}</span></div>
              <div style={{ color: 'var(--color-text-muted)', marginTop: '2px' }}>Event Type: <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-positive)' }}>{selectedEvent.event_type}</span></div>
            </div>

            <pre
              style={{
                flex: 1,
                padding: '12px',
                borderRadius: '6px',
                backgroundColor: 'var(--color-bg)',
                border: '1px solid var(--color-border)',
                fontFamily: 'var(--font-mono)',
                fontSize: '11px',
                overflowX: 'auto',
                color: 'var(--color-text-primary)',
              }}
            >
              {JSON.stringify(selectedEvent.metadata || {}, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
