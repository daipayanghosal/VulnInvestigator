import React, { useEffect, useState } from 'react';
import { ActivePage, Navbar } from './components/Navbar';
import { CustomCveModal } from './components/CustomCveModal';
import { ApiKeyModal } from './components/ApiKeyModal';
import { OverviewPage } from './pages/OverviewPage';
import { RankingsPage } from './pages/RankingsPage';
import { InvestigationPage } from './pages/InvestigationPage';
import { AiAssistantPage } from './pages/AiAssistantPage';
import { EvaluationPage } from './pages/EvaluationPage';

import initialVulns from './data/vulnerabilities_top.json';
import allVulnsCompact from './data/vulnerabilities_all.json';
import initialAssets from './data/assets.json';
import initialTechniques from './data/techniques.json';
import initialLogs from './data/logs.json';

import { Asset, SecurityLog, Technique, Vulnerability } from './types';
import { getStoredApiKey } from './utils/gemini';

export const App: React.FC = () => {
  const [activePage, setActivePage] = useState<ActivePage>('overview');
  const [isDark, setIsDark] = useState<boolean>(() => {
    if (typeof window !== 'undefined') {
      return (
        localStorage.getItem('theme') === 'dark' ||
        (!localStorage.getItem('theme') &&
          window.matchMedia('(prefers-color-scheme: dark)').matches)
      );
    }
    return false;
  });

  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>(() => {
    const topMap = new Map((initialVulns as Vulnerability[]).map((v) => [v.cve_id, v]));
    const fullList: Vulnerability[] = (allVulnsCompact as any[]).map((c) => {
      if (topMap.has(c.cve_id)) {
        return topMap.get(c.cve_id)!;
      }
      return {
        cve_id: c.cve_id,
        cvss_score: c.cvss_score,
        cvss_severity: c.cvss_severity,
        cvss_vector: 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H',
        in_kev: c.in_kev,
        risk_score: c.risk_score,
        risk_band: c.risk_band,
        matched_asset_id: c.matched_asset_id || 'SRV-WEB-001',
        rank_cvss: c.rank_cvss,
        rank_contextual: c.rank_contextual,
        rank_displacement: c.rank_displacement,
        description: c.desc || 'Vulnerability cataloged in NIST NVD.',
        affected_products: 'General software component',
        published_date: c.published_date,
      };
    });
    return fullList;
  });

  const [assets, setAssets] = useState<Asset[]>(initialAssets as any);
  const [techniques, setTechniques] = useState<Technique[]>(initialTechniques as any);
  const [logs, setLogs] = useState<SecurityLog[]>(initialLogs as any);

  const [selectedCveId, setSelectedCveId] = useState<string>('CVE-2021-44228');
  const [isCustomCveOpen, setIsCustomCveOpen] = useState(false);
  const [isKeyModalOpen, setIsKeyModalOpen] = useState(false);
  const [hasApiKey, setHasApiKey] = useState(() => Boolean(getStoredApiKey()));

  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      root.classList.add('dark');
      root.style.colorScheme = 'dark';
      localStorage.setItem('theme', 'dark');
    } else {
      root.classList.remove('dark');
      root.style.colorScheme = 'light';
      localStorage.setItem('theme', 'light');
    }
  }, [isDark]);

  const handleToggleTheme = () => {
    setIsDark(!isDark);
  };

  const handleSelectCve = (cveId: string) => {
    setSelectedCveId(cveId);
    setActivePage('investigation');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleRunAiInvestigation = (cveId: string) => {
    setSelectedCveId(cveId);
    setActivePage('ai_assistant');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleAddCustomCve = (newVuln: Vulnerability) => {
    const updated = [newVuln, ...vulnerabilities];
    updated.sort((a, b) => b.risk_score - a.risk_score);
    updated.forEach((v, idx) => {
      v.rank_contextual = idx + 1;
    });

    const cvssSorted = [...updated].sort((a, b) => b.cvss_score - a.cvss_score);
    cvssSorted.forEach((v, idx) => {
      v.rank_cvss = idx + 1;
      v.rank_displacement = v.rank_cvss - v.rank_contextual;
    });

    setVulnerabilities(updated);
    setSelectedCveId(newVuln.cve_id);
    setActivePage('investigation');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-[#F5F5F7] dark:bg-[#000000] text-[#1D1D1F] dark:text-[#F5F5F7] font-sans antialiased transition-colors flex flex-col selection:bg-[#0071E3]/20 selection:text-[#0071E3]">
      <Navbar
        activePage={activePage}
        onPageChange={(page) => {
          setActivePage(page);
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }}
        isDark={isDark}
        onToggleTheme={handleToggleTheme}
        onOpenKeyModal={() => setIsKeyModalOpen(true)}
        onOpenCustomCveModal={() => setIsCustomCveOpen(true)}
        hasApiKey={hasApiKey}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activePage === 'overview' && (
          <OverviewPage
            vulnerabilities={vulnerabilities}
            onSelectCve={handleSelectCve}
            onNavigateToRankings={() => setActivePage('rankings')}
            onNavigateToInvestigation={() => setActivePage('investigation')}
          />
        )}

        {activePage === 'rankings' && (
          <RankingsPage
            vulnerabilities={vulnerabilities}
            onSelectCve={handleSelectCve}
            onOpenCustomCveModal={() => setIsCustomCveOpen(true)}
          />
        )}

        {activePage === 'investigation' && (
          <InvestigationPage
            vulnerabilities={vulnerabilities}
            assets={assets}
            techniques={techniques}
            logs={logs}
            selectedCveId={selectedCveId}
            onSelectCve={(id) => setSelectedCveId(id)}
            onRunAiInvestigation={handleRunAiInvestigation}
            onOpenCustomCveModal={() => setIsCustomCveOpen(true)}
            onAddCustomCve={handleAddCustomCve}
          />
        )}

        {activePage === 'ai_assistant' && (
          <AiAssistantPage
            vulnerabilities={vulnerabilities}
            assets={assets}
            techniques={techniques}
            logs={logs}
            selectedCveId={selectedCveId}
            onSelectCve={(id) => setSelectedCveId(id)}
            onOpenKeyModal={() => setIsKeyModalOpen(true)}
            hasApiKey={hasApiKey}
          />
        )}

        {activePage === 'evaluation' && <EvaluationPage />}
      </main>

      <footer className="mt-auto border-t border-black/5 dark:border-white/10 bg-white/50 dark:bg-[#1C1C1E]/50 backdrop-blur-md py-6 text-xs text-[#86868B] dark:text-[#A1A1A6]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3 text-center sm:text-left">
          <div>
            <span className="font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">VulnInvestigator</span>
            <span className="mx-2">&bull;</span>
            <span>Contextual Threat Intelligence &amp; Prioritization</span>
          </div>
          <div>
            <span>Developed by Daipayan Ghosal</span>
          </div>
        </div>
      </footer>

      <CustomCveModal
        isOpen={isCustomCveOpen}
        onClose={() => setIsCustomCveOpen(false)}
        onAddCve={handleAddCustomCve}
        assets={assets}
      />

      <ApiKeyModal
        isOpen={isKeyModalOpen}
        onClose={() => setIsKeyModalOpen(false)}
        onKeySaved={(hasKey) => setHasApiKey(hasKey)}
      />
    </div>
  );
};

export default App;
