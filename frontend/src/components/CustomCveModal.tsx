import React, { useState } from 'react';
import {
  FiCheckCircle,
  FiExternalLink,
  FiGlobe,
  FiInfo,
  FiLoader,
  FiPlus,
  FiSearch,
  FiServer,
  FiShield,
  FiX,
} from 'react-icons/fi';
import { Asset, RiskBand, Severity, Vulnerability } from '../types';
import { calculateFactorBreakdown, getRiskBand } from '../utils/scoring';
import { Badge } from './common/Badge';
import { Button } from './common/Button';

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
    setNvdStatus('Querying NIST NVD API 2.0...');

    try {
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
      description: description || `Ingested custom vulnerability ${cveId.trim().toUpperCase()}`,
      affected_products: affectedProducts || 'Custom Enterprise Service',
      published_date: new Date().toISOString().split('T')[0],
    };

    onAddCve(newVuln);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs transition-all overflow-y-auto">
      <div className="w-full max-w-2xl border-3 border-black dark:border-white bg-[#F7F6F2] dark:bg-[#141418] neo-shadow-xl overflow-hidden animate-in zoom-in-95 duration-100 my-8">
        {/* Title Bar */}
        <div className="px-4 py-3 bg-[#00F0FF] text-black border-b-2 border-black flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 bg-black text-[#00F0FF] border border-black flex items-center justify-center neo-shadow-sm font-mono font-bold text-xs">
              <FiPlus className="w-3.5 h-3.5 stroke-[3]" />
            </div>
            <span className="font-mono font-black text-sm uppercase tracking-tight">
              INGEST CUSTOM VULNERABILITY // RISK ENGINE
            </span>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="neo-btn w-6 h-6 border-2 border-black bg-white text-black flex items-center justify-center font-mono font-bold text-xs hover:bg-[#FF5376] hover:text-white"
          >
            <FiX className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Content Form */}
        <form onSubmit={handleSubmit} className="p-4 sm:p-6 space-y-4 text-xs font-mono">
          {/* CVE Input & NVD Fetch */}
          <div>
            <label className="block font-bold uppercase text-black dark:text-white mb-1">
              1. Vulnerability Identifier (CVE ID)
            </label>
            <div className="flex items-center space-x-2">
              <input
                type="text"
                value={cveId}
                onChange={(e) => setCveId(e.target.value)}
                placeholder="CVE-2024-XXXX"
                className="flex-1 px-3 py-2 border-2 border-black dark:border-white bg-white dark:bg-black text-black dark:text-white uppercase font-bold neo-shadow-sm focus:outline-none focus:bg-[#FFFBEB] dark:focus:bg-[#1C1C22]"
                required
              />
              <Button
                type="button"
                variant="primary"
                size="sm"
                icon={isFetchingNvd ? <FiLoader className="w-3.5 h-3.5 animate-spin" /> : <FiSearch className="w-3.5 h-3.5" />}
                onClick={handleFetchNvd}
                disabled={isFetchingNvd}
              >
                {isFetchingNvd ? 'QUERYING...' : 'FETCH NVD'}
              </Button>
            </div>
            {nvdStatus && (
              <p className="mt-1.5 text-[11px] font-bold text-[#0071E3] dark:text-[#38BDF8]">
                &gt; {nvdStatus}
              </p>
            )}
          </div>

          {/* Grid: CVSS Score & KEV Toggle */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t-2 border-black/10 dark:border-white/10">
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="font-bold uppercase text-black dark:text-white">
                  2. CVSS v3.1 Base Score: <span className="bg-[#FFE600] text-black px-1.5 py-0.2 border border-black">{cvssScore.toFixed(1)}</span>
                </label>
              </div>
              <input
                type="range"
                min="0.0"
                max="10.0"
                step="0.1"
                value={cvssScore}
                onChange={(e) => {
                  const val = parseFloat(e.target.value);
                  setCvssScore(val);
                  if (val >= 9.0) setSeverity('CRITICAL');
                  else if (val >= 7.0) setSeverity('HIGH');
                  else if (val >= 4.0) setSeverity('MEDIUM');
                  else setSeverity('LOW');
                }}
                className="w-full accent-black dark:accent-white cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-neutral-500 mt-1 font-bold">
                <span>0.0 (NONE)</span>
                <span>4.0 (MED)</span>
                <span>7.0 (HIGH)</span>
                <span>10.0 (CRIT)</span>
              </div>
            </div>

            <div>
              <label className="block font-bold uppercase text-black dark:text-white mb-1">
                3. Active CISA KEV Weaponization
              </label>
              <div className="flex items-center space-x-2 pt-1">
                <button
                  type="button"
                  onClick={() => setInKev(!inKev)}
                  className={`neo-btn flex-1 py-2 px-3 border-2 border-black dark:border-white font-bold flex items-center justify-center space-x-2 ${
                    inKev
                      ? 'bg-[#FF5376] text-white neo-shadow-sm'
                      : 'bg-white dark:bg-black text-black dark:text-white hover:bg-neutral-100'
                  }`}
                >
                  <FiShield className="w-3.5 h-3.5" />
                  <span>{inKev ? 'WEAPONIZED IN WILD (+0.30)' : 'NO EXPLOIT OBSERVED (0.0)'}</span>
                </button>
              </div>
            </div>
          </div>

          {/* Target Asset Assignment */}
          <div className="pt-2 border-t-2 border-black/10 dark:border-white/10">
            <label className="block font-bold uppercase text-black dark:text-white mb-1">
              4. Target Enterprise Asset Node
            </label>
            <select
              value={selectedAssetId}
              onChange={(e) => setSelectedAssetId(e.target.value)}
              className="w-full px-3 py-2 border-2 border-black dark:border-white bg-white dark:bg-black text-black dark:text-white font-bold neo-shadow-sm focus:outline-none"
            >
              {assets.map((a) => (
                <option key={a.asset_id} value={a.asset_id}>
                  {a.hostname} [{a.asset_id}] &bull; Tier {a.criticality.toUpperCase()} &bull; Zone: {a.exposure.toUpperCase()}
                </option>
              ))}
            </select>
          </div>

          {/* Live Contextual Math Calculation Preview Strip */}
          <div className="p-3 border-2 border-black dark:border-white bg-[#FFE600] text-black neo-shadow-sm space-y-1">
            <div className="flex items-center justify-between font-bold">
              <span>REAL-TIME VULNINVESTIGATOR SCORE:</span>
              <span className="text-base font-black px-2 py-0.5 bg-black text-[#FFE600] border border-black">
                {breakdown.total_score.toFixed(3)} [{calculatedBand.toUpperCase()}]
              </span>
            </div>
            <p className="text-[11px] text-black/80 font-medium">
              S_ctx = (0.35 &times; {breakdown.cvss_val.toFixed(1)}/10) + (0.30 &times; {inKev ? '1.0' : '0.0'}) + (0.20 &times; {breakdown.crit_score.toFixed(2)}) + (0.15 &times; {breakdown.expo_score.toFixed(2)})
            </p>
          </div>

          {/* Form Actions */}
          <div className="flex items-center justify-end space-x-2 pt-3 border-t-2 border-black dark:border-white">
            <Button type="button" variant="secondary" size="md" onClick={onClose}>
              CANCEL
            </Button>
            <Button
              type="submit"
              variant="primary"
              size="md"
              icon={<FiCheckCircle className="w-4 h-4" />}
            >
              INJECT INTO ACTIVE QUEUE
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
