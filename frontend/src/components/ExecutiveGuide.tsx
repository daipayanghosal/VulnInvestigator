import React, { useState } from 'react';
import { BookOpen, ChevronDown, ChevronUp, Crosshair, HelpCircle, Server, ShieldAlert, Sparkles } from 'lucide-react';

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
    <div className="mb-6 rounded-2xl border border-black/8 dark:border-white/10 bg-white/60 dark:bg-[#1C1C1E]/60 backdrop-blur-sm overflow-hidden transition-all duration-200">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-5 py-3.5 flex items-center justify-between text-left hover:bg-black/[0.02] dark:hover:bg-white/[0.02] transition-colors"
      >
        <div className="flex items-center space-x-2.5">
          <div className="w-6 h-6 rounded-md bg-[#0071E3]/10 dark:bg-[#0071E3]/20 flex items-center justify-center text-[#0071E3]">
            <BookOpen className="w-3.5 h-3.5" />
          </div>
          <span className="text-xs font-semibold tracking-tight text-[#1D1D1F] dark:text-[#F5F5F7]">
            {title}
          </span>
          <span className="text-[10px] uppercase font-medium px-2 py-0.5 rounded-full bg-black/[0.04] dark:bg-white/[0.08] text-[#86868B] dark:text-[#A1A1A6]">
            Guidance for Evaluators
          </span>
        </div>
        <div className="text-[#86868B] dark:text-[#A1A1A6]">
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {isOpen && (
        <div className="px-5 pb-5 pt-2 border-t border-black/5 dark:border-white/5 text-xs text-[#1D1D1F] dark:text-[#E5E5EA] leading-relaxed">
          {children}
        </div>
      )}
    </div>
  );
};

export const OverviewExecutiveGuide: React.FC = () => {
  return (
    <ExecutiveGuide title="Executive & Evaluator Guide: What is VulnInvestigator?" defaultExpanded={false}>
      <div className="space-y-4">
        <div>
          <h4 className="font-semibold text-sm text-[#1D1D1F] dark:text-[#F5F5F7] mb-1">
            The Core Enterprise Problem
          </h4>
          <p className="text-neutral-600 dark:text-neutral-300">
            Modern enterprise security teams are inundated with thousands of software vulnerabilities annually. Traditional IT workflows rely almost exclusively on vendor-published <strong>CVSS base scores</strong> (0.0 to 10.0), which evaluate flaws in an isolated theoretical laboratory vacuum. Because standard CVSS scores approximately 40% of all published flaws as &ldquo;High&rdquo; or &ldquo;Critical&rdquo;, security operations suffer from severe <strong>alert fatigue</strong>&mdash;wasting engineering resources panic-patching unexploited internal systems while actively weaponized perimeter vulnerabilities remain unaddressed.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 pt-1">
          <div className="p-3 rounded-xl bg-black/[0.02] dark:bg-white/[0.03] border border-black/5 dark:border-white/5">
            <div className="flex items-center space-x-1.5 mb-1 text-[#0071E3]">
              <Crosshair className="w-3.5 h-3.5" />
              <span className="font-semibold text-xs text-[#1D1D1F] dark:text-[#F5F5F7]">1. Real Weaponization</span>
            </div>
            <p className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
              Corroborated with CISA Known Exploited Vulnerabilities (KEV) to confirm active threat actor attacks in the wild.
            </p>
          </div>

          <div className="p-3 rounded-xl bg-black/[0.02] dark:bg-white/[0.03] border border-black/5 dark:border-white/5">
            <div className="flex items-center space-x-1.5 mb-1 text-[#0071E3]">
              <Server className="w-3.5 h-3.5" />
              <span className="font-semibold text-xs text-[#1D1D1F] dark:text-[#F5F5F7]">2. Asset Importance</span>
            </div>
            <p className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
              Calculates business criticality (Customer PII database vs. developer testing laptop).
            </p>
          </div>

          <div className="p-3 rounded-xl bg-black/[0.02] dark:bg-white/[0.03] border border-black/5 dark:border-white/5">
            <div className="flex items-center space-x-1.5 mb-1 text-[#0071E3]">
              <ShieldAlert className="w-3.5 h-3.5" />
              <span className="font-semibold text-xs text-[#1D1D1F] dark:text-[#F5F5F7]">3. Network Exposure</span>
            </div>
            <p className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
              Evaluates accessibility (public Internet-facing perimeter vs. private air-gapped subnet).
            </p>
          </div>

          <div className="p-3 rounded-xl bg-black/[0.02] dark:bg-white/[0.03] border border-black/5 dark:border-white/5">
            <div className="flex items-center space-x-1.5 mb-1 text-[#0071E3]">
              <Sparkles className="w-3.5 h-3.5" />
              <span className="font-semibold text-xs text-[#1D1D1F] dark:text-[#F5F5F7]">4. Evidence-Grounded AI</span>
            </div>
            <p className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
              Bifurcates deterministic mathematical scoring from GenAI reasoning, automatically validating citations and flagging hallucinations.
            </p>
          </div>
        </div>

        <div className="pt-1 border-t border-black/5 dark:border-white/5 flex flex-wrap gap-x-6 gap-y-2 text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
          <div><strong>8,328 CVEs Analyzed</strong>: Full corpus from NIST NVD</div>
          <div><strong>1,768 in CISA KEV</strong>: Actively weaponized flaws</div>
          <div><strong>Kendall&rsquo;s &tau; = 0.5791</strong>: Significant, non-random prioritization correction</div>
          <div><strong>100% Citation Rate</strong>: Zero unsupported technical fabrications</div>
        </div>
      </div>
    </ExecutiveGuide>
  );
};
