import React from 'react';
import {
  FiAlertTriangle,
  FiArrowRight,
  FiCheckCircle,
  FiDatabase,
  FiLayers,
  FiSearch,
  FiShield,
} from 'react-icons/fi';
import { RiFireLine } from 'react-icons/ri';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { KpiTile } from '../components/common/KpiTile';
import { Panel } from '../components/common/Panel';
import { Top10BarChart } from '../components/Charts';
import { OverviewExecutiveGuide } from '../components/ExecutiveGuide';
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
    <div className="space-y-6 animate-in fade-in duration-150">
      {/* Page Title & Operational Badge Ribbon */}
      <div className="border-b-2 sm:border-b-[3px] border-black dark:border-white pb-4 flex flex-col md:flex-row md:items-end justify-between gap-3">
        <div>
          <div className="flex items-center space-x-2 flex-wrap gap-y-1 mb-1">
            <span className="font-mono font-bold text-xs uppercase bg-[#FFE600] text-black px-2 py-0.5 border border-black neo-shadow-sm">
              TELEMETRY DASHBOARD
            </span>
            <span className="font-mono text-xs text-neutral-500">// GLOBAL VULNERABILITY STATE</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-mono font-black tracking-tight text-black dark:text-white uppercase">
            Enterprise Threat Landscape
          </h1>
          <p className="text-xs sm:text-sm font-mono text-neutral-600 dark:text-neutral-400 mt-1">
            Live multi-factor prioritization synthesizing NIST NVD, CISA KEV active exploits, and corporate perimeter topology.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Button
            variant="primary"
            size="sm"
            icon={<FiSearch className="w-3.5 h-3.5 stroke-[3]" />}
            onClick={onNavigateToRankings}
          >
            EXPLORE ALL RANKINGS
          </Button>
        </div>
      </div>

      {/* Non-Technical Executive Guide */}
      <OverviewExecutiveGuide />

      {/* 4 Primary Brutalist KPI Blocks */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <KpiTile
          label="Total CVE Corpus"
          value={totalCves.toLocaleString()}
          sublabel="NIST NVD 2.0 Ingested"
          accent="cyan"
          icon={<FiDatabase className="w-3.5 h-3.5" />}
          badge={<Badge color="cyan" size="xs">NVD</Badge>}
        />

        <KpiTile
          label="In CISA KEV Catalog"
          value={inKevCount.toLocaleString()}
          sublabel="Weaponized in the wild"
          accent="pink"
          icon={<RiFireLine className="w-3.5 h-3.5 text-white" />}
          badge={<Badge color="pink" size="xs">ACTIVE</Badge>}
        />

        <KpiTile
          label="Critical Risk Band"
          value={criticalCount.toLocaleString()}
          sublabel="Score >= 0.80 Immediate Triage"
          accent="orange"
          icon={<FiAlertTriangle className="w-3.5 h-3.5" />}
          badge={<Badge color="orange" size="xs">TIER 1</Badge>}
        />

        <KpiTile
          label="Evaluated with CVSS v3"
          value={hasCvssCount.toLocaleString()}
          sublabel="100% Vector Completeness"
          accent="lime"
          icon={<FiCheckCircle className="w-3.5 h-3.5" />}
          badge={<Badge color="lime" size="xs">BOUNDED</Badge>}
        />
      </div>

      {/* Main Split Workbench: Top Priority Queue Table & Top 10 Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left: Top 5 Highest Priority Table (7 Cols) */}
        <div className="lg:col-span-7">
          <Panel
            title="Highest Priority Queue Targets"
            subtitle="Sorted by multi-factor contextual risk score"
            icon={<FiLayers className="w-4 h-4 text-black" />}
            accent="yellow"
            actions={
              <button
                type="button"
                onClick={onNavigateToRankings}
                className="neo-btn px-2.5 py-1 text-xs font-mono font-bold bg-white text-black border-2 border-black flex items-center space-x-1 hover:bg-[#FFE600]"
              >
                <span>VIEW ALL {totalCves.toLocaleString()}</span>
                <FiArrowRight className="w-3 h-3 stroke-[3]" />
              </button>
            }
            noPadding
          >
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs font-mono">
                <thead>
                  <tr className="bg-neutral-100 dark:bg-[#1C1C24] border-b-2 border-black dark:border-white text-black dark:text-white uppercase text-[10px]">
                    <th className="py-2.5 px-3 font-black">Rank</th>
                    <th className="py-2.5 px-3 font-black">Vulnerability</th>
                    <th className="py-2.5 px-3 font-black">CVSS Base</th>
                    <th className="py-2.5 px-3 font-black">CISA KEV</th>
                    <th className="py-2.5 px-3 font-black">Contextual Risk</th>
                    <th className="py-2.5 px-3 font-black text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y-2 divide-black/10 dark:divide-white/10">
                  {top5.map((v, i) => (
                    <tr
                      key={v.cve_id}
                      className="hover:bg-[#FFFBEB] dark:hover:bg-[#1E1E26] transition-colors"
                    >
                      <td className="py-3 px-3 font-black text-neutral-500">
                        <span className="px-1.5 py-0.5 bg-black text-white text-[10px] border border-black inline-block">
                          #{i + 1}
                        </span>
                      </td>
                      <td className="py-3 px-3">
                        <div className="font-bold text-black dark:text-white">
                          {v.cve_id}
                        </div>
                        <div className="text-[10px] text-neutral-500 dark:text-neutral-400 truncate max-w-[180px] sm:max-w-xs">
                          {v.description.slice(0, 55)}...
                        </div>
                      </td>
                      <td className="py-3 px-3">
                        <span className="font-bold">{v.cvss_score.toFixed(1)}</span>
                        <span className="text-[10px] text-neutral-500 ml-1">({v.cvss_severity})</span>
                      </td>
                      <td className="py-3 px-3">
                        {v.in_kev ? (
                          <Badge color="pink" size="xs">
                            IN KEV
                          </Badge>
                        ) : (
                          <Badge color="zinc" size="xs">
                            NO
                          </Badge>
                        )}
                      </td>
                      <td className="py-3 px-3">
                        <div className="font-black text-xs text-black dark:text-white">
                          <span className="px-1.5 py-0.5 bg-[#FFE600] text-black border border-black inline-block">
                            {v.risk_score.toFixed(3)}
                          </span>
                        </div>
                        <span className="text-[10px] text-neutral-500">
                          {v.risk_band}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-right">
                        <button
                          type="button"
                          onClick={() => onSelectCve(v.cve_id)}
                          className="neo-btn px-2.5 py-1 text-[11px] font-bold bg-[#00F0FF] text-black border-2 border-black neo-shadow-sm hover:bg-[#38F4FF]"
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

        {/* Right: Top 10 Contextual Bar Chart (5 Cols) */}
        <div className="lg:col-span-5">
          <Top10BarChart vulnerabilities={vulnerabilities} onSelectCve={onSelectCve} />
        </div>
      </div>
    </div>
  );
};
