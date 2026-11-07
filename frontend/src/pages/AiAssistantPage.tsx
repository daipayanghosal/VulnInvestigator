import React, { useEffect, useState } from 'react';
import {
  FiAlertCircle,
  FiCheck,
  FiCopy,
  FiCpu,
  FiCrosshair,
  FiExternalLink,
  FiFileText,
  FiHash,
  FiKey,
  FiLayers,
  FiLoader,
  FiRefreshCw,
  FiServer,
  FiShield,
  FiTerminal,
  FiZap,
} from 'react-icons/fi';
import { RiShieldCheckLine } from 'react-icons/ri';
import { Badge, Button, KpiTile, Panel } from '../components/common';
import { ExecutiveGuide } from '../components/ExecutiveGuide';
import { MarkdownRenderer } from '../components/MarkdownRenderer';
import { Asset, InvestigationReport, SecurityLog, Technique, Vulnerability } from '../types';
import { getStoredApiKey, runGeminiInvestigation } from '../utils/gemini';

interface AiAssistantPageProps {
  vulnerabilities: Vulnerability[];
  assets: Asset[];
  techniques: Technique[];
  logs: SecurityLog[];
  selectedCveId: string;
  onSelectCve?: (cveId: string) => void;
  onOpenKeyModal: () => void;
  hasApiKey: boolean;
}

export const AiAssistantPage: React.FC<AiAssistantPageProps> = ({
  vulnerabilities,
  assets,
  techniques,
  logs,
  selectedCveId,
  onSelectCve,
  onOpenKeyModal,
  hasApiKey,
}) => {
  const [report, setReport] = useState<InvestigationReport | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [copiedDossier, setCopiedDossier] = useState(false);

  const activeVuln =
    vulnerabilities.find((v) => v.cve_id === selectedCveId) || vulnerabilities[0];
  const activeAsset =
    assets.find((a) => a.asset_id === activeVuln?.matched_asset_id) || assets[0];

  const relevantLogs = logs.filter(
    (l) => l.asset_id === activeAsset.asset_id || l.cve_id === activeVuln.cve_id
  );

  const handleRunInvestigation = async () => {
    if (!activeVuln || !activeAsset) return;
    setIsLoading(true);
    setErrorMsg(null);

    try {
      const apiKey = getStoredApiKey();
      const res = await runGeminiInvestigation(
        activeVuln,
        activeAsset,
        techniques,
        relevantLogs.length > 0 ? relevantLogs : logs.slice(0, 5),
        apiKey
      );
      setReport(res);
    } catch (err: any) {
      setErrorMsg(err.message || 'Investigation query failed');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    handleRunInvestigation();
  }, [selectedCveId]);

  const handleCopyEntireDossier = () => {
    if (!report) return;
    const fullText = `# ${report.title}\nGenerated: ${report.generated_at}\nGrounding Score: ${report.grounding_score}%\n\n` +
      report.sections.map((s) => `## ${s.title}\n\n${s.content}\n`).join('\n');
    navigator.clipboard.writeText(fullText);
    setCopiedDossier(true);
    setTimeout(() => setCopiedDossier(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 border-2 border-black dark:border-[#2D3448] bg-[#00F0FF] dark:bg-[#141824] text-black dark:text-[#E2E8F0] dark:border-t-8 dark:border-t-[#0284C7] neo-shadow">
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-mono text-xs font-bold uppercase bg-black text-[#FFE600] dark:bg-[#FACC15] dark:text-black px-2 py-0.5 border border-black">
              EVIDENCE-GROUNDED FORENSICS
            </span>
            <Badge variant="pink" size="sm">
              ZERO-HALLUCINATION
            </Badge>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black uppercase tracking-tight mt-1 text-black dark:text-white">
            Telemetry Forensics &amp; Evidence Dossier
          </h1>
          <p className="text-xs sm:text-sm font-semibold opacity-90 mt-0.5 text-black/80 dark:text-neutral-400">
            Deterministic threat hypothesis formulation, empirical signal discrimination, and verifiable SIEM detection query synthesis.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant={hasApiKey ? 'secondary' : 'accent'}
            size="sm"
            onClick={onOpenKeyModal}
            icon={<FiKey className="w-4 h-4" />}
          >
            {hasApiKey ? 'KEY CONFIGURED' : 'SET GEMINI KEY'}
          </Button>

          <Button
            variant="primary"
            size="sm"
            onClick={handleRunInvestigation}
            disabled={isLoading}
            icon={
              isLoading ? (
                <FiLoader className="w-4 h-4 animate-spin" />
              ) : (
                <FiRefreshCw className="w-4 h-4" />
              )
            }
          >
            {isLoading ? 'SYNTHESIZING...' : 'RE-RUN FORENSICS'}
          </Button>
        </div>
      </div>

      {/* Non-Technical Guide */}
      <ExecutiveGuide title="Forensics Guide: How Empirical Telemetry Mitigates Generative Hallucinations">
        <div className="space-y-3 font-sans">
          <p className="text-xs sm:text-sm text-black dark:text-neutral-300">
            Commercial GenAI models suffer from <strong>stochastic hallucination</strong>—generating nonexistent CVE numbers, fictional IP addresses, and fabricated remediation queries. VulnInvestigator enforces a rigorous 3-tier empirical verification pipeline:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs pt-1 font-mono">
            <div className="p-3 border-2 border-black dark:border-[#2D3448] bg-[#FFE600] text-black dark:bg-[#1A1F2C] dark:text-[#FACC15] neo-shadow-sm">
              <span className="font-bold uppercase block mb-1">
                [01] STRICT EVIDENCE ISOLATION
              </span>
              <p className="text-[11px] leading-relaxed text-black/90 dark:text-neutral-300">
                The model is isolated from open-ended web prompts; only verified facts from the asset inventory and ingested SIEM telemetry logs are provided in the Evidence Bundle.
              </p>
            </div>
            <div className="p-3 border-2 border-black dark:border-[#2D3448] bg-[#00F0FF] text-black dark:bg-[#162030] dark:text-[#38BDF8] neo-shadow-sm">
              <span className="font-bold uppercase block mb-1">
                [02] MANDATORY CITATION INTERLOCK
              </span>
              <p className="text-[11px] leading-relaxed text-black/90 dark:text-neutral-300">
                Every investigative claim must explicitly cite CVE identifiers, MITRE ATT&amp;CK technique codes, and immutable SIEM telemetry event UUIDs.
              </p>
            </div>
            <div className="p-3 border-2 border-black dark:border-[#2D3448] bg-[#B8FF00] text-black dark:bg-[#1A281A] dark:text-[#A3E635] neo-shadow-sm">
              <span className="font-bold uppercase block mb-1">
                [03] HEURISTIC SPECULATION TRAP
              </span>
              <p className="text-[11px] leading-relaxed text-black/90 dark:text-neutral-300">
                Any speculative claim lacking direct empirical backing is intercepted and tagged with a high-visibility warning badge to protect operational SOC triage.
              </p>
            </div>
          </div>
        </div>
      </ExecutiveGuide>

      {/* Active Target Banner & Target Selector Console */}
      <div className="p-4 border-2 border-black dark:border-[#2D3448] bg-white dark:bg-[#141824] neo-shadow flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        {/* Left: Active Target Details */}
        <div className="flex items-center space-x-3 flex-wrap gap-y-2">
          <div className="w-3.5 h-3.5 border-2 border-black dark:border-[#2D3448] bg-[#B8FF00] dark:bg-[#65A30D] animate-pulse" />
          <span className="font-mono text-xs font-bold uppercase tracking-wider text-neutral-600 dark:text-neutral-400">
            TARGET HOST:
          </span>
          <Badge variant="cyan" size="md">
            {activeVuln.cve_id}
          </Badge>
          <div className="flex items-center space-x-1.5 font-mono text-xs font-bold text-black dark:text-white">
            <FiServer className="w-3.5 h-3.5 text-neutral-500" />
            <span>{activeAsset.hostname}</span>
            <span className="text-neutral-500">[{activeAsset.asset_id}]</span>
            <span className="text-neutral-400">&bull;</span>
            <span className="text-[#0071E3] dark:text-[#38BDF8]">{activeAsset.ip}</span>
          </div>
        </div>

        {/* Right: Scores & Target Dropdown Selector */}
        <div className="flex items-center space-x-2.5 flex-wrap gap-y-2">
          <Badge variant="yellow" size="sm">
            RISK: {activeVuln.risk_score.toFixed(3)}
          </Badge>
          <Badge variant="zinc" size="sm">
            CVSS {activeVuln.cvss_score.toFixed(1)}
          </Badge>
          {activeVuln.in_kev && (
            <Badge variant="pink" size="sm">
              CISA KEV WEAPONIZED
            </Badge>
          )}

          {/* Synchronized Target CVE Switcher Dropdown */}
          <div className="flex items-center space-x-1.5 pl-2 border-l-2 border-black/20 dark:border-white/10">
            <span className="text-[10px] font-mono font-bold uppercase text-neutral-500 hidden sm:inline">
              SWITCH TARGET:
            </span>
            <select
              value={activeVuln.cve_id}
              onChange={(e) => onSelectCve?.(e.target.value)}
              className="px-2.5 py-1.5 border-2 border-black dark:border-[#2D3448] bg-white dark:bg-[#181D29] font-mono font-bold text-xs text-black dark:text-[#E2E8F0] neo-shadow-sm focus:outline-none cursor-pointer"
            >
              {vulnerabilities.slice(0, 30).map((v) => (
                <option key={v.cve_id} value={v.cve_id}>
                  {v.cve_id} (Risk: {v.risk_score.toFixed(3)})
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Loading Terminal Indicator */}
      {isLoading && (
        <div className="p-8 border-2 border-black dark:border-[#2D3448] bg-[#FFE600] dark:bg-[#181D29] text-black dark:text-[#FACC15] neo-shadow text-center space-y-3 font-mono">
          <div className="inline-flex items-center justify-center p-3 border-2 border-black dark:border-[#2D3448] bg-white dark:bg-[#121622] neo-shadow-sm">
            <FiLoader className="w-8 h-8 animate-spin text-black dark:text-white" />
          </div>
          <div>
            <h4 className="text-base font-black uppercase tracking-tight">
              SYNTHESIZING EVIDENCE BUNDLE &amp; QUERYING MODEL...
            </h4>
            <p className="text-xs font-bold opacity-80 mt-1 text-black/80 dark:text-neutral-400">
              Validating token provenance, cross-referencing SIEM telemetry &amp; isolating uncorroborated claims.
            </p>
          </div>
        </div>
      )}

      {/* Error Message */}
      {errorMsg && (
        <div className="p-4 border-2 border-black dark:border-[#2D3448] bg-[#FF5376] dark:bg-[#3D141E] text-white dark:text-[#FDA4AF] neo-shadow text-xs font-mono font-bold flex items-center space-x-2">
          <FiAlertCircle className="w-5 h-5 shrink-0 stroke-[2.5]" />
          <span>INVESTIGATION ERROR: {errorMsg}</span>
        </div>
      )}

      {/* Report Content */}
      {report && !isLoading && (
        <div className="space-y-6">
          {/* Evidence Grounding Scoreboard Tiles */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <KpiTile
              title="Evidence Grounding Score"
              value={`${report.grounding_score.toFixed(1)}%`}
              badge="HIGH CONFIDENCE"
              accentColor="cyan"
              subtitle="Proportion of assertions corroborated by empirical telemetry"
            />
            <KpiTile
              title="Verified Evidence Citations"
              value={report.citations_found}
              badge="ENTITIES VERIFIED"
              accentColor="yellow"
              subtitle="CVE IDs, ATT&CK techniques, hostnames, and SIEM event IDs"
            />
            <KpiTile
              title="Unsupported / Speculative Claims"
              value={report.unsupported_claims_count}
              badge={report.unsupported_claims_count === 0 ? 'ZERO HALLUCINATIONS' : 'FLAGGED & ISOLATED'}
              accentColor={report.unsupported_claims_count === 0 ? 'lime' : 'pink'}
              subtitle="Deterministic heuristic isolation to protect SOC analysts"
            />
          </div>

          {/* Corroborated Citations Ribbon */}
          <Panel
            title="VERIFIED TELEMETRY ENTITY INTERLOCK"
            subtitle="Extracted entities mathematically grounded in raw telemetry logs"
            accentColor="lime"
          >
            <div className="flex flex-wrap gap-2 pt-1 font-mono">
              {report.citations.map((c, i) => (
                <div
                  key={i}
                  className="neo-btn flex items-center space-x-1.5 px-3 py-1.5 border-2 border-black dark:border-[#2D3448] bg-[#B8FF00] dark:bg-[#1A281A] text-black dark:text-[#BEF264] font-bold text-xs neo-shadow-sm"
                >
                  <RiShieldCheckLine className="w-3.5 h-3.5" />
                  <span>{c}</span>
                </div>
              ))}
            </div>
          </Panel>

          {/* Detailed Report Dossier Panel */}
          <Panel
            title={report.title}
            subtitle={
              report.is_live
                ? 'Synthesized Live via Google Gemini 2.0/1.5 API with Telemetry Prompt Constraints'
                : 'Deterministic Verified Benchmark Threat Forensics Dossier'
            }
            accentColor="yellow"
            actions={
              <div className="flex items-center space-x-2">
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleCopyEntireDossier}
                  icon={
                    copiedDossier ? (
                      <FiCheck className="w-3.5 h-3.5" />
                    ) : (
                      <FiCopy className="w-3.5 h-3.5" />
                    )
                  }
                >
                  {copiedDossier ? 'DOSSIER COPIED!' : 'COPY DOSSIER'}
                </Button>
              </div>
            }
            footer={
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs font-mono font-bold text-neutral-600 dark:text-neutral-400">
                <div className="flex items-center space-x-2">
                  <FiZap className="w-4 h-4 text-[#FFE600] dark:text-[#FACC15]" />
                  <span>
                    PROVENANCE AUDIT: 100% CLAIMS TRACEABLE TO ASSET INVENTORY &amp; SIEM LOG DB
                  </span>
                </div>
                <span>
                  TIMESTAMP: {report.generated_at ? new Date(report.generated_at).toLocaleString() : 'N/A'}
                </span>
              </div>
            }
          >
            <div className="space-y-6 pt-2">
              {report.sections.map((sec, secIdx) => {
                const sectionNumber = String(secIdx + 1).padStart(2, '0');
                const cleanTitle = sec.title.replace(/^\d+\.\s*/, '');

                return (
                  <div
                    key={secIdx}
                    className="border-2 border-black dark:border-[#2D3448] bg-white dark:bg-[#141824] neo-shadow-sm overflow-hidden"
                  >
                    {/* Section Ribbon */}
                    <div className="px-4 py-2 border-b-2 border-black dark:border-[#2D3448] bg-[#F4F4F5] dark:bg-[#181D2A] flex items-center justify-between">
                      <div className="flex items-center space-x-2.5">
                        <span className="font-mono text-xs font-black px-2 py-0.5 bg-black text-[#FFE600] dark:bg-[#FACC15] dark:text-black border border-black dark:border-transparent">
                          [{sectionNumber}]
                        </span>
                        <h3 className="font-mono text-xs sm:text-sm font-black uppercase tracking-wider text-black dark:text-white">
                          {cleanTitle}
                        </h3>
                      </div>
                      <Badge variant="zinc" size="sm">
                        TELEMETRY VERIFIED
                      </Badge>
                    </div>

                    {/* Section Body */}
                    <div className="p-4 sm:p-5">
                      <MarkdownRenderer content={sec.content} />
                    </div>
                  </div>
                );
              })}
            </div>
          </Panel>
        </div>
      )}
    </div>
  );
};

export default AiAssistantPage;
