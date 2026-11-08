import React, { useMemo, useState } from 'react';
import {
  FiAlertCircle,
  FiArrowDownRight,
  FiArrowRight,
  FiArrowUpRight,
  FiBarChart2,
  FiCheckCircle,
  FiFilter,
  FiPlus,
  FiSearch,
  FiSliders,
} from 'react-icons/fi';
import { Badge, BadgeColor } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { Panel } from '../components/common/Panel';
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

  const bandBadges: Record<RiskBand, { color: BadgeColor; label: string }> = {
    Critical: { color: 'pink', label: 'CRITICAL' },
    High: { color: 'orange', label: 'HIGH' },
    Medium: { color: 'yellow', label: 'MEDIUM' },
    Low: { color: 'lime', label: 'LOW' },
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-150 font-mono">
      {/* Page Title & Ingest Button */}
      <div className="border-b-2 sm:border-b-[3px] border-black dark:border-[#2D3448] pb-4 flex flex-col sm:flex-row sm:items-end justify-between gap-3">
        <div>
          <div className="flex items-center space-x-2 flex-wrap gap-y-1 mb-1">
            <span className="font-bold text-xs uppercase bg-[#00F0FF] dark:bg-[#0284C7] text-black dark:text-white px-2 py-0.5 border border-black dark:border-[#2D3448] neo-shadow-sm">
              COMPARATIVE MATRIX
            </span>
            <span className="text-xs text-neutral-500">// CVSS vs VULNINVESTIGATOR</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-black tracking-tight text-black dark:text-white uppercase">
            Vulnerability Prioritization &amp; Rankings
          </h1>
          <p className="text-xs sm:text-sm text-neutral-600 dark:text-neutral-400 mt-1 font-sans">
            Head-to-head empirical comparison: Static CVSS vendor severity vs. contextual multi-factor risk scores.
          </p>
        </div>

        <Button
          variant="primary"
          size="md"
          icon={<FiPlus className="w-4 h-4 stroke-[3]" />}
          onClick={onOpenCustomCveModal}
        >
          INGEST CUSTOM CVE
        </Button>
      </div>

      {/* Non-Technical Guide */}
      <ExecutiveGuide title="Evaluator Guide: Understanding Comparative Prioritization Divergence">
        <div className="space-y-3 font-sans">
          <div>
            <h4 className="font-mono font-bold text-sm text-black dark:text-white uppercase mb-1">
              Why Two Distinct Prioritization Tables?
            </h4>
            <p className="text-neutral-700 dark:text-neutral-300">
              <strong>Left Table (CVSS Baseline):</strong> Traditional vendor rating evaluating code flaws in isolation. High scores are distributed liberally without regard for deployment context.
            </p>
            <p className="text-neutral-700 dark:text-neutral-300 mt-1">
              <strong>Right Table (Contextual Risk):</strong> Real enterprise risk incorporating active threat exploitation (CISA KEV), corporate asset importance, and perimeter network exposure.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1 font-mono text-xs">
            <div className="p-3 border-2 border-black dark:border-white bg-[#FFF1F2] dark:bg-[#251317] neo-shadow-sm">
              <div className="font-bold flex items-center space-x-1 mb-1 text-[#FF5376] dark:text-[#FB7185]">
                <FiArrowUpRight className="w-4 h-4 stroke-[3]" />
                <span className="uppercase">Escalations (+ Shifts): Critical Perimeter Threats</span>
              </div>
              <p className="text-[11px] text-neutral-700 dark:text-neutral-300 font-sans">
                Vulnerabilities with moderate vendor scores (e.g. CVSS 5.5) under active in-the-wild exploitation on public internet gateways escalated to top triage queues.
              </p>
            </div>

            <div className="p-3 border-2 border-black dark:border-white bg-[#F0FDF4] dark:bg-[#122418] neo-shadow-sm">
              <div className="font-bold flex items-center space-x-1 mb-1 text-emerald-700 dark:text-emerald-400">
                <FiArrowDownRight className="w-4 h-4 stroke-[3]" />
                <span className="uppercase">De-escalations (&minus; Shifts): Deprioritized Lab Flaws</span>
              </div>
              <p className="text-[11px] text-neutral-700 dark:text-neutral-300 font-sans">
                Flaws with alarming vendor scores (e.g. CVSS 9.8) on offline testbeds with zero wild exploits de-escalated to save hundreds of wasted engineering hours.
              </p>
            </div>
          </div>
        </div>
      </ExecutiveGuide>

      {/* Neobrutalist Tactical Filter & Search Ribbon */}
      <div className="border-2 sm:border-[2.5px] border-black dark:border-[#2D3448] bg-white dark:bg-[#141824] p-3 sm:p-4 neo-shadow flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        {/* Search Input */}
        <div className="relative flex-1">
          <FiSearch className="w-4 h-4 absolute left-3 top-3 text-neutral-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="FILTER BY CVE ID, ASSET NAME, OR TECH KEYWORD..."
            className="w-full pl-9 pr-3 py-2 text-xs font-bold border-2 border-black dark:border-[#2D3448] bg-neutral-50 dark:bg-[#11141D] text-black dark:text-[#E2E8F0] uppercase neo-shadow-sm focus:outline-none focus:bg-[#F5EEFF] dark:focus:bg-[#181D29]"
          />
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          {/* Risk Band Select */}
          <div className="flex items-center space-x-1">
            <span className="font-bold text-neutral-600 dark:text-neutral-400">BAND:</span>
            <select
              value={selectedBand}
              onChange={(e) => setSelectedBand(e.target.value)}
              className="px-2.5 py-1.5 text-xs font-bold border-2 border-black dark:border-[#2D3448] bg-white dark:bg-[#181D29] text-black dark:text-[#E2E8F0] neo-shadow-sm focus:outline-none"
            >
              <option value="All">ALL BANDS</option>
              <option value="Critical">CRITICAL ONLY</option>
              <option value="High">HIGH ONLY</option>
              <option value="Medium">MEDIUM ONLY</option>
              <option value="Low">LOW ONLY</option>
            </select>
          </div>

          {/* KEV Filter Segmented Buttons */}
          <div className="flex items-center p-0.5 border-2 border-black dark:border-[#2D3448] bg-neutral-100 dark:bg-[#121622] neo-shadow-sm gap-1">
            <button
              type="button"
              onClick={() => setKevFilter('all')}
              className={`neo-btn px-2.5 py-1 text-[11px] font-bold border transition-all ${
                kevFilter === 'all'
                  ? 'bg-black text-white dark:bg-[#202738] dark:text-[#E2E8F0] dark:border-[#38425C] border-black neo-shadow-sm'
                  : 'border-transparent text-neutral-600 dark:text-neutral-400 hover:text-black dark:hover:text-white'
              }`}
            >
              ALL
            </button>
            <button
              type="button"
              onClick={() => setKevFilter('in_kev')}
              className={`neo-btn px-2.5 py-1 text-[11px] font-bold border transition-all ${
                kevFilter === 'in_kev'
                  ? 'bg-[#FF5376] dark:bg-[#E11D48] text-white border-black dark:border-transparent neo-shadow-sm'
                  : 'border-transparent text-neutral-600 dark:text-neutral-400 hover:text-black dark:hover:text-white'
              }`}
            >
              IN KEV ONLY
            </button>
            <button
              type="button"
              onClick={() => setKevFilter('not_in_kev')}
              className={`neo-btn px-2.5 py-1 text-[11px] font-bold border transition-all ${
                kevFilter === 'not_in_kev'
                  ? 'bg-[#B8FF00] dark:bg-[#65A30D] text-black dark:text-white border-black dark:border-transparent neo-shadow-sm'
                  : 'border-transparent text-neutral-600 dark:text-neutral-400 hover:text-black dark:hover:text-white'
              }`}
            >
              NOT IN KEV
            </button>
          </div>
        </div>
      </div>

      <div className="text-xs text-neutral-600 dark:text-neutral-400 px-1 font-mono">
        Showing <strong className="text-black dark:text-white">{filteredVulns.length.toLocaleString()}</strong> of {vulnerabilities.length.toLocaleString()} vulnerabilities matching active filter criteria.
      </div>

      {/* Side-by-Side Dual Table View */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Left Table: CVSS Baseline Ranking */}
        <Panel
          title="CVSS Baseline Ranking"
          subtitle="Vendor severity calculated in laboratory isolation"
          icon={<FiBarChart2 className="w-4 h-4 text-black dark:text-white" />}
          accent="zinc"
          badge={<Badge color="zinc" size="xs">TOP 20 CVSS</Badge>}
          noPadding
        >
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="bg-neutral-100 dark:bg-[#1C1C24] border-b-2 border-black dark:border-white text-[10px] uppercase text-black dark:text-white">
                  <th className="py-2.5 px-3 font-bold">Rank</th>
                  <th className="py-2.5 px-3 font-bold">CVE Identifier</th>
                  <th className="py-2.5 px-3 font-bold">CVSS Base</th>
                  <th className="py-2.5 px-3 font-bold text-right">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y-2 divide-black/10 dark:divide-white/10">
                {cvssTop20.map((v, i) => (
                  <tr
                    key={v.cve_id}
                    className="hover:bg-neutral-100 dark:hover:bg-[#1A1A22] transition-colors"
                  >
                    <td className="py-2.5 px-3 font-bold text-neutral-500">
                      <span className="px-1.5 py-0.2 bg-neutral-200 dark:bg-neutral-800 text-black dark:text-white border border-black dark:border-zinc-500 inline-block text-[10px]">
                        #{i + 1}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-bold text-black dark:text-white">
                      {v.cve_id}
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="font-bold">{v.cvss_score.toFixed(1)}</span>
                      <span className="text-[10px] text-neutral-500 ml-1">({v.cvss_severity})</span>
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <button
                        type="button"
                        onClick={() => onSelectCve(v.cve_id)}
                        className="neo-btn px-2 py-0.5 text-[11px] font-bold bg-white text-black border border-black hover:bg-[#C4A1FF]"
                      >
                        SELECT
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>

        {/* Right Table: Contextual Risk Ranking */}
        <Panel
          title="Contextual Risk Ranking"
          subtitle="Multi-factor score: CVSS + CISA KEV + Asset + Exposure"
          icon={<FiCheckCircle className="w-4 h-4 text-black" />}
          accent="yellow"
          badge={<Badge color="yellow" size="xs">TOP 20 RE-RANKED</Badge>}
          noPadding
        >
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="bg-neutral-100 dark:bg-[#1C1C24] border-b-2 border-black dark:border-white text-[10px] uppercase text-black dark:text-white">
                  <th className="py-2.5 px-3 font-bold">Rank</th>
                  <th className="py-2.5 px-3 font-bold">CVE Identifier</th>
                  <th className="py-2.5 px-3 font-bold">Score</th>
                  <th className="py-2.5 px-3 font-bold">Band</th>
                  <th className="py-2.5 px-3 font-bold text-right">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y-2 divide-black/10 dark:divide-white/10">
                {contextualTop20.map((v, i) => (
                  <tr
                    key={v.cve_id}
                    className="hover:bg-[#F5EEFF] dark:hover:bg-[#1E1E26] transition-colors"
                  >
                    <td className="py-2.5 px-3 font-bold">
                      <span className="px-1.5 py-0.2 bg-[#C4A1FF] text-black border border-black inline-block text-[10px]">
                        #{i + 1}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-bold text-black dark:text-white">
                      <div className="flex items-center space-x-1.5">
                        <span>{v.cve_id}</span>
                        {v.in_kev && (
                          <Badge color="pink" size="xs">
                            KEV
                          </Badge>
                        )}
                      </div>
                    </td>
                    <td className="py-2.5 px-3 font-black text-black dark:text-white">
                      {v.risk_score.toFixed(3)}
                    </td>
                    <td className="py-2.5 px-3">
                      <Badge color={bandBadges[v.risk_band].color} size="xs">
                        {v.risk_band}
                      </Badge>
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <button
                        type="button"
                        onClick={() => onSelectCve(v.cve_id)}
                        className="neo-btn px-2 py-0.5 text-[11px] font-bold bg-[#00F0FF] text-black border border-black hover:bg-[#38F4FF]"
                      >
                        INVESTIGATE
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>

      {/* Top 20 Displacements Matrix Table */}
      <Panel
        title="Top Priority Queue Displacements (Δ = Rank_CVSS − Rank_Contextual)"
        subtitle="Vulnerabilities experiencing the greatest reallocation of enterprise remediation priority"
        icon={<FiSliders className="w-4 h-4 text-black" />}
        accent="cyan"
        badge={<Badge color="cyan" size="xs">N = 8,328</Badge>}
        noPadding
      >
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="bg-neutral-100 dark:bg-[#1C1C24] border-b-2 border-black dark:border-white text-[10px] uppercase text-black dark:text-white">
                <th className="py-2.5 px-3 font-bold">CVE Identifier</th>
                <th className="py-2.5 px-3 font-bold">CVSS (Rank)</th>
                <th className="py-2.5 px-3 font-bold">Contextual Score (Rank)</th>
                <th className="py-2.5 px-3 font-bold">Priority Shift (Δ)</th>
                <th className="py-2.5 px-3 font-bold">Operational Context</th>
                <th className="py-2.5 px-3 font-bold text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y-2 divide-black/10 dark:divide-white/10">
              {topDisplacements.map((v) => {
                const isEsc = v.rank_displacement > 0;
                const isDeesc = v.rank_displacement < 0;
                return (
                  <tr
                    key={v.cve_id}
                    className="hover:bg-[#F5EEFF] dark:hover:bg-[#1E1E26] transition-colors"
                  >
                    <td className="py-2.5 px-3 font-bold text-black dark:text-white">
                      {v.cve_id}
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="font-bold">{v.cvss_score.toFixed(1)}</span>
                      <span className="text-[10px] text-neutral-500 ml-1">(#{v.rank_cvss})</span>
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="font-bold text-black dark:text-white">
                        {v.risk_score.toFixed(3)}
                      </span>
                      <span className="text-[10px] text-neutral-500 ml-1">(#{v.rank_contextual})</span>
                    </td>
                    <td className="py-2.5 px-3">
                      <span
                        className={`inline-flex items-center space-x-1 font-bold px-2 py-0.5 border border-black text-[11px] ${
                          isEsc
                            ? 'bg-[#FF5376] text-white'
                            : isDeesc
                            ? 'bg-[#00F0FF] text-black'
                            : 'bg-neutral-200 text-black'
                        }`}
                      >
                        {isEsc ? (
                          <FiArrowUpRight className="w-3.5 h-3.5 stroke-[3]" />
                        ) : isDeesc ? (
                          <FiArrowDownRight className="w-3.5 h-3.5 stroke-[3]" />
                        ) : null}
                        <span>
                          {v.rank_displacement > 0 ? `+${v.rank_displacement}` : v.rank_displacement}
                        </span>
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-[11px] text-neutral-700 dark:text-neutral-300 font-sans">
                      {isEsc
                        ? `Elevated urgency: weaponized in KEV on asset ${v.matched_asset_id}.`
                        : isDeesc
                        ? `De-escalated false alarm: internal placement with zero wild weaponization.`
                        : 'Identical priority standing.'}
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <button
                        type="button"
                        onClick={() => onSelectCve(v.cve_id)}
                        className="neo-btn px-2 py-0.5 text-[11px] font-bold bg-[#C4A1FF] text-black border border-black hover:bg-[#D4B8FF]"
                      >
                        INVESTIGATE
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Panel>
    </div>
  );
};
