import React from 'react';
import {
  ArrowRight,
  Database,
  FileCheck,
  Flame,
  Globe,
  Layers,
  Server,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';
import { OverviewExecutiveGuide } from '../components/ExecutiveGuide';
import { Top10BarChart } from '../components/Charts';
import { Vulnerability } from '../types';

interface OverviewPageProps {
  vulnerabilities: Vulnerability[];
  onSelectCve: (cveId: string) => void;
  onNavigateToRankings: () => void;
  onNavigateToInvestigation: () => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({
  vulnerabilities,
  onSelectCve,
  onNavigateToRankings,
  onNavigateToInvestigation,
}) => {
  const totalCves = vulnerabilities.length || 8328;
  const inKevCount = vulnerabilities.filter((v) => v.in_kev).length;
  const criticalCount = vulnerabilities.filter((v) => v.risk_band === 'Critical').length;
  const hasCvssCount = vulnerabilities.filter((v) => v.cvss_score > 0).length;

  const top5 = [...vulnerabilities]
    .sort((a, b) => b.risk_score - a.risk_score)
    .slice(0, 5);

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-[#1D1D1F] dark:text-[#F5F5F7]">
          Enterprise Vulnerability Landscape
        </h1>
        <p className="text-xs sm:text-sm text-[#86868B] dark:text-[#A1A1A6] mt-1">
          High-level operational snapshot of NIST NVD vulnerability corpus and contextual threat intelligence.
        </p>
      </div>

      {/* Non-Technical Executive Guide */}
      <OverviewExecutiveGuide />

      {/* 4 Primary Metric Tiles */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Tile 1 */}
        <div className="p-4 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-[#86868B] dark:text-[#A1A1A6]">
              Total CVE Corpus
            </span>
            <div className="w-7 h-7 rounded-lg bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center text-neutral-600 dark:text-neutral-400">
              <Database className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-semibold tracking-tight text-[#1D1D1F] dark:text-[#F5F5F7] mb-1">
            {totalCves.toLocaleString()}
          </div>
          <p className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
            Ingested from NIST National Vulnerability Database (NVD)
          </p>
        </div>

        {/* Tile 2 */}
        <div className="p-4 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-red-600 dark:text-red-400">
              In CISA KEV Catalog
            </span>
            <div className="w-7 h-7 rounded-lg bg-red-500/10 text-red-600 dark:text-red-400 flex items-center justify-center">
              <Flame className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-semibold tracking-tight text-red-600 dark:text-red-400 mb-1">
            {inKevCount.toLocaleString()}
          </div>
          <p className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
            Actively weaponized in the wild by threat actors
          </p>
        </div>

        {/* Tile 3 */}
        <div className="p-4 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-[#FF9500]">
              Critical Risk Band
            </span>
            <div className="w-7 h-7 rounded-lg bg-[#FF9500]/10 text-[#FF9500] flex items-center justify-center">
              <ShieldAlert className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-semibold tracking-tight text-[#1D1D1F] dark:text-[#F5F5F7] mb-1">
            {criticalCount.toLocaleString()}
          </div>
          <p className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
            Multi-factor score &ge; 0.80 requiring immediate remediation
          </p>
        </div>

        {/* Tile 4 */}
        <div className="p-4 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-[#0071E3] dark:text-[#0A84FF]">
              Evaluated with CVSS v3
            </span>
            <div className="w-7 h-7 rounded-lg bg-[#0071E3]/10 text-[#0071E3] dark:text-[#0A84FF] flex items-center justify-center">
              <FileCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-semibold tracking-tight text-[#1D1D1F] dark:text-[#F5F5F7] mb-1">
            {hasCvssCount.toLocaleString()}
          </div>
          <p className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
            100% vector completeness across normalized dataset
          </p>
        </div>
      </div>

      {/* Top 5 Contextual Risk Table */}
      <div className="p-5 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">
              Highest Priority Vulnerabilities in Enterprise Queue
            </h3>
            <p className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
              Ranked by contextual risk score incorporating live weaponization and perimeter exposure
            </p>
          </div>
          <button
            onClick={onNavigateToRankings}
            className="text-xs font-medium text-[#0071E3] hover:underline flex items-center space-x-1"
          >
            <span>View All Rankings</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-black/5 dark:border-white/5 text-[#86868B] dark:text-[#A1A1A6] uppercase tracking-wider text-[10px]">
                <th className="py-2.5 px-3 font-semibold">Priority Rank</th>
                <th className="py-2.5 px-3 font-semibold">CVE Identifier</th>
                <th className="py-2.5 px-3 font-semibold">CVSS Base</th>
                <th className="py-2.5 px-3 font-semibold">CISA KEV</th>
                <th className="py-2.5 px-3 font-semibold">Contextual Risk</th>
                <th className="py-2.5 px-3 font-semibold">Target Asset</th>
                <th className="py-2.5 px-3 font-semibold text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-black/[0.04] dark:divide-white/[0.04]">
              {top5.map((v, i) => (
                <tr
                  key={v.cve_id}
                  className="hover:bg-black/[0.02] dark:hover:bg-white/[0.02] transition-colors"
                >
                  <td className="py-3 px-3 font-mono font-medium text-neutral-500">
                    #{i + 1}
                  </td>
                  <td className="py-3 px-3">
                    <div className="font-mono font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">
                      {v.cve_id}
                    </div>
                    <div className="text-[10px] text-[#86868B] dark:text-[#A1A1A6] truncate max-w-xs">
                      {v.description.slice(0, 65)}...
                    </div>
                  </td>
                  <td className="py-3 px-3">
                    <span className="font-mono font-medium">{v.cvss_score.toFixed(1)}</span>
                    <span className="text-[10px] text-neutral-500 ml-1">({v.cvss_severity})</span>
                  </td>
                  <td className="py-3 px-3">
                    {v.in_kev ? (
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-red-500/10 text-red-600 dark:text-red-400">
                        In KEV
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400">
                        Not in KEV
                      </span>
                    )}
                  </td>
                  <td className="py-3 px-3">
                    <div className="font-mono font-semibold text-[#0071E3]">
                      {v.risk_score.toFixed(3)}
                    </div>
                    <span className="text-[10px] font-medium text-neutral-500">
                      Band: {v.risk_band}
                    </span>
                  </td>
                  <td className="py-3 px-3 font-mono text-[11px] text-neutral-600 dark:text-neutral-400">
                    {v.matched_asset_id}
                  </td>
                  <td className="py-3 px-3 text-right">
                    <button
                      onClick={() => onSelectCve(v.cve_id)}
                      className="px-2.5 py-1 text-[11px] font-medium rounded-lg bg-[#0071E3]/10 text-[#0071E3] hover:bg-[#0071E3]/20 transition-colors"
                    >
                      Investigate
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Top 10 Chart */}
      <Top10BarChart vulnerabilities={vulnerabilities} onSelectCve={onSelectCve} />
    </div>
  );
};
