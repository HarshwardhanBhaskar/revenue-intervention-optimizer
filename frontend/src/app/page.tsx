'use client';

import React, { useEffect, useRef } from 'react';
import Link from 'next/link';
import {
  ArrowRight,
  ShieldCheck,
  TrendingUp,
  FlaskConical,
  Scale,
  Sparkles,
  Layers,
  CheckCircle2,
  Lock,
  FileSpreadsheet,
  Building2,
  ChevronRight,
} from 'lucide-react';
import KeystoneLogo from '@/components/brand/KeystoneLogo';

export default function LandingPage() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // Subtle ambient particle / dither background on landing hero
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let width = (canvas.width = canvas.parentElement?.clientWidth || 800);
    let height = (canvas.height = canvas.parentElement?.clientHeight || 400);

    const particles: Array<{ x: number; y: number; vx: number; vy: number; radius: number; alpha: number }> = [];
    const particleCount = 28;

    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.25,
        vy: (Math.random() - 0.5) * 0.25,
        radius: Math.random() * 1.5 + 0.5,
        alpha: Math.random() * 0.4 + 0.1,
      });
    }

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // Subtle architectural grid background
      ctx.strokeStyle = 'rgba(194, 155, 39, 0.04)';
      ctx.lineWidth = 1;
      const gridSize = 40;
      for (let x = 0; x < width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y < height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // Draw ambient particles
      particles.forEach((p) => {
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0) p.x = width;
        if (p.x > width) p.x = 0;
        if (p.y < 0) p.y = height;
        if (p.y > height) p.y = 0;

        ctx.fillStyle = `rgba(194, 155, 39, ${p.alpha})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fill();
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    const handleResize = () => {
      if (!canvas || !canvas.parentElement) return;
      width = canvas.width = canvas.parentElement.clientWidth;
      height = canvas.height = canvas.parentElement.clientHeight;
    };

    window.addEventListener('resize', handleResize);
    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <div style={{ backgroundColor: 'var(--color-bg)', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Editorial Navbar */}
      <header
        style={{
          borderBottom: '1px solid var(--color-border)',
          backgroundColor: 'rgba(249, 248, 246, 0.9)',
          backdropFilter: 'blur(8px)',
          position: 'sticky',
          top: 0,
          zIndex: 50,
          padding: '0 40px',
          height: '64px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <KeystoneLogo size={34} showText={true} />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
          <nav style={{ display: 'flex', gap: '20px', fontSize: '13px', color: 'var(--color-text-secondary)' }}>
            <a href="#thesis" style={{ transition: 'color 0.1s ease' }}>Thesis</a>
            <a href="#loop" style={{ transition: 'color 0.1s ease' }}>Core Loop</a>
            <a href="#benchmarks" style={{ transition: 'color 0.1s ease' }}>Empirical Uplift</a>
            <a href="#guardrails" style={{ transition: 'color 0.1s ease' }}>Policy Controls</a>
          </nav>
          <div style={{ display: 'flex', gap: '10px' }}>
            <Link href="/login" className="btn btn-secondary" style={{ padding: '6px 14px', fontSize: '12px' }}>
              Sign In
            </Link>
            <Link href="/overview" className="btn btn-gold" style={{ padding: '6px 16px', fontSize: '12px' }}>
              <span>Launch Control Center</span>
              <ArrowRight size={13} />
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section
        style={{
          position: 'relative',
          padding: '80px 40px 60px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center',
          overflow: 'hidden',
          borderBottom: '1px solid var(--color-border)',
        }}
      >
        <canvas
          ref={canvasRef}
          style={{
            position: 'absolute',
            inset: 0,
            width: '100%',
            height: '100%',
            pointerEvents: 'none',
            zIndex: 1,
          }}
        />

        <div style={{ position: 'relative', zIndex: 2, maxWidth: '840px' }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '3px 10px',
              borderRadius: '20px',
              backgroundColor: 'var(--color-gold-bg)',
              border: '1px solid var(--color-gold-border)',
              color: 'var(--color-gold-text)',
              fontSize: '11px',
              fontFamily: 'var(--font-mono)',
              fontWeight: 600,
              marginBottom: '20px',
            }}
          >
            <Sparkles size={12} color="var(--color-gold)" />
            <span>AI REVENUE RECOVERY • FINTECH INTELLIGENCE</span>
          </div>

          <h1
            className="font-serif"
            style={{
              fontSize: '48px',
              lineHeight: 1.15,
              fontWeight: 400,
              letterSpacing: '-0.02em',
              color: 'var(--color-text-primary)',
              marginBottom: '20px',
            }}
          >
            Recover the revenue <br />
            <span style={{ fontStyle: 'italic', color: 'var(--color-gold)' }}>worth recovering</span>.
          </h1>

          <p
            style={{
              fontSize: '16px',
              lineHeight: 1.6,
              color: 'var(--color-text-secondary)',
              maxWidth: '680px',
              margin: '0 auto 32px',
            }}
          >
            Traditional recovery systems ask <em>&quot;Will this customer pay?&quot;</em> and spam reminders.
            RIO asks <strong>&quot;Will this customer pay BECAUSE OF this intervention, and is it economically worthwhile?&quot;</strong>
            treating <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--color-text-primary)' }}>DO NOTHING</span> as an optimal, first-class financial decision.
          </p>

          <div style={{ display: 'flex', justifyContent: 'center', gap: '14px' }}>
            <Link href="/overview" className="btn btn-gold" style={{ padding: '10px 24px', fontSize: '13px' }}>
              <span>Enter Operational Dashboard</span>
              <ArrowRight size={14} />
            </Link>
            <Link href="/decision-lab" className="btn btn-secondary" style={{ padding: '10px 20px', fontSize: '13px', fontFamily: 'var(--font-mono)' }}>
              <FlaskConical size={14} color="var(--color-gold)" />
              <span>Explore Decision Lab</span>
            </Link>
          </div>
        </div>
      </section>

      {/* Financial Impact Numbers Bar */}
      <section
        id="benchmarks"
        style={{
          backgroundColor: 'var(--color-surface)',
          borderBottom: '1px solid var(--color-border)',
          padding: '36px 40px',
        }}
      >
        <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '28px' }}>
            <div>
              <div style={{ fontSize: '10.5px', fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                Incremental Net Uplift
              </div>
              <div style={{ fontSize: '28px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--color-recovery)', marginTop: '4px' }}>
                +15.7%
              </div>
              <div style={{ fontSize: '11.5px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                vs standard retry heuristics
              </div>
            </div>

            <div>
              <div style={{ fontSize: '10.5px', fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                Net Recovered Value
              </div>
              <div style={{ fontSize: '28px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--color-text-primary)', marginTop: '4px' }}>
                ₹27.38 Lakh
              </div>
              <div style={{ fontSize: '11.5px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                Across ₹42.38L test set at risk
              </div>
            </div>

            <div>
              <div style={{ fontSize: '10.5px', fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                DO NOTHING Frequency
              </div>
              <div style={{ fontSize: '28px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--color-gold-text)', marginTop: '4px' }}>
                5.2%
              </div>
              <div style={{ fontSize: '11.5px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                Zero margin spend on natural recoveries
              </div>
            </div>

            <div>
              <div style={{ fontSize: '10.5px', fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                Safety Enforcement
              </div>
              <div style={{ fontSize: '28px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--color-text-primary)', marginTop: '4px' }}>
                100%
              </div>
              <div style={{ fontSize: '11.5px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                Deterministic backend policy checks
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* The Core Operational Loop */}
      <section
        id="loop"
        style={{
          padding: '60px 40px',
          maxWidth: '1100px',
          margin: '0 auto',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <span className="badge badge-gold" style={{ marginBottom: '8px' }}>FINTECH ARCHITECTURE</span>
          <h2 className="font-serif" style={{ fontSize: '32px', fontWeight: 400, color: 'var(--color-text-primary)' }}>
            The 11-Stage Recovery Loop
          </h2>
          <p style={{ fontSize: '14px', color: 'var(--color-text-secondary)', maxWidth: '580px', margin: '8px auto 0' }}>
            Every payment failure moves through a bounded, explainable, and mathematically auditable pipeline.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
          {[
            { step: '01', name: 'DETECT & INGEST', desc: 'HMAC signature verification and idempotency deduplication of Razorpay failure webhooks.' },
            { step: '02', name: 'PREDICT UPLIFT', desc: 'T-Learner Meta-Learner estimates counterfactual recovery probabilities for all 5 actions.' },
            { step: '03', name: 'DECIDE & RANK', desc: 'Economic net value optimization identifies argmax incremental yield over baseline.' },
            { step: '04', name: 'POLICY CHECK', desc: 'Deterministic rules enforce ₹10k caps, opt-out status, and active dispute blocks.' },
            { step: '05', name: 'HUMAN APPROVAL', desc: 'High-value transactions route to operator queue for concurrency-safe sign-off.' },
            { step: '06', name: 'SAFE EXECUTE', desc: 'Dispatches Razorpay payment links, retries, or enforces DO NOTHING.' },
            { step: '07', name: 'OBSERVE & MEASURE', desc: 'Tracks actual payment capture vs counterfactual potential outcomes.' },
            { step: '08', name: 'IMMUTABLE AUDIT', desc: 'Every state transition is recorded in an append-only event ledger.' },
          ].map((s, idx) => (
            <div key={idx} className="card" style={{ padding: '18px', backgroundColor: 'var(--color-surface)' }}>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--color-gold)', fontWeight: 700 }}>
                {s.step}
              </div>
              <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-text-primary)', margin: '6px 0 4px' }}>
                {s.name}
              </div>
              <div style={{ fontSize: '11.5px', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
                {s.desc}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer
        style={{
          marginTop: 'auto',
          borderTop: '1px solid var(--color-border)',
          backgroundColor: 'var(--color-surface)',
          padding: '24px 40px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '12px',
          color: 'var(--color-text-muted)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>RIO Fintech</span> • Razorpay AI Buildathon Submission
        </div>
        <div style={{ display: 'flex', gap: '16px' }}>
          <Link href="/overview" style={{ color: 'var(--color-text-secondary)' }}>Dashboard</Link>
          <Link href="/decision-lab" style={{ color: 'var(--color-text-secondary)' }}>Decision Lab</Link>
          <Link href="/audit" style={{ color: 'var(--color-text-secondary)' }}>Audit Trail</Link>
        </div>
      </footer>
    </div>
  );
}
