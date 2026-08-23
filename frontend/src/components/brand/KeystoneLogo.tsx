'use client';

import React from 'react';
import Image from 'next/image';

interface KeystoneLogoProps {
  size?: number;
  className?: string;
  showText?: boolean;
  textSize?: 'sm' | 'md' | 'lg';
}

export default function KeystoneLogo({
  size = 32,
  className = '',
  showText = false,
  textSize = 'md',
}: KeystoneLogoProps) {
  return (
    <div className={`flex items-center gap-3 ${className}`} style={{ display: 'inline-flex', alignItems: 'center' }}>
      <div
        style={{
          width: `${size}px`,
          height: `${size}px`,
          position: 'relative',
          flexShrink: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          filter: 'drop-shadow(0 2px 8px rgba(194, 155, 39, 0.25))',
        }}
      >
        <img
          src="/rio_logo.png"
          alt="RIO Keystone Shield Logo"
          width={size}
          height={size}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'contain',
            display: 'block',
          }}
        />
      </div>

      {showText && (
        <div>
          <div
            style={{
              fontSize: textSize === 'lg' ? '18px' : textSize === 'md' ? '14px' : '12px',
              fontWeight: 800,
              letterSpacing: '-0.02em',
              color: 'var(--color-text-primary, #1C1917)',
              lineHeight: 1.1,
              fontFamily: 'var(--font-serif, Georgia, serif)',
            }}
          >
            RIO <span style={{ fontWeight: 400, color: 'var(--color-text-muted, #78716C)', fontSize: '11px', fontFamily: 'var(--font-mono, monospace)', letterSpacing: '0.05em' }}>FINTECH</span>
          </div>
          <div
            style={{
              fontSize: '10px',
              color: 'var(--color-text-muted, #78716C)',
              fontFamily: 'var(--font-mono, monospace)',
              letterSpacing: '0.04em',
              textTransform: 'uppercase',
            }}
          >
            Revenue Intervention Optimizer
          </div>
        </div>
      )}
    </div>
  );
}
