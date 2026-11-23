import React, { useState } from 'react';
import { Send, SearchCheck, CheckCircle2, ChevronUp, ChevronDown, Sparkles } from 'lucide-react';
import { getTranslation } from '../i18n';

export default function FirstRunExplainer({ lang = 'en' }) {
  const [collapsed, setCollapsed] = useState(false);
  const t = (key) => getTranslation(lang, key);

  return (
    <div className="bg-gradient-to-r from-blue-50/80 via-white to-amber-50/70 rounded-xl border border-blue-200/70 p-4 sm:p-5 shadow-xs transition-all">
      {/* Principle Headline & Collapse Trigger */}
      <div className="flex items-center justify-between gap-3 pb-3 border-b border-line/60">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue text-white flex items-center justify-center font-bold shadow-xs">
            <Sparkles className="w-4 h-4 text-amber" />
          </div>
          <div>
            <div className="text-[11px] font-bold tracking-wider uppercase text-blue">
              {t('firstRunTitle')}
            </div>
            <div className="font-heading text-sm text-ink tracking-wide font-black">
              &ldquo;{t('principle')}&rdquo;
            </div>
          </div>
        </div>

        <button
          type="button"
          onClick={() => setCollapsed(!collapsed)}
          className="text-xs text-grey-600 hover:text-ink flex items-center space-x-1 px-2.5 py-1 rounded-md border border-line bg-white/80 transition cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue"
          title={collapsed ? 'Show explainer' : 'Hide explainer'}
        >
          <span className="text-[11px] font-semibold">{collapsed ? 'Show Steps' : 'Collapse'}</span>
          {collapsed ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
        </button>
      </div>

      {/* 3 Step Cards */}
      {!collapsed && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-3">
          {/* Step 1: Send */}
          <div className="p-3.5 bg-white/90 rounded-lg border border-line shadow-2xs space-y-1.5">
            <div className="flex items-center space-x-2 text-blue">
              <div className="w-6 h-6 rounded-md bg-blue/10 flex items-center justify-center font-bold text-xs">
                <Send className="w-3.5 h-3.5" />
              </div>
              <h4 className="font-heading text-xs uppercase tracking-wider text-ink font-bold">
                {t('step1Title')}
              </h4>
            </div>
            <p className="text-xs text-grey-700 leading-relaxed font-body">
              {t('step1Desc')}
            </p>
          </div>

          {/* Step 2: Review */}
          <div className="p-3.5 bg-white/90 rounded-lg border border-line shadow-2xs space-y-1.5">
            <div className="flex items-center space-x-2 text-amber-dark">
              <div className="w-6 h-6 rounded-md bg-amber-100 flex items-center justify-center font-bold text-xs text-amber-dark">
                <SearchCheck className="w-3.5 h-3.5" />
              </div>
              <h4 className="font-heading text-xs uppercase tracking-wider text-ink font-bold">
                {t('step2Title')}
              </h4>
            </div>
            <p className="text-xs text-grey-700 leading-relaxed font-body">
              {t('step2Desc')}
            </p>
          </div>

          {/* Step 3: Confirm */}
          <div className="p-3.5 bg-white/90 rounded-lg border border-line shadow-2xs space-y-1.5">
            <div className="flex items-center space-x-2 text-status-ok">
              <div className="w-6 h-6 rounded-md bg-emerald-100 flex items-center justify-center font-bold text-xs text-status-ok">
                <CheckCircle2 className="w-3.5 h-3.5" />
              </div>
              <h4 className="font-heading text-xs uppercase tracking-wider text-ink font-bold">
                {t('step3Title')}
              </h4>
            </div>
            <p className="text-xs text-grey-700 leading-relaxed font-body">
              {t('step3Desc')}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
