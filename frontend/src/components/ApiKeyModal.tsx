import React, { useState } from 'react';
import { Check, ExternalLink, Key, ShieldCheck, X } from 'lucide-react';
import { getStoredApiKey, setStoredApiKey } from '../utils/gemini';

interface ApiKeyModalProps {
  isOpen: boolean;
  onClose: () => void;
  onKeySaved: (hasKey: boolean) => void;
}

export const ApiKeyModal: React.FC<ApiKeyModalProps> = ({
  isOpen,
  onClose,
  onKeySaved,
}) => {
  const [apiKey, setApiKey] = useState(getStoredApiKey());
  const [isSaved, setIsSaved] = useState(false);

  if (!isOpen) return null;

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setStoredApiKey(apiKey);
    setIsSaved(true);
    onKeySaved(Boolean(apiKey.trim()));
    setTimeout(() => {
      setIsSaved(false);
      onClose();
    }, 800);
  };

  const handleClear = () => {
    setApiKey('');
    setStoredApiKey('');
    onKeySaved(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm transition-all">
      <div className="w-full max-w-md rounded-3xl bg-white dark:bg-[#1C1C1E] border border-black/10 dark:border-white/10 shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        <div className="px-6 py-4 border-b border-black/5 dark:border-white/5 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-7 h-7 rounded-lg bg-[#0071E3]/10 dark:bg-[#0071E3]/20 flex items-center justify-center text-[#0071E3]">
              <Key className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">
                Google Gemini API Key
              </h3>
              <p className="text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
                Configure live LLM evidence-grounded threat synthesis
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

        <form onSubmit={handleSave} className="p-6 space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-[#86868B] dark:text-[#A1A1A6] mb-1.5">
              API Key
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="AIzaSy..."
              className="w-full px-3 py-2 text-xs rounded-xl bg-black/[0.03] dark:bg-white/[0.05] border border-black/10 dark:border-white/10 text-[#1D1D1F] dark:text-[#F5F5F7] focus:outline-none focus:ring-2 focus:ring-[#0071E3]"
            />
            <p className="mt-1.5 text-[11px] text-[#86868B] dark:text-[#A1A1A6]">
              Your key is stored only in your local browser storage (<code className="text-[10px]">localStorage</code>) and is sent directly to Google&rsquo;s API endpoint. It is never logged or transmitted elsewhere.
            </p>
          </div>

          <div className="p-3 rounded-xl bg-neutral-50 dark:bg-neutral-800/50 border border-neutral-200 dark:border-neutral-700/50 text-[11px] text-neutral-600 dark:text-neutral-400 space-y-1">
            <div className="font-semibold text-neutral-800 dark:text-neutral-200 flex items-center space-x-1">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
              <span>Offline / Demo Mode Supported</span>
            </div>
            <p>
              Don&rsquo;t have a key? Leave this empty. The platform automatically uses pre-generated high-fidelity benchmark reports so you can evaluate the AI Assistant and grounding validator instantly.
            </p>
          </div>

          <div className="flex items-center justify-between pt-2">
            <a
              href="https://aistudio.google.com/app/apikey"
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-[#0071E3] hover:underline flex items-center space-x-1"
            >
              <span>Get a free key at Google AI Studio</span>
              <ExternalLink className="w-3 h-3" />
            </a>

            <div className="flex items-center space-x-2">
              {apiKey && (
                <button
                  type="button"
                  onClick={handleClear}
                  className="px-3 py-1.5 text-xs font-medium text-neutral-500 hover:text-red-500 transition-colors"
                >
                  Clear Key
                </button>
              )}
              <button
                type="submit"
                className="px-4 py-1.5 text-xs font-medium rounded-xl bg-[#0071E3] hover:bg-[#0077ED] text-white transition-colors flex items-center space-x-1"
              >
                {isSaved ? <Check className="w-3.5 h-3.5" /> : null}
                <span>{isSaved ? 'Saved' : 'Save Key'}</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};
