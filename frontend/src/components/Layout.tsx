'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Coins,
  FlaskConical,
  Sliders,
  ShieldCheck,
  ClipboardList,
  AlertOctagon,
  Sparkles,
  Layers,
  ArrowUpRight,
  Building2,
  CheckCircle2,
  Settings,
  Bot,
  LogOut,
  ExternalLink,
} from 'lucide-react';
import AIAssistantModal from './AIAssistantModal';
import KeystoneLogo from './brand/KeystoneLogo';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const pathname = usePathname();
  const [isAssistantOpen, setIsAssistantOpen] = useState(false);

  // If on landing or login, render without dashboard sidebar
  const isMarketingPage = pathname === '/' || pathname === '/login';

  if (isMarketingPage) {
    return <>{children}</>;
  }

  const navItems = [
    { label: 'Overview', href: '/overview', icon: LayoutDashboard },
    { label: 'Opportunities', href: '/recovery', icon: Coins },
    { label: 'Decision Lab', href: '/decision-lab', icon: FlaskConical, badge: 'Signature' },
    { label: 'Experiments', href: '/experiments', icon: Layers },
    { label: 'Approval Queue', href: '/approvals', icon: ShieldCheck, badge: '3' },
    { label: 'Exceptions', href: '/exceptions', icon: AlertOctagon },
    { label: 'Policy Center', href: '/policies', icon: Sliders },
    { label: 'Audit Log', href: '/audit', icon: ClipboardList },
    { label: 'AI Analyst', href: '/analyst', icon: Bot },
    { label: 'Settings', href: '/settings', icon: Settings },
  ];

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: 'var(--color-bg)' }}>
      {/* Editorial Financial Sidebar */}
      <aside
        style={{
          width: '236px',
          backgroundColor: 'var(--color-surface)',
          borderRight: '1px solid var(--color-border)',
          display: 'flex',
          flexDirection: 'column',
          position: 'fixed',
          top: 0,
          bottom: 0,
          left: 0,
          zIndex: 40,
        }}
      >
        {/* Brand Header */}
        <Link
          href="/"
          style={{
            padding: '18px 20px',
            borderBottom: '1px solid var(--color-border)',
            display: 'flex',
            alignItems: 'center',
            textDecoration: 'none',
          }}
        >
          <KeystoneLogo size={30} showText={true} />
        </Link>

        {/* Navigation Section */}
        <nav style={{ flex: 1, padding: '16px 10px', overflowY: 'auto' }}>
          <div
            style={{
              fontSize: '9.5px',
              fontWeight: 700,
              color: 'var(--color-text-muted)',
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              padding: '6px 12px 8px',
            }}
          >
            Revenue Operations
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || (item.href !== '/overview' && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '8px 12px',
                    borderRadius: '4px',
                    fontSize: '12.5px',
                    fontWeight: isActive ? 600 : 500,
                    color: isActive ? 'var(--color-text-primary)' : 'var(--color-text-secondary)',
                    backgroundColor: isActive ? 'var(--color-surface-2)' : 'transparent',
                    border: isActive ? '1px solid var(--color-border)' : '1px solid transparent',
                    transition: 'all 0.1s ease',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <Icon size={15} color={isActive ? 'var(--color-gold)' : 'var(--color-text-muted)'} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span
                      style={{
                        fontSize: '9px',
                        padding: '1px 6px',
                        borderRadius: '3px',
                        fontFamily: 'var(--font-mono)',
                        fontWeight: 600,
                        backgroundColor: item.badge === 'Signature' ? 'var(--color-gold-bg)' : 'var(--color-warning-bg)',
                        color: item.badge === 'Signature' ? 'var(--color-gold-text)' : 'var(--color-warning)',
                        border: `1px solid ${item.badge === 'Signature' ? 'var(--color-gold-border)' : 'var(--color-warning-border)'}`,
                      }}
                    >
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </div>
        </nav>

        {/* AI Quick Launcher Button */}
        <div style={{ padding: '12px 14px', borderTop: '1px solid var(--color-border)', backgroundColor: 'var(--color-surface-2)' }}>
          <button
            onClick={() => setIsAssistantOpen(true)}
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '8px 10px',
              borderRadius: '4px',
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              color: 'var(--color-text-primary)',
              fontSize: '11.5px',
              fontWeight: 500,
              cursor: 'pointer',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={14} color="var(--color-gold)" />
              <span>Grounded AI Analyst</span>
            </div>
            <span style={{ fontSize: '10px', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>⌘K</span>
          </button>
        </div>

        {/* Merchant Indicator & Landing Link */}
        <div
          style={{
            padding: '14px 16px',
            borderTop: '1px solid var(--color-border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: 0 }}>
            <Building2 size={15} color="var(--color-text-muted)" />
            <div style={{ minWidth: 0 }}>
              <div style={{ fontSize: '11.5px', fontWeight: 600, color: 'var(--color-text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                Apex Direct D2C
              </div>
              <div style={{ fontSize: '9.5px', color: 'var(--color-recovery)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span style={{ width: '5px', height: '5px', borderRadius: '50%', backgroundColor: 'var(--color-recovery)' }}></span>
                Razorpay Test Mode
              </div>
            </div>
          </div>
          <Link href="/" title="View Marketing Site" style={{ color: 'var(--color-text-muted)' }}>
            <ExternalLink size={13} />
          </Link>
        </div>
      </aside>

      {/* Main Content Area */}
      <div style={{ flex: 1, marginLeft: '236px', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        {/* Top Operational Bar */}
        <header
          style={{
            height: '52px',
            backgroundColor: 'var(--color-surface)',
            borderBottom: '1px solid var(--color-border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 28px',
            position: 'sticky',
            top: 0,
            zIndex: 30,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
              BUILDATHON TRACK 03: <span style={{ color: 'var(--color-text-primary)', fontWeight: 600 }}>AI REVENUE RECOVERY</span>
            </div>
            <span style={{ color: 'var(--color-border)' }}>|</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11.5px', color: 'var(--color-recovery)', fontFamily: 'var(--font-mono)' }}>
              <CheckCircle2 size={13} />
              <span>Deterministic Guardrails Active</span>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Link
              href="/decision-lab"
              className="btn btn-secondary"
              style={{ padding: '5px 10px', fontSize: '11.5px', fontFamily: 'var(--font-mono)' }}
            >
              <FlaskConical size={13} color="var(--color-gold)" />
              <span>Decision Lab</span>
            </Link>

            <button
              onClick={() => setIsAssistantOpen(true)}
              className="btn btn-gold"
              style={{ padding: '5px 12px', fontSize: '11.5px' }}
            >
              <Sparkles size={13} />
              <span>Ask Analyst</span>
            </button>
          </div>
        </header>

        {/* Page Content Body */}
        <main style={{ flex: 1, padding: '28px' }}>{children}</main>
      </div>

      {/* Floating AI Analytics Modal */}
      {isAssistantOpen && <AIAssistantModal onClose={() => setIsAssistantOpen(false)} />}
    </div>
  );
}
