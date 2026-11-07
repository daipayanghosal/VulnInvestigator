import React, { useMemo, useState } from 'react';
import {
  AlertTriangle,
  ArrowRight,
  Code2,
  Crosshair,
  Database,
  ExternalLink,
  FileText,
  Flame,
  Globe,
  Layers,
  RefreshCw,
  Search,
  Server,
  Shield,
  ShieldAlert,
  Sparkles,
  Terminal,
} from 'lucide-react';
import { HeroScoreboard } from '../components/HeroScoreboard';
import { ExecutiveGuide } from '../components/ExecutiveGuide';
import { Asset, SecurityLog, Technique, Vulnerability } from '../types';
import { calculateFactorBreakdown } from '../utils/scoring';

interface InvestigationPageProps {
  vulnerabilities: Vulnerability[];
  assets: Asset[];
  techniques: Technique[];
  logs: SecurityLog[];
  selectedCveId: string;
  onSelectCve: (cveId: string) => void;
  onRunAiInvestigation: (cveId: string) => void;
  onOpenCustomCveModal: () => void;
}

export const InvestigationPage: React.FC<InvestigationPageProps> = ({
  vulnerabilities,
  assets,
  techniques,
  logs,
  selectedCveId,
  onSelectCve,
  onRunAiInvestigation,
  onOpenCustomCveModal,
}) => {
  const [cveSearch, setCveSearch] = useState('');

  // Find active vulnerability
  const activeVuln = useMemo(() => {
    return (
      vulnerabilities.find((v) => v.cve_id === selectedCveId) ||
      vulnerabilities[0] || {
        cve_id: 'CVE-2021-44228',
        cvss_score: 10.0,
        cvss_severity: 'CRITICAL',
        cvss_vector: 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H',
        in_kev: true,
        risk_score: 0.99,
        risk_band: 'Critical',
        matched_asset_id: 'SRV-WEB-001',
        rank_cvss: 1,
        rank_contextual: 1,
        rank_displacement: 0,
        description: 'Apache Log4j2 JNDI features do not protect against attacker controlled LDAP and other JNDI related endpoints.',
        affected_products: 'cpe:2.3:a:apache:log4j:*:*:*:*:*:*:*:*',
      }
    );
  }, [vulnerabilities, selectedCveId]);

  // Find matched asset
  const activeAsset = useMemo(() => {
    return (
      assets.find((a) => a.asset_id === activeVuln.matched_asset_id) ||
      assets[0] || {
        asset_id: 'SRV-WEB-001',
        hostname: 'web-proxy-01',
        ip: '203.0.113.10',
        type: 'server',
        os: 'Ubuntu 22.04 LTS',
        software: ['Apache HTTP Server 2.4.58', 'OpenSSL 3.1.4'],
        criticality: 'critical',
        exposure: 'internet_facing',
        notes: 'Public-facing reverse proxy serving main corporate website and API gateway',
      }
    );
  }, [assets, activeVuln]);

  // Calculate factor breakdown
  const breakdown = useMemo(() => {
    return calculateFactorBreakdown(activeVuln.cvss_score, activeVuln.in_kev, activeAsset);
  }, [activeVuln, activeAsset]);

  // Correlate relevant logs
  const relevantLogs = useMemo(() => {
    const assetLogs = logs.filter(
      (l) => l.asset_id === activeAsset.asset_id || l.cve_id === activeVuln.cve_id
    );
    if (assetLogs.length > 0) return assetLogs;
    // Fallback simulation logs if unmapped
    return logs.slice(0, 5);
  }, [logs, activeAsset, activeVuln]);

  const signalLogs = relevantLogs.filter((l) => !l.is_noise);
  const noiseLogs = relevantLogs.filter((l) => Boolean(l.is_noise));

  // Search filtered CVE options for dropdown
  const filteredCves = useMemo(() => {
    if (!cveSearch.trim()) return vulnerabilities.slice(0, 50);
    const q = cveSearch.toLowerCase();
    return vulnerabilities
      .filter((v) => v.cve_id.toLowerCase().includes(q) || v.description.toLowerCase().includes(q))
      .slice(0, 50);
  }, [vulnerabilities, cveSearch]);

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-[#1D1D1F] dark:text-[#F5F5F7]">
          Threat Investigation &amp; Evidence Correlation
        </h1>
        <p className="text-xs sm:text-sm text-[#86868B] dark:text-[#A1A1A6] mt-1">
          Synthesize vulnerability mechanics with organizational asset coordinates, MITRE ATT&amp;CK adversary techniques, and SIEM security logs.
        </p>
      </div>

      {/* Non-Technical Guide */}
      <ExecutiveGuide title="Executive Guide: How Threat Investigation &amp; Evidence Correlation Works">
        <div className="space-y-3">
          <p className="text-neutral-600 dark:text-neutral-300">
            Traditional vulnerability reports present isolated CVE numbers. This module reconstructs a <strong>complete digital threat scenario</strong> by integrating four indispensable puzzle pieces:
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
            <div className="p-3 rounded-xl bg-black/[0.02] dark:bg-white/[0.02] border border-black/5 dark:border-white/5">
              <span className="font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">1. Flaw Profile</span>
              <p className="text-[11px] text-neutral-500 mt-1">
                Vendor-rated technical vulnerability mechanics and affected libraries.
              </p>
            </div>
            <div className="p-3 rounded-xl bg-black/[0.02] dark:bg-white/[0.02] border border-black/5 dark:border-white/5">
              <span className="font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">2. Target System</span>
              <p className="text-[11px] text-neutral-500 mt-1">
                Specific enterprise machine hosting that component, its network IP, and perimeter exposure.
              </p>
            </div>
            <div className="p-3 rounded-xl bg-black/[0.02] dark:bg-white/[0.02] border border-black/5 dark:border-white/5">
              <span className="font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">3. MITRE ATT&amp;CK</span>
              <p className="text-[11px] text-neutral-500 mt-1">
                Standard adversary tactics and techniques used to weaponize this weakness.
              </p>
            </div>
            <div className="p-3 rounded-xl bg-black/[0.02] dark:bg-white/[0.02] border border-black/5 dark:border-white/5">
              <span className="font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">4. SIEM Telemetry</span>
              <p className="text-[11px] text-neutral-500 mt-1">
                Security log events showing whether suspicious traffic has touched the host.
              </p>
            </div>
          </div>
        </div>
      </ExecutiveGuide>

      {/* CVE Selector Bar */}
      <div className="p-4 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="flex-1 flex flex-col sm:flex-row sm:items-center gap-2">
          <label className="text-xs font-semibold uppercase tracking-wider text-[#86868B] dark:text-[#A1A1A6] whitespace-nowrap">
            Investigate CVE:
          </label>
          <div className="relative flex-1">
            <select
              value={activeVuln.cve_id}
              onChange={(e) => onSelectCve(e.target.value)}
              className="w-full px-3 py-2 text-xs font-mono font-medium rounded-xl bg-black/[0.03] dark:bg-white/[0.05] border border-black/10 dark:border-white/10 text-[#1D1D1F] dark:text-[#F5F5F7] focus:outline-none focus:ring-2 focus:ring-[#0071E3]"
            >
              {vulnerabilities.slice(0, 100).map((v) => (
                <option key={v.cve_id} value={v.cve_id}>
                  {v.cve_id} &mdash; Risk: {v.risk_score.toFixed(3)} ({v.risk_band}) &bull; CVSS: {v.cvss_score.toFixed(1)} {v.in_kev ? '[KEV]' : ''}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          onClick={onOpenCustomCveModal}
          className="px-3.5 py-2 text-xs font-medium rounded-xl bg-black/[0.04] dark:bg-white/[0.08] hover:bg-black/[0.08] dark:hover:bg-white/[0.12] text-[#1D1D1F] dark:text-[#F5F5F7] border border-black/10 dark:border-white/10 flex items-center justify-center space-x-1.5 transition-colors whitespace-nowrap"
        >
          <span>Lookup Another CVE</span>
        </button>
      </div>

      {/* Hero Scoreboard Component */}
      <HeroScoreboard vuln={activeVuln} asset={activeAsset} breakdown={breakdown} />

      {/* Two-Column Details: Vulnerability Mechanics vs. Target Asset Coordinates */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Left Card: Vulnerability Profile */}
        <div className="p-5 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm space-y-3">
          <div className="flex items-center space-x-2 pb-2 border-b border-black/5 dark:border-white/5">
            <FileText className="w-4 h-4 text-[#0071E3]" />
            <h3 className="text-sm font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">
              Vulnerability Details &amp; Mechanics
            </h3>
          </div>

          <div className="space-y-2 text-xs">
            <div>
              <span className="text-[10px] font-semibold uppercase tracking-wider text-[#86868B] dark:text-[#A1A1A6] block mb-0.5">
                Description
              </span>
              <p className="text-neutral-700 dark:text-neutral-300 leading-relaxed bg-black/[0.02] dark:bg-white/[0.02] p-3 rounded-xl border border-black/5 dark:border-white/5">
                {activeVuln.description || 'No description recorded in database.'}
              </p>
            </div>

            {activeVuln.cvss_vector && (
              <div>
                <span className="text-[10px] font-semibold uppercase tracking-wider text-[#86868B] dark:text-[#A1A1A6] block mb-0.5">
                  CVSS v3.1 Vector String
                </span>
                <code className="text-[11px] font-mono px-2 py-1 rounded-lg bg-neutral-100 dark:bg-neutral-800 text-neutral-800 dark:text-neutral-200 block overflow-x-auto">
                  {activeVuln.cvss_vector}
                </code>
              </div>
            )}

            {activeVuln.affected_products && (
              <div>
                <span className="text-[10px] font-semibold uppercase tracking-wider text-[#86868B] dark:text-[#A1A1A6] block mb-0.5">
                  Affected Products / CPE Match
                </span>
                <code className="text-[11px] font-mono px-2 py-1 rounded-lg bg-neutral-100 dark:bg-neutral-800 text-neutral-800 dark:text-neutral-200 block truncate">
                  {activeVuln.affected_products}
                </code>
              </div>
            )}
          </div>
        </div>

        {/* Right Card: Target Asset Environment */}
        <div className="p-5 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm space-y-3">
          <div className="flex items-center space-x-2 pb-2 border-b border-black/5 dark:border-white/5">
            <Server className="w-4 h-4 text-[#0071E3]" />
            <h3 className="text-sm font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">
              Target Enterprise Asset Coordinates
            </h3>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-2.5 rounded-xl bg-black/[0.02] dark:bg-white/[0.02] border border-black/5 dark:border-white/5">
              <span className="text-[10px] uppercase font-semibold text-[#86868B] dark:text-[#A1A1A6] block">
                Hostname
              </span>
              <span className="font-mono font-semibold text-sm text-[#1D1D1F] dark:text-[#F5F5F7]">
                {activeAsset.hostname}
              </span>
            </div>

            <div className="p-2.5 rounded-xl bg-black/[0.02] dark:bg-white/[0.02] border border-black/5 dark:border-white/5">
              <span className="text-[10px] uppercase font-semibold text-[#86868B] dark:text-[#A1A1A6] block">
                Asset ID / IP
              </span>
              <span className="font-mono font-semibold text-sm text-[#0071E3]">
                {activeAsset.asset_id} ({activeAsset.ip})
              </span>
            </div>

            <div className="p-2.5 rounded-xl bg-black/[0.02] dark:bg-white/[0.02] border border-black/5 dark:border-white/5">
              <span className="text-[10px] uppercase font-semibold text-[#86868B] dark:text-[#A1A1A6] block">
                Criticality Tier
              </span>
              <span className="font-semibold text-xs capitalize text-[#1D1D1F] dark:text-[#F5F5F7]">
                {activeAsset.criticality}
              </span>
            </div>

            <div className="p-2.5 rounded-xl bg-black/[0.02] dark:bg-white/[0.02] border border-black/5 dark:border-white/5">
              <span className="text-[10px] uppercase font-semibold text-[#86868B] dark:text-[#A1A1A6] block">
                Network Exposure
              </span>
              <span className="font-semibold text-xs capitalize text-[#1D1D1F] dark:text-[#F5F5F7]">
                {activeAsset.exposure.replace('_', '-')}
              </span>
            </div>
          </div>

          <div className="text-xs space-y-1 pt-1">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-[#86868B] dark:text-[#A1A1A6] block">
              Operational Role &amp; Software Stack
            </span>
            <p className="text-[11px] text-neutral-600 dark:text-neutral-400">
              {activeAsset.notes || 'Enterprise production server system.'}
            </p>
            <div className="flex flex-wrap gap-1 pt-1">
              {Array.isArray(activeAsset.software) ? (
                activeAsset.software.map((sw, i) => (
                  <span
                    key={i}
                    className="px-2 py-0.5 rounded-md bg-neutral-100 dark:bg-neutral-800 text-[10px] font-mono text-neutral-700 dark:text-neutral-300"
                  >
                    {sw}
                  </span>
                ))
              ) : (
                <span className="text-[11px] font-mono text-neutral-600">{activeAsset.software}</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Correlated MITRE ATT&CK Techniques */}
      <div className="p-5 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-black/5 dark:border-white/5">
          <div className="flex items-center space-x-2">
            <Crosshair className="w-4 h-4 text-[#0071E3]" />
            <h3 className="text-sm font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">
              Correlated MITRE ATT&amp;CK Techniques
            </h3>
          </div>
          <span className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
            Adversary TTPs mapped to target software component
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {techniques.slice(0, 4).map((tech) => (
            <div
              key={tech.id}
              className="p-3.5 rounded-xl bg-black/[0.02] dark:bg-white/[0.02] border border-black/5 dark:border-white/5 space-y-1.5"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono font-semibold text-xs text-[#0071E3]">
                  {tech.id}
                </span>
                <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400">
                  {tech.tactics}
                </span>
              </div>
              <h4 className="text-xs font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">
                {tech.name}
              </h4>
              <p className="text-[11px] text-neutral-600 dark:text-neutral-400 leading-relaxed">
                {tech.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Correlated SIEM Security Logs */}
      <div className="p-5 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-black/5 dark:border-white/5">
          <div className="flex items-center space-x-2">
            <Terminal className="w-4 h-4 text-[#0071E3]" />
            <h3 className="text-sm font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">
              Correlated SIEM Security Telemetry
            </h3>
          </div>
          <span className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
            {signalLogs.length} suspicious attack events &bull; {noiseLogs.length} benign noise probes
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-black/5 dark:border-white/5 text-[10px] uppercase text-[#86868B] dark:text-[#A1A1A6]">
                <th className="py-2 px-2">Event ID</th>
                <th className="py-2 px-2">Timestamp</th>
                <th className="py-2 px-2">Source IP</th>
                <th className="py-2 px-2">Technique</th>
                <th className="py-2 px-2">Raw Payload / Event Log</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-black/[0.03] dark:divide-white/[0.03]">
              {signalLogs.map((log) => (
                <tr
                  key={log.event_id}
                  className="hover:bg-black/[0.02] dark:hover:bg-white/[0.02] transition-colors"
                >
                  <td className="py-2.5 px-2 font-mono font-medium text-[#0071E3]">
                    {log.event_id}
                  </td>
                  <td className="py-2.5 px-2 font-mono text-[11px] text-neutral-500">
                    {log.timestamp.slice(0, 19).replace('T', ' ')}
                  </td>
                  <td className="py-2.5 px-2 font-mono text-[11px] text-neutral-700 dark:text-neutral-300">
                    {log.source_ip}
                  </td>
                  <td className="py-2.5 px-2">
                    <span className="px-1.5 py-0.5 rounded bg-[#0071E3]/10 text-[#0071E3] font-mono text-[10px]">
                      {log.technique_id}
                    </span>
                  </td>
                  <td className="py-2.5 px-2 font-mono text-[11px] text-neutral-600 dark:text-neutral-400 max-w-md truncate">
                    {log.raw_log}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Action Footer: Run AI Investigation with Gemini */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-[#0071E3]/10 via-[#5856D6]/10 to-transparent border border-[#0071E3]/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-[#0071E3]" />
            <h3 className="text-sm font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">
              Synthesize Evidence with Constrained GenAI Assistant
            </h3>
          </div>
          <p className="text-xs text-[#86868B] dark:text-[#A1A1A6] mt-0.5">
            Formulate evidence-grounded investigation hypotheses, defensive SIEM query blocks, and validated remediation playbooks.
          </p>
        </div>

        <button
          onClick={() => onRunAiInvestigation(activeVuln.cve_id)}
          className="px-5 py-2.5 rounded-xl bg-[#0071E3] hover:bg-[#0077ED] text-white text-xs font-semibold shadow-md flex items-center space-x-2 transition-all duration-150 whitespace-nowrap"
        >
          <Sparkles className="w-4 h-4" />
          <span>Run AI Investigation with Gemini</span>
        </button>
      </div>
    </div>
  );
};
