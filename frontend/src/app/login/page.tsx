'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ArrowRight, ShieldCheck, Lock, Sparkles, Building2 } from 'lucide-react';
import KeystoneLogo from '@/components/brand/KeystoneLogo';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('operations@apex-d2c.com');
  const [password, setPassword] = useState('••••••••••••');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setTimeout(() => {
      router.push('/overview');
    }, 400);
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', minHeight: '100vh', backgroundColor: 'var(--color-bg)' }}>
      {/* Left Editorial Brand Pane */}
      <div
        style={{
          backgroundColor: 'var(--color-surface-2)',
          borderRight: '1px solid var(--color-border)',
          padding: '60px 80px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
        }}
      >
        <Link href="/" style={{ textDecoration: 'none' }}>
          <KeystoneLogo size={38} showText={true} textSize="md" />
        </Link>

        <div style={{ maxWidth: '460px' }}>
          <span className="badge badge-gold" style={{ marginBottom: '14px' }}>
            OPERATIONAL AUTHENTICATION
          </span>
          <h2
            className="font-serif"
            style={{
              fontSize: '36px',
              lineHeight: 1.2,
              fontWeight: 400,
              color: 'var(--color-text-primary)',
              marginBottom: '16px',
            }}
          >
            Financial intelligence bounded by deterministic policy.
          </h2>
          <p style={{ fontSize: '14px', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
            Every action dispatched is logged in the append-only ledger. Operator approvals, discount caps, and opt-out rules are enforced server-side.
          </p>

          <div style={{ marginTop: '28px', display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '12px', color: 'var(--color-text-secondary)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldCheck size={15} color="var(--color-recovery)" />
              <span>Razorpay Test Mode Client Certified</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldCheck size={15} color="var(--color-recovery)" />
              <span>HMAC-SHA256 Cryptographic Webhook Deduplication</span>
            </div>
          </div>
        </div>

        <div style={{ fontSize: '11.5px', color: 'var(--color-text-muted)' }}>
          Razorpay AI Buildathon 2026 • Track 03 Submission
        </div>
      </div>

      {/* Right Login Form Pane */}
      <div style={{ padding: '60px', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
        <div style={{ width: '100%', maxWidth: '360px' }}>
          <h1 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--color-text-primary)' }}>
            Merchant Sign In
          </h1>
          <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginTop: '4px', marginBottom: '24px' }}>
            Access Apex Direct D2C live recovery ledger
          </p>

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '11.5px', fontWeight: 600, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '6px' }}>
                Operator Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={{ width: '100%' }}
                required
              />
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <label style={{ fontSize: '11.5px', fontWeight: 600, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  Password
                </label>
                <span style={{ fontSize: '11px', color: 'var(--color-gold-text)', cursor: 'pointer' }}>Reset</span>
              </div>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{ width: '100%' }}
                required
              />
            </div>

            <button
              type="submit"
              className="btn btn-gold"
              style={{ width: '100%', padding: '9px', marginTop: '8px', fontSize: '13px' }}
              disabled={submitting}
            >
              <span>{submitting ? 'Authenticating...' : 'Sign In to Operations'}</span>
              <ArrowRight size={14} />
            </button>
          </form>

          <div style={{ marginTop: '24px', padding: '12px', borderRadius: '4px', backgroundColor: 'var(--color-surface-2)', border: '1px solid var(--color-border)', fontSize: '11px', color: 'var(--color-text-muted)' }}>
            <div style={{ fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: '2px' }}>Demo Credentials:</div>
            Pre-authenticated with active demo merchant context. Click Sign In to proceed directly.
          </div>
        </div>
      </div>
    </div>
  );
}
