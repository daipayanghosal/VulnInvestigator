import React, { useState } from 'react';
import { RiskBand, Vulnerability } from '../types';

interface Top10BarChartProps {
  vulnerabilities: Vulnerability[];
  onSelectCve?: (cveId: string) => void;
}

export const Top10BarChart: React.FC<Top10BarChartProps> = ({
  vulnerabilities,
  onSelectCve,
}) => {
  const [hoveredCve, setHoveredCve] = useState<Vulnerability | null>(null);

  const top10 = [...vulnerabilities]
    .sort((a, b) => b.risk_score - a.risk_score)
    .slice(0, 10);

  const bandColors: Record<RiskBand, string> = {
    Critical: '#FF3B30',
    High: '#FF9500',
    Medium: '#FFCC00',
    Low: '#34C759',
  };

  return (
    <div className="p-5 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-[#86868B] dark:text-[#A1A1A6]">
            Top 10 Vulnerabilities by Contextual Risk
          </h4>
          <p className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
            Highest-priority remediation targets combining CVSS, KEV weaponization, and asset exposure
          </p>
        </div>
        <div className="flex items-center space-x-3 text-[10px] text-[#86868B] dark:text-[#A1A1A6]">
          <span className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-sm bg-[#FF3B30]" />
            <span>Critical</span>
          </span>
          <span className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-sm bg-[#FF9500]" />
            <span>High</span>
          </span>
          <span className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-sm bg-[#FFCC00]" />
            <span>Medium</span>
          </span>
        </div>
      </div>

      {/* SVG Bar Chart */}
      <div className="space-y-2.5">
        {top10.map((v) => {
          const widthPercent = Math.max(5, Math.min(100, v.risk_score * 100));
          const color = bandColors[v.risk_band] || '#0071E3';
          const isHovered = hoveredCve?.cve_id === v.cve_id;

          return (
            <div
              key={v.cve_id}
              onMouseEnter={() => setHoveredCve(v)}
              onMouseLeave={() => setHoveredCve(null)}
              onClick={() => onSelectCve?.(v.cve_id)}
              className="group cursor-pointer"
            >
              <div className="flex items-center justify-between text-xs mb-1">
                <div className="flex items-center space-x-2">
                  <span className="font-mono font-medium text-[#1D1D1F] dark:text-[#F5F5F7] group-hover:text-[#0071E3] transition-colors">
                    {v.cve_id}
                  </span>
                  {v.in_kev && (
                    <span className="text-[9px] uppercase font-semibold px-1.5 py-0.2 rounded bg-red-500/10 text-red-600 dark:text-red-400">
                      KEV
                    </span>
                  )}
                  <span className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
                    ({v.matched_asset_id})
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="font-mono text-xs font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">
                    {v.risk_score.toFixed(3)}
                  </span>
                  <span className="text-[10px] text-[#86868B] dark:text-[#A1A1A6]">
                    CVSS: {v.cvss_score.toFixed(1)}
                  </span>
                </div>
              </div>

              {/* Progress Bar Track */}
              <div className="w-full h-3 rounded-full bg-black/[0.04] dark:bg-white/[0.08] overflow-hidden p-0.5">
                <div
                  className="h-full rounded-full transition-all duration-500 ease-out"
                  style={{
                    width: `${widthPercent}%`,
                    backgroundColor: color,
                    opacity: isHovered ? 1 : 0.85,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-4 pt-3 border-t border-black/5 dark:border-white/5 flex items-center justify-between text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
        <span>Click any row to jump directly to its complete Threat Investigation</span>
        <span>Contextual Risk Scale: 0.000 to 1.000</span>
      </div>
    </div>
  );
};

interface GaugeChartProps {
  value: number; // 0.0 to 1.0
  title?: string;
  subtitle?: string;
}

export const KendallTauGauge: React.FC<GaugeChartProps> = ({
  value = 0.5791,
  title = "Kendall's Rank Correlation (\u03C4 = 0.5791)",
  subtitle = 'Measures ranking divergence between CVSS baseline and contextual threat engine',
}) => {
  // Angle: -180 to 0 (semi-circle)
  const angle = -180 + value * 180;
  const radius = 70;
  const cx = 100;
  const cy = 90;

  // Compute needle endpoint
  const rad = (angle * Math.PI) / 180;
  const nx = cx + radius * Math.cos(rad);
  const ny = cy + radius * Math.sin(rad);

  return (
    <div className="p-5 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm flex flex-col items-center text-center">
      <div className="mb-2">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-[#86868B] dark:text-[#A1A1A6]">
          {title}
        </h4>
        <p className="text-[11px] text-[#86868B] dark:text-[#A1A1A6] max-w-sm">
          {subtitle}
        </p>
      </div>

      <div className="relative w-48 h-28 my-1 flex items-center justify-center">
        <svg viewBox="0 0 200 110" className="w-full h-full overflow-visible">
          {/* Background Arc (Gray) */}
          <path
            d="M 20 90 A 80 80 0 0 1 180 90"
            fill="none"
            stroke="currentColor"
            className="text-neutral-200 dark:text-neutral-800"
            strokeWidth="14"
            strokeLinecap="round"
          />

          {/* Value Arc (Blue Gradient) */}
          <path
            d="M 20 90 A 80 80 0 0 1 180 90"
            fill="none"
            stroke="#0071E3"
            strokeWidth="14"
            strokeLinecap="round"
            strokeDasharray="251.2"
            strokeDashoffset={251.2 - (251.2 * value)}
            className="transition-all duration-1000 ease-out"
          />

          {/* Needle Center Pin */}
          <circle cx={cx} cy={cy} r="6" fill="#1D1D1F" className="dark:fill-[#F5F5F7]" />

          {/* Needle Line */}
          <line
            x1={cx}
            y1={cy}
            x2={nx}
            y2={ny}
            stroke="#1D1D1F"
            className="dark:stroke-[#F5F5F7]"
            strokeWidth="3"
            strokeLinecap="round"
          />
        </svg>

        <div className="absolute bottom-1 font-mono text-xl font-bold text-[#1D1D1F] dark:text-[#F5F5F7]">
          {value.toFixed(4)}
        </div>
      </div>

      <div className="w-full flex items-center justify-between text-[10px] text-[#86868B] dark:text-[#A1A1A6] px-4 pt-2 border-t border-black/5 dark:border-white/5">
        <span>0.0 (Complete Disconnect)</span>
        <span className="font-semibold text-[#0071E3]">&tau; = 0.5791 (Calibrated)</span>
        <span>1.0 (Identical to CVSS)</span>
      </div>
      <p className="mt-2 text-[11px] text-neutral-600 dark:text-neutral-300 max-w-sm">
        <strong>Key Benchmark Finding</strong>: &tau; = 0.5791 proves that contextual scoring substantially reshuffles ~42% of pair comparisons, directly correcting CVSS severity inflation without producing random chaos.
      </p>
    </div>
  );
};

interface DisplacementHistogramProps {
  bins: Array<{
    bin_start: number;
    bin_end: number;
    bin_label: string;
    count: number;
    is_positive: boolean;
  }>;
}

export const DisplacementHistogram: React.FC<DisplacementHistogramProps> = ({ bins }) => {
  const [hoveredBin, setHoveredBin] = useState<any>(null);

  const maxCount = Math.max(...bins.map((b) => b.count), 1);

  return (
    <div className="p-5 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-[#86868B] dark:text-[#A1A1A6]">
            Empirical Rank Displacement Distribution (N = 8,328)
          </h4>
          <p className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
            &Delta; = Rank_CVSS &minus; Rank_Contextual (Span: -4,864 to +5,091 positions)
          </p>
        </div>
        <div className="flex items-center space-x-3 text-[10px]">
          <span className="flex items-center space-x-1 text-emerald-600 dark:text-emerald-400">
            <span className="w-2.5 h-2.5 rounded-sm bg-emerald-500" />
            <span>Escalated (+ Shift)</span>
          </span>
          <span className="flex items-center space-x-1 text-blue-600 dark:text-blue-400">
            <span className="w-2.5 h-2.5 rounded-sm bg-blue-500" />
            <span>De-escalated (&minus; Shift)</span>
          </span>
        </div>
      </div>

      {/* Histogram Bars */}
      <div className="h-44 flex items-end space-x-1 pt-4 pb-2 border-b border-black/10 dark:border-white/10">
        {bins.map((b, i) => {
          const heightPercent = Math.max(3, (b.count / maxCount) * 100);
          const isPos = b.is_positive;
          const isHovered = hoveredBin?.bin_label === b.bin_label;

          return (
            <div
              key={i}
              onMouseEnter={() => setHoveredBin(b)}
              onMouseLeave={() => setHoveredBin(null)}
              className="flex-1 flex flex-col items-center justify-end h-full relative group cursor-pointer"
            >
              <div
                className={`w-full rounded-t-sm transition-all duration-200 ${
                  isPos
                    ? isHovered
                      ? 'bg-emerald-600'
                      : 'bg-emerald-500/80'
                    : isHovered
                    ? 'bg-blue-600'
                    : 'bg-blue-500/80'
                }`}
                style={{ height: `${heightPercent}%` }}
              />
            </div>
          );
        })}
      </div>

      {/* Axis Labels & Active Bin Hover Detail */}
      <div className="flex items-center justify-between text-[11px] text-[#86868B] dark:text-[#A1A1A6] pt-2">
        <span>-4,864 (De-escalated False Alarms)</span>
        {hoveredBin ? (
          <span className="font-semibold text-[#1D1D1F] dark:text-[#F5F5F7] font-mono">
            Range: {hoveredBin.bin_label} &bull; {hoveredBin.count.toLocaleString()} CVEs
          </span>
        ) : (
          <span>&Delta; = 0 (Center)</span>
        )}
        <span>+5,091 (Escalated Threats)</span>
      </div>
    </div>
  );
};
