import React, { useState } from 'react';
import {
  CheckCircle2,
  Copy,
  Check,
  Languages,
  RotateCcw,
  ShieldCheck,
  BookOpen,
  CalendarCheck,
  FileCheck2,
} from 'lucide-react';

export default function SuccessPanel({ confirmResult, onNewMessage }) {
  const [draftLanguage, setDraftLanguage] = useState('English');
  const [copiedId, setCopiedId] = useState(null);
  const [copiedAudit, setCopiedAudit] = useState(false);

  if (!confirmResult) return null;

  const handleCopy = async (text, id) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (err) {
      console.error('Clipboard copy failed:', err);
    }
  };

  const handleCopyAudit = async () => {
    try {
      await navigator.clipboard.writeText(confirmResult.audit_id);
      setCopiedAudit(true);
      setTimeout(() => setCopiedAudit(false), 2000);
    } catch (err) {
      console.error('Clipboard copy failed:', err);
    }
  };

  // Filter drafts by chosen language toggle
  const filteredDrafts = (confirmResult.drafts || []).filter(
    (d) => d.language.toLowerCase() === draftLanguage.toLowerCase()
  );

  return (
    <div className="bg-white rounded-xl border border-emerald-200 p-6 shadow-sm space-y-6">
      {/* 1. Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-line gap-3">
        <div className="flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-xl bg-emerald-100 text-status-ok flex items-center justify-center flex-shrink-0">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <div>
            <h2 className="font-heading text-lg tracking-wide uppercase text-ink">
              Records Successfully Created &amp; Committed
            </h2>
            <p className="text-xs text-grey font-medium">
              Single atomic database transaction verified and recorded in the audit log.
            </p>
          </div>
        </div>

        {/* Audit ID Badge with Copy */}
        <div className="flex items-center space-x-2 bg-grey-50 border border-line rounded-lg px-3 py-1.5 self-start sm:self-center">
          <ShieldCheck className="w-4 h-4 text-status-ok" />
          <div className="text-xs font-mono">
            <span className="text-grey font-semibold">Audit ID: </span>
            <span className="font-bold text-ink">{confirmResult.audit_id}</span>
          </div>
          <button
            onClick={handleCopyAudit}
            className="p-1 rounded text-grey hover:text-ink focus:outline-none focus:ring-1 focus:ring-blue transition cursor-pointer"
            title="Copy Audit ID"
            aria-label="Copy Audit ID"
          >
            {copiedAudit ? (
              <Check className="w-3.5 h-3.5 text-status-ok" />
            ) : (
              <Copy className="w-3.5 h-3.5" />
            )}
          </button>
        </div>
      </div>

      {/* 2. Records Created Breakdown Cards */}
      <div>
        <h3 className="font-heading text-xs tracking-wider uppercase text-grey mb-3">
          Committed Database Records (Atomic Transaction)
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="p-4 bg-emerald-50/60 rounded-xl border border-emerald-200/80 flex items-center space-x-3">
            <div className="w-9 h-9 rounded-lg bg-emerald-100 text-status-ok flex items-center justify-center">
              <CalendarCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xl font-heading font-black text-ink">
                {confirmResult.records.attendance || 0}
              </div>
              <div className="text-xs font-semibold text-status-ok">
                Attendance Records
              </div>
            </div>
          </div>

          <div className="p-4 bg-blue-50/60 rounded-xl border border-blue-200/80 flex items-center space-x-3">
            <div className="w-9 h-9 rounded-lg bg-blue-100 text-blue flex items-center justify-center">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xl font-heading font-black text-ink">
                {confirmResult.records.diary || 0}
              </div>
              <div className="text-xs font-semibold text-blue">
                Class Diary Entry
              </div>
            </div>
          </div>

          <div className="p-4 bg-amber-50/60 rounded-xl border border-amber-200/80 flex items-center space-x-3">
            <div className="w-9 h-9 rounded-lg bg-amber-100 text-amber-dark flex items-center justify-center">
              <FileCheck2 className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xl font-heading font-black text-ink">
                {confirmResult.records.homework || 0}
              </div>
              <div className="text-xs font-semibold text-amber-dark">
                Homework Task
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Notification Drafts with English/Hindi Toggle & Copy Buttons */}
      <div className="space-y-3 pt-2 border-t border-line">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <Languages className="w-4 h-4 text-blue" />
            <h3 className="font-heading text-xs tracking-wider uppercase text-grey">
              Parent &amp; Student Notification Drafts
            </h3>
          </div>

          {/* Language Toggle: English & Hindi */}
          <div className="inline-flex rounded-lg border border-line bg-grey-50 p-0.5 text-xs">
            {['English', 'Hindi'].map((lang) => (
              <button
                key={lang}
                type="button"
                onClick={() => setDraftLanguage(lang)}
                className={`px-3 py-1 rounded-md font-semibold transition cursor-pointer ${
                  draftLanguage.toLowerCase() === lang.toLowerCase()
                    ? 'bg-white text-blue shadow-xs font-bold'
                    : 'text-grey-600 hover:text-ink'
                }`}
              >
                {lang === 'Hindi' ? 'हिन्दी (Hindi)' : 'English'}
              </button>
            ))}
          </div>
        </div>

        {/* Draft Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
          {filteredDrafts.map((draft) => {
            const isCopied = copiedId === draft.id;
            return (
              <div
                key={draft.id}
                className="p-4 bg-[#F9FAFB] rounded-xl border border-line flex flex-col justify-between space-y-3 hover:border-grey transition"
              >
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-blue bg-tint px-2 py-0.5 rounded border border-blue/20">
                      {draft.audience}
                    </span>
                    <span className="text-[10px] font-mono text-grey">
                      {draft.language}
                    </span>
                  </div>
                  <p className="text-xs text-ink leading-relaxed font-body select-text">
                    {draft.text}
                  </p>
                </div>

                <div className="pt-2 border-t border-line/60 flex items-center justify-end">
                  <button
                    type="button"
                    onClick={() => handleCopy(draft.text, draft.id)}
                    className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold border transition cursor-pointer ${
                      isCopied
                        ? 'bg-emerald-50 text-status-ok border-status-ok/30'
                        : 'bg-white text-grey-700 border-line hover:border-grey hover:bg-grey-50'
                    }`}
                  >
                    {isCopied ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-status-ok" />
                        <span className="text-status-ok">Copied!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5" />
                        <span>Copy Draft</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 4. Action Button: New Message */}
      <div className="pt-4 border-t border-line flex justify-end">
        <button
          type="button"
          onClick={onNewMessage}
          className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-lg bg-blue text-white font-semibold text-sm hover:bg-blue-700 transition shadow-xs cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue focus:ring-offset-2"
        >
          <RotateCcw className="w-4 h-4" />
          <span>Compose Another Message</span>
        </button>
      </div>
    </div>
  );
}
