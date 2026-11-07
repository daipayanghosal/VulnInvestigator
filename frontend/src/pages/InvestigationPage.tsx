import React, { useMemo, useState } from 'react';
import {
  AlertCircle,
  AlertTriangle,
  ArrowRight,
  Check,
  CheckCircle2,
  Code2,
  Compass,
  Crosshair,
  Database,
  ExternalLink,
  FileText,
  Flame,
  Globe,
  Layers,
  Loader2,
  Plus,
  RefreshCw,
  Search,
  Server,
  Settings2,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Sliders,
  Sparkles,
  Terminal,
} from 'lucide-react';
import { HeroScoreboard } from '../components/HeroScoreboard';
import { ExecutiveGuide } from '../components/ExecutiveGuide';
import { VulnerabilityPropagationMap } from '../components/VulnerabilityPropagationMap';
import { Asset, RiskBand, SecurityLog, Severity, Technique, Vulnerability } from '../types';
import { calculateFactorBreakdown, getRiskBand } from '../utils/scoring';

interface InvestigationPageProps {
  vulnerabilities: Vulnerability[];
  assets: Asset[];
  techniques: Technique[];
  logs: SecurityLog[];
  selectedCveId: string;
  onSelectCve: (cveId: string) => void;
  onRunAiInvestigation: (cveId: string) => void;
  onOpenCustomCveModal: () => void;
  onAddCustomCve?: (vuln: Vulnerability) => void;
}

const PRESET_BENCHMARKS = [
  { id: 'CVE-2021-44228', name: 'Log4Shell', cvss: 10.0, assetId: 'SRV-WEB-001', kev: true },
  { id: 'CVE-2023-4966', name: 'Citrix Bleed', cvss: 9.4, assetId: 'SRV-VPN-001', kev: true },
  { id: 'CVE-2024-3400', name: 'PAN-OS Command Injection', cvss: 10.0, assetId: 'SRV-VPN-001', kev: true },
  { id: 'CVE-2023-3519', name: 'Citrix ADC RCE', cvss: 9.8, assetId: 'SRV-VPN-001', kev: true },
  { id: 'CVE-2020-1938', name: 'Tomcat Ghostcat', cvss: 9.8, assetId: 'SRV-WEB-001', kev: true },
  { id: 'CVE-2024-21762', name: 'Fortinet Out-of-Bounds', cvss: 9.8, assetId: 'SRV-VPN-001', kev: true },
];

export const InvestigationPage: React.FC<InvestigationPageProps> = ({
  vulnerabilities,
  assets,
  techniques,
  logs,
  selectedCveId,
  onSelectCve,
  onRunAiInvestigation,
  onOpenCustomCveModal,
  onAddCustomCve,
}) => {
  const [cveInput, setCveInput] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [statusFeedback, setStatusFeedback] = useState<{
    type: 'success' | 'info' | 'error';
    text: string;
  } | null>(null);

  // Fine-tuning drawer controls
  const [showTuning, setShowTuning] = useState(false);
  const [overrideAssetId, setOverrideAssetId] = useState<string>(assets[0]?.asset_id || 'SRV-WEB-001');
  const [overrideCvss, setOverrideCvss] = useState<number>(9.5);
  const [overrideInKev, setOverrideInKev] = useState<boolean>(true);

  // History of investigated targets in this session
  const [investigatedHistory, setInvestigatedHistory] = useState<string[]>(() => {
    return selectedCveId ? [selectedCveId] : ['CVE-2021-44228'];
  });

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
    return logs.slice(0, 5);
  }, [logs, activeAsset, activeVuln]);

  const signalLogs = relevantLogs.filter((l) => !l.is_noise);
  const noiseLogs = relevantLogs.filter((l) => Boolean(l.is_noise));

  // Core handler: Input any CVE -> Analyze and ingest
  const handleAnalyzeCve = async (rawTarget?: string) => {
    const query = (rawTarget || cveInput).trim().toUpperCase();

    if (!query) {
      setStatusFeedback({
        type: 'error',
        text: 'Please enter a CVE ID (e.g. CVE-2024-3400).',
      });
      return;
    }

    const formattedCve = query.startsWith('CVE-') ? query : `CVE-${query}`;

    // 1. Check if already present in loaded corpus
    const existing = vulnerabilities.find((v) => v.cve_id === formattedCve);
    if (existing) {
      onSelectCve(existing.cve_id);
      if (!investigatedHistory.includes(existing.cve_id)) {
        setInvestigatedHistory((prev) => [existing.cve_id, ...prev.slice(0, 6)]);
      }
      setCveInput('');
      setStatusFeedback({
        type: 'success',
        text: `Loaded ${existing.cve_id} from database. Correlated with ${activeAsset.hostname} (Risk: ${existing.risk_score.toFixed(3)}).`,
      });
      return;
    }

    // 2. Custom CVE not in local list -> Ingest on the fly
    setIsAnalyzing(true);
    setStatusFeedback({
      type: 'info',
      text: `Querying NIST NVD & synthesizing contextual asset correlation for ${formattedCve}...`,
    });

    try {
      let fetchedScore = overrideCvss;
      let fetchedSeverity: Severity = 'CRITICAL';
      let fetchedDesc = `Custom security investigation target for ${formattedCve}. Requires immediate triage and telemetry correlation.`;
      let fetchedProducts = 'Enterprise Network Software';

      // Live NIST NVD API v2 attempt
      try {
        const res = await fetch(`https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=${formattedCve}`);
        if (res.ok) {
          const data = await res.json();
          const item = data.vulnerabilities?.[0]?.cve;
          if (item) {
            const metrics =
              item.metrics?.cvssMetricV31?.[0]?.cvssData ||
              item.metrics?.cvssMetricV30?.[0]?.cvssData;
            if (metrics) {
              fetchedScore = metrics.baseScore;
              fetchedSeverity = (metrics.baseSeverity || 'HIGH').toUpperCase() as Severity;
            }
            const desc = item.descriptions?.find((d: any) => d.lang === 'en')?.value;
            if (desc) fetchedDesc = desc;
          }
        }
      } catch (nvdErr) {
        console.warn('NVD live query fallback:', nvdErr);
      }

      // Auto-correlate with asset based on keywords
      let targetAssetId = overrideAssetId;
      const descLower = fetchedDesc.toLowerCase();
      if (descLower.includes('vpn') || descLower.includes('gateway') || descLower.includes('citrix') || descLower.includes('palo alto')) {
        targetAssetId = 'SRV-VPN-001';
      } else if (descLower.includes('database') || descLower.includes('sql') || descLower.includes('oracle') || descLower.includes('postgres')) {
        targetAssetId = 'SRV-DB-001';
      } else if (descLower.includes('web') || descLower.includes('apache') || descLower.includes('nginx') || descLower.includes('http')) {
        targetAssetId = 'SRV-WEB-001';
      }

      const assignedAsset = assets.find((a) => a.asset_id === targetAssetId) || assets[0];
      const customBreakdown = calculateFactorBreakdown(fetchedScore, overrideInKev, assignedAsset);
      const riskBand = getRiskBand(customBreakdown.total_score);

      const newVuln: Vulnerability = {
        cve_id: formattedCve,
        cvss_score: fetchedScore,
        cvss_severity: fetchedSeverity,
        cvss_vector: 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H',
        in_kev: overrideInKev,
        risk_score: customBreakdown.total_score,
        risk_band: riskBand,
        matched_asset_id: assignedAsset.asset_id,
        rank_cvss: 1,
        rank_contextual: 1,
        rank_displacement: 0,
        description: fetchedDesc,
        affected_products: fetchedProducts,
        published_date: new Date().toISOString().slice(0, 10),
      };

      if (onAddCustomCve) {
        onAddCustomCve(newVuln);
      } else {
        onSelectCve(newVuln.cve_id);
      }

      setInvestigatedHistory((prev) => [newVuln.cve_id, ...prev.filter((id) => id !== newVuln.cve_id).slice(0, 6)]);
      setCveInput('');
      setStatusFeedback({
        type: 'success',
        text: `Successfully analyzed ${formattedCve}! Mapped to ${assignedAsset.hostname} (${assignedAsset.ip}) with Contextual Risk ${newVuln.risk_score.toFixed(3)}.`,
      });
    } catch (err: any) {
      setStatusFeedback({
        type: 'error',
        text: `Analysis error for ${formattedCve}: ${err.message || 'Check connection'}`,
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-[#1D1D1F] dark:text-[#F5F5F7]">
          Threat Investigation &amp; Evidence Correlation
        </h1>
        <p className="text-xs sm:text-sm text-[#86868B] dark:text-[#A1A1A6] mt-1">
          Input any CVE to synthesize vulnerability mechanics with organizational coordinates, 2D plotted attack vectors, and SIEM security logs.
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

      {/* ───────────────────────────────────────────────────────────── */}
      {/* CORE CVE INVESTIGATION & CUSTOM INGESTION ENGINE               */}
      {/* ───────────────────────────────────────────────────────────── */}
      <div className="p-5 sm:p-6 rounded-3xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center space-x-2">
            <Crosshair className="w-4 h-4 text-[#0071E3]" />
            <h3 className="text-xs font-semibold uppercase tracking-wider text-[#1D1D1F] dark:text-[#F5F5F7]">
              Investigate Target CVE
            </h3>
          </div>
          <span className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
            Enter any CVE ID &bull; Instant multi-factor risk synthesis &amp; architecture plotting
          </span>
        </div>

        {/* Apple-style Command Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleAnalyzeCve();
          }}
          className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5"
        >
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-neutral-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={cveInput}
              onChange={(e) => setCveInput(e.target.value.toUpperCase())}
              placeholder="Enter CVE ID to investigate (e.g. CVE-2024-3400, CVE-2023-3519, CVE-2021-44228)..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-black/[0.03] dark:bg-white/[0.05] border border-black/10 dark:border-white/10 text-xs font-mono font-medium text-[#1D1D1F] dark:text-[#F5F5F7] placeholder:text-neutral-400 focus:outline-none focus:ring-2 focus:ring-[#0071E3] transition-all"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            <button
              type="submit"
              disabled={isAnalyzing}
              className="px-5 py-2.5 rounded-xl bg-[#0071E3] hover:bg-[#0077ED] text-white text-xs font-semibold shadow-xs flex items-center justify-center space-x-2 transition-all cursor-pointer disabled:opacity-50 shrink-0"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Analyze &amp; Investigate</span>
                </>
              )}
            </button>

            <button
              type="button"
              onClick={() => setShowTuning(!showTuning)}
              className={`p-2.5 rounded-xl border transition-all cursor-pointer ${
                showTuning
                  ? 'bg-black/10 dark:bg-white/15 border-black/20 dark:border-white/20 text-[#0071E3]'
                  : 'bg-black/[0.04] dark:bg-white/[0.08] border-black/10 dark:border-white/10 text-neutral-600 dark:text-neutral-300 hover:bg-black/[0.08] dark:hover:bg-white/[0.12]'
              }`}
              title="Fine-Tune Context & Asset Mapping"
            >
              <Sliders className="w-4 h-4" />
            </button>
          </div>
        </form>

        {/* Collapsible Context & Parameter Fine-Tuning Drawer */}
        {showTuning && (
          <div className="p-4 rounded-2xl bg-black/[0.02] dark:bg-white/[0.03] border border-black/8 dark:border-white/10 grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div>
              <label className="text-[10px] font-semibold uppercase text-neutral-500 block mb-1">
                Target Enterprise Asset
              </label>
              <select
                value={overrideAssetId}
                onChange={(e) => setOverrideAssetId(e.target.value)}
                className="w-full px-2.5 py-1.5 rounded-lg bg-white dark:bg-[#2C2C2E] border border-black/10 dark:border-white/10 text-xs font-mono"
              >
                {assets.map((a) => (
                  <option key={a.asset_id} value={a.asset_id}>
                    {a.hostname} ({a.asset_id} - {a.criticality})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-[10px] font-semibold uppercase text-neutral-500 block mb-1">
                CVSS v3.1 Baseline Score ({overrideCvss})
              </label>
              <input
                type="range"
                min="1.0"
                max="10.0"
                step="0.1"
                value={overrideCvss}
                onChange={(e) => setOverrideCvss(parseFloat(e.target.value))}
                className="w-full accent-[#0071E3]"
              />
            </div>

            <div className="flex flex-col justify-center">
              <label className="text-[10px] font-semibold uppercase text-neutral-500 block mb-1">
                CISA KEV Wild Exploitation
              </label>
              <label className="flex items-center space-x-2 cursor-pointer mt-1">
                <input
                  type="checkbox"
                  checked={overrideInKev}
                  onChange={(e) => setOverrideInKev(e.target.checked)}
                  className="rounded text-[#0071E3] focus:ring-0"
                />
                <span className="text-xs font-medium text-neutral-700 dark:text-neutral-300">
                  Actively Exploited (KEV Listed)
                </span>
              </label>
            </div>
          </div>
        )}

        {/* Quick Benchmark Presets Row */}
        <div className="pt-1 flex flex-wrap items-center gap-1.5 text-xs">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-[#86868B] dark:text-[#A1A1A6] mr-1">
            Quick Benchmarks:
          </span>
          {PRESET_BENCHMARKS.map((preset) => {
            const isActive = activeVuln.cve_id === preset.id;
            return (
              <button
                key={preset.id}
                type="button"
                onClick={() => handleAnalyzeCve(preset.id)}
                className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all cursor-pointer flex items-center space-x-1 border ${
                  isActive
                    ? 'bg-[#0071E3] text-white border-[#0071E3] shadow-xs'
                    : 'bg-black/[0.03] dark:bg-white/[0.05] hover:bg-black/[0.07] dark:hover:bg-white/[0.1] text-neutral-700 dark:text-neutral-300 border-black/5 dark:border-white/10'
                }`}
              >
                <span>{preset.name}</span>
                <span className="font-mono text-[10px] opacity-75">({preset.id})</span>
              </button>
            );
          })}
        </div>

        {/* Feedback / Notification Banner */}
        {statusFeedback && (
          <div
            className={`p-3 rounded-xl border text-xs flex items-center space-x-2 ${
              statusFeedback.type === 'success'
                ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-800 dark:text-emerald-300'
                : statusFeedback.type === 'info'
                ? 'bg-blue-500/10 border-blue-500/20 text-blue-800 dark:text-blue-300'
                : 'bg-red-500/10 border-red-500/20 text-red-800 dark:text-red-300'
            }`}
          >
            {statusFeedback.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600 dark:text-emerald-400" />
            ) : statusFeedback.type === 'info' ? (
              <Loader2 className="w-4 h-4 shrink-0 animate-spin text-[#0071E3]" />
            ) : (
              <AlertCircle className="w-4 h-4 shrink-0 text-red-600 dark:text-red-400" />
            )}
            <span>{statusFeedback.text}</span>
          </div>
        )}

        {/* Active Target Banner — Only showing the single investigated CVE */}
        <div className="p-3.5 rounded-2xl bg-[#0071E3]/5 dark:bg-[#0071E3]/10 border border-[#0071E3]/20 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="font-semibold text-neutral-500 dark:text-neutral-400">
              Active Investigation:
            </span>
            <span className="font-mono font-bold text-sm text-[#0071E3] dark:text-[#389BF2]">
              {activeVuln.cve_id}
            </span>
            <span className="px-1.5 py-0.5 rounded bg-black/5 dark:bg-white/10 font-mono text-[10px] text-neutral-600 dark:text-neutral-300">
              Risk: {activeVuln.risk_score.toFixed(3)} ({activeVuln.risk_band})
            </span>
          </div>

          <div className="flex items-center space-x-2 text-[11px] text-neutral-600 dark:text-neutral-400">
            <span>Target Host:</span>
            <span className="font-mono font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">
              {activeAsset.hostname} ({activeAsset.ip})
            </span>
            {activeVuln.in_kev && (
              <span className="px-1.5 py-0.5 rounded bg-red-500/10 text-red-600 dark:text-red-400 font-bold text-[9px]">
                KEV
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Hero Scoreboard Component */}
      <HeroScoreboard vuln={activeVuln} asset={activeAsset} breakdown={breakdown} />

      {/* Vulnerability Mechanics & Plotted Attack Architecture Map */}
      <VulnerabilityPropagationMap
        vuln={activeVuln}
        asset={activeAsset}
        allAssets={assets}
        sourceIp={signalLogs[0]?.source_ip || '198.51.100.44'}
      />

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
          className="px-5 py-2.5 rounded-xl bg-[#0071E3] hover:bg-[#0077ED] text-white text-xs font-semibold shadow-md flex items-center space-x-2 transition-all duration-150 whitespace-nowrap cursor-pointer"
        >
          <Sparkles className="w-4 h-4" />
          <span>Run AI Investigation with Gemini</span>
        </button>
      </div>
    </div>
  );
};
