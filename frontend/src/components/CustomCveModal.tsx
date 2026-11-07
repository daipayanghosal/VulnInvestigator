import React, { useState } from 'react';
import {
  AlertCircle,
  Check,
  CheckCircle2,
  Database,
  Globe,
  Info,
  Loader2,
  Plus,
  Server,
  ShieldAlert,
  X,
} from 'lucide-react';
import { Asset, RiskBand, Severity, Vulnerability } from '../types';
import { calculateFactorBreakdown, getRiskBand } from '../utils/scoring';

interface CustomCveModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAddCve: (vuln: Vulnerability) => void;
  assets: Asset[];
}

export const CustomCveModal: React.FC<CustomCveModalProps> = ({
  isOpen,
  onClose,
  onAddCve,
  assets,
}) => {
  const [cveId, setCveId] = useState('');
  const [cvssScore, setCvssScore] = useState(7.5);
  const [severity, setSeverity] = useState<Severity>('HIGH');
  const [inKev, setInKev] = useState(false);
  const [selectedAssetId, setSelectedAssetId] = useState(assets[0]?.asset_id || 'SRV-WEB-001');
  const [affectedProducts, setAffectedProducts] = useState('');
  const [description, setDescription] = useState('');
  const [isFetchingNvd, setIsFetchingNvd] = useState(false);
  const [nvdStatus, setNvdStatus] = useState<string | null>(null);

  if (!isOpen) return null;

  const currentAsset = assets.find((a) => a.asset_id === selectedAssetId) || assets[0];
  const breakdown = calculateFactorBreakdown(cvssScore, inKev, currentAsset);
  const calculatedBand = getRiskBand(breakdown.total_score);

  const handleFetchNvd = async () => {
    if (!cveId.trim() || !cveId.toUpperCase().startsWith('CVE-')) {
      setNvdStatus('Please enter a valid CVE ID format (e.g. CVE-2024-1234)');
      return;
    }

    setIsFetchingNvd(true);
    setNvdStatus('Querying NIST NVD API...');

    try {
      // Use corsproxy or public NVD endpoint with fallback
      const formattedCve = cveId.trim().toUpperCase();
      const res = await fetch(`https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=${formattedCve}`);
      if (!res.ok) throw new Error(`NVD returned HTTP ${res.status}`);

      const data = await res.json();
      const item = data.vulnerabilities?.[0]?.cve;
      if (!item) throw new Error('CVE record not found in NVD database.');

      const metrics = item.metrics?.cvssMetricV31?.[0]?.cvssData || item.metrics?.cvssMetricV30?.[0]?.cvssData;
      if (metrics) {
        setCvssScore(metrics.baseScore);
        setSeverity((metrics.baseSeverity || 'HIGH').toUpperCase() as Severity);
      }

      const desc = item.descriptions?.find((d: any) => d.lang === 'en')?.value || '';
      setDescription(desc);
      setNvdStatus('Successfully imported NIST NVD technical parameters!');
    } catch (err: any) {
      console.warn('NVD live fetch fallback:', err);
      // Fallback pre-fill so user experience is smooth
      setDescription(`Manual investigation profile created for ${cveId.toUpperCase()}. Software flaw requiring security verification.`);
      setNvdStatus('NVD live query timed out. Pre-filled standard baseline parameters for manual editing.');
    } finally {
      setIsFetchingNvd(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!cveId.trim()) return;

    const newVuln: Vulnerability = {
      cve_id: cveId.trim().toUpperCase(),
      cvss_score: cvssScore,
      cvss_severity: severity,
      cvss_vector: 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H',
      in_kev: inKev,
      risk_score: breakdown.total_score,
      risk_band: calculatedBand,
      matched_asset_id: selectedAssetId,
      rank_cvss: 1,
      rank_contextual: 1,
      rank_displacement: 0,
      description: description.trim() || 'Custom vulnerability ingested for enterprise threat evaluation.',
      affected_products: affectedProducts.trim() || (Array.isArray(currentAsset.software) ? currentAsset.software[0] : currentAsset.software),
      published_date: new Date().toISOString().slice(0, 10),
    };

    onAddCve(newVuln);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm transition-all">
      <div className="w-full max-w-lg rounded-3xl bg-white dark:bg-[#1C1C1E] border border-black/10 dark:border-white/10 shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="px-6 py-4 border-b border-black/5 dark:border-white/5 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-7 h-7 rounded-lg bg-[#0071E3]/10 dark:bg-[#0071E3]/20 flex items-center justify-center text-[#0071E3]">
              <Plus className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">
                Ingest Custom Vulnerability
              </h3>
              <p className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
                Enter unlisted CVE details or query live NIST NVD
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-full flex items-center justify-center text-[#86868B] hover:text-[#1D1D1F] dark:hover:text-[#F5F5F7] hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* CVE ID + Live NIST NVD Query */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-[#86868B] dark:text-[#A1A1A6] mb-1.5">
              CVE Identifier
            </label>
            <div className="flex space-x-2">
              <input
                type="text"
                value={cveId}
                onChange={(e) => setCveId(e.target.value)}
                placeholder="CVE-2024-XXXX"
                required
                className="flex-1 px-3 py-2 text-xs rounded-xl bg-black/[0.03] dark:bg-white/[0.05] border border-black/10 dark:border-white/10 text-[#1D1D1F] dark:text-[#F5F5F7] focus:outline-none focus:ring-2 focus:ring-[#0071E3]"
              />
              <button
                type="button"
                onClick={handleFetchNvd}
                disabled={isFetchingNvd}
                className="px-3 py-2 rounded-xl bg-black/[0.04] dark:bg-white/[0.08] hover:bg-black/[0.08] dark:hover:bg-white/[0.12] text-xs font-medium text-[#1D1D1F] dark:text-[#F5F5F7] flex items-center space-x-1 border border-black/10 dark:border-white/10 transition-colors"
              >
                {isFetchingNvd ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Globe className="w-3.5 h-3.5 text-[#0071E3]" />
                )}
                <span>Fetch NVD</span>
              </button>
            </div>
            {nvdStatus && (
              <p className="mt-1.5 text-[11px] text-[#0071E3] flex items-center space-x-1">
                <Info className="w-3 h-3" />
                <span>{nvdStatus}</span>
              </p>
            )}
          </div>

          {/* CVSS Score Slider + Severity */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="font-semibold text-[#86868B] dark:text-[#A1A1A6] uppercase tracking-wider text-[10px]">
                  CVSS Base Score
                </span>
                <span className="font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">
                  {cvssScore.toFixed(1)} / 10
                </span>
              </div>
              <input
                type="range"
                min="0.0"
                max="10.0"
                step="0.1"
                value={cvssScore}
                onChange={(e) => setCvssScore(parseFloat(e.target.value))}
                className="w-full accent-[#0071E3]"
              />
            </div>

            <div>
              <label className="block text-[10px] font-semibold uppercase tracking-wider text-[#86868B] dark:text-[#A1A1A6] mb-1">
                Severity Rating
              </label>
              <select
                value={severity}
                onChange={(e) => setSeverity(e.target.value as Severity)}
                className="w-full px-2.5 py-1.5 text-xs rounded-xl bg-black/[0.03] dark:bg-white/[0.05] border border-black/10 dark:border-white/10 text-[#1D1D1F] dark:text-[#F5F5F7] focus:outline-none"
              >
                <option value="CRITICAL">Critical</option>
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
              </select>
            </div>
          </div>

          {/* CISA KEV Checkbox */}
          <div className="p-3 rounded-xl bg-black/[0.02] dark:bg-white/[0.02] border border-black/5 dark:border-white/5 flex items-center justify-between">
            <div>
              <div className="text-xs font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">
                CISA KEV Wild Exploitation
              </div>
              <div className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
                Threat actors actively weaponizing this flaw
              </div>
            </div>
            <input
              type="checkbox"
              checked={inKev}
              onChange={(e) => setInKev(e.target.checked)}
              className="w-4 h-4 rounded text-[#0071E3] accent-[#0071E3]"
            />
          </div>

          {/* Target Asset Assignment */}
          <div>
            <label className="block text-[10px] font-semibold uppercase tracking-wider text-[#86868B] dark:text-[#A1A1A6] mb-1">
              Target Enterprise Asset
            </label>
            <select
              value={selectedAssetId}
              onChange={(e) => setSelectedAssetId(e.target.value)}
              className="w-full px-3 py-2 text-xs rounded-xl bg-black/[0.03] dark:bg-white/[0.05] border border-black/10 dark:border-white/10 text-[#1D1D1F] dark:text-[#F5F5F7] focus:outline-none"
            >
              {assets.map((a) => (
                <option key={a.asset_id} value={a.asset_id}>
                  {a.asset_id} &mdash; {a.hostname} ({a.criticality.toUpperCase()}, {a.exposure})
                </option>
              ))}
            </select>
          </div>

          {/* Description */}
          <div>
            <label className="block text-[10px] font-semibold uppercase tracking-wider text-[#86868B] dark:text-[#A1A1A6] mb-1">
              Technical Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe flaw mechanics, affected service, or payload behavior..."
              rows={2}
              className="w-full px-3 py-2 text-xs rounded-xl bg-black/[0.03] dark:bg-white/[0.05] border border-black/10 dark:border-white/10 text-[#1D1D1F] dark:text-[#F5F5F7] focus:outline-none focus:ring-2 focus:ring-[#0071E3]"
            />
          </div>

          {/* Real-time Calculated Score Preview */}
          <div className="p-3.5 rounded-xl bg-[#0071E3]/5 dark:bg-[#0071E3]/10 border border-[#0071E3]/20 flex items-center justify-between">
            <div>
              <span className="text-[10px] font-semibold uppercase tracking-wider text-[#0071E3]">
                Calculated Contextual Risk
              </span>
              <div className="text-xl font-semibold tracking-tight text-[#0071E3]">
                {breakdown.total_score.toFixed(3)} / 1.000
              </div>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-[#0071E3] text-white">
              Band: {calculatedBand}
            </span>
          </div>

          {/* Footer Action */}
          <div className="pt-2 flex items-center justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-medium rounded-xl text-[#86868B] hover:text-[#1D1D1F] dark:hover:text-[#F5F5F7] hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 text-xs font-medium rounded-xl bg-[#0071E3] hover:bg-[#0077ED] text-white shadow-sm transition-colors"
            >
              Ingest &amp; Calculate
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
