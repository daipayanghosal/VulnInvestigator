import React, { useEffect, useState } from 'react';
import { ActivePage, Navbar, ThemeMode } from './components/Navbar';
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
  const [themeMode, setThemeMode] = useState<ThemeMode>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('theme_mode') || localStorage.getItem('theme');
      if (saved === 'light' || saved === 'dark' || saved === 'system') {
        return saved as ThemeMode;
      }
    }
    return 'system';
  });

  const [systemPrefersDark, setSystemPrefersDark] = useState<boolean>(() => {
    if (typeof window !== 'undefined') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    return true;
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = (e: MediaQueryListEvent) => setSystemPrefersDark(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  const isDark = themeMode === 'system' ? systemPrefersDark : themeMode === 'dark';

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
    } else {
      root.classList.remove('dark');
      root.style.colorScheme = 'light';
    }
    localStorage.setItem('theme_mode', themeMode);
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }, [themeMode, isDark]);

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
    <div className="min-h-screen bg-[#FDFBF7] dark:bg-[#0B0E14] text-black dark:text-[#E2E8F0] font-sans antialiased transition-colors flex flex-col selection:bg-[#C4A1FF] selection:text-black">
      <Navbar
        activePage={activePage}
        onPageChange={(page) => {
          setActivePage(page);
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }}
        themeMode={themeMode}
        onThemeModeChange={setThemeMode}
        isDark={isDark}
        onOpenKeyModal={() => setIsKeyModalOpen(true)}
        onOpenCustomCveModal={() => setIsCustomCveOpen(true)}
        hasApiKey={hasApiKey}
      />

      <main className="flex-1 max-w-[1600px] w-full mx-auto px-3 sm:px-6 lg:px-8 py-6">
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

      <footer className="mt-auto border-t-4 border-black dark:border-t-[#EAB308] bg-[#C4A1FF] dark:bg-[#0E121B] text-black dark:text-[#E2E8F0] font-mono py-4 px-4 sm:px-8">
        <div className="max-w-[1600px] mx-auto flex flex-col sm:flex-row items-center justify-between gap-3 text-center sm:text-left text-xs font-bold">
          <div className="flex items-center space-x-2 flex-wrap justify-center sm:justify-start">
            <span className="px-1.5 py-0.5 bg-black text-white dark:bg-[#FACC15] dark:text-black border border-black">[VI]</span>
            <span className="uppercase tracking-wider">VulnInvestigator</span>
            <span>&bull;</span>
            <span className="text-black/80 dark:text-neutral-400">Contextual Threat Prioritization &amp; Verifiable Telemetry</span>
          </div>
          <div className="flex items-center space-x-3 text-[11px]">
            <span>ENGINEERED BY <strong className="underline">DAIPAYAN GHOSAL</strong></span>
            <span>&bull;</span>
            <a
              href="https://daipayanghosal.github.io/VulnInvestigator/"
              target="_blank"
              rel="noreferrer"
              className="neo-btn px-2 py-0.5 border-2 border-black dark:border-[#2D3448] bg-white dark:bg-[#181D29] text-black dark:text-white hover:bg-neutral-100 uppercase"
            >
              GitHub Live Demo
            </a>
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
