import React from 'react';
import {
  Activity,
  BarChart3,
  Key,
  LayoutDashboard,
  Monitor,
  Moon,
  Plus,
  Search,
  Sparkles,
  Sun,
} from 'lucide-react';

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
  const navItems = [
    { id: 'overview' as ActivePage, label: 'Overview', icon: LayoutDashboard },
    { id: 'rankings' as ActivePage, label: 'Rankings', icon: BarChart3 },
    { id: 'investigation' as ActivePage, label: 'Investigation', icon: Search },
    { id: 'ai_assistant' as ActivePage, label: 'AI Assistant', icon: Sparkles },
    { id: 'evaluation' as ActivePage, label: 'Evaluation', icon: Activity },
  ];

  return (
    <header className="sticky top-0 z-50 w-full backdrop-blur-xl bg-white/75 dark:bg-[#1c1c1e]/75 border-b border-black/5 dark:border-white/10 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        {/* Brand / Logo */}
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#0071E3] to-[#0051A8] flex items-center justify-center text-white shadow-sm">
            <Search className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-semibold text-sm tracking-tight text-[#1D1D1F] dark:text-[#F5F5F7]">
                VulnInvestigator
              </span>
              <span className="text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded-full bg-black/5 dark:bg-white/10 text-neutral-600 dark:text-neutral-300 tracking-wider">
                Evidence AI
              </span>
            </div>
            <span className="hidden sm:block text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
              Contextual Risk &amp; Threat Intelligence
            </span>
          </div>
        </div>

        {/* Apple-style Segmented Navigation Pills */}
        <nav className="hidden md:flex items-center p-1 rounded-full bg-black/[0.04] dark:bg-white/[0.08] border border-black/[0.04] dark:border-white/[0.06]">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onPageChange(item.id)}
                className={`flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-white dark:bg-[#2C2C2E] text-[#1D1D1F] dark:text-[#F5F5F7] shadow-sm'
                    : 'text-[#86868B] dark:text-[#A1A1A6] hover:text-[#1D1D1F] dark:hover:text-[#F5F5F7]'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-[#0071E3]' : ''}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Right Action Icons & Controls */}
        <div className="flex items-center space-x-2">
          {/* Custom CVE Ingest Action */}
          <button
            onClick={onOpenCustomCveModal}
            className="flex items-center space-x-1 px-2.5 py-1 text-xs font-medium rounded-full bg-black/[0.04] dark:bg-white/[0.08] hover:bg-black/[0.08] dark:hover:bg-white/[0.12] text-[#1D1D1F] dark:text-[#F5F5F7] border border-black/[0.04] dark:border-white/[0.06] transition-colors"
            title="Ingest custom or unlisted CVE"
          >
            <Plus className="w-3.5 h-3.5 text-[#0071E3]" />
            <span className="hidden lg:inline">Add CVE</span>
          </button>

          {/* Gemini API Key Indicator */}
          <button
            onClick={onOpenKeyModal}
            className={`flex items-center space-x-1 px-2.5 py-1 text-xs font-medium rounded-full border transition-colors ${
              hasApiKey
                ? 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-emerald-500/20 hover:bg-emerald-500/15'
                : 'bg-amber-500/10 text-amber-700 dark:text-amber-400 border-amber-500/20 hover:bg-amber-500/15'
            }`}
            title="Configure Google Gemini API Key"
          >
            <Key className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">
              {hasApiKey ? 'Gemini Ready' : 'Set Gemini Key'}
            </span>
          </button>

          {/* 3-State Theme Toggle (Light / Dark / System) */}
          <div
            className="flex items-center p-0.5 rounded-full bg-black/[0.04] dark:bg-white/[0.08] border border-black/10 dark:border-white/10"
            role="group"
            aria-label="Theme appearance switcher"
          >
            <button
              onClick={() => onThemeModeChange('light')}
              className={`flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-medium transition-all cursor-pointer ${
                themeMode === 'light'
                  ? 'bg-white dark:bg-[#2C2C2E] text-[#1D1D1F] dark:text-[#F5F5F7] shadow-xs font-semibold'
                  : 'text-[#86868B] dark:text-[#A1A1A6] hover:text-[#1D1D1F] dark:hover:text-[#F5F5F7]'
              }`}
              title="Force Light Theme"
              aria-pressed={themeMode === 'light'}
            >
              <Sun className={`w-3.5 h-3.5 ${themeMode === 'light' ? 'text-amber-500' : ''}`} />
              <span className="hidden sm:inline text-[11px]">Light</span>
            </button>

            <button
              onClick={() => onThemeModeChange('dark')}
              className={`flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-medium transition-all cursor-pointer ${
                themeMode === 'dark'
                  ? 'bg-white dark:bg-[#2C2C2E] text-[#1D1D1F] dark:text-[#F5F5F7] shadow-xs font-semibold'
                  : 'text-[#86868B] dark:text-[#A1A1A6] hover:text-[#1D1D1F] dark:hover:text-[#F5F5F7]'
              }`}
              title="Force Dark Theme"
              aria-pressed={themeMode === 'dark'}
            >
              <Moon className={`w-3.5 h-3.5 ${themeMode === 'dark' ? 'text-[#0071E3]' : ''}`} />
              <span className="hidden sm:inline text-[11px]">Dark</span>
            </button>

            <button
              onClick={() => onThemeModeChange('system')}
              className={`flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-medium transition-all cursor-pointer ${
                themeMode === 'system'
                  ? 'bg-white dark:bg-[#2C2C2E] text-[#1D1D1F] dark:text-[#F5F5F7] shadow-xs font-semibold'
                  : 'text-[#86868B] dark:text-[#A1A1A6] hover:text-[#1D1D1F] dark:hover:text-[#F5F5F7]'
              }`}
              title={`Match System Appearance (${isDark ? 'Dark' : 'Light'})`}
              aria-pressed={themeMode === 'system'}
            >
              <Monitor className={`w-3.5 h-3.5 ${themeMode === 'system' ? 'text-emerald-500 dark:text-emerald-400' : ''}`} />
              <span className="hidden sm:inline text-[11px]">System</span>
            </button>
          </div>

          {/* GitHub Repo */}
          <a
            href="https://github.com/daipayanghosal/VulnInvestigator"
            target="_blank"
            rel="noopener noreferrer"
            className="w-8 h-8 rounded-full flex items-center justify-center text-[#86868B] dark:text-[#A1A1A6] hover:text-[#1D1D1F] dark:hover:text-[#F5F5F7] hover:bg-black/[0.04] dark:hover:bg-white/[0.08] transition-colors"
            aria-label="GitHub Repository"
          >
            <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24" aria-hidden="true">
              <path
                fillRule="evenodd"
                clipRule="evenodd"
                d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
              />
            </svg>
          </a>
        </div>
      </div>

      {/* Mobile Navigation Bar */}
      <div className="md:hidden flex items-center justify-around px-2 py-1.5 border-t border-black/[0.04] dark:border-white/[0.06] bg-black/[0.01] dark:bg-white/[0.02]">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onPageChange(item.id)}
              className={`flex flex-col items-center py-1 px-2 text-[10px] font-medium transition-colors ${
                isActive
                  ? 'text-[#0071E3]'
                  : 'text-[#86868B] dark:text-[#A1A1A6]'
              }`}
            >
              <Icon className="w-4 h-4 mb-0.5" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>
    </header>
  );
};
