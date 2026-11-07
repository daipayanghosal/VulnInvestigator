import React, { useState } from 'react';
import {
  RiBarChartBoxLine,
  RiDashboardLine,
  RiGithubFill,
  RiPulseLine,
  RiSearchEyeLine,
  RiTerminalBoxLine,
} from 'react-icons/ri';
import {
  FiCheck,
  FiKey,
  FiMenu,
  FiMonitor,
  FiMoon,
  FiPlus,
  FiSun,
  FiX,
} from 'react-icons/fi';
import { Badge } from './common/Badge';

export type ActivePage = 'overview' | 'rankings' | 'investigation' | 'ai_assistant' | 'evaluation';
export type ThemeMode = 'light' | 'dark' | 'system';

interface NavbarProps {
  activePage: ActivePage;
  onPageChange: (page: ActivePage) => void;
  themeMode: ThemeMode;
  onThemeModeChange: (mode: ThemeMode) => void;
  isDark: boolean;
  onOpenKeyModal: () => void;
  onOpenCustomCveModal: () => void;
  hasApiKey: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  activePage,
  onPageChange,
  themeMode,
  onThemeModeChange,
  isDark,
  onOpenKeyModal,
  onOpenCustomCveModal,
  hasApiKey,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { id: 'overview' as ActivePage, label: 'Overview', icon: RiDashboardLine, accent: 'bg-[#FFE600]' },
    { id: 'rankings' as ActivePage, label: 'Rankings', icon: RiBarChartBoxLine, accent: 'bg-[#00F0FF]' },
    { id: 'investigation' as ActivePage, label: 'Investigation', icon: RiSearchEyeLine, accent: 'bg-[#B8FF00]' },
    { id: 'ai_assistant' as ActivePage, label: 'Telemetry Forensics', icon: RiTerminalBoxLine, accent: 'bg-[#A78BFA]' },
    { id: 'evaluation' as ActivePage, label: 'Evaluation', icon: RiPulseLine, accent: 'bg-[#FF5376]' },
  ];

  const handleNavClick = (page: ActivePage) => {
    onPageChange(page);
    setMobileMenuOpen(false);
  };

  return (
    <header className="sticky top-0 z-50 w-full bg-[#F7F6F2] dark:bg-[#0B0E14] border-b-2 sm:border-b-[3px] border-black dark:border-[#2D3448] transition-colors">
      {/* Top Banner Ribbon */}
      <div className="bg-[#FFE600] text-black dark:bg-[#0E121B] dark:text-[#E2E8F0] border-b-2 border-black dark:border-[#222838] px-4 py-1 text-[11px] font-mono font-bold flex items-center justify-between overflow-x-auto whitespace-nowrap">
        <div className="flex items-center space-x-3">
          <span className="bg-black text-[#FFE600] dark:bg-[#FACC15] dark:text-black px-1.5 py-0.2 border border-black uppercase tracking-wider text-[10px]">
            EVIDENCE-GROUNDED CTI
          </span>
          <span className="hidden sm:inline">
            DISSERTATION DEFENSE WORKBENCH // CSIW ZG628T // BITS PILANI &amp; WIPRO
          </span>
          <span className="sm:hidden">BITS PILANI // WIPRO</span>
        </div>
        <div className="flex items-center space-x-3 text-[10px]">
          <span className="hidden md:inline">8,328 CVES INGESTED</span>
          <span>•</span>
          <span className="text-rose-900 dark:text-[#FB7185] font-extrabold">1,350 CISA KEVS</span>
          <span>•</span>
          <span className="text-emerald-900 dark:text-[#34D399] font-extrabold">94.0% GROUNDED</span>
        </div>
      </div>

      {/* Main Nav Bar */}
      <div className="w-full max-w-[1600px] mx-auto px-3 sm:px-6 lg:px-8 h-14 sm:h-16 flex items-center justify-between gap-2">
        {/* Brand / Logo */}
        <div
          onClick={() => handleNavClick('overview')}
          className="flex items-center space-x-2.5 cursor-pointer select-none group"
        >
          <div className="w-9 h-9 sm:w-10 sm:h-10 bg-[#FFE600] dark:bg-[#FACC15] border-2 border-black dark:border-[#2D3448] flex items-center justify-center font-mono font-black text-black text-base neo-shadow-sm group-hover:-translate-y-0.5 transition-transform">
            VI
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-mono font-extrabold text-sm sm:text-base tracking-tight text-black dark:text-white uppercase">
                VulnInvestigator
              </span>
              <span className="hidden lg:inline-block px-1.5 py-0.2 text-[9px] font-mono font-extrabold bg-[#B8FF00] dark:bg-[#65A30D] text-black dark:text-white border border-black dark:border-transparent uppercase tracking-wider">
                PROD
              </span>
            </div>
            <div className="text-[10px] font-mono text-neutral-600 dark:text-neutral-400 hidden sm:block tracking-wide">
              Contextual Risk &amp; Threat Telemetry
            </div>
          </div>
        </div>

        {/* Desktop Navigation Segmented Buttons */}
        <nav className="hidden lg:flex items-center p-1 border-2 border-black dark:border-[#2D3448] bg-white dark:bg-[#121622] neo-shadow-sm gap-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => handleNavClick(item.id)}
                className={`neo-btn flex items-center space-x-1.5 px-3 py-1.5 text-xs font-mono font-bold tracking-tight select-none border-2 transition-all ${
                  isActive
                    ? `border-black dark:border-[#3E4964] ${item.accent} text-black dark:bg-[#1E2536] dark:text-[#FACC15] neo-shadow-sm`
                    : 'border-transparent text-neutral-700 dark:text-neutral-300 hover:border-black/30 dark:hover:border-[#38415A] hover:bg-black/5 dark:hover:bg-white/5'
                }`}
              >
                <Icon className="w-3.5 h-3.5 shrink-0" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Right Action Controls */}
        <div className="flex items-center space-x-1.5 sm:space-x-2">
          {/* Custom CVE Ingest Action Button */}
          <button
            type="button"
            onClick={onOpenCustomCveModal}
            className="neo-btn flex items-center space-x-1 px-2.5 sm:px-3 py-1.5 text-xs font-mono font-bold bg-[#00F0FF] dark:bg-[#0284C7] text-black dark:text-white border-2 border-black dark:border-[#2D3448] neo-shadow-sm hover:bg-[#38F4FF] dark:hover:bg-[#0369A1]"
            title="Ingest custom or unlisted CVE into risk engine"
          >
            <FiPlus className="w-3.5 h-3.5 stroke-[3]" />
            <span className="hidden sm:inline">INGEST CVE</span>
            <span className="sm:hidden">CVE</span>
          </button>

          {/* Gemini API Key Status Button */}
          <button
            type="button"
            onClick={onOpenKeyModal}
            className={`neo-btn flex items-center space-x-1 px-2.5 sm:px-3 py-1.5 text-xs font-mono font-bold border-2 border-black dark:border-[#2D3448] neo-shadow-sm ${
              hasApiKey
                ? 'bg-[#B8FF00] dark:bg-[#1A2E1A] text-black dark:text-[#BEF264] hover:bg-[#C9FF38] dark:border-[#305228]'
                : 'bg-white dark:bg-[#181D29] text-black dark:text-[#E2E8F0] hover:bg-neutral-100 dark:hover:bg-[#202737]'
            }`}
            title={hasApiKey ? 'Gemini API Key Configured' : 'Configure Gemini API Key'}
          >
            <FiKey className="w-3 h-3 stroke-[2.5]" />
            <span className="hidden md:inline">
              {hasApiKey ? 'API READY' : 'SET KEY'}
            </span>
            {hasApiKey && (
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-700 dark:bg-emerald-400 inline-block animate-pulse" />
            )}
          </button>

          {/* 3-Way Theme Toggle: Light, Dark, System */}
          <div className="flex items-center border-2 border-black dark:border-[#2D3448] bg-white dark:bg-[#121622] p-0.5 neo-shadow-sm">
            <button
              type="button"
              onClick={() => onThemeModeChange('light')}
              className={`p-1.5 text-xs font-mono transition-colors ${
                themeMode === 'light'
                  ? 'bg-[#FFE600] text-black font-bold border border-black shadow-[1px_1px_0px_#000]'
                  : 'text-neutral-500 hover:text-black dark:hover:text-white'
              }`}
              title="Light Mode"
            >
              <FiSun className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={() => onThemeModeChange('dark')}
              className={`p-1.5 text-xs font-mono transition-colors ${
                themeMode === 'dark'
                  ? 'bg-[#FFE600] dark:bg-[#202738] text-black dark:text-[#FACC15] font-bold border border-black dark:border-[#38425C] shadow-[1px_1px_0px_#000] dark:shadow-none'
                  : 'text-neutral-500 hover:text-black dark:hover:text-white'
              }`}
              title="Dark Mode"
            >
              <FiMoon className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={() => onThemeModeChange('system')}
              className={`p-1.5 text-xs font-mono transition-colors ${
                themeMode === 'system'
                  ? 'bg-[#FFE600] dark:bg-[#202738] text-black dark:text-[#FACC15] font-bold border border-black dark:border-[#38425C] shadow-[1px_1px_0px_#000] dark:shadow-none'
                  : 'text-neutral-500 hover:text-black dark:hover:text-white'
              }`}
              title="System Theme"
            >
              <FiMonitor className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* GitHub Link */}
          <a
            href="https://github.com/daipayanghosal/VulnInvestigator"
            target="_blank"
            rel="noopener noreferrer"
            className="neo-btn p-1.5 sm:p-2 border-2 border-black dark:border-[#2D3448] bg-white dark:bg-[#181D29] text-black dark:text-white neo-shadow-sm hover:bg-neutral-100 dark:hover:bg-[#202737] hidden sm:flex items-center justify-center"
            title="View Source on GitHub"
          >
            <RiGithubFill className="w-4 h-4" />
          </a>

          {/* Mobile Menu Hamburger */}
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden neo-btn p-1.5 border-2 border-black dark:border-[#2D3448] bg-white dark:bg-[#181D29] text-black dark:text-white neo-shadow-sm"
            aria-label="Toggle Navigation"
          >
            {mobileMenuOpen ? <FiX className="w-5 h-5" /> : <FiMenu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation Dropdown Drawer */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-t-2 border-black dark:border-[#2D3448] bg-[#F7F6F2] dark:bg-[#0B0E14] p-3 space-y-2 animate-in slide-in-from-top-2">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activePage === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => handleNavClick(item.id)}
                  className={`neo-btn flex items-center space-x-2 px-3 py-2 text-xs font-mono font-bold tracking-tight border-2 border-black dark:border-[#2D3448] ${
                    isActive
                      ? `${item.accent} text-black dark:bg-[#1E2536] dark:text-[#FACC15] neo-shadow-sm`
                      : 'bg-white dark:bg-[#141824] text-black dark:text-white'
                  }`}
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>
          <div className="pt-2 border-t border-black/10 dark:border-white/10 flex items-center justify-between text-xs font-mono">
            <span className="text-neutral-600 dark:text-neutral-400">GitHub Source Code</span>
            <a
              href="https://github.com/daipayanghosal/VulnInvestigator"
              target="_blank"
              rel="noopener noreferrer"
              className="font-bold underline text-black dark:text-white flex items-center space-x-1"
            >
              <span>Repo</span>
              <RiGithubFill className="w-3.5 h-3.5" />
            </a>
          </div>
        </div>
      )}
    </header>
  );
};

export default Navbar;
