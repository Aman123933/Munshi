import React from 'react';
import { UserCheck, Shield, ChevronDown, Languages } from 'lucide-react';
import { MOCK_TEACHERS } from '../api/mock';
import { getTranslation } from '../i18n';

export default function TopBar({
  currentUser,
  onTeacherChange,
  apiMode,
  onToggleApiMode,
  uiLang = 'en',
  onToggleUiLang,
}) {
  const t = (key) => getTranslation(uiLang, key);

  return (
    <header className="bg-white border-b border-line shadow-xs sticky top-0 z-40">
      {/* Top amber accent bar */}
      <div className="h-1.5 w-full bg-[#FFB020]" />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-3 flex flex-wrap items-center justify-between gap-3">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-blue flex items-center justify-center text-white font-heading font-black text-xl shadow-xs">
            M
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl sm:text-2xl font-heading tracking-wider text-ink uppercase">
                MUNSHI
              </h1>
              <span className="hidden sm:inline-block px-2 py-0.5 text-[10px] font-bold tracking-wider uppercase rounded bg-tint text-blue border border-blue/20">
                AI Assistant
              </span>
            </div>
            <p className="text-xs text-grey-700 font-medium tracking-tight">
              {t('principle')}
            </p>
          </div>
        </div>

        {/* Right side controls: Language toggle, API mode & Demo Teacher Switcher */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* UI Language Toggle (English / हिन्दी) */}
          <div className="inline-flex rounded-lg border border-line bg-grey-50 p-0.5 text-xs">
            <button
              type="button"
              onClick={() => onToggleUiLang && onToggleUiLang('en')}
              className={`px-2.5 py-1 rounded-md text-xs font-semibold transition cursor-pointer focus:outline-none focus:ring-1 focus:ring-blue ${
                uiLang === 'en'
                  ? 'bg-white text-blue shadow-xs font-bold'
                  : 'text-grey-700 hover:text-ink'
              }`}
              title="English UI Labels"
            >
              EN
            </button>
            <button
              type="button"
              onClick={() => onToggleUiLang && onToggleUiLang('hi')}
              className={`px-2.5 py-1 rounded-md text-xs font-semibold transition cursor-pointer focus:outline-none focus:ring-1 focus:ring-blue ${
                uiLang === 'hi'
                  ? 'bg-white text-blue shadow-xs font-bold'
                  : 'text-grey-700 hover:text-ink'
              }`}
              title="हिन्दी UI लेबल्स"
            >
              हिन्दी
            </button>
          </div>

          {/* API Mode Indicator */}
          <button
            onClick={onToggleApiMode}
            title="Click to toggle Mock / Live API mode"
            className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border transition focus:outline-none focus:ring-2 focus:ring-blue ${
              apiMode === 'mock'
                ? 'bg-amber-50 text-amber-dark border-amber/40 hover:bg-amber-100'
                : 'bg-emerald-50 text-status-ok border-status-ok/30 hover:bg-emerald-100'
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                apiMode === 'mock' ? 'bg-[#FFB020] animate-pulse' : 'bg-status-ok'
              }`}
            />
            <span className="font-mono uppercase text-[11px] font-bold">
              {apiMode}
            </span>
          </button>

          {/* Demo Teacher Switcher */}
          <div className="relative flex items-center bg-[#F9FAFB] border border-line rounded-lg px-2.5 py-1.5 shadow-xs hover:border-grey transition">
            <div className="mr-2 flex items-center">
              {currentUser?.role === 'principal' ? (
                <div className="w-6 h-6 rounded-full bg-amber-100 text-amber-dark flex items-center justify-center font-bold text-xs">
                  <Shield className="w-3.5 h-3.5" />
                </div>
              ) : (
                <div className="w-6 h-6 rounded-full bg-tint text-blue flex items-center justify-center font-bold text-xs">
                  <UserCheck className="w-3.5 h-3.5" />
                </div>
              )}
            </div>

            <div className="flex flex-col text-left mr-2">
              <span className="text-[9px] font-bold tracking-wider uppercase text-grey-500">
                {currentUser?.role === 'principal' ? 'Principal' : 'Teacher Login'}
              </span>
              <select
                aria-label="Demo Teacher Switcher"
                value={currentUser?.id || 'T01'}
                onChange={(e) => onTeacherChange(e.target.value)}
                className="bg-transparent text-xs font-semibold text-ink focus:outline-none cursor-pointer pr-4 max-w-[130px] sm:max-w-[200px] truncate"
              >
                <optgroup label="Teachers">
                  {MOCK_TEACHERS.filter((t) => t.role === 'teacher').map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.name} ({t.subject} - {t.classes.join(', ')})
                    </option>
                  ))}
                </optgroup>
                <optgroup label="Administration">
                  {MOCK_TEACHERS.filter((t) => t.role === 'principal').map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.name} (Principal)
                    </option>
                  ))}
                </optgroup>
              </select>
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-grey pointer-events-none -ml-3" />
          </div>
        </div>
      </div>
    </header>
  );
}
