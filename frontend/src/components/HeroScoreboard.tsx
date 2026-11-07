import React from 'react';
import {
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  CheckCircle2,
  Crosshair,
  Flame,
  Globe,
  HelpCircle,
  Info,
  Server,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Target,
} from 'lucide-react';
import { Asset, FactorBreakdown, RiskBand, Vulnerability } from '../types';
import { generateExecutiveVerdict } from '../utils/scoring';

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

  const bandColors: Record<RiskBand, { bg: string; text: string; border: string }> = {
    Critical: {
      bg: 'bg-red-500/10 dark:bg-red-500/20',
      text: 'text-red-700 dark:text-red-400',
      border: 'border-red-500/30',
    },
    High: {
      bg: 'bg-orange-500/10 dark:bg-orange-500/20',
      text: 'text-orange-700 dark:text-orange-400',
      border: 'border-orange-500/30',
    },
    Medium: {
      bg: 'bg-amber-500/10 dark:bg-amber-500/20',
      text: 'text-amber-700 dark:text-amber-400',
      border: 'border-amber-500/30',
    },
    Low: {
      bg: 'bg-emerald-500/10 dark:bg-emerald-500/20',
      text: 'text-emerald-700 dark:text-emerald-400',
      border: 'border-emerald-500/30',
    },
  };

  return (
    <div className="space-y-4">
      {/* 4-Column Metric Scoreboard */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        {/* Metric 1: CVSS Base Score */}
        <div className="p-4 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-[#86868B] dark:text-[#A1A1A6]">
              Standard CVSS Base
            </span>
            <div className="w-6 h-6 rounded-md bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center text-neutral-600 dark:text-neutral-400">
              <Globe className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="flex items-baseline space-x-1.5 mb-1.5">
            <span className="text-3xl font-semibold tracking-tight text-[#1D1D1F] dark:text-[#F5F5F7]">
              {vuln.cvss_score.toFixed(1)}
            </span>
            <span className="text-xs text-[#86868B] dark:text-[#A1A1A6]">/ 10.0</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="text-xs font-medium px-2 py-0.5 rounded-md bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300">
              {vuln.cvss_severity}
            </span>
            <span className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">Vendor Base</span>
          </div>
        </div>

        {/* Metric 2: Contextual Risk Score */}
        <div className="p-4 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm transition-all relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-[#0071E3]/5 rounded-bl-full pointer-events-none" />
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-[#0071E3] dark:text-[#0A84FF]">
              Contextual Risk Score
            </span>
            <div className="w-6 h-6 rounded-md bg-[#0071E3]/10 dark:bg-[#0071E3]/20 flex items-center justify-center text-[#0071E3] dark:text-[#0A84FF]">
              <Target className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="flex items-baseline space-x-1.5 mb-1.5">
            <span className="text-3xl font-semibold tracking-tight text-[#0071E3] dark:text-[#0A84FF]">
              {vuln.risk_score.toFixed(3)}
            </span>
            <span className="text-xs text-[#86868B] dark:text-[#A1A1A6]">/ 1.000</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span
              className={`text-xs font-semibold px-2 py-0.5 rounded-md border ${bandColors[vuln.risk_band].bg} ${bandColors[vuln.risk_band].text} ${bandColors[vuln.risk_band].border}`}
            >
              Band: {vuln.risk_band}
            </span>
            <span className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">Weighted Risk</span>
          </div>
        </div>

        {/* Metric 3: CISA KEV Exploitation Status */}
        <div className="p-4 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-[#86868B] dark:text-[#A1A1A6]">
              CISA KEV Exploit Status
            </span>
            <div
              className={`w-6 h-6 rounded-md flex items-center justify-center ${
                vuln.in_kev
                  ? 'bg-red-500/10 text-red-600 dark:text-red-400'
                  : 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
              }`}
            >
              {vuln.in_kev ? <Flame className="w-3.5 h-3.5" /> : <ShieldCheck className="w-3.5 h-3.5" />}
            </div>
          </div>
          <div className="mb-1.5">
            <span
              className={`text-lg font-semibold tracking-tight ${
                vuln.in_kev ? 'text-red-600 dark:text-red-400' : 'text-[#1D1D1F] dark:text-[#F5F5F7]'
              }`}
            >
              {vuln.in_kev ? 'Actively Weaponized' : 'Not In KEV'}
            </span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span
              className={`text-xs font-medium px-2 py-0.5 rounded-md ${
                vuln.in_kev
                  ? 'bg-red-500/10 text-red-700 dark:text-red-400'
                  : 'bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400'
              }`}
            >
              {vuln.in_kev ? 'Threat Actor Weaponized' : 'No Wild Exploits Known'}
            </span>
          </div>
        </div>

        {/* Metric 4: Priority Queue Displacement */}
        <div className="p-4 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-[#86868B] dark:text-[#A1A1A6]">
              Queue Rank Displacement
            </span>
            <div
              className={`w-6 h-6 rounded-md flex items-center justify-center ${
                isEscalated
                  ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
                  : isDeescalated
                  ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400'
                  : 'bg-neutral-100 dark:bg-neutral-800 text-neutral-500'
              }`}
            >
              {isEscalated ? (
                <ArrowUpRight className="w-3.5 h-3.5" />
              ) : isDeescalated ? (
                <ArrowDownRight className="w-3.5 h-3.5" />
              ) : (
                <CheckCircle2 className="w-3.5 h-3.5" />
              )}
            </div>
          </div>
          <div className="flex items-baseline space-x-1.5 mb-1.5">
            <span
              className={`text-3xl font-semibold tracking-tight ${
                isEscalated
                  ? 'text-emerald-600 dark:text-emerald-400'
                  : isDeescalated
                  ? 'text-blue-600 dark:text-blue-400'
                  : 'text-[#1D1D1F] dark:text-[#F5F5F7]'
              }`}
            >
              {vuln.rank_displacement > 0 ? `+${vuln.rank_displacement}` : vuln.rank_displacement}
            </span>
            <span className="text-xs text-[#86868B] dark:text-[#A1A1A6]">spots shifted</span>
          </div>
          <div className="flex items-center space-x-1.5 text-xs text-[#86868B] dark:text-[#A1A1A6]">
            <span>
              Rank #{vuln.rank_contextual} (was CVSS #{vuln.rank_cvss})
            </span>
          </div>
        </div>
      </div>

      {/* Executive Justification & Non-Technical Analogy Card */}
      <div className="p-5 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-black/5 dark:border-white/5">
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 rounded-md bg-[#0071E3]/10 dark:bg-[#0071E3]/20 flex items-center justify-center text-[#0071E3]">
              <Info className="w-3.5 h-3.5" />
            </div>
            <div>
              <h4 className="text-xs font-semibold tracking-tight text-[#1D1D1F] dark:text-[#F5F5F7]">
                Executive Justification: Why Contextual Risk Differs from CVSS
              </h4>
              <p className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
                Plain-English explanation designed for non-technical leadership and academic evaluators
              </p>
            </div>
          </div>
          <span
            className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full border ${
              verdict.status === 'escalated'
                ? 'bg-red-500/10 text-red-700 dark:text-red-400 border-red-500/20'
                : verdict.status === 'de-escalated'
                ? 'bg-blue-500/10 text-blue-700 dark:text-blue-400 border-blue-500/20'
                : 'bg-neutral-100 text-neutral-700 dark:bg-neutral-800 dark:text-neutral-300 border-neutral-300'
            }`}
          >
            {verdict.title}
          </span>
        </div>

        {/* Non-Technical Analogy Banner */}
        <div className="p-3.5 rounded-xl bg-black/[0.02] dark:bg-white/[0.02] border border-black/5 dark:border-white/5 text-xs text-[#1D1D1F] dark:text-[#E5E5EA] space-y-1.5">
          <div className="font-semibold text-[#0071E3] flex items-center space-x-1.5">
            <Target className="w-3.5 h-3.5" />
            <span>Non-Technical Analogy for Evaluators</span>
          </div>
          <p className="text-neutral-600 dark:text-neutral-300">
            <strong>Standard CVSS ({breakdown.cvss_val.toFixed(1)} / 10)</strong> is like a factory laboratory safety rating on a pressurized boiler: it measures how violently the boiler could theoretically burst in an engineered vacuum.
          </p>
          <p className="text-neutral-600 dark:text-neutral-300">
            <strong>Our Contextual Risk Score ({breakdown.total_score.toFixed(3)} / 1.0)</strong> checks ground reality: Is the boiler <strong>actually leaking right now</strong> (CISA KEV), is it placed in your <strong>most critical server room</strong> (Asset: {asset.hostname} &mdash; Tier: {breakdown.crit_tier}), and are the <strong>doors wide open to the public street</strong> (Exposure: {breakdown.expo_tier})?
          </p>
        </div>

        {/* Executive Verdict Text */}
        <p className="text-xs text-[#1D1D1F] dark:text-[#E5E5EA] leading-relaxed">
          {verdict.text}
        </p>

        {/* 4-Factor Mathematical Transparency Grid */}
        <div className="pt-3 border-t border-black/5 dark:border-white/5">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-[#86868B] dark:text-[#A1A1A6]">
              Mathematical Factor Breakdown (Weights Sum to 100%)
            </span>
            <span className="text-[11px] text-[#0071E3] font-mono">
              Score: {breakdown.total_score.toFixed(3)}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {/* Factor 1: CVSS (35%) */}
            <div className="p-3 rounded-xl bg-black/[0.015] dark:bg-white/[0.02] border border-black/5 dark:border-white/5">
              <div className="flex items-center justify-between text-[11px] text-[#86868B] dark:text-[#A1A1A6] mb-1">
                <span>1. CVSS Flaw Base (35%)</span>
                <span className="font-mono text-[#1D1D1F] dark:text-[#F5F5F7]">
                  +{breakdown.cvss_contrib.toFixed(3)}
                </span>
              </div>
              <div className="text-xs font-semibold text-[#1D1D1F] dark:text-[#F5F5F7] mb-0.5">
                {breakdown.cvss_val.toFixed(1)} / 10.0
              </div>
              <div className="text-[10px] text-[#86868B] dark:text-[#A1A1A6]">
                Theoretical flaw severity in isolation
              </div>
            </div>

            {/* Factor 2: KEV (30%) */}
            <div className="p-3 rounded-xl bg-black/[0.015] dark:bg-white/[0.02] border border-black/5 dark:border-white/5">
              <div className="flex items-center justify-between text-[11px] text-[#86868B] dark:text-[#A1A1A6] mb-1">
                <span>2. Real Exploits / KEV (30%)</span>
                <span className="font-mono text-[#1D1D1F] dark:text-[#F5F5F7]">
                  +{breakdown.kev_contrib.toFixed(3)}
                </span>
              </div>
              <div
                className={`text-xs font-semibold mb-0.5 ${
                  breakdown.in_kev ? 'text-red-600 dark:text-red-400' : 'text-[#1D1D1F] dark:text-[#F5F5F7]'
                }`}
              >
                {breakdown.in_kev ? 'Confirmed in CISA KEV' : 'Zero Observed Exploits'}
              </div>
              <div className="text-[10px] text-[#86868B] dark:text-[#A1A1A6]">
                Observed in real-world attacks
              </div>
            </div>

            {/* Factor 3: Asset Criticality (20%) */}
            <div className="p-3 rounded-xl bg-black/[0.015] dark:bg-white/[0.02] border border-black/5 dark:border-white/5">
              <div className="flex items-center justify-between text-[11px] text-[#86868B] dark:text-[#A1A1A6] mb-1">
                <span>3. Asset Criticality (20%)</span>
                <span className="font-mono text-[#1D1D1F] dark:text-[#F5F5F7]">
                  +{breakdown.asset_contrib.toFixed(3)}
                </span>
              </div>
              <div className="text-xs font-semibold text-[#1D1D1F] dark:text-[#F5F5F7] mb-0.5 capitalize">
                Tier: {breakdown.crit_tier} ({breakdown.crit_score.toFixed(2)})
              </div>
              <div className="text-[10px] text-[#86868B] dark:text-[#A1A1A6]">
                Business impact on {asset.hostname}
              </div>
            </div>

            {/* Factor 4: Network Exposure (15%) */}
            <div className="p-3 rounded-xl bg-black/[0.015] dark:bg-white/[0.02] border border-black/5 dark:border-white/5">
              <div className="flex items-center justify-between text-[11px] text-[#86868B] dark:text-[#A1A1A6] mb-1">
                <span>4. Network Exposure (15%)</span>
                <span className="font-mono text-[#1D1D1F] dark:text-[#F5F5F7]">
                  +{breakdown.expo_contrib.toFixed(3)}
                </span>
              </div>
              <div className="text-xs font-semibold text-[#1D1D1F] dark:text-[#F5F5F7] mb-0.5 capitalize">
                Tier: {breakdown.expo_tier.replace('_', '-')} ({breakdown.expo_score.toFixed(2)})
              </div>
              <div className="text-[10px] text-[#86868B] dark:text-[#A1A1A6]">
                Perimeter attack surface access
              </div>
            </div>
          </div>

          {/* Mathematical Equation Card */}
          <div className="mt-3 p-3 rounded-xl bg-neutral-900 text-neutral-100 font-mono text-[11px] flex items-center justify-between overflow-x-auto">
            <span>
              Risk_Score = ({breakdown.cvss_contrib.toFixed(3)} [CVSS]) + ({breakdown.kev_contrib.toFixed(3)} [KEV]) + ({breakdown.asset_contrib.toFixed(3)} [Asset]) + ({breakdown.expo_contrib.toFixed(3)} [Exposure]) = <strong className="text-[#34C759]">{breakdown.total_score.toFixed(3)}</strong>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
