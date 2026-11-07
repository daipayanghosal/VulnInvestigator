import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import Prism from 'prismjs';
import 'prismjs/components/prism-json';
import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-sql';
import 'prismjs/components/prism-splunk-spl';
import { AlertTriangle, Check, Copy } from 'lucide-react';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content, className = '' }) => {
  const [copiedCodeId, setCopiedCodeId] = useState<string | null>(null);

  const handleCopy = (codeText: string, id: string) => {
    navigator.clipboard.writeText(codeText);
    setCopiedCodeId(id);
    setTimeout(() => {
      setCopiedCodeId((cur) => (cur === id ? null : cur));
    }, 2000);
  };

  const getGrammarForLang = (lang: string) => {
    const l = lang.toLowerCase();
    if (l === 'spl' || l === 'splunk' || l === 'splunk-spl') {
      return { grammar: Prism.languages['splunk-spl'], id: 'splunk-spl', label: 'SPL' };
    }
    if (l === 'elasticsearch' || l === 'elastic' || l === 'json') {
      return { grammar: Prism.languages['json'], id: 'json', label: l === 'elasticsearch' ? 'ELASTICSEARCH' : 'JSON' };
    }
    if (l === 'bash' || l === 'sh' || l === 'shell' || l === 'zsh') {
      return { grammar: Prism.languages['bash'], id: 'bash', label: 'BASH' };
    }
    if (l === 'python' || l === 'py') {
      return { grammar: Prism.languages['python'], id: 'python', label: 'PYTHON' };
    }
    if (l === 'sql') {
      return { grammar: Prism.languages['sql'], id: 'sql', label: 'SQL' };
    }
    return { grammar: null, id: l, label: lang.toUpperCase() || 'CODE' };
  };

  // Pre-process unsupported claims to cleanly display warning callouts
  const preprocessUnsupported = (rawText: string) => {
    return rawText.replace(/(\s*)\[UNSUPPORTED\]\s*/g, '\n\n[UNSUPPORTED] ');
  };

  return (
    <div className={`prose-sm max-w-none text-xs text-[#1D1D1F] dark:text-[#E5E5EA] ${className}`}>
      <ReactMarkdown
        children={preprocessUnsupported(content)}
        components={{
          code({ className: codeClassName, children, ...props }: any) {
            const rawString = String(children);
            const match = /language-(\w+)/.exec(codeClassName || '');
            const isBlock = Boolean(match || rawString.includes('\n'));

            if (!isBlock) {
              return (
                <code
                  className="px-1.5 py-0.5 rounded-md font-mono text-[11px] bg-black/[0.05] dark:bg-white/[0.08] text-[#0071E3] dark:text-[#389BF2] border border-black/5 dark:border-white/10 font-semibold inline-block my-0.5"
                  {...props}
                >
                  {children}
                </code>
              );
            }

            const lang = match ? match[1] : '';
            const { grammar, id: prismId, label } = getGrammarForLang(lang);
            const cleanCode = rawString.replace(/\n$/, '');
            const codeHash = Math.abs(cleanCode.split('').reduce((acc, c) => (acc << 5) - acc + c.charCodeAt(0), 0)).toString(36);

            let highlightedHtml = cleanCode;
            if (grammar) {
              try {
                highlightedHtml = Prism.highlight(cleanCode, grammar, prismId);
              } catch (e) {
                highlightedHtml = cleanCode;
              }
            }

            return (
              <div className="my-3 rounded-2xl overflow-hidden border border-black/10 dark:border-white/10 bg-[#0d1117] text-neutral-100 shadow-md">
                {/* Apple Terminal Window Header */}
                <div className="px-3.5 py-2 bg-[#161b22] border-b border-white/5 flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {/* macOS Traffic Lights */}
                    <div className="flex items-center space-x-1.5">
                      <div className="w-2.5 h-2.5 rounded-full bg-[#ff5f56]" />
                      <div className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e]" />
                      <div className="w-2.5 h-2.5 rounded-full bg-[#27c93f]" />
                    </div>
                    <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-white/10 text-neutral-300 ml-2 tracking-wide">
                      {label}
                    </span>
                  </div>

                  <button
                    onClick={() => handleCopy(cleanCode, codeHash)}
                    className="flex items-center space-x-1 px-2.5 py-1 rounded-lg text-[11px] font-medium text-neutral-400 hover:text-white hover:bg-white/10 transition-all cursor-pointer"
                    title="Copy code snippet"
                  >
                    {copiedCodeId === codeHash ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                        <span className="text-emerald-400 font-semibold">Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5" />
                        <span>Copy</span>
                      </>
                    )}
                  </button>
                </div>

                {/* Highlighted Code Body */}
                <pre className="p-4 overflow-x-auto font-mono text-[11px] leading-relaxed select-text">
                  <code
                    className={`language-${prismId}`}
                    dangerouslySetInnerHTML={{ __html: highlightedHtml }}
                  />
                </pre>
              </div>
            );
          },

          strong({ children }) {
            return (
              <strong className="font-semibold text-[#1D1D1F] dark:text-[#F5F5F7]">
                {children}
              </strong>
            );
          },

          em({ children }) {
            return <em className="italic text-neutral-700 dark:text-neutral-300">{children}</em>;
          },

          p({ children }) {
            const hasUnsupported = React.Children.toArray(children).some(
              (child) => typeof child === 'string' && child.includes('[UNSUPPORTED]')
            );

            if (hasUnsupported) {
              const cleanedChildren = React.Children.map(children, (child) => {
                if (typeof child === 'string') {
                  return child.replace(/\[UNSUPPORTED\]/g, '').trimStart();
                }
                return child;
              });

              return (
                <div className="my-3 p-3.5 rounded-2xl bg-amber-500/10 border border-amber-500/25 text-amber-900 dark:text-amber-200 flex items-start space-x-2.5 leading-relaxed">
                  <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
                  <div className="text-xs">
                    <span className="font-semibold uppercase text-[10px] tracking-wider text-amber-700 dark:text-amber-400 block mb-0.5">
                      Speculative Claim (Uncorroborated by Logs)
                    </span>
                    {cleanedChildren}
                  </div>
                </div>
              );
            }

            return <p className="mb-2 leading-relaxed last:mb-0">{children}</p>;
          },

          ul({ children }) {
            return <ul className="list-disc pl-4 space-y-1.5 my-2.5 leading-relaxed">{children}</ul>;
          },

          ol({ children }) {
            return <ol className="list-decimal pl-4 space-y-2 my-2.5 leading-relaxed">{children}</ol>;
          },

          li({ children }) {
            return <li className="pl-0.5 leading-relaxed">{children}</li>;
          },
        }}
      />
    </div>
  );
};
