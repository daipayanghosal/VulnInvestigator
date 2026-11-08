import React, { useState } from 'react';
import { FiCheck, FiExternalLink, FiKey, FiTrash2, FiX } from 'react-icons/fi';
import { getStoredApiKey, setStoredApiKey } from '../utils/gemini';
import { Button } from './common/Button';

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
    }, 700);
  };

  const handleClear = () => {
    setApiKey('');
    setStoredApiKey('');
    onKeySaved(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs transition-all">
      <div className="w-full max-w-md border-3 border-black dark:border-[#2D3448] bg-[#F7F6F2] dark:bg-[#141824] neo-shadow-xl overflow-hidden animate-in zoom-in-95 duration-100">
        {/* Title Bar */}
        <div className="px-4 py-3 bg-[#C4A1FF] dark:bg-[#181D2A] text-black dark:text-[#E2E8F0] border-b-2 border-black dark:border-[#2D3448] flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 bg-black dark:bg-[#FACC15] text-[#C4A1FF] dark:text-black border border-black flex items-center justify-center neo-shadow-sm">
              <FiKey className="w-3.5 h-3.5" />
            </div>
            <span className="font-mono font-black text-sm uppercase tracking-tight">
              GEMINI API CONFIGURATION
            </span>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="neo-btn w-6 h-6 border-2 border-black dark:border-[#2D3448] bg-white dark:bg-[#202738] text-black dark:text-white flex items-center justify-center font-mono font-bold text-xs hover:bg-[#FF5376] hover:text-white"
          >
            <FiX className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Content Form */}
        <form onSubmit={handleSave} className="p-4 sm:p-5 space-y-4">
          <div>
            <label className="block text-xs font-mono font-bold uppercase tracking-wider text-black dark:text-white mb-1.5">
              Google Gemini API Key
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="AIzaSy..."
              className="w-full px-3 py-2 text-xs font-mono border-2 border-black dark:border-[#2D3448] bg-white dark:bg-[#11141D] text-black dark:text-[#E2E8F0] neo-shadow-sm focus:outline-none focus:bg-[#F5EEFF] dark:focus:bg-[#181D29]"
            />
            <p className="mt-2 text-[11px] font-mono text-neutral-600 dark:text-neutral-400 leading-relaxed">
              Stored 100% locally in your browser (<code className="text-black dark:text-white font-bold">localStorage</code>). Sent directly to Google&rsquo;s official API endpoint; zero server storage.
            </p>
          </div>

          <div className="p-3 border-2 border-dashed border-black dark:border-[#2D3448] bg-neutral-100 dark:bg-[#181D2A] text-xs font-mono">
            <span className="font-bold text-black dark:text-white block mb-1">
              Need a free API key?
            </span>
            <a
              href="https://aistudio.google.com/app/apikey"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[#0071E3] dark:text-[#38BDF8] font-bold underline inline-flex items-center space-x-1 hover:text-black dark:hover:text-white"
            >
              <span>Get key from Google AI Studio</span>
              <FiExternalLink className="w-3 h-3 ml-1" />
            </a>
          </div>

          <div className="flex items-center justify-between pt-2 border-t-2 border-black dark:border-white">
            <Button
              type="button"
              variant="danger"
              size="sm"
              icon={<FiTrash2 className="w-3 h-3" />}
              onClick={handleClear}
            >
              CLEAR
            </Button>
            <div className="flex items-center space-x-2">
              <Button type="button" variant="secondary" size="sm" onClick={onClose}>
                CANCEL
              </Button>
              <Button
                type="submit"
                variant="primary"
                size="sm"
                icon={isSaved ? <FiCheck className="w-3.5 h-3.5" /> : undefined}
              >
                {isSaved ? 'SAVED!' : 'SAVE KEY'}
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};
