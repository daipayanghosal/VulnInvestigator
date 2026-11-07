import React, { useState } from 'react';
import {
  FiBookOpen,
  FiChevronDown,
  FiChevronUp,
  FiCpu,
  FiServer,
  FiShield,
  FiTarget,
} from 'react-icons/fi';
import { Badge } from './common/Badge';

interface ExecutiveGuideProps {
  title?: string;
  defaultExpanded?: boolean;
  children: React.ReactNode;
}

export const ExecutiveGuide: React.FC<ExecutiveGuideProps> = ({
  title = 'Executive & Non-Technical Briefing',
  defaultExpanded = false,
  children,
}) => {
  const [isOpen, setIsOpen] = useState(defaultExpanded);

  return (
    <div className="mb-6 border-2 border-black dark:border-white bg-white dark:bg-[#141418] neo-shadow-sm transition-all">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-3 flex items-center justify-between text-left bg-neutral-100 dark:bg-[#1C1C22] hover:bg-[#FFE600] dark:hover:bg-[#2A2A35] transition-colors group cursor-pointer border-b-2 border-black dark:border-white"
      >
        <div className="flex items-center space-x-2.5 flex-wrap gap-y-1">
          <div className="w-6 h-6 bg-[#FFE600] text-black border border-black flex items-center justify-center neo-shadow-sm font-mono font-bold text-xs">
            <FiBookOpen className="w-3.5 h-3.5" />
          </div>
          <span className="font-mono font-bold text-xs sm:text-sm tracking-tight text-black dark:text-white uppercase">
            {title}
          </span>
          <Badge color="yellow" size="xs">
            DOCS &amp; GUIDANCE
          </Badge>
        </div>
        <div className="font-mono font-bold text-xs text-black dark:text-white flex items-center space-x-1 shrink-0 ml-2">
          <span className="hidden sm:inline text-[11px] uppercase">
            {isOpen ? '[ COLLAPSE ]' : '[ EXPAND ]'}
          </span>
          {isOpen ? <FiChevronUp className="w-4 h-4" /> : <FiChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {isOpen && (
        <div className="p-4 sm:p-5 text-xs sm:text-sm text-neutral-800 dark:text-neutral-200 leading-relaxed font-sans space-y-3">
          {children}
        </div>
      )}
    </div>
  );
};

export const OverviewExecutiveGuide: React.FC = () => {
  return (
    <ExecutiveGuide title="System Architectural Briefing: VulnInvestigator Paradigm" defaultExpanded={false}>
      <div className="space-y-4">
        <div>
          <h4 className="font-mono font-bold text-sm text-black dark:text-white uppercase mb-1">
            The Core Enterprise Problem: Static CVSS Alert Fatigue
          </h4>
          <p className="text-neutral-700 dark:text-neutral-300">
            Enterprise SOCs receive thousands of vulnerability alerts annually. Legacy triage workflows rely almost exclusively on vendor-published <strong>CVSS base scores</strong> (0.0 to 10.0), evaluating software bugs in an isolated laboratory vacuum. Because over 50% of published CVEs receive &ldquo;High&rdquo; or &ldquo;Critical&rdquo; ratings, security teams drown in alert fatigue&mdash;wasting days patching non-exploitable test environments while weaponized edge gateway vulnerabilities remain unpatched.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 pt-1">
          <div className="p-3 border-2 border-black dark:border-white bg-[#FFFBEB] dark:bg-[#1E1B13] neo-shadow-sm">
            <div className="flex items-center space-x-1.5 mb-1.5 text-black dark:text-white">
              <div className="w-5 h-5 bg-[#FFE600] border border-black flex items-center justify-center">
                <FiTarget className="w-3 h-3 text-black" />
              </div>
              <span className="font-mono font-bold text-xs uppercase">1. Active Weaponization</span>
            </div>
            <p className="text-[11px] font-mono text-neutral-600 dark:text-neutral-400">
              Cross-referenced with CISA Known Exploited Vulnerabilities (KEV) to confirm real-world attacker campaigns.
            </p>
          </div>

          <div className="p-3 border-2 border-black dark:border-white bg-[#EFF6FF] dark:bg-[#111928] neo-shadow-sm">
            <div className="flex items-center space-x-1.5 mb-1.5 text-black dark:text-white">
              <div className="w-5 h-5 bg-[#00F0FF] border border-black flex items-center justify-center">
                <FiServer className="w-3 h-3 text-black" />
              </div>
              <span className="font-mono font-bold text-xs uppercase">2. Business Criticality</span>
            </div>
            <p className="text-[11px] font-mono text-neutral-600 dark:text-neutral-400">
              Evaluates asset mission importance (Domain Controller &amp; ERP DB vs. ephemeral developer sandbox).
            </p>
          </div>

          <div className="p-3 border-2 border-black dark:border-white bg-[#FEF2F2] dark:bg-[#221516] neo-shadow-sm">
            <div className="flex items-center space-x-1.5 mb-1.5 text-black dark:text-white">
              <div className="w-5 h-5 bg-[#FF5376] border border-black flex items-center justify-center">
                <FiShield className="w-3 h-3 text-white" />
              </div>
              <span className="font-mono font-bold text-xs uppercase">3. Perimeter Exposure</span>
            </div>
            <p className="text-[11px] font-mono text-neutral-600 dark:text-neutral-400">
              Models attack surface accessibility (Internet-facing gateway vs. air-gapped segmented subnet).
            </p>
          </div>

          <div className="p-3 border-2 border-black dark:border-white bg-[#ECFDF5] dark:bg-[#102319] neo-shadow-sm">
            <div className="flex items-center space-x-1.5 mb-1.5 text-black dark:text-white">
              <div className="w-5 h-5 bg-[#B8FF00] border border-black flex items-center justify-center">
                <FiCpu className="w-3 h-3 text-black" />
              </div>
              <span className="font-mono font-bold text-xs uppercase">4. Grounded AI Interlock</span>
            </div>
            <p className="text-[11px] font-mono text-neutral-600 dark:text-neutral-400">
              Dual-bifurcated architecture: deterministic math computes priority; constrained Gemini synthesizes verifiable dossiers without hallucination.
            </p>
          </div>
        </div>
      </div>
    </ExecutiveGuide>
  );
};
