import React from 'react';
import {
  FiActivity,
  FiAlertTriangle,
  FiArrowDownRight,
  FiArrowUpRight,
  FiCheckCircle,
  FiGlobe,
  FiInfo,
  FiShield,
  FiTarget,
} from 'react-icons/fi';
import { RiFireLine } from 'react-icons/ri';
import { Asset, FactorBreakdown, RiskBand, Vulnerability } from '../types';
import { generateExecutiveVerdict } from '../utils/scoring';
import { Badge, BadgeColor } from './common/Badge';
import { Panel } from './common/Panel';

interface HeroScoreboardProps {
  vuln: Vulnerability;
  asset: Asset;
  breakdown: FactorBreakdown;
}

export const HeroScoreboard: React.FC<HeroScoreboardProps> = ({ vuln, asset, breakdown }) => {
  const verdict = generateExecutiveVerdict(
    vuln.cve_id,
    breakdown,
    asset,
    vuln.risk_band,
    vuln.rank_displacement
  );

  const isEscalated = vuln.rank_displacement > 0;
  const isDeescalated = vuln.rank_displacement < 0;

  const bandBadges: Record<RiskBand, { color: BadgeColor; label: string }> = {
    Critical: { color: 'pink', label: 'CRITICAL' },
    High: { color: 'orange', label: 'HIGH' },
    Medium: { color: 'yellow', label: 'MEDIUM' },
    Low: { color: 'lime', label: 'LOW' },
  };

  return (
    <div className="space-y-4">
      {/* 4-Column Neobrutalist Tactical Metric Blocks */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {/* Metric 1: Standard CVSS Base */}
        <div className="border-2 sm:border-[2.5px] border-black dark:border-white bg-white dark:bg-[#141418] p-3.5 sm:p-4 neo-shadow flex flex-col justify-between">
          <div className="flex items-center justify-between gap-1 mb-2">
            <span className="font-mono font-bold text-[11px] uppercase tracking-wider text-neutral-600 dark:text-neutral-400">
              Vendor CVSS Base
            </span>
            <div className="w-6 h-6 border border-black dark:border-white bg-[#00F0FF] text-black flex items-center justify-center neo-shadow-sm">
              <FiGlobe className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="my-1 flex items-baseline space-x-1.5">
            <span className="font-mono font-black text-3xl sm:text-4xl text-black dark:text-white tracking-tight">
              {vuln.cvss_score.toFixed(1)}
            </span>
            <span className="font-mono text-xs text-neutral-500">/ 10.0</span>
          </div>
          <div className="flex items-center space-x-1.5 pt-2 border-t border-black/10 dark:border-white/10 mt-1">
            <Badge color="zinc" size="xs">
              {vuln.cvss_severity}
            </Badge>
            <span className="text-[10px] font-mono text-neutral-500 dark:text-neutral-400">
              Lab Isolation
            </span>
          </div>
        </div>

        {/* Metric 2: Contextual Risk Score */}
        <div className="border-2 sm:border-[2.5px] border-black dark:border-white bg-[#FFE600] text-black p-3.5 sm:p-4 neo-shadow flex flex-col justify-between">
          <div className="flex items-center justify-between gap-1 mb-2">
            <span className="font-mono font-black text-[11px] uppercase tracking-wider text-black">
              Contextual Risk Score
            </span>
            <div className="w-6 h-6 border border-black bg-black text-[#FFE600] flex items-center justify-center neo-shadow-sm">
              <FiTarget className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="my-1 flex items-baseline space-x-1.5">
            <span className="font-mono font-black text-3xl sm:text-4xl text-black tracking-tight">
              {vuln.risk_score.toFixed(3)}
            </span>
            <span className="font-mono text-xs text-black/70 font-bold">/ 1.000</span>
          </div>
          <div className="flex items-center space-x-1.5 pt-2 border-t border-black/20 mt-1">
            <Badge color={bandBadges[vuln.risk_band].color} size="xs">
              {vuln.risk_band}
            </Badge>
            <span className="text-[10px] font-mono text-black/80 font-bold">
              Multi-Factor Bounded
            </span>
          </div>
        </div>

        {/* Metric 3: CISA KEV Weaponization */}
        <div className="border-2 sm:border-[2.5px] border-black dark:border-white bg-white dark:bg-[#141418] p-3.5 sm:p-4 neo-shadow flex flex-col justify-between">
          <div className="flex items-center justify-between gap-1 mb-2">
            <span className="font-mono font-bold text-[11px] uppercase tracking-wider text-neutral-600 dark:text-neutral-400">
              CISA KEV Weaponization
            </span>
            <div
              className={`w-6 h-6 border border-black dark:border-white flex items-center justify-center neo-shadow-sm ${
                vuln.in_kev ? 'bg-[#FF5376] text-white' : 'bg-[#B8FF00] text-black'
              }`}
            >
              {vuln.in_kev ? <RiFireLine className="w-3.5 h-3.5" /> : <FiShield className="w-3.5 h-3.5" />}
            </div>
          </div>
          <div className="my-1">
            <span
              className={`font-mono font-black text-lg sm:text-xl uppercase tracking-tight block truncate ${
                vuln.in_kev ? 'text-[#FF5376] dark:text-[#FB7185]' : 'text-emerald-700 dark:text-emerald-400'
              }`}
            >
              {vuln.in_kev ? 'WEAPONIZED IN WILD' : 'NO KNOWN EXPLOIT'}
            </span>
          </div>
          <div className="flex items-center space-x-1.5 pt-2 border-t border-black/10 dark:border-white/10 mt-1">
            <Badge color={vuln.in_kev ? 'pink' : 'lime'} size="xs" dot>
              {vuln.in_kev ? 'ACTIVE ATTACK' : 'BENIGN THREAT'}
            </Badge>
          </div>
        </div>

        {/* Metric 4: Priority Queue Displacement */}
        <div className="border-2 sm:border-[2.5px] border-black dark:border-white bg-white dark:bg-[#141418] p-3.5 sm:p-4 neo-shadow flex flex-col justify-between">
          <div className="flex items-center justify-between gap-1 mb-2">
            <span className="font-mono font-bold text-[11px] uppercase tracking-wider text-neutral-600 dark:text-neutral-400">
              Queue Displacement
            </span>
            <div
              className={`w-6 h-6 border border-black dark:border-white flex items-center justify-center neo-shadow-sm ${
                isEscalated
                  ? 'bg-[#FF5376] text-white'
                  : isDeescalated
                  ? 'bg-[#00F0FF] text-black'
                  : 'bg-neutral-200 text-black'
              }`}
            >
              {isEscalated ? (
                <FiArrowUpRight className="w-4 h-4 stroke-[3]" />
              ) : isDeescalated ? (
                <FiArrowDownRight className="w-4 h-4 stroke-[3]" />
              ) : (
                <FiCheckCircle className="w-3.5 h-3.5" />
              )}
            </div>
          </div>
          <div className="my-1 flex items-baseline space-x-1.5">
            <span
              className={`font-mono font-black text-3xl sm:text-4xl tracking-tight ${
                isEscalated
                  ? 'text-[#FF5376] dark:text-[#FB7185]'
                  : isDeescalated
                  ? 'text-sky-600 dark:text-sky-400'
                  : 'text-black dark:text-white'
              }`}
            >
              {vuln.rank_displacement > 0 ? `+${vuln.rank_displacement}` : vuln.rank_displacement}
            </span>
            <span className="font-mono text-xs text-neutral-500">ranks</span>
          </div>
          <div className="flex items-center space-x-1.5 pt-2 border-t border-black/10 dark:border-white/10 mt-1 text-[11px] font-mono text-neutral-600 dark:text-neutral-400">
            <span>
              Rank #{vuln.rank_contextual} (was CVSS #{vuln.rank_cvss})
            </span>
          </div>
        </div>
      </div>

      {/* Executive Verdict & Mathematical Transparency Panel */}
      <Panel
        title="Tactical Verdict & Mathematical Transparency"
        subtitle="Empirical justification for security leadership and technical evaluators"
        icon={<FiInfo className="w-4 h-4 text-black" />}
        accent="yellow"
        badge={
          <Badge
            color={verdict.status === 'escalated' ? 'pink' : verdict.status === 'de-escalated' ? 'cyan' : 'zinc'}
            size="xs"
          >
            {verdict.title}
          </Badge>
        }
      >
        <div className="space-y-4">
          {/* Plain-English Analogy Callout Box */}
          <div className="p-3.5 sm:p-4 border-2 border-black dark:border-white bg-[#FDFBF7] dark:bg-[#18181E] neo-shadow-sm space-y-2">
            <div className="flex items-center space-x-2 text-black dark:text-white font-mono font-bold text-xs uppercase">
              <span className="w-2 h-2 bg-[#00F0FF] inline-block border border-black" />
              <span>Operational Ground Reality Analogy</span>
            </div>
            <p className="text-xs sm:text-sm text-neutral-700 dark:text-neutral-300">
              <strong>CVSS Flaw Base ({breakdown.cvss_val.toFixed(1)} / 10.0)</strong> measures theoretical damage in an isolated vacuum. Our <strong>Contextual Engine ({breakdown.total_score.toFixed(3)})</strong> validates the operational environment: Is the software <strong>actively exploited right now in CISA KEV</strong> ({vuln.in_kev ? 'YES' : 'NO'}), is it on a <strong>mission-critical host</strong> ({asset.hostname} &bull; Tier {breakdown.crit_tier}), and is the machine <strong>exposed to the open internet</strong> (Zone: {breakdown.expo_tier.toUpperCase()})?
            </p>
          </div>

          {/* Detailed Verdict Text */}
          <div className="p-3 border-l-4 border-black dark:border-white bg-neutral-100 dark:bg-[#1A1A22] text-xs sm:text-sm font-sans text-neutral-900 dark:text-neutral-100 leading-relaxed">
            {verdict.text}
          </div>

          {/* 4-Factor Mathematical Progression Bars */}
          <div className="pt-2">
            <div className="flex items-center justify-between mb-3">
              <span className="font-mono font-bold text-xs uppercase tracking-wider text-black dark:text-white">
                Four-Factor Scoring Invariants (Weights Sum to 1.00)
              </span>
              <span className="font-mono font-bold text-xs px-2 py-0.5 bg-[#B8FF00] text-black border border-black">
                TOTAL: {breakdown.total_score.toFixed(3)} / 1.000
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {/* Factor 1: CVSS (35%) */}
              <div className="p-3 border-2 border-black dark:border-white bg-white dark:bg-[#1A1A22] neo-shadow-sm">
                <div className="flex items-center justify-between text-[11px] font-mono text-neutral-600 dark:text-neutral-400 mb-1">
                  <span>1. BASE (35%)</span>
                  <span className="font-bold text-black dark:text-white">+{breakdown.cvss_contrib.toFixed(3)}</span>
                </div>
                <div className="w-full h-3 border border-black dark:border-white bg-neutral-200 dark:bg-neutral-800 my-1 overflow-hidden">
                  <div
                    className="h-full bg-[#00F0FF] transition-all duration-300"
                    style={{ width: `${Math.min(100, (breakdown.cvss_contrib / 0.35) * 100)}%` }}
                  />
                </div>
                <div className="text-[11px] font-mono font-bold text-black dark:text-white mt-1">
                  {breakdown.cvss_val.toFixed(1)} / 10.0
                </div>
              </div>

              {/* Factor 2: KEV (30%) */}
              <div className="p-3 border-2 border-black dark:border-white bg-white dark:bg-[#1A1A22] neo-shadow-sm">
                <div className="flex items-center justify-between text-[11px] font-mono text-neutral-600 dark:text-neutral-400 mb-1">
                  <span>2. KEV EXPLOIT (30%)</span>
                  <span className="font-bold text-black dark:text-white">+{breakdown.kev_contrib.toFixed(3)}</span>
                </div>
                <div className="w-full h-3 border border-black dark:border-white bg-neutral-200 dark:bg-neutral-800 my-1 overflow-hidden">
                  <div
                    className="h-full bg-[#FF5376] transition-all duration-300"
                    style={{ width: `${Math.min(100, (breakdown.kev_contrib / 0.30) * 100)}%` }}
                  />
                </div>
                <div className="text-[11px] font-mono font-bold text-black dark:text-white mt-1">
                  {breakdown.in_kev ? 'Active in Wild (1.0)' : 'Not Exploited (0.0)'}
                </div>
              </div>

              {/* Factor 3: Asset Criticality (20%) */}
              <div className="p-3 border-2 border-black dark:border-white bg-white dark:bg-[#1A1A22] neo-shadow-sm">
                <div className="flex items-center justify-between text-[11px] font-mono text-neutral-600 dark:text-neutral-400 mb-1">
                  <span>3. ASSET TIER (20%)</span>
                  <span className="font-bold text-black dark:text-white">+{breakdown.asset_contrib.toFixed(3)}</span>
                </div>
                <div className="w-full h-3 border border-black dark:border-white bg-neutral-200 dark:bg-neutral-800 my-1 overflow-hidden">
                  <div
                    className="h-full bg-[#FFE600] transition-all duration-300"
                    style={{ width: `${Math.min(100, (breakdown.asset_contrib / 0.20) * 100)}%` }}
                  />
                </div>
                <div className="text-[11px] font-mono font-bold text-black dark:text-white mt-1 capitalize">
                  Tier: {breakdown.crit_tier} ({breakdown.crit_score.toFixed(2)})
                </div>
              </div>

              {/* Factor 4: Network Exposure (15%) */}
              <div className="p-3 border-2 border-black dark:border-white bg-white dark:bg-[#1A1A22] neo-shadow-sm">
                <div className="flex items-center justify-between text-[11px] font-mono text-neutral-600 dark:text-neutral-400 mb-1">
                  <span>4. EXPOSURE (15%)</span>
                  <span className="font-bold text-black dark:text-white">+{breakdown.expo_contrib.toFixed(3)}</span>
                </div>
                <div className="w-full h-3 border border-black dark:border-white bg-neutral-200 dark:bg-neutral-800 my-1 overflow-hidden">
                  <div
                    className="h-full bg-[#B8FF00] transition-all duration-300"
                    style={{ width: `${Math.min(100, (breakdown.expo_contrib / 0.15) * 100)}%` }}
                  />
                </div>
                <div className="text-[11px] font-mono font-bold text-black dark:text-white mt-1 uppercase">
                  {breakdown.expo_tier.replace('_', '-')} ({breakdown.expo_score.toFixed(2)})
                </div>
              </div>
            </div>

            {/* Exact Algebraic Equation Strip */}
            <div className="mt-3 p-2.5 sm:p-3 border-2 border-black dark:border-white bg-neutral-100 dark:bg-black font-mono text-xs text-black dark:text-white flex items-center justify-between overflow-x-auto whitespace-nowrap neo-shadow-sm">
              <span>
                S_ctx = (0.35 &times; {breakdown.cvss_val.toFixed(1)}/10) + (0.30 &times; {breakdown.in_kev ? '1.0' : '0.0'}) + (0.20 &times; {breakdown.crit_score.toFixed(2)}) + (0.15 &times; {breakdown.expo_score.toFixed(2)}) = <strong className="bg-[#FFE600] text-black px-1.5 py-0.5 border border-black">{breakdown.total_score.toFixed(3)}</strong>
              </span>
            </div>
          </div>
        </div>
      </Panel>
    </div>
  );
};
