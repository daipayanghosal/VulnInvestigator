import React, { useMemo, useState } from 'react';
import {
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  BarChart3,
  CheckCircle2,
  Filter,
  Plus,
  Search,
  SlidersHorizontal,
} from 'lucide-react';
import { ExecutiveGuide } from '../components/ExecutiveGuide';
import { RiskBand, Vulnerability } from '../types';

interface RankingsPageProps {
  vulnerabilities: Vulnerability[];
  onSelectCve: (cveId: string) => void;
  onOpenCustomCveModal: () => void;
}

export const RankingsPage: React.FC<RankingsPageProps> = ({
  vulnerabilities,
  onSelectCve,
  onOpenCustomCveModal,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedBand, setSelectedBand] = useState<string>('All');
  const [kevFilter, setKevFilter] = useState<'all' | 'in_kev' | 'not_in_kev'>('all');

  const filteredVulns = useMemo(() => {
    return vulnerabilities.filter((v) => {
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchCve = v.cve_id.toLowerCase().includes(q);
        const matchDesc = v.description.toLowerCase().includes(q);
        const matchAsset = (v.matched_asset_id || '').toLowerCase().includes(q);
        if (!matchCve && !matchDesc && !matchAsset) return false;
      }
      if (selectedBand !== 'All' && v.risk_band !== selectedBand) return false;
      if (kevFilter === 'in_kev' && !v.in_kev) return false;
      if (kevFilter === 'not_in_kev' && v.in_kev) return false;
      return true;
    });
  }, [vulnerabilities, searchQuery, selectedBand, kevFilter]);

  // Top 20 for CVSS Baseline
  const cvssTop20 = useMemo(() => {
    return [...filteredVulns]
      .sort((a, b) => b.cvss_score - a.cvss_score)
      .slice(0, 20);
  }, [filteredVulns]);

  // Top 20 for Contextual Risk
  const contextualTop20 = useMemo(() => {
    return [...filteredVulns]
      .sort((a, b) => b.risk_score - a.risk_score)
      .slice(0, 20);
  }, [filteredVulns]);

  // Top 20 by absolute displacement
  const topDisplacements = useMemo(() => {
    return [...filteredVulns]
      .sort((a, b) => Math.abs(b.rank_displacement) - Math.abs(a.rank_displacement))
      .slice(0, 20);
  }, [filteredVulns]);

  const bandBadgeColors: Record<RiskBand, string> = {
    Critical: 'bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20',
    High: 'bg-orange-500/10 text-orange-600 dark:text-orange-400 border-orange-500/20',
    Medium: 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20',
    Low: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20',
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-[#1D1D1F] dark:text-[#F5F5F7]">
            Vulnerability Prioritization &amp; Rankings
          </h1>
          <p className="text-xs sm:text-sm text-[#86868B] dark:text-[#A1A1A6] mt-1">
            Direct comparison: Static CVSS vendor baselines vs. empirical multi-factor contextual risk.
          </p>
        </div>
        <button
          onClick={onOpenCustomCveModal}
          className="self-start sm:self-auto px-4 py-2 text-xs font-medium rounded-xl bg-[#0071E3] hover:bg-[#0077ED] text-white shadow-sm flex items-center space-x-1.5 transition-colors"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Ingest Custom CVE</span>
        </button>
      </div>

      {/* Executive & Non-Technical Guide */}
      <ExecutiveGuide title="Executive Guide: How to Understand These Comparative Rankings">
        <div className="space-y-3">
          <div>
            <h4 className="font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">
              Why Two Distinct Prioritization Tables?
            </h4>
            <p className="text-neutral-600 dark:text-neutral-300 mt-0.5">
              <strong>Left Table (CVSS Baseline)</strong> represents the traditional industry status quo. It sorts vulnerabilities purely by generic lab technical scores. Because vendors assign high scores liberally, teams face overwhelming backlogs.
            </p>
            <p className="text-neutral-600 dark:text-neutral-300 mt-1">
              <strong>Right Table (Contextual Risk)</strong> reflects real enterprise risk. It recalibrates priorities by cross-referencing active threat actor weaponization (CISA KEV), asset business importance, and network perimeter exposure.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
            <div className="p-3 rounded-xl bg-emerald-500/5 border border-emerald-500/20 text-emerald-900 dark:text-emerald-300">
              <div className="font-semibold text-xs flex items-center space-x-1 mb-1">
                <ArrowUpRight className="w-3.5 h-3.5 text-emerald-600" />
                <span>Green (+ Shifts): Hidden Urgent Threats</span>
              </div>
              <p className="text-[11px] text-neutral-600 dark:text-neutral-300">
                Flaws with moderate vendor scores (e.g. CVSS 7.2) that traditional tools de-prioritize. Because adversaries are actively weaponizing them against your public-facing systems, contextual scoring escalates them to prevent an immediate breach.
              </p>
            </div>

            <div className="p-3 rounded-xl bg-blue-500/5 border border-blue-500/20 text-blue-900 dark:text-blue-300">
              <div className="font-semibold text-xs flex items-center space-x-1 mb-1">
                <ArrowDownRight className="w-3.5 h-3.5 text-blue-600" />
                <span>Blue (&minus; Shifts): Prevented False Alarms</span>
              </div>
              <p className="text-[11px] text-neutral-600 dark:text-neutral-300">
                Flaws with alarming vendor scores (e.g. CVSS 9.8) that trigger emergency firefighting. Because CISA confirms zero wild exploits and the host is an isolated internal server, contextual scoring de-escalates them to scheduled maintenance.
              </p>
            </div>
          </div>
        </div>
      </ExecutiveGuide>

      {/* Filter & Search Bar */}
      <div className="p-4 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        {/* Search Input */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-[#86868B]" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by CVE ID, asset name, or keywords..."
            className="w-full pl-9 pr-3 py-1.5 text-xs rounded-xl bg-black/[0.03] dark:bg-white/[0.05] border border-black/10 dark:border-white/10 text-[#1D1D1F] dark:text-[#F5F5F7] focus:outline-none focus:ring-2 focus:ring-[#0071E3]"
          />
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Risk Band Select */}
          <div className="flex items-center space-x-1 text-xs">
            <span className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">Band:</span>
            <select
              value={selectedBand}
              onChange={(e) => setSelectedBand(e.target.value)}
              className="px-2.5 py-1.5 text-xs rounded-xl bg-black/[0.03] dark:bg-white/[0.05] border border-black/10 dark:border-white/10 text-[#1D1D1F] dark:text-[#F5F5F7] focus:outline-none"
            >
              <option value="All">All Risk Bands</option>
              <option value="Critical">Critical Only</option>
              <option value="High">High Only</option>
              <option value="Medium">Medium Only</option>
              <option value="Low">Low Only</option>
            </select>
          </div>

          {/* KEV Filter Pills */}
          <div className="flex items-center p-0.5 rounded-xl bg-black/[0.04] dark:bg-white/[0.06] text-xs">
            <button
              onClick={() => setKevFilter('all')}
              className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition-colors ${
                kevFilter === 'all'
                  ? 'bg-white dark:bg-[#2C2C2E] text-[#1D1D1F] dark:text-[#F5F5F7] shadow-sm'
                  : 'text-[#86868B] dark:text-[#A1A1A6]'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setKevFilter('in_kev')}
              className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition-colors ${
                kevFilter === 'in_kev'
                  ? 'bg-white dark:bg-[#2C2C2E] text-red-600 dark:text-red-400 shadow-sm'
                  : 'text-[#86868B] dark:text-[#A1A1A6]'
              }`}
            >
              In KEV Only
            </button>
            <button
              onClick={() => setKevFilter('not_in_kev')}
              className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition-colors ${
                kevFilter === 'not_in_kev'
                  ? 'bg-white dark:bg-[#2C2C2E] text-neutral-800 dark:text-neutral-200 shadow-sm'
                  : 'text-[#86868B] dark:text-[#A1A1A6]'
              }`}
            >
              Not in KEV
            </button>
          </div>
        </div>
      </div>

      <div className="text-xs text-[#86868B] dark:text-[#A1A1A6] px-1">
        Showing <strong>{filteredVulns.length.toLocaleString()}</strong> of {vulnerabilities.length.toLocaleString()} vulnerabilities matching current filters.
      </div>

      {/* Side-by-Side Dual Table View */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Left Table: CVSS Baseline Ranking */}
        <div className="p-5 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm flex flex-col">
          <div className="flex items-center justify-between mb-3 pb-2 border-b border-black/5 dark:border-white/5">
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="w-2 h-2 rounded-full bg-neutral-400" />
                <h3 className="text-sm font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">
                  CVSS Baseline Ranking
                </h3>
              </div>
              <p className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
                Traditional theoretical laboratory severity
              </p>
            </div>
            <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400">
              Top 20
            </span>
          </div>

          <div className="overflow-x-auto flex-1">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-black/5 dark:border-white/5 text-[10px] uppercase text-[#86868B] dark:text-[#A1A1A6]">
                  <th className="py-2 px-2">Rank</th>
                  <th className="py-2 px-2">CVE ID</th>
                  <th className="py-2 px-2">CVSS Base</th>
                  <th className="py-2 px-2 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-black/[0.03] dark:divide-white/[0.03]">
                {cvssTop20.map((v, i) => (
                  <tr
                    key={v.cve_id}
                    className="hover:bg-black/[0.02] dark:hover:bg-white/[0.02] transition-colors"
                  >
                    <td className="py-2.5 px-2 font-mono font-medium text-neutral-400">
                      #{i + 1}
                    </td>
                    <td className="py-2.5 px-2 font-mono font-medium text-[#1D1D1F] dark:text-[#F5F5F7]">
                      {v.cve_id}
                    </td>
                    <td className="py-2.5 px-2">
                      <span className="font-mono font-semibold">{v.cvss_score.toFixed(1)}</span>
                      <span className="text-[10px] text-neutral-500 ml-1">({v.cvss_severity})</span>
                    </td>
                    <td className="py-2.5 px-2 text-right">
                      <button
                        onClick={() => onSelectCve(v.cve_id)}
                        className="text-[11px] text-[#0071E3] hover:underline"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right Table: Contextual Risk Ranking */}
        <div className="p-5 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm flex flex-col relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-[#0071E3]/5 rounded-bl-full pointer-events-none" />
          <div className="flex items-center justify-between mb-3 pb-2 border-b border-black/5 dark:border-white/5">
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="w-2 h-2 rounded-full bg-[#0071E3]" />
                <h3 className="text-sm font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">
                  Contextual Risk Ranking
                </h3>
              </div>
              <p className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
                Multi-factor score: CVSS + CISA KEV + Asset + Exposure
              </p>
            </div>
            <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-[#0071E3]/10 text-[#0071E3]">
              Top 20 Calibrated
            </span>
          </div>

          <div className="overflow-x-auto flex-1">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-black/5 dark:border-white/5 text-[10px] uppercase text-[#86868B] dark:text-[#A1A1A6]">
                  <th className="py-2 px-2">Rank</th>
                  <th className="py-2 px-2">CVE ID</th>
                  <th className="py-2 px-2">Contextual Risk</th>
                  <th className="py-2 px-2">Risk Band</th>
                  <th className="py-2 px-2 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-black/[0.03] dark:divide-white/[0.03]">
                {contextualTop20.map((v, i) => (
                  <tr
                    key={v.cve_id}
                    className="hover:bg-black/[0.02] dark:hover:bg-white/[0.02] transition-colors"
                  >
                    <td className="py-2.5 px-2 font-mono font-medium text-[#0071E3]">
                      #{i + 1}
                    </td>
                    <td className="py-2.5 px-2">
                      <div className="font-mono font-medium text-[#1D1D1F] dark:text-[#F5F5F7] flex items-center space-x-1.5">
                        <span>{v.cve_id}</span>
                        {v.in_kev && (
                          <span className="text-[9px] uppercase px-1 rounded bg-red-500/10 text-red-600 dark:text-red-400 font-semibold">
                            KEV
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-2.5 px-2 font-mono font-semibold text-[#0071E3]">
                      {v.risk_score.toFixed(3)}
                    </td>
                    <td className="py-2.5 px-2">
                      <span
                        className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${bandBadgeColors[v.risk_band]}`}
                      >
                        {v.risk_band}
                      </span>
                    </td>
                    <td className="py-2.5 px-2 text-right">
                      <button
                        onClick={() => onSelectCve(v.cve_id)}
                        className="text-[11px] text-[#0071E3] hover:underline"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Top 20 Displacements Table */}
      <div className="p-5 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm">
        <div className="flex items-center justify-between mb-3 pb-2 border-b border-black/5 dark:border-white/5">
          <div>
            <h3 className="text-sm font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">
              Top Priority Queue Displacements (&Delta; = Rank_CVSS &minus; Rank_Contextual)
            </h3>
            <p className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
              Vulnerabilities experiencing the greatest reallocation of enterprise remediation priority
            </p>
          </div>
          <span className="text-xs text-[#86868B] dark:text-[#A1A1A6]">
            Sorted by magnitude of shift
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-black/5 dark:border-white/5 text-[10px] uppercase text-[#86868B] dark:text-[#A1A1A6]">
                <th className="py-2 px-2">CVE ID</th>
                <th className="py-2 px-2">CVSS Score (Rank)</th>
                <th className="py-2 px-2">Contextual Score (Rank)</th>
                <th className="py-2 px-2">Priority Shift (&Delta;)</th>
                <th className="py-2 px-2">Operational Interpretation</th>
                <th className="py-2 px-2 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-black/[0.03] dark:divide-white/[0.03]">
              {topDisplacements.map((v) => {
                const isEsc = v.rank_displacement > 0;
                const isDeesc = v.rank_displacement < 0;
                return (
                  <tr
                    key={v.cve_id}
                    className="hover:bg-black/[0.02] dark:hover:bg-white/[0.02] transition-colors"
                  >
                    <td className="py-2.5 px-2 font-mono font-medium text-[#1D1D1F] dark:text-[#F5F5F7]">
                      {v.cve_id}
                    </td>
                    <td className="py-2.5 px-2">
                      <span className="font-mono">{v.cvss_score.toFixed(1)}</span>
                      <span className="text-[10px] text-neutral-400 ml-1">(#{v.rank_cvss})</span>
                    </td>
                    <td className="py-2.5 px-2">
                      <span className="font-mono text-[#0071E3] font-semibold">
                        {v.risk_score.toFixed(3)}
                      </span>
                      <span className="text-[10px] text-neutral-400 ml-1">(#{v.rank_contextual})</span>
                    </td>
                    <td className="py-2.5 px-2">
                      <span
                        className={`inline-flex items-center space-x-1 font-mono font-semibold px-2 py-0.5 rounded-md ${
                          isEsc
                            ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
                            : isDeesc
                            ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400'
                            : 'bg-neutral-100 text-neutral-600'
                        }`}
                      >
                        {isEsc ? <ArrowUpRight className="w-3 h-3" /> : isDeesc ? <ArrowDownRight className="w-3 h-3" /> : null}
                        <span>
                          {v.rank_displacement > 0 ? `+${v.rank_displacement}` : v.rank_displacement}
                        </span>
                      </span>
                    </td>
                    <td className="py-2.5 px-2 text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
                      {isEsc
                        ? `Elevated urgency: weaponized in KEV on asset ${v.matched_asset_id}.`
                        : isDeesc
                        ? `De-escalated false alarm: internal placement with zero wild weaponization.`
                        : 'Identical priority standing.'}
                    </td>
                    <td className="py-2.5 px-2 text-right">
                      <button
                        onClick={() => onSelectCve(v.cve_id)}
                        className="text-[11px] text-[#0071E3] hover:underline"
                      >
                        Investigate
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
