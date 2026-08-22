'use client';

import React from 'react';

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
      <svg
        width={size}
        height={size}
        viewBox="0 0 120 120"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{ flexShrink: 0 }}
      >
        <defs>
          {/* Champagne Gold Gradients */}
          <linearGradient id="goldTop" x1="20" y1="15" x2="100" y2="45" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#F5E6BE" />
            <stop offset="50%" stopColor="#D4AF37" />
            <stop offset="100%" stopColor="#AA820A" />
          </linearGradient>

          <linearGradient id="goldFacetLeft" x1="20" y1="20" x2="60" y2="48" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#DFC377" />
            <stop offset="100%" stopColor="#9C781A" />
          </linearGradient>

          <linearGradient id="goldFacetRight" x1="100" y1="20" x2="60" y2="48" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#FFF2D1" />
            <stop offset="100%" stopColor="#C29B27" />
          </linearGradient>

          {/* Emerald & Obsidian Facet Gradients */}
          <linearGradient id="emeraldShieldLeft" x1="15" y1="45" x2="60" y2="105" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#0F766E" />
            <stop offset="50%" stopColor="#064E3B" />
            <stop offset="100%" stopColor="#022C22" />
          </linearGradient>

          <linearGradient id="emeraldShieldRight" x1="105" y1="45" x2="60" y2="105" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#10B981" />
            <stop offset="50%" stopColor="#059669" />
            <stop offset="100%" stopColor="#047857" />
          </linearGradient>

          <linearGradient id="coreGoldFacet" x1="40" y1="50" x2="80" y2="90" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#F9E29D" />
            <stop offset="100%" stopColor="#B38715" />
          </linearGradient>

          {/* Subtle Ambient Glow */}
          <filter id="keystoneGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="4" stdDeviation="6" floodColor="#C29B27" floodOpacity="0.25" />
          </filter>
        </defs>

        <g filter="url(#keystoneGlow)">
          {/* --- TOP KEYSTONE CREST --- */}
          {/* Top Left Keystone Wing */}
          <polygon points="22,22 60,38 60,18 28,15" fill="url(#goldFacetLeft)" />
          {/* Top Right Keystone Wing */}
          <polygon points="98,22 60,38 60,18 92,15" fill="url(#goldFacetRight)" />
          {/* Top Center Keystone Bevel */}
          <polygon points="28,15 60,18 92,15 60,26" fill="url(#goldTop)" opacity="0.9" />

          {/* --- LOWER FACETED SHIELD BODY --- */}
          {/* Left Obsidian/Emerald Flank */}
          <polygon points="16,42 50,48 38,82 16,56" fill="url(#emeraldShieldLeft)" />
          {/* Right Emerald Shield Flank */}
          <polygon points="104,42 70,48 82,82 104,56" fill="url(#emeraldShieldRight)" />
          
          {/* Center Lower Shield Base */}
          <polygon points="38,82 60,108 82,82 60,66" fill="#064E3B" />
          <polygon points="60,66 82,82 60,108" fill="#047857" />
          <polygon points="38,82 60,108 60,95" fill="#022C22" />

          {/* --- CENTRAL GOLDEN RECOVERY KEYSTONE --- */}
          <polygon points="38,44 82,44 60,86" fill="url(#coreGoldFacet)" />
          {/* Subtle inner facet line */}
          <polygon points="60,44 82,44 60,86" fill="url(#goldFacetRight)" opacity="0.65" />

          {/* Precision Micro Delta Inset */}
          <polygon points="50,50 70,50 60,68" fill="#1C1917" />
          <polygon points="53,53 67,53 60,64" fill="url(#goldTop)" />
        </g>
      </svg>

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
