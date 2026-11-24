import React, { useState, useMemo } from 'react';
import {
  ArrowLeft,
  FileCheck2,
  Lock,
  AlertTriangle,
  RotateCcw,
  CheckCircle2,
  Info,
} from 'lucide-react';
import ReviewBanner from './ReviewBanner';
import MessageHighlighter from './MessageHighlighter';
import FieldsTable from './FieldsTable';
import SuccessPanel from './SuccessPanel';
import { apiClient } from '../api/client';
import { setMockLlmMode } from '../api/mock';
import { getTranslation } from '../i18n';

export default function ReviewScreen({
  review: initialReview,
  onEditMessage,
  onReviewUpdated,
  uiLang = 'en',
}) {
  const [review, setReview] = useState(initialReview);
  const [resolutions, setResolutions] = useState({});
  const [hoveredFieldId, setHoveredFieldId] = useState(null);
  const [recheckingFieldId, setRecheckingFieldId] = useState(null);
  const [confirming, setConfirming] = useState(false);
  const [confirmResult, setConfirmResult] = useState(null);
  const [confirmError, setConfirmError] = useState(null);
  const [showConfirmTooltip, setShowConfirmTooltip] = useState(false);

  const t = (key) => getTranslation(uiLang, key);

  // Compute unresolved candidate fields
  const unresolvedCandidates = useMemo(() => {
    return review.fields.filter(
      (f) =>
        f.type === 'absent_student' &&
        f.candidates &&
        f.candidates.length > 1 &&
        !resolutions[f.id] &&
        !f.resolved_student_id
    );
  }, [review.fields, resolutions]);

  // Compute block-level rule fields (both field-level and message/rule-level)
  const blockedFields = useMemo(() => {
    const fromFields = review.fields.filter((f) => f.status === 'Block');
    const fromRules = (review.rule_results || []).filter((r) => r.status === 'Block');
    return [...fromFields, ...fromRules];
  }, [review.fields, review.rule_results]);

  // Number of items left to resolve
  const itemsLeft = unresolvedCandidates.length + blockedFields.length;

  // Dynamic status based on resolutions and edits
  const dynamicStatus = useMemo(() => {
    if (blockedFields.length > 0) return 'blocked';
    if (unresolvedCandidates.length > 0) return 'needs_review';
    return 'ready';
  }, [blockedFields.length, unresolvedCandidates.length]);

  // List of reasons for disabled confirm tooltip
  const unresolvedReasons = useMemo(() => {
    const list = [];
    if (blockedFields.length > 0) {
      blockedFields.forEach((bf) => {
        const identifier = bf.label || bf.type || bf.rule_id || 'Rule';
        const valStr = bf.value ? ` (${bf.value})` : '';
        list.push(`Block Violation: ${identifier}${valStr} — ${bf.reason || 'Blocked by rule'}`);
      });
    }
    if (unresolvedCandidates.length > 0) {
      unresolvedCandidates.forEach((uc) => {
        list.push(`Ambiguity: Select one candidate for "${uc.value}" (${uc.candidates.length} options)`);
      });
    }
    return list;
  }, [blockedFields, unresolvedCandidates]);

  const isConfirmDisabled = itemsLeft > 0 || confirming;

  // Handle selecting a candidate for a name field
  const handleSelectCandidate = (fieldId, studentId) => {
    setResolutions((prev) => ({
      ...prev,
      [fieldId]: studentId,
    }));
    setConfirmError(null);
  };

  // Handle editing a value and rechecking through API
  const handleEditValue = async (fieldId, newValue) => {
    setRecheckingFieldId(fieldId);
    setConfirmError(null);
    try {
      const updatedReview = await apiClient.recheckField(
        review.message_id,
        fieldId,
        newValue
      );
      setReview(updatedReview);
      if (onReviewUpdated) {
        onReviewUpdated(updatedReview);
      }
    } catch (err) {
      console.error('Re-check failed:', err);
      alert('Re-check failed: ' + err.message);
    } finally {
      setRecheckingFieldId(null);
    }
  };

  // Handle LLM mode change in mock mode
  const handleLlmModeChange = (newMode) => {
    setMockLlmMode(newMode);
    const updated = {
      ...review,
      llm_mode: newMode,
    };
    setReview(updated);
    if (onReviewUpdated) {
      onReviewUpdated(updated);
    }
  };

  // Handle confirm and commit
  const handleConfirm = async () => {
    if (isConfirmDisabled) return;
    setConfirming(true);
    setConfirmError(null);
    try {
      const response = await apiClient.confirmMessage(review.message_id, {
        resolutions,
        edits: {},
      });
      setConfirmResult(response);
    } catch (err) {
      console.error('Confirm error:', err);
      setConfirmError(
        err.message || 'Confirmation failed. Please ensure all rules are satisfied.'
      );
    } finally {
      setConfirming(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. If Confirm Succeeded, show the Post-Confirm Success Panel */}
      {confirmResult ? (
        <SuccessPanel
          confirmResult={confirmResult}
          onNewMessage={() => onEditMessage('')}
        />
      ) : (
        <>
          {/* Top Banner: Status, Items Left, and LLM Mode Badge */}
          <ReviewBanner
            status={dynamicStatus}
            itemsLeft={itemsLeft}
            unresolvedReasons={unresolvedReasons}
            llmMode={review.llm_mode || 'gemini'}
            onLlmModeChange={handleLlmModeChange}
            uiLang={uiLang}
          />

          {/* Confirm Error Alert */}
          {confirmError && (
            <div className="p-3.5 bg-red-50 border border-status-block/30 rounded-xl text-xs text-status-block flex items-start space-x-2.5">
              <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <div className="flex-1 font-medium">{confirmError}</div>
              <button
                onClick={() => setConfirmError(null)}
                className="underline font-semibold ml-2 hover:opacity-80"
              >
                Dismiss
              </button>
            </div>
          )}

          {/* Main 2-Column Responsive Workspace:
              At 390px (mobile): stacks message above the table (flex-col).
              At >=1024px: side-by-side (flex-row).
          */}
          <div className="flex flex-col lg:flex-row items-stretch gap-6">
            {/* Left Column: Teacher Message with Offset Highlights */}
            <div className="w-full lg:w-5/12 flex-shrink-0">
              <MessageHighlighter
                text={review.text}
                fields={review.fields}
                hoveredFieldId={hoveredFieldId}
                onHoverField={setHoveredFieldId}
              />
            </div>

            {/* Right Column: Entity Table with Editable Values, Radios & Reason */}
            <div className="w-full lg:w-7/12 flex-1">
              <FieldsTable
                fields={review.fields}
                resolutions={resolutions}
                onSelectCandidate={handleSelectCandidate}
                onEditValue={handleEditValue}
                hoveredFieldId={hoveredFieldId}
                onHoverField={setHoveredFieldId}
                recheckingFieldId={recheckingFieldId}
              />
            </div>
          </div>

          {/* Action Buttons Bar */}
          <div className="bg-white rounded-xl border border-line p-4 sm:p-5 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            {/* Edit Message Button: returns to composer with text kept */}
            <button
              type="button"
              onClick={() => onEditMessage(review.text)}
              className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-lg border border-line bg-white hover:bg-grey-50 text-grey-700 text-xs font-semibold transition cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue focus:ring-offset-2 self-start sm:self-center"
            >
              <ArrowLeft className="w-4 h-4 text-grey-600" />
              <span>{t('editMessage')}</span>
            </button>

            {/* Confirm and Create Records Button (with tooltip when disabled) */}
            <div className="relative self-stretch sm:self-center">
              <div
                onMouseEnter={() => {
                  if (isConfirmDisabled) setShowConfirmTooltip(true);
                }}
                onMouseLeave={() => setShowConfirmTooltip(false)}
                onFocus={() => {
                  if (isConfirmDisabled) setShowConfirmTooltip(true);
                }}
                onBlur={() => setShowConfirmTooltip(false)}
                className="inline-block w-full sm:w-auto"
              >
                <button
                  type="button"
                  onClick={handleConfirm}
                  disabled={isConfirmDisabled}
                  className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-6 py-2.5 rounded-lg font-semibold text-sm transition shadow-xs cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed bg-blue text-white hover:bg-blue-700 active:bg-blue-800"
                >
                  {isConfirmDisabled ? (
                    blockedFields.length > 0 ? (
                      <>
                        <Lock className="w-4 h-4 text-white/80" />
                        <span>{t('submissionBlocked')}</span>
                      </>
                    ) : (
                      <>
                        <AlertTriangle className="w-4 h-4 text-white/80" />
                        <span>
                          {t('confirm')} ({itemsLeft} {t('itemsLeft')})
                        </span>
                      </>
                    )
                  ) : confirming ? (
                    <>
                      <RotateCcw className="w-4 h-4 animate-spin" />
                      <span>Committing Transaction...</span>
                    </>
                  ) : (
                    <>
                      <FileCheck2 className="w-4 h-4 text-white" />
                      <span>{t('confirm')}</span>
                    </>
                  )}
                </button>
              </div>

              {/* Tooltip listing what is unresolved when disabled */}
              {showConfirmTooltip && isConfirmDisabled && (
                <div
                  role="tooltip"
                  className="absolute right-0 bottom-full mb-2 w-72 p-3 bg-ink text-white text-xs rounded-xl shadow-2xl z-50 animate-fadeIn border border-grey-700 pointer-events-none"
                >
                  <div className="font-bold text-amber mb-1.5 flex items-center space-x-1.5">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber" />
                    <span>Cannot Confirm Yet ({itemsLeft} unresolved):</span>
                  </div>
                  <ul className="space-y-1 text-grey-200 text-[11px] list-disc list-inside">
                    {unresolvedReasons.map((reason, idx) => (
                      <li key={idx} className="leading-tight">
                        {reason}
                      </li>
                    ))}
                  </ul>
                  <div className="mt-2 pt-1.5 border-t border-grey-700 text-[10px] text-grey-400">
                    Rule R1-R9: The teacher must resolve ambiguities and blocks before records are written.
                  </div>
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
