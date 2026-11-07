import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import Prism from 'prismjs';
import 'prismjs/components/prism-json';
import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-sql';
import 'prismjs/components/prism-splunk-spl';
import { FiAlertTriangle, FiCheck, FiCopy, FiTerminal } from 'react-icons/fi';

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
      return { grammar: Prism.languages['splunk-spl'], id: 'splunk-spl', label: 'SPL (SPLUNK)' };
    }
    if (l === 'elasticsearch' || l === 'elastic' || l === 'json') {
      return {
        grammar: Prism.languages['json'],
        id: 'json',
        label: l === 'elasticsearch' ? 'ELASTICSEARCH QUERY' : 'JSON',
      };
    }
    if (l === 'bash' || l === 'sh' || l === 'shell' || l === 'zsh') {
      return { grammar: Prism.languages['bash'], id: 'bash', label: 'BASH / CLI' };
    }
    if (l === 'python' || l === 'py') {
      return { grammar: Prism.languages['python'], id: 'python', label: 'PYTHON' };
    }
    if (l === 'sql') {
      return { grammar: Prism.languages['sql'], id: 'sql', label: 'SQL QUERY' };
    }
    return { grammar: null, id: l, label: lang.toUpperCase() || 'RAW' };
  };

  // Pre-process unsupported claims to cleanly display warning callouts
  const preprocessUnsupported = (rawText: string) => {
    return rawText.replace(/(\s*)\[UNSUPPORTED\]\s*/g, '\n\n[UNSUPPORTED] ');
  };

  return (
    <div className={`prose-sm max-w-none text-xs text-black dark:text-neutral-200 ${className}`}>
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
                  className="px-1.5 py-0.5 border border-black dark:border-[#2D3448] font-mono text-[11px] font-bold bg-[#FFE600] text-black dark:bg-[#1C2334] dark:text-[#FACC15] inline-block my-0.5"
                  {...props}
                >
                  {children}
                </code>
              );
            }

            const lang = match ? match[1] : '';
            const { grammar, id: prismId, label } = getGrammarForLang(lang);
            const cleanCode = rawString.replace(/\n$/, '');
            const codeHash = Math.abs(
              cleanCode.split('').reduce((acc, c) => (acc << 5) - acc + c.charCodeAt(0), 0)
            ).toString(36);

            let highlightedHtml = cleanCode;
            if (grammar) {
              try {
                highlightedHtml = Prism.highlight(cleanCode, grammar, prismId);
              } catch (e) {
                highlightedHtml = cleanCode;
              }
            }

            return (
              <div className="my-3 border-2 border-black dark:border-[#2D3448] neo-shadow-sm bg-[#0c0d12] text-neutral-100 overflow-hidden">
                {/* Neobrutalist Terminal Console Ribbon */}
                <div className="px-3 py-1.5 bg-[#00F0FF] dark:bg-[#181E2C] text-black dark:text-[#E2E8F0] border-b-2 border-black dark:border-[#2D3448] flex items-center justify-between font-mono">
                  <div className="flex items-center space-x-2">
                    <FiTerminal className="w-3.5 h-3.5 stroke-[2.5]" />
                    <span className="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.2 bg-black text-white dark:bg-[#202738] dark:text-[#38BDF8] border border-black dark:border-[#38425C]">
                      {label}
                    </span>
                    <span className="hidden sm:inline text-[10px] font-bold opacity-75">
                      // DEFENSIVE QUERY
                    </span>
                  </div>

                  <button
                    onClick={() => handleCopy(cleanCode, codeHash)}
                    className="neo-btn flex items-center space-x-1 px-2.5 py-1 border-2 border-black dark:border-[#2D3448] bg-[#FFE600] dark:bg-[#FACC15] text-black text-[10px] font-bold uppercase tracking-wider cursor-pointer"
                    title="Copy verifiable query to clipboard"
                  >
                    {copiedCodeId === codeHash ? (
                      <>
                        <FiCheck className="w-3.5 h-3.5 stroke-[3]" />
                        <span>COPIED!</span>
                      </>
                    ) : (
                      <>
                        <FiCopy className="w-3 h-3 stroke-[2.5]" />
                        <span>COPY QUERY</span>
                      </>
                    )}
                  </button>
                </div>

                {/* Highlighted Code Body */}
                <pre className="p-3.5 overflow-x-auto font-mono text-[11px] leading-relaxed select-text bg-[#0e1017]">
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
              <strong className="font-bold text-black dark:text-white bg-black/5 dark:bg-[#202738]/60 px-1 py-0.2 border-b-2 border-black dark:border-[#38425C]">
                {children}
              </strong>
            );
          },

          em({ children }) {
            return <em className="italic text-neutral-800 dark:text-neutral-200">{children}</em>;
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
                <div className="my-3 p-3 border-2 border-black dark:border-[#2D3448] bg-[#FF5376] dark:bg-[#3D141E] text-white dark:text-[#FDA4AF] neo-shadow-sm flex items-start space-x-2.5">
                  <FiAlertTriangle className="w-4 h-4 shrink-0 mt-0.5 stroke-[2.5]" />
                  <div className="text-xs">
                    <span className="font-mono font-bold uppercase text-[10px] tracking-wider bg-black dark:bg-[#202738] text-[#FFE600] dark:text-[#FACC15] px-1.5 py-0.5 border border-black dark:border-[#38425C] inline-block mb-1">
                      [UNSUPPORTED CLAIM] - SPECULATIVE / UNCORROBORATED BY SIEM
                    </span>
                    <div className="font-semibold">{cleanedChildren}</div>
                  </div>
                </div>
              );
            }

            return <p className="mb-2 leading-relaxed font-sans">{children}</p>;
          },

          ul({ children }) {
            return <ul className="list-disc pl-5 space-y-1 my-2 leading-relaxed">{children}</ul>;
          },

          ol({ children }) {
            return <ol className="list-decimal pl-5 space-y-1 my-2 leading-relaxed">{children}</ol>;
          },

          li({ children }) {
            return <li className="pl-0.5 leading-relaxed font-sans">{children}</li>;
          },
        }}
      />
    </div>
  );
};
