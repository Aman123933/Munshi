import React, { useState } from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  Lock,
  Edit2,
  Check,
  X,
  UserCheck,
  RefreshCw,
} from 'lucide-react';

export default function FieldsTable({
  fields = [],
  resolutions = {},
  onSelectCandidate,
  onEditValue,
  hoveredFieldId,
  onHoverField,
  recheckingFieldId,
}) {
  const [editingFieldId, setEditingFieldId] = useState(null);
  const [editValue, setEditValue] = useState('');

  const handleStartEdit = (field) => {
    setEditingFieldId(field.id);
    setEditValue(field.value);
  };

  const handleCancelEdit = () => {
    setEditingFieldId(null);
    setEditValue('');
  };

  const handleSaveEdit = async (fieldId) => {
    if (!editValue.trim()) return;
    const val = editValue.trim();
    setEditingFieldId(null);
    if (onEditValue) {
      await onEditValue(fieldId, val);
    }
  };

  const handleRowHover = (fieldId) => {
    onHoverField(fieldId);
    if (fieldId) {
      const targetSpan = document.getElementById(`highlight-${fieldId}`);
      if (targetSpan) {
        targetSpan.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }
  };

  return (
    <div className="bg-white rounded-xl border border-line shadow-sm overflow-hidden flex flex-col h-full">
      <div className="p-4 border-b border-line flex flex-wrap items-center justify-between gap-2 bg-white">
        <div>
          <h3 className="font-heading text-xs tracking-wider uppercase text-grey">
            Extracted Entities &amp; Rule Verifications
          </h3>
          <p className="text-xs text-grey-500 font-medium mt-0.5">
            Hover any row to pulse its source span in the message. Edit values to re-check API rules.
          </p>
        </div>
        <span className="text-xs font-mono text-grey-500">
          Total Fields: {fields.length}
        </span>
      </div>

      <div className="overflow-x-auto flex-1">
        <table className="w-full text-left text-xs border-collapse min-w-[620px]">
          <thead className="bg-[#F9FAFB] text-grey uppercase tracking-wider font-semibold border-b border-line text-[11px]">
            <tr>
              <th className="py-3 px-3.5">Field</th>
              <th className="py-3 px-3.5">Value (Editable)</th>
              <th className="py-3 px-3.5">Source Words</th>
              <th className="py-3 px-3.5">Status</th>
              <th className="py-3 px-3.5">Reason &amp; Resolution</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {fields.map((field) => {
              const isHovered = hoveredFieldId === field.id;
              const isEditing = editingFieldId === field.id;
              const isRechecking = recheckingFieldId === field.id;
              const hasCandidates = field.candidates && field.candidates.length > 1;
              const selectedCandidateId =
                resolutions[field.id] || field.resolved_student_id;
              const isResolved = Boolean(selectedCandidateId);

              // Row status determination
              const currentStatus =
                hasCandidates && isResolved ? 'OK' : field.status;

              return (
                <tr
                  key={field.id}
                  id={`row-${field.id}`}
                  onMouseEnter={() => handleRowHover(field.id)}
                  onMouseLeave={() => handleRowHover(null)}
                  className={`transition-all duration-200 ${
                    isHovered
                      ? 'bg-blue-50/70 ring-2 ring-blue/70 shadow-xs'
                      : currentStatus === 'Block'
                      ? 'bg-red-50/30 hover:bg-red-50/60'
                      : currentStatus === 'Review'
                      ? 'bg-amber-50/25 hover:bg-amber-50/50'
                      : 'hover:bg-grey-50/80'
                  }`}
                >
                  {/* 1. Field Label & Type */}
                  <td className="py-3.5 px-3.5 align-top">
                    <div className="font-bold text-ink text-xs">
                      {field.label || field.type}
                    </div>
                    <div className="text-[10px] font-mono text-grey uppercase tracking-wider">
                      {field.type}
                    </div>
                  </td>

                  {/* 2. Value (Editable) */}
                  <td className="py-3.5 px-3.5 align-top">
                    {isEditing ? (
                      <div className="flex items-center space-x-1.5">
                        <input
                          type="text"
                          aria-label={`Edit ${field.label || field.type}`}
                          value={editValue}
                          onChange={(e) => setEditValue(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleSaveEdit(field.id);
                            if (e.key === 'Escape') handleCancelEdit();
                          }}
                          className="px-2 py-1 border border-blue rounded text-xs font-semibold focus:outline-none focus:ring-1 focus:ring-blue w-36 bg-white text-ink"
                          autoFocus
                        />
                        <button
                          type="button"
                          onClick={() => handleSaveEdit(field.id)}
                          className="p-1 rounded bg-blue text-white hover:bg-blue-700 focus:outline-none focus:ring-1 focus:ring-blue"
                          title="Save and re-check"
                        >
                          <Check className="w-3 h-3" />
                        </button>
                        <button
                          type="button"
                          onClick={handleCancelEdit}
                          className="p-1 rounded bg-grey-200 text-grey hover:bg-grey-300 focus:outline-none"
                          title="Cancel"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2 group">
                        <span className="font-semibold text-ink text-xs">
                          {field.value}
                        </span>
                        {isRechecking ? (
                          <RefreshCw className="w-3 h-3 text-blue animate-spin" />
                        ) : (
                          <button
                            type="button"
                            onClick={() => handleStartEdit(field)}
                            className="opacity-0 group-hover:opacity-100 focus:opacity-100 p-1 text-grey hover:text-blue rounded focus:outline-none focus:ring-1 focus:ring-blue transition"
                            title="Edit value to re-check"
                            aria-label={`Edit value for ${field.label || field.type}`}
                          >
                            <Edit2 className="w-3 h-3" />
                          </button>
                        )}
                      </div>
                    )}
                  </td>

                  {/* 3. Source Words (Verbatim Quote) */}
                  <td className="py-3.5 px-3.5 align-top">
                    <div className="font-mono text-grey-700 bg-white border border-line/70 px-2 py-0.5 rounded text-[11px] inline-block shadow-2xs">
                      &quot;{field.quote}&quot;
                    </div>
                    {field.start !== undefined && field.end !== undefined && (
                      <div className="text-[10px] text-grey-400 font-mono mt-0.5">
                        [{field.start}, {field.end})
                      </div>
                    )}
                  </td>

                  {/* 4. Status Chip (Icon + Word, never color alone) */}
                  <td className="py-3.5 px-3.5 align-top whitespace-nowrap">
                    {currentStatus === 'OK' && (
                      <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-100 text-status-ok border border-status-ok/30">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>{isResolved && hasCandidates ? 'OK (Resolved)' : 'OK'}</span>
                      </span>
                    )}
                    {currentStatus === 'Review' && (
                      <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold bg-amber-100 text-status-review border border-status-review/30">
                        <AlertTriangle className="w-3.5 h-3.5" />
                        <span>Review</span>
                      </span>
                    )}
                    {currentStatus === 'Block' && (
                      <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold bg-red-100 text-status-block border border-status-block/30">
                        <Lock className="w-3.5 h-3.5" />
                        <span>Block</span>
                      </span>
                    )}
                  </td>

                  {/* 5. Plain-English Reason & Candidate Radio List */}
                  <td className="py-3.5 px-3.5 align-top space-y-2">
                    <div className="flex items-start space-x-1.5">
                      {field.status === 'Block' && (
                        <Lock className="w-3.5 h-3.5 text-status-block flex-shrink-0 mt-0.5" />
                      )}
                      <span
                        className={`text-xs font-medium leading-relaxed ${
                          field.status === 'Block'
                            ? 'text-status-block font-semibold'
                            : field.status === 'Review'
                            ? 'text-status-review'
                            : 'text-grey-700'
                        }`}
                      >
                        {field.reason || 'Verified successfully against pipeline rules.'}
                      </span>
                    </div>

                    {/* Radio List for Name Fields with Multiple Candidates */}
                    {hasCandidates && (
                      <div className="mt-2 p-2.5 bg-white rounded-lg border border-line shadow-2xs space-y-2">
                        <div className="flex items-center space-x-1.5 text-[11px] font-bold text-ink">
                          <UserCheck className="w-3.5 h-3.5 text-blue" />
                          <span>
                            Select correct student for &quot;{field.value}&quot;:
                          </span>
                        </div>

                        <div className="space-y-1.5">
                          {field.candidates.map((cand) => {
                            const isChecked = selectedCandidateId === cand.student_id;
                            const radioId = `candidate-${field.id}-${cand.student_id}`;

                            return (
                              <label
                                key={cand.student_id}
                                htmlFor={radioId}
                                className={`flex items-center justify-between p-2 rounded-md border text-xs cursor-pointer transition ${
                                  isChecked
                                    ? 'bg-blue/5 border-blue text-ink font-semibold ring-1 ring-blue'
                                    : 'border-line/70 hover:bg-grey-50 text-grey-700'
                                }`}
                              >
                                <div className="flex items-center space-x-2">
                                  <input
                                    type="radio"
                                    id={radioId}
                                    name={`candidates-${field.id}`}
                                    value={cand.student_id}
                                    checked={isChecked}
                                    onChange={() =>
                                      onSelectCandidate(field.id, cand.student_id)
                                    }
                                    className="text-blue focus:ring-blue h-3.5 w-3.5 cursor-pointer"
                                  />
                                  <span className="font-semibold text-ink">
                                    {cand.name}
                                  </span>
                                </div>

                                <div className="flex items-center space-x-2 font-mono text-[11px] text-grey">
                                  <span>Roll: {cand.roll_no}</span>
                                  <span>&bull;</span>
                                  <span className="font-bold text-ink">
                                    Class: {cand.class_label || '8A'}
                                  </span>
                                </div>
                              </label>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
