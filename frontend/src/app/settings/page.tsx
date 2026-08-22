'use client';

import React, { useState } from 'react';
import { Settings, ShieldCheck, Key, Webhook, Bell, Save, CheckCircle2, Building2 } from 'lucide-react';

export default function SettingsPage() {
  const [saved, setSaved] = useState(false);
  const [merchantName, setMerchantName] = useState('Apex Direct D2C Retailers Pvt Ltd');
  const [keyId, setKeyId] = useState('rzp_test_1DP5mmOlF5G5ag');
  const [keySecret, setKeySecret] = useState('••••••••••••••••••••••••');
  const [webhookSecret, setWebhookSecret] = useState('rio_whsec_test_live_sandbox_99');
  const [webhookUrl, setWebhookUrl] = useState('https://api.rio-fintech.internal/api/webhooks/razorpay');

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', maxWidth: '900px' }}>
      {/* Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="badge badge-gold">SYSTEM</span>
          <h1 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--color-text-primary)' }}>
            Merchant & Gateway Settings
          </h1>
        </div>
        <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
          Configure Razorpay API credentials, webhook verification keys, and operational parameters.
        </p>
      </div>

      {saved && (
        <div style={{ padding: '12px 16px', borderRadius: '4px', backgroundColor: 'var(--color-recovery-bg)', border: '1px solid var(--color-recovery-border)', color: 'var(--color-recovery)', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CheckCircle2 size={16} />
          <span>Gateway credentials and webhook configurations updated successfully.</span>
        </div>
      )}

      <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {/* Merchant Profile */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">Merchant Identity</div>
            <Building2 size={16} color="var(--color-text-muted)" />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '11.5px', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Business Entity Legal Name
              </label>
              <input
                type="text"
                value={merchantName}
                onChange={(e) => setMerchantName(e.target.value)}
                style={{ width: '100%' }}
              />
            </div>
          </div>
        </div>

        {/* Razorpay Integration */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Razorpay Test Mode Integration</div>
              <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                Authenticated against official Razorpay Test Mode endpoints
              </div>
            </div>
            <span className="badge badge-recovery">Connected</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '11.5px', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Key ID
              </label>
              <input
                type="text"
                value={keyId}
                onChange={(e) => setKeyId(e.target.value)}
                style={{ width: '100%', fontFamily: 'var(--font-mono)' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '11.5px', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Key Secret
              </label>
              <input
                type="password"
                value={keySecret}
                onChange={(e) => setKeySecret(e.target.value)}
                style={{ width: '100%', fontFamily: 'var(--font-mono)' }}
              />
            </div>
          </div>
        </div>

        {/* Webhook Configuration */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Webhook Signature & Ingestion</div>
              <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                HMAC-SHA256 signature verification and idempotency deduplication
              </div>
            </div>
            <Webhook size={16} color="var(--color-text-muted)" />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '11.5px', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Webhook Secret
              </label>
              <input
                type="text"
                value={webhookSecret}
                onChange={(e) => setWebhookSecret(e.target.value)}
                style={{ width: '100%', fontFamily: 'var(--font-mono)' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '11.5px', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Receiver Endpoint URL
              </label>
              <input
                type="text"
                value={webhookUrl}
                onChange={(e) => setWebhookUrl(e.target.value)}
                style={{ width: '100%', fontFamily: 'var(--font-mono)' }}
              />
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button type="submit" className="btn btn-gold" style={{ padding: '8px 20px', fontSize: '13px' }}>
            <Save size={14} />
            <span>Save Configuration</span>
          </button>
        </div>
      </form>
    </div>
  );
}
