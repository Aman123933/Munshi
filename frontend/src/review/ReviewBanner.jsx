import React, { useState } from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  Lock,
  Cpu,
  Info,
} from 'lucide-react';
import { getTranslation } from '../i18n';

export default function ReviewBanner({
  status,
  itemsLeft,
  unresolvedReasons = [],
  llmMode,
  onLlmModeChange,
  uiLang = 'en',
}) {
  const [showTooltip, setShowTooltip] = useState(false);
  const t = (key) => getTranslation(uiLang, key);

  // LLM mode labels and tooltips
  const modeDetails = {
    gemini: {
      label: 'Gemini',
      fullName: 'Google Gemini 1.5 Pro',
      tooltip: 'Structured field extraction with temperature 0 via Gemini API',
      badgeClass: 'bg-blue/10 text-blue border-blue/30',
    },
    fallback: {
      label: 'Fallback parser',
      fullName: 'Deterministic Regex Fallback',
      tooltip: 'Deterministic pattern-matching parser fallback when LLM is unavailable',
      badgeClass: 'bg-purple-50 text-purple-700 border-purple-200',
    },
    cached: {
      label: 'Cached demo',
      fullName: 'Pre-Verified Cache',
      tooltip: 'Pre-verified extraction cache for deterministic evaluation reliability',
      badgeClass: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    },
  };

  const currentModeInfo = modeDetails[llmMode] || modeDetails.gemini;

  return (
    <div className="bg-white rounded-xl border border-line p-4 sm:p-5 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
      {/* Left: Overall Status Banner */}
      <div className="flex items-center space-x-3.5">
        {status === 'ready' && (
          <div className="w-10 h-10 rounded-xl bg-emerald-100 text-status-ok flex items-center justify-center flex-shrink-0">
            <CheckCircle2 className="w-6 h-6" />
          </div>
        )}
        {status === 'needs_review' && (
          <div className="w-10 h-10 rounded-xl bg-amber-100 text-status-review flex items-center justify-center flex-shrink-0">
            <AlertTriangle className="w-6 h-6" />
          </div>
        )}
        {status === 'blocked' && (
          <div className="w-10 h-10 rounded-xl bg-red-100 text-status-block flex items-center justify-center flex-shrink-0">
            <Lock className="w-6 h-6" />
          </div>
        )}

        <div>
          <div className="flex items-center space-x-2">
            <h2 className="font-heading text-base tracking-wide uppercase text-ink">
              {status === 'ready' && t('readyToConfirm')}
              {status === 'needs_review' && t('needsReview')}
              {status === 'blocked' && t('submissionBlocked')}
            </h2>
            <span
              className={`px-2 py-0.5 rounded text-[11px] font-bold font-mono uppercase tracking-wider border ${
                status === 'ready'
                  ? 'bg-emerald-50 text-status-ok border-status-ok/30'
                  : status === 'needs_review'
                  ? 'bg-amber-50 text-status-review border-status-review/30'
                  : 'bg-red-50 text-status-block border-status-block/30'
              }`}
            >
              {itemsLeft === 0
                ? t('zeroItemsLeft')
                : `${itemsLeft} ${t('itemsLeft')}`}
            </span>
          </div>
          <p className="text-xs text-grey mt-0.5 font-medium">
            {status === 'ready' &&
              'All fields verified and consistent. Ready to create database records.'}
            {status === 'needs_review' &&
              'Select ambiguous candidates or verify flagged fields below before confirming.'}
            {status === 'blocked' &&
              'Rule violations prevent confirmation. Edit blocked fields to re-check.'}
          </p>
        </div>
      </div>

      {/* Right: LLM Mode Badge with Tooltip */}
      <div className="flex items-center space-x-3 self-start md:self-center">
        <div className="relative">
          <div
            className={`inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border cursor-help ${currentModeInfo.badgeClass}`}
            onMouseEnter={() => setShowTooltip(true)}
            onMouseLeave={() => setShowTooltip(false)}
            onFocus={() => setShowTooltip(true)}
            onBlur={() => setShowTooltip(false)}
            tabIndex={0}
            role="region"
            aria-label={`LLM Mode: ${currentModeInfo.fullName}`}
          >
            <Cpu className="w-3.5 h-3.5" />
            <span className="font-heading uppercase text-[11px] tracking-wider text-grey-500">
              Pipeline:
            </span>
            <span className="font-bold">{currentModeInfo.label}</span>
            <Info className="w-3 h-3 text-grey-400" />
          </div>

          {/* Accessible Tooltip */}
          {showTooltip && (
            <div
              role="tooltip"
              className="absolute right-0 top-full mt-2 w-64 p-2.5 bg-ink text-white text-xs rounded-lg shadow-xl z-50 pointer-events-none animate-fadeIn"
            >
              <div className="font-bold text-amber mb-0.5">{currentModeInfo.fullName}</div>
              <p className="text-grey-200 text-[11px] leading-relaxed">
                {currentModeInfo.tooltip}
              </p>
              <div className="mt-1.5 pt-1.5 border-t border-grey-700 text-[10px] text-grey-400 font-mono">
                ENGINE: {llmMode.toUpperCase()}
              </div>
            </div>
          )}
        </div>

        {/* Demo Switcher for LLM mode testing */}
        {onLlmModeChange && (
          <div className="hidden sm:flex items-center text-xs text-grey bg-grey-50 border border-line rounded-lg px-2 py-1">
            <span className="text-[10px] font-bold uppercase tracking-wider mr-1.5 text-grey-400">
              Mode:
            </span>
            <select
              aria-label="Switch LLM Mode"
              value={llmMode}
              onChange={(e) => onLlmModeChange(e.target.value)}
              className="bg-transparent font-semibold text-ink text-xs focus:outline-none cursor-pointer"
            >
              <option value="gemini">Gemini</option>
              <option value="fallback">Fallback parser</option>
              <option value="cached">Cached demo</option>
            </select>
          </div>
        )}
      </div>
    </div>
  );
}
