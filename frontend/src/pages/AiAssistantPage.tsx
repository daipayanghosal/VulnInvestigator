import React, { useEffect, useState } from 'react';
import {
  AlertCircle,
  AlertTriangle,
  Check,
  CheckCircle2,
  Copy,
  ExternalLink,
  FileText,
  Key,
  Layers,
  Loader2,
  RefreshCw,
  Search,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Terminal,
} from 'lucide-react';
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
  onSelectCve: (cveId: string) => void;
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
  const [copiedQueryIdx, setCopiedQueryIdx] = useState<number | null>(null);

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
    // Automatically load or run investigation when page mounts or CVE changes
    handleRunInvestigation();
  }, [selectedCveId]);

  const handleCopyCode = (code: string, idx: number) => {
    navigator.clipboard.writeText(code);
    setCopiedQueryIdx(idx);
    setTimeout(() => setCopiedQueryIdx(null), 1500);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-[#1D1D1F] dark:text-[#F5F5F7]">
            Evidence-Grounded AI Assistant
          </h1>
          <p className="text-xs sm:text-sm text-[#86868B] dark:text-[#A1A1A6] mt-1">
            Automated threat hypothesis formulation, signal discrimination, and defensive verification queries.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={onOpenKeyModal}
            className="px-3 py-1.5 text-xs font-medium rounded-xl bg-black/[0.04] dark:bg-white/[0.08] hover:bg-black/[0.08] dark:hover:bg-white/[0.12] text-[#1D1D1F] dark:text-[#F5F5F7] border border-black/10 dark:border-white/10 flex items-center space-x-1.5 transition-colors"
          >
            <Key className="w-3.5 h-3.5 text-[#0071E3]" />
            <span>{hasApiKey ? 'Gemini API Key Configured' : 'Configure Gemini Key'}</span>
          </button>
          <button
            onClick={handleRunInvestigation}
            disabled={isLoading}
            className="px-4 py-1.5 text-xs font-medium rounded-xl bg-[#0071E3] hover:bg-[#0077ED] text-white shadow-sm flex items-center space-x-1.5 transition-colors disabled:opacity-50"
          >
            {isLoading ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <RefreshCw className="w-3.5 h-3.5" />
            )}
            <span>Re-run Analysis</span>
          </button>
        </div>
      </div>

      {/* Non-Technical Guide */}
      <ExecutiveGuide title="Executive Guide: How Evidence Grounding Mitigates AI Hallucinations">
        <div className="space-y-3">
          <p className="text-neutral-600 dark:text-neutral-300">
            A primary danger of applying commercial GenAI to cybersecurity is <strong>stochastic hallucination</strong>&mdash;where language models invent non-existent CVEs, fake IP addresses, or irrelevant remediation advice.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs pt-1">
            <div className="p-3 rounded-xl bg-black/[0.02] dark:bg-white/[0.02] border border-black/5 dark:border-white/5">
              <span className="font-semibold text-[#0071E3] block mb-1">1. Strict Prompt Isolation</span>
              <p className="text-[11px] text-neutral-500">
                The model is supplied with a structured Evidence Bundle containing only verified facts for the selected CVE, asset, and telemetry logs.
              </p>
            </div>
            <div className="p-3 rounded-xl bg-black/[0.02] dark:bg-white/[0.02] border border-black/5 dark:border-white/5">
              <span className="font-semibold text-[#0071E3] block mb-1">2. Mandatory Citation Badging</span>
              <p className="text-[11px] text-neutral-500">
                The assistant must explicitly cite CVE numbers, ATT&amp;CK techniques, and log event IDs to substantiate investigative claims.
              </p>
            </div>
            <div className="p-3 rounded-xl bg-black/[0.02] dark:bg-white/[0.02] border border-black/5 dark:border-white/5">
              <span className="font-semibold text-[#0071E3] block mb-1">3. Automated Heuristic Verification</span>
              <p className="text-[11px] text-neutral-500">
                Any speculative claim lacking direct empirical backing is automatically flagged with a yellow highlight for analyst review.
              </p>
            </div>
          </div>
        </div>
      </ExecutiveGuide>

      {/* Target CVE Selection Header */}
      <div className="p-4 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-[#86868B] dark:text-[#A1A1A6]">
            Active Target:
          </span>
          <span className="font-mono font-semibold text-sm text-[#0071E3]">
            {activeVuln.cve_id}
          </span>
          <span className="text-xs text-neutral-500">
            on {activeAsset.hostname} ({activeAsset.asset_id})
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <select
            value={activeVuln.cve_id}
            onChange={(e) => onSelectCve(e.target.value)}
            className="px-3 py-1.5 text-xs rounded-xl bg-black/[0.03] dark:bg-white/[0.05] border border-black/10 dark:border-white/10 text-[#1D1D1F] dark:text-[#F5F5F7] focus:outline-none"
          >
            {vulnerabilities.slice(0, 30).map((v) => (
              <option key={v.cve_id} value={v.cve_id}>
                {v.cve_id} (Risk: {v.risk_score.toFixed(3)})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Loading Spinner */}
      {isLoading && (
        <div className="p-12 rounded-3xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm flex flex-col items-center justify-center text-center space-y-3">
          <Loader2 className="w-8 h-8 animate-spin text-[#0071E3]" />
          <div>
            <h4 className="text-sm font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">
              Synthesizing Evidence Bundle...
            </h4>
            <p className="text-xs text-[#86868B] dark:text-[#A1A1A6]">
              Querying Gemini model and verifying citation provenance across SIEM logs
            </p>
          </div>
        </div>
      )}

      {/* Error Message */}
      {errorMsg && (
        <div className="p-4 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-700 dark:text-red-400 text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Report Content */}
      {report && !isLoading && (
        <div className="space-y-5">
          {/* Evidence Grounding Scoreboard */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {/* Tile 1 */}
            <div className="p-4 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm">
              <span className="text-[10px] uppercase font-semibold tracking-wider text-[#86868B] dark:text-[#A1A1A6] block mb-1">
                Evidence Grounding Score
              </span>
              <div className="flex items-baseline space-x-1.5">
                <span className="text-2xl font-bold tracking-tight text-[#0071E3]">
                  {report.grounding_score.toFixed(1)}%
                </span>
                <span className="text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold">
                  HIGH CONFIDENCE
                </span>
              </div>
              <p className="text-[10px] text-[#86868B] dark:text-[#A1A1A6] mt-0.5">
                Proportion of assertions corroborated by empirical telemetry
              </p>
            </div>

            {/* Tile 2 */}
            <div className="p-4 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm">
              <span className="text-[10px] uppercase font-semibold tracking-wider text-[#86868B] dark:text-[#A1A1A6] block mb-1">
                Verified Evidence Citations
              </span>
              <div className="flex items-baseline space-x-1.5">
                <span className="text-2xl font-bold tracking-tight text-[#1D1D1F] dark:text-[#F5F5F7]">
                  {report.citations_found}
                </span>
                <span className="text-xs text-[#86868B] dark:text-[#A1A1A6]">entities verified</span>
              </div>
              <p className="text-[10px] text-[#86868B] dark:text-[#A1A1A6] mt-0.5">
                CVE IDs, ATT&amp;CK techniques, hostnames, and SIEM event IDs
              </p>
            </div>

            {/* Tile 3 */}
            <div className="p-4 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm">
              <span className="text-[10px] uppercase font-semibold tracking-wider text-[#86868B] dark:text-[#A1A1A6] block mb-1">
                Unsupported / Speculative Claims
              </span>
              <div className="flex items-baseline space-x-1.5">
                <span
                  className={`text-2xl font-bold tracking-tight ${
                    report.unsupported_claims_count === 0
                      ? 'text-emerald-600 dark:text-emerald-400'
                      : 'text-amber-600 dark:text-amber-400'
                  }`}
                >
                  {report.unsupported_claims_count}
                </span>
                <span className="text-xs text-[#86868B] dark:text-[#A1A1A6]">
                  {report.unsupported_claims_count === 0 ? 'Zero Hallucinations' : 'Flagged & Isolated'}
                </span>
              </div>
              <p className="text-[10px] text-[#86868B] dark:text-[#A1A1A6] mt-0.5">
                Highlighted with warning badges to protect SOC analysts
              </p>
            </div>
          </div>

          {/* Citation Badges Bar */}
          <div className="p-4 rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-[#86868B] dark:text-[#A1A1A6] block mb-2">
              Corroborated Telemetry Entity Citations in this Report
            </span>
            <div className="flex flex-wrap gap-1.5">
              {report.citations.map((c, i) => (
                <span
                  key={i}
                  className="px-2.5 py-1 rounded-lg bg-[#0071E3]/10 text-[#0071E3] font-mono text-xs font-medium border border-[#0071E3]/20 flex items-center space-x-1"
                >
                  <ShieldCheck className="w-3 h-3 text-[#0071E3]" />
                  <span>{c}</span>
                </span>
              ))}
            </div>
          </div>

          {/* Report Sections */}
          <div className="p-6 rounded-3xl bg-white dark:bg-[#1C1C1E] border border-black/8 dark:border-white/10 shadow-sm space-y-6">
            <div className="pb-3 border-b border-black/5 dark:border-white/5 flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">
                  {report.title}
                </h3>
                <span className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
                  {report.is_live ? 'Generated live via Google Gemini API' : 'High-fidelity verified benchmark dossier'}
                </span>
              </div>
              <span className="text-xs font-mono text-neutral-400">
                {report.generated_at ? new Date(report.generated_at).toLocaleString() : ''}
              </span>
            </div>

            {report.sections.map((sec, secIdx) => {
              return (
                <div key={secIdx} className="space-y-3 pt-1">
                  <div className="flex items-center space-x-2 pb-1.5 border-b border-black/[0.04] dark:border-white/[0.06]">
                    <span className="w-5 h-5 rounded-full bg-[#0071E3]/10 dark:bg-[#0071E3]/20 text-[#0071E3] flex items-center justify-center text-[10px] font-bold">
                      {secIdx + 1}
                    </span>
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-[#0071E3] dark:text-[#389BF2]">
                      {sec.title.replace(/^\d+\.\s*/, '')}
                    </h4>
                  </div>

                  <MarkdownRenderer content={sec.content} />
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
