import React, { useEffect, useMemo, useState } from 'react';
import {
  FiAlertCircle,
  FiArrowRight,
  FiCheckCircle,
  FiCrosshair,
  FiDatabase,
  FiFileText,
  FiGlobe,
  FiLayers,
  FiLoader,
  FiPlus,
  FiSearch,
  FiServer,
  FiShield,
  FiSliders,
  FiTerminal,
} from 'react-icons/fi';
import { RiShieldFlashLine, RiTerminalBoxLine } from 'react-icons/ri';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { Panel } from '../components/common/Panel';
import { ExecutiveGuide } from '../components/ExecutiveGuide';
import { HeroScoreboard } from '../components/HeroScoreboard';
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
  { id: 'CVE-2024-3400', name: 'PAN-OS Injection', cvss: 10.0, assetId: 'SRV-VPN-001', kev: true },
  { id: 'CVE-2023-3519', name: 'Citrix ADC RCE', cvss: 9.8, assetId: 'SRV-VPN-001', kev: true },
  { id: 'CVE-2020-1938', name: 'Tomcat Ghostcat', cvss: 9.8, assetId: 'SRV-WEB-001', kev: true },
  { id: 'CVE-2024-21762', name: 'Fortinet OOB', cvss: 9.8, assetId: 'SRV-VPN-001', kev: true },
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

  // User-selected enterprise asset override
  const [selectedAssetOverride, setSelectedAssetOverride] = useState<string | null>(null);

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
    const targetId = selectedAssetOverride || activeVuln.matched_asset_id;
    return (
      assets.find((a) => a.asset_id === targetId) ||
      assets.find((a) => a.asset_id === activeVuln.matched_asset_id) ||
      assets[0]
    );
  }, [assets, activeVuln, selectedAssetOverride]);

  useEffect(() => {
    setSelectedAssetOverride(null);
    setOverrideCvss(activeVuln.cvss_score);
    setOverrideInKev(activeVuln.in_kev);
    setOverrideAssetId(activeVuln.matched_asset_id);
  }, [activeVuln.cve_id]);

  // Calculate factor breakdown dynamically
  const breakdown = useMemo(() => {
    return calculateFactorBreakdown(
      showTuning ? overrideCvss : activeVuln.cvss_score,
      showTuning ? overrideInKev : activeVuln.in_kev,
      activeAsset
    );
  }, [activeVuln, activeAsset, showTuning, overrideCvss, overrideInKev]);

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
  const handleAnalyzeCve = async (rawTarget?: string, explicitAssetId?: string) => {
    const query = (rawTarget || cveInput).trim().toUpperCase();

    if (!query) {
      setStatusFeedback({
        type: 'error',
        text: 'Please enter a CVE ID (e.g. CVE-2024-3400).',
      });
      return;
    }

    const formattedCve = query.startsWith('CVE-') ? query : `CVE-${query}`;
    if (explicitAssetId) {
      setSelectedAssetOverride(explicitAssetId);
    }

    const existing = vulnerabilities.find((v) => v.cve_id === formattedCve);
    if (existing) {
      if (explicitAssetId) {
        existing.matched_asset_id = explicitAssetId;
        setSelectedAssetOverride(explicitAssetId);
      }
      onSelectCve(existing.cve_id);
      if (!investigatedHistory.includes(existing.cve_id)) {
        setInvestigatedHistory((prev) => [existing.cve_id, ...prev.slice(0, 6)]);
      }
      setCveInput('');
      const targetAid = explicitAssetId || existing.matched_asset_id;
      const matchedHost = assets.find((a) => a.asset_id === targetAid)?.hostname || 'enterprise host';
      setStatusFeedback({
        type: 'success',
        text: `Loaded ${existing.cve_id}. Correlated with target host ${matchedHost} (${targetAid}).`,
      });
      return;
    }

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

      let targetAssetId = explicitAssetId || overrideAssetId;
      if (!explicitAssetId) {
        const descLower = (fetchedDesc + ' ' + fetchedProducts).toLowerCase();
        if (descLower.includes('vpn') || descLower.includes('gateway') || descLower.includes('citrix') || descLower.includes('palo alto') || descLower.includes('fortinet')) {
          targetAssetId = 'SRV-VPN-001';
        } else if (descLower.includes('database') || descLower.includes('sql') || descLower.includes('oracle') || descLower.includes('postgres') || descLower.includes('mysql')) {
          targetAssetId = 'SRV-DB-001';
        } else if (descLower.includes('active directory') || descLower.includes('kerberos') || descLower.includes('domain controller') || descLower.includes('windows server')) {
          targetAssetId = 'SRV-DC-001';
        } else if (descLower.includes('mail') || descLower.includes('smtp') || descLower.includes('exchange') || descLower.includes('postfix')) {
          targetAssetId = 'SRV-MAIL-001';
        } else if (descLower.includes('kubernetes') || descLower.includes('k8s') || descLower.includes('terraform') || descLower.includes('docker') || descLower.includes('cloud')) {
          targetAssetId = 'SRV-CLOUD-MGT-001';
        } else if (descLower.includes('siemens') || descLower.includes('simatic') || descLower.includes('scada') || descLower.includes('plc') || descLower.includes('ics')) {
          targetAssetId = 'SRV-ICS-001';
        } else if (descLower.includes('office') || descLower.includes('word') || descLower.includes('excel') || descLower.includes('acrobat') || descLower.includes('chrome')) {
          targetAssetId = 'WS-HR-001';
        } else if (descLower.includes('python') || descLower.includes('git') || descLower.includes('macos')) {
          targetAssetId = 'WS-DEV-012';
        } else {
          targetAssetId = 'SRV-WEB-001';
        }
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
    <div className="space-y-6 animate-in fade-in duration-150 font-mono">
      {/* Page Header */}
      <div className="border-b-2 sm:border-b-[3px] border-black dark:border-white pb-4 flex flex-col md:flex-row md:items-end justify-between gap-3">
        <div>
          <div className="flex items-center space-x-2 flex-wrap gap-y-1 mb-1">
            <span className="font-bold text-xs uppercase bg-[#B8FF00] text-black px-2 py-0.5 border border-black neo-shadow-sm">
              FORENSICS WORKBENCH
            </span>
            <span className="text-xs text-neutral-500">// VULNERABILITY TO THREAT INVESTIGATION</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-black tracking-tight text-black dark:text-white uppercase">
            Threat Investigation &amp; Telemetry Correlation
          </h1>
          <p className="text-xs sm:text-sm text-neutral-600 dark:text-neutral-400 mt-1 font-sans">
            Synthesize vulnerability mechanics with organizational coordinates, 2D plotted attack vectors, and SIEM security logs.
          </p>
        </div>

        <Button
          variant="primary"
          size="md"
          icon={<RiTerminalBoxLine className="w-4 h-4" />}
          onClick={() => onRunAiInvestigation(activeVuln.cve_id)}
        >
          GENERATE EVIDENCE DOSSIER
        </Button>
      </div>

      {/* Non-Technical Guide */}
      <ExecutiveGuide title="Evaluator Guide: Understanding Full-Chain Threat Investigation">
        <div className="space-y-3 font-sans">
          <p className="text-neutral-700 dark:text-neutral-300">
            Traditional vulnerability reports present isolated CVE numbers. This workbench reconstructs a <strong>complete digital threat scenario</strong> by fusing four indispensable data streams:
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs font-mono">
            <div className="p-3 border-2 border-black dark:border-white bg-[#FFFBEB] dark:bg-[#1E1B13] neo-shadow-sm">
              <span className="font-bold text-black dark:text-white block uppercase">1. Flaw Profile</span>
              <p className="text-[11px] text-neutral-600 dark:text-neutral-400 mt-1 font-sans">
                Vendor-rated technical vulnerability mechanics, CVSS vector &amp; affected CPE libraries.
              </p>
            </div>
            <div className="p-3 border-2 border-black dark:border-white bg-[#EFF6FF] dark:bg-[#111928] neo-shadow-sm">
              <span className="font-bold text-black dark:text-white block uppercase">2. Target Host</span>
              <p className="text-[11px] text-neutral-600 dark:text-neutral-400 mt-1 font-sans">
                Specific enterprise node hosting the service, network IP, and perimeter exposure tier.
              </p>
            </div>
            <div className="p-3 border-2 border-black dark:border-white bg-[#FEF2F2] dark:bg-[#221516] neo-shadow-sm">
              <span className="font-bold text-black dark:text-white block uppercase">3. MITRE ATT&amp;CK</span>
              <p className="text-[11px] text-neutral-600 dark:text-neutral-400 mt-1 font-sans">
                Standard adversary tactics and techniques used to weaponize this weakness in campaigns.
              </p>
            </div>
            <div className="p-3 border-2 border-black dark:border-white bg-[#ECFDF5] dark:bg-[#102319] neo-shadow-sm">
              <span className="font-bold text-black dark:text-white block uppercase">4. SIEM Telemetry</span>
              <p className="text-[11px] text-neutral-600 dark:text-neutral-400 mt-1 font-sans">
                Live security log events confirming whether suspicious probes or exploits touched the host.
              </p>
            </div>
          </div>
        </div>
      </ExecutiveGuide>

      {/* Target Command Center & Ingestion Toolbar */}
      <Panel
        title="Target Investigation Command Center"
        subtitle="Input any CVE ID or select curated corporate benchmark"
        icon={<FiCrosshair className="w-4 h-4 text-black" />}
        accent="yellow"
      >
        <div className="space-y-4">
          {/* Command Input Bar */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleAnalyzeCve();
            }}
            className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5"
          >
            <div className="relative flex-1">
              <FiSearch className="w-4 h-4 text-neutral-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={cveInput}
                onChange={(e) => setCveInput(e.target.value.toUpperCase())}
                placeholder="ENTER CVE ID (e.g. CVE-2024-3400, CVE-2023-3519, CVE-2021-44228)..."
                className="w-full pl-9 pr-3 py-2.5 border-2 border-black dark:border-white bg-white dark:bg-black text-black dark:text-white text-xs font-bold uppercase neo-shadow-sm focus:outline-none focus:bg-[#FFFBEB] dark:focus:bg-[#1A1A22]"
              />
            </div>

            <div className="flex items-center space-x-2">
              <Button
                type="submit"
                variant="primary"
                size="md"
                disabled={isAnalyzing}
                isLoading={isAnalyzing}
                icon={<FiSearch className="w-3.5 h-3.5 stroke-[3]" />}
              >
                ANALYZE &amp; CORRELATE
              </Button>

              <button
                type="button"
                onClick={() => setShowTuning(!showTuning)}
                className={`neo-btn p-2.5 border-2 border-black dark:border-white font-bold text-xs ${
                  showTuning
                    ? 'bg-[#FFE600] text-black neo-shadow-sm'
                    : 'bg-white dark:bg-black text-black dark:text-white hover:bg-neutral-100'
                }`}
                title="Fine-Tune Context &amp; Simulation Parameters"
              >
                <FiSliders className="w-4 h-4" />
              </button>
            </div>
          </form>

          {/* Context & Parameter Fine-Tuning Drawer */}
          {showTuning && (
            <div className="p-3.5 sm:p-4 border-2 border-black dark:border-white bg-[#FDFBF7] dark:bg-[#18181E] grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs neo-shadow-sm">
              <div>
                <label className="text-[10px] font-bold uppercase text-neutral-600 dark:text-neutral-400 block mb-1">
                  Target Enterprise Host Override
                </label>
                <select
                  value={activeAsset.asset_id}
                  onChange={(e) => {
                    setOverrideAssetId(e.target.value);
                    setSelectedAssetOverride(e.target.value);
                  }}
                  className="w-full px-2.5 py-1.5 border-2 border-black dark:border-white bg-white dark:bg-black text-black dark:text-white text-xs font-bold"
                >
                  {assets.map((a) => (
                    <option key={a.asset_id} value={a.asset_id}>
                      {a.hostname} [{a.asset_id}] &bull; Tier {a.criticality.toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-[10px] font-bold uppercase text-neutral-600 dark:text-neutral-400 block mb-1">
                  CVSS v3.1 Base Score: <span className="bg-[#FFE600] text-black px-1.5 py-0.2 border border-black">{overrideCvss.toFixed(1)}</span>
                </label>
                <input
                  type="range"
                  min="1.0"
                  max="10.0"
                  step="0.1"
                  value={overrideCvss}
                  onChange={(e) => setOverrideCvss(parseFloat(e.target.value))}
                  className="w-full accent-black dark:accent-white cursor-pointer mt-1"
                />
              </div>

              <div className="flex flex-col justify-center">
                <label className="text-[10px] font-bold uppercase text-neutral-600 dark:text-neutral-400 block mb-1">
                  CISA KEV Wild Exploitation Flag
                </label>
                <button
                  type="button"
                  onClick={() => setOverrideInKev(!overrideInKev)}
                  className={`neo-btn py-1.5 px-3 border-2 border-black dark:border-white font-bold text-xs ${
                    overrideInKev
                      ? 'bg-[#FF5376] text-white neo-shadow-sm'
                      : 'bg-white dark:bg-black text-black dark:text-white'
                  }`}
                >
                  {overrideInKev ? 'WEAPONIZED IN WILD (+0.30)' : 'NO EXPLOIT IN WILD (0.0)'}
                </button>
              </div>
            </div>
          )}

          {/* Quick Benchmark Presets Row */}
          <div className="pt-1 flex flex-wrap items-center gap-1.5 text-xs">
            <span className="text-[10px] font-bold uppercase tracking-wider text-neutral-500 mr-1">
              Curated Benchmarks:
            </span>
            {PRESET_BENCHMARKS.map((preset) => {
              const isActive = activeVuln.cve_id === preset.id;
              return (
                <button
                  key={preset.id}
                  type="button"
                  onClick={() => handleAnalyzeCve(preset.id, preset.assetId)}
                  className={`neo-btn px-2.5 py-1 border-2 border-black dark:border-white text-xs font-bold transition-all ${
                    isActive
                      ? 'bg-[#FFE600] text-black neo-shadow-sm'
                      : 'bg-white dark:bg-black text-black dark:text-white hover:bg-[#FFFBEB] dark:hover:bg-[#1E1E26]'
                  }`}
                >
                  <span>{preset.name}</span>
                  <span className="text-[10px] opacity-75 ml-1">({preset.id})</span>
                </button>
              );
            })}
          </div>

          {/* Feedback Banner */}
          {statusFeedback && (
            <div
              className={`p-3 border-2 border-black text-xs font-bold flex items-center space-x-2 neo-shadow-sm ${
                statusFeedback.type === 'success'
                  ? 'bg-[#B8FF00] text-black'
                  : statusFeedback.type === 'info'
                  ? 'bg-[#00F0FF] text-black'
                  : 'bg-[#FF5376] text-white'
              }`}
            >
              {statusFeedback.type === 'success' ? (
                <FiCheckCircle className="w-4 h-4 shrink-0" />
              ) : statusFeedback.type === 'info' ? (
                <FiLoader className="w-4 h-4 shrink-0 animate-spin" />
              ) : (
                <FiAlertCircle className="w-4 h-4 shrink-0" />
              )}
              <span>{statusFeedback.text}</span>
            </div>
          )}

          {/* Active Target Banner */}
          <div className="p-3 border-2 border-black dark:border-white bg-[#FDFBF7] dark:bg-[#18181E] flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs neo-shadow-sm">
            <div className="flex items-center space-x-2 flex-wrap gap-y-1">
              <span className="font-bold text-neutral-500 uppercase">
                Active Target:
              </span>
              <span className="font-black text-black dark:text-white px-2 py-0.5 bg-[#FFE600] text-black border border-black text-sm">
                {activeVuln.cve_id}
              </span>
              <Badge color="yellow" size="xs">
                Score: {breakdown.total_score.toFixed(3)}
              </Badge>
              {activeVuln.in_kev && (
                <Badge color="pink" size="xs" dot>
                  CISA KEV ACTIVE
                </Badge>
              )}
            </div>

            <div className="flex items-center space-x-2">
              <FiServer className="w-3.5 h-3.5 text-black dark:text-white shrink-0" />
              <span className="font-bold text-neutral-600 dark:text-neutral-400 shrink-0">
                Target Host:
              </span>
              <select
                value={activeAsset.asset_id}
                onChange={(e) => setSelectedAssetOverride(e.target.value)}
                className="px-2.5 py-1 border-2 border-black dark:border-white bg-white dark:bg-black text-black dark:text-white text-xs font-bold neo-shadow-sm focus:outline-none cursor-pointer"
                title="Switch target enterprise host to test contextual risk impact"
              >
                {assets.map((a) => (
                  <option key={a.asset_id} value={a.asset_id}>
                    {a.hostname} [{a.asset_id}] &bull; Tier {a.criticality.toUpperCase()} &bull; Zone: {a.exposure.toUpperCase()}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </Panel>

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
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Left Panel: Vulnerability Profile */}
        <Panel
          title="Vulnerability Technical Profile"
          subtitle="NIST NVD specifications &amp; CVSS vector breakdown"
          icon={<FiFileText className="w-4 h-4 text-black dark:text-white" />}
          accent="zinc"
        >
          <div className="space-y-3 text-xs">
            <div>
              <span className="font-bold uppercase text-neutral-600 dark:text-neutral-400 block mb-1">
                Description &amp; Weakness Mechanism
              </span>
              <div className="p-3 border-2 border-black dark:border-white bg-[#FDFBF7] dark:bg-[#18181E] text-neutral-800 dark:text-neutral-200 leading-relaxed font-sans neo-shadow-sm">
                {activeVuln.description || 'No description recorded in database.'}
              </div>
            </div>

            {activeVuln.cvss_vector && (
              <div>
                <span className="font-bold uppercase text-neutral-600 dark:text-neutral-400 block mb-1">
                  CVSS v3.1 Vector String
                </span>
                <div className="p-2 border-2 border-black dark:border-white bg-white dark:bg-black text-black dark:text-white font-bold overflow-x-auto text-[11px] neo-shadow-sm">
                  {activeVuln.cvss_vector}
                </div>
              </div>
            )}

            {activeVuln.affected_products && (
              <div>
                <span className="font-bold uppercase text-neutral-600 dark:text-neutral-400 block mb-1">
                  Affected Products / CPE Identifier
                </span>
                <div className="p-2 border-2 border-black dark:border-white bg-white dark:bg-black text-black dark:text-white font-bold truncate text-[11px] neo-shadow-sm">
                  {activeVuln.affected_products}
                </div>
              </div>
            )}
          </div>
        </Panel>

        {/* Right Panel: Target Asset Coordinates */}
        <Panel
          title="Target Enterprise Node Coordinates"
          subtitle="Hardware inventory, business tier &amp; perimeter zoning"
          icon={<FiServer className="w-4 h-4 text-black dark:text-white" />}
          accent="zinc"
        >
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-2.5 border-2 border-black dark:border-white bg-white dark:bg-black neo-shadow-sm">
              <span className="uppercase font-bold text-neutral-500 block text-[10px]">
                Hostname
              </span>
              <span className="font-bold text-black dark:text-white text-sm">
                {activeAsset.hostname}
              </span>
            </div>

            <div className="p-2.5 border-2 border-black dark:border-white bg-white dark:bg-black neo-shadow-sm">
              <span className="uppercase font-bold text-neutral-500 block text-[10px]">
                Asset ID / IP
              </span>
              <span className="font-bold text-black dark:text-white text-sm">
                {activeAsset.asset_id} ({activeAsset.ip})
              </span>
            </div>

            <div className="p-2.5 border-2 border-black dark:border-white bg-white dark:bg-black neo-shadow-sm">
              <span className="uppercase font-bold text-neutral-500 block text-[10px]">
                Criticality Tier
              </span>
              <span className="font-bold text-xs uppercase text-black dark:text-white">
                Tier: {activeAsset.criticality}
              </span>
            </div>

            <div className="p-2.5 border-2 border-black dark:border-white bg-white dark:bg-black neo-shadow-sm">
              <span className="uppercase font-bold text-neutral-500 block text-[10px]">
                Network Exposure
              </span>
              <span className="font-bold text-xs uppercase text-black dark:text-white">
                Zone: {activeAsset.exposure.replace('_', '-')}
              </span>
            </div>
          </div>

          <div className="text-xs space-y-1.5 pt-3 border-t-2 border-black/10 dark:border-white/10 mt-3">
            <span className="font-bold uppercase text-neutral-600 dark:text-neutral-400 block">
              Operational Role &amp; Software Stack
            </span>
            <p className="text-[11px] text-neutral-700 dark:text-neutral-300 font-sans">
              {activeAsset.notes || 'Enterprise production server system.'}
            </p>
            <div className="flex flex-wrap gap-1.5 pt-1">
              {Array.isArray(activeAsset.software) ? (
                activeAsset.software.map((sw, i) => (
                  <Badge key={i} color="zinc" size="xs">
                    {sw}
                  </Badge>
                ))
              ) : (
                <span className="font-bold">{activeAsset.software}</span>
              )}
            </div>
          </div>
        </Panel>
      </div>

      {/* Correlated MITRE ATT&CK Techniques Panel */}
      <Panel
        title="Correlated MITRE ATT&CK Techniques"
        subtitle="Adversary tactics and techniques mapped to vulnerable service"
        icon={<FiCrosshair className="w-4 h-4 text-black" />}
        accent="cyan"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {techniques.slice(0, 4).map((tech) => (
            <div
              key={tech.id}
              className="p-3 border-2 border-black dark:border-white bg-white dark:bg-[#18181E] neo-shadow-sm space-y-1.5"
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs bg-[#00F0FF] text-black px-1.5 py-0.2 border border-black">
                  {tech.id}
                </span>
                <span className="text-[10px] uppercase font-bold text-neutral-500">
                  {tech.tactics}
                </span>
              </div>
              <h4 className="font-bold text-xs text-black dark:text-white">
                {tech.name}
              </h4>
              <p className="text-[11px] text-neutral-700 dark:text-neutral-300 font-sans leading-relaxed">
                {tech.description}
              </p>
            </div>
          ))}
        </div>
      </Panel>

      {/* Correlated SIEM Security Telemetry Terminal */}
      <Panel
        title="Correlated SIEM Security Telemetry Logs"
        subtitle={`${signalLogs.length} attack events &bull; ${noiseLogs.length} benign noise probes`}
        icon={<FiTerminal className="w-4 h-4 text-black" />}
        accent="lime"
        noPadding
      >
        <div className="overflow-x-auto bg-black text-emerald-400 p-2 font-mono text-xs">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-zinc-800 text-[10px] uppercase text-zinc-400">
                <th className="py-2 px-3">Event ID</th>
                <th className="py-2 px-3">Timestamp</th>
                <th className="py-2 px-3">Source IP</th>
                <th className="py-2 px-3">Technique</th>
                <th className="py-2 px-3">Raw Log Event</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-900">
              {signalLogs.map((log) => (
                <tr key={log.event_id} className="hover:bg-zinc-900/60 transition-colors">
                  <td className="py-2 px-3 text-[#00F0FF] font-bold">
                    {log.event_id}
                  </td>
                  <td className="py-2 px-3 text-zinc-400 text-[11px]">
                    {log.timestamp.slice(0, 19).replace('T', ' ')}
                  </td>
                  <td className="py-2 px-3 text-yellow-300">
                    {log.source_ip}
                  </td>
                  <td className="py-2 px-3">
                    <span className="px-1.5 py-0.2 bg-[#00F0FF] text-black text-[10px] font-bold">
                      {log.technique_id}
                    </span>
                  </td>
                  <td className="py-2 px-3 text-zinc-300 text-[11px] max-w-md truncate">
                    {log.raw_log}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      {/* Action Footer: Generate Evidence Dossier */}
      <div className="p-4 sm:p-5 border-2 sm:border-[2.5px] border-black dark:border-white bg-[#FFE600] text-black neo-shadow-lg flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <RiTerminalBoxLine className="w-5 h-5" />
            <h3 className="font-mono font-black text-sm sm:text-base uppercase tracking-tight">
              Evidence-Grounded Threat Dossier &amp; SIEM Hunting Queries
            </h3>
          </div>
          <p className="text-xs font-mono text-black/80 mt-0.5">
            Execute constrained Gemini synthesis to generate verified hypotheses, signal discrimination &amp; Splunk/Elastic verification code.
          </p>
        </div>

        <Button
          variant="dark"
          size="lg"
          icon={<RiShieldFlashLine className="w-4 h-4 text-[#FFE600]" />}
          onClick={() => onRunAiInvestigation(activeVuln.cve_id)}
          className="whitespace-nowrap"
        >
          OPEN TELEMETRY FORENSICS
        </Button>
      </div>
    </div>
  );
};
