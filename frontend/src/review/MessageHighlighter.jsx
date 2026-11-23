import React, { useMemo } from 'react';
import { MessageSquare, CheckCircle2, AlertTriangle, Lock } from 'lucide-react';

export default function MessageHighlighter({
  text,
  fields = [],
  hoveredFieldId,
  onHoverField,
}) {
  // Build non-overlapping text and highlight segments from start/end offsets
  const segments = useMemo(() => {
    if (!text) return [];

    // Filter fields with valid numeric offsets
    const validFields = fields
      .filter(
        (f) =>
          typeof f.start === 'number' &&
          typeof f.end === 'number' &&
          f.start >= 0 &&
          f.end <= text.length &&
          f.start < f.end
      )
      .sort((a, b) => a.start - b.start);

    if (validFields.length === 0) {
      return [{ type: 'text', content: text }];
    }

    const result = [];
    let cursor = 0;

    validFields.forEach((field) => {
      // If gap before field
      if (field.start > cursor) {
        result.push({
          type: 'text',
          content: text.slice(cursor, field.start),
        });
      }

      // Add highlighted field
      if (field.start >= cursor) {
        result.push({
          type: 'highlight',
          field,
          content: text.slice(field.start, field.end),
        });
        cursor = field.end;
      }
    });

    // Remainder text after last field
    if (cursor < text.length) {
      result.push({
        type: 'text',
        content: text.slice(cursor),
      });
    }

    return result;
  }, [text, fields]);

  const handleSpanHover = (fieldId) => {
    onHoverField(fieldId);
    if (fieldId) {
      const targetRow = document.getElementById(`row-${fieldId}`);
      if (targetRow) {
        targetRow.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }
  };

  return (
    <div className="bg-white rounded-xl border border-line p-5 shadow-sm space-y-4 flex flex-col h-full">
      {/* Header and Legend */}
      <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-line">
        <div className="flex items-center space-x-2 text-ink">
          <MessageSquare className="w-4 h-4 text-blue" />
          <h3 className="font-heading text-xs tracking-wider uppercase text-grey">
            Original Teacher Message
          </h3>
        </div>

        {/* Status Colour Legend */}
        <div className="flex items-center space-x-2.5 text-[11px] font-semibold">
          <span className="inline-flex items-center space-x-1 text-status-ok">
            <span className="w-2 h-2 rounded-full bg-status-ok" />
            <span>OK</span>
          </span>
          <span className="inline-flex items-center space-x-1 text-status-review">
            <span className="w-2 h-2 rounded-full bg-[#FFB020]" />
            <span>Review</span>
          </span>
          <span className="inline-flex items-center space-x-1 text-status-block">
            <span className="w-2 h-2 rounded-full bg-status-block" />
            <span>Block</span>
          </span>
        </div>
      </div>

      <div className="text-[11px] text-grey-500 font-medium">
        Hover a highlighted span to scroll to and pulse its corresponding table row on the right.
      </div>

      {/* Message Box with Offset Highlights */}
      <div className="flex-1 p-4 bg-[#F9FAFB] rounded-xl border border-line text-sm sm:text-base leading-relaxed font-body text-ink select-text">
        <span className="text-grey-400 font-serif mr-1 text-lg">&ldquo;</span>
        {segments.map((seg, idx) => {
          if (seg.type === 'text') {
            return <span key={idx}>{seg.content}</span>;
          }

          const field = seg.field;
          const isHovered = hoveredFieldId === field.id;

          // Status colour tokens
          let statusStyle = 'bg-emerald-100 text-status-ok border-b-2 border-status-ok';
          if (field.status === 'Review') {
            statusStyle = 'bg-amber-100 text-status-review border-b-2 border-status-review';
          } else if (field.status === 'Block') {
            statusStyle = 'bg-red-100 text-status-block border-b-2 border-status-block';
          }

          return (
            <mark
              key={field.id}
              id={`highlight-${field.id}`}
              onMouseEnter={() => handleSpanHover(field.id)}
              onMouseLeave={() => handleSpanHover(null)}
              onFocus={() => handleSpanHover(field.id)}
              onBlur={() => handleSpanHover(null)}
              tabIndex={0}
              className={`rounded px-1.5 py-0.5 mx-0.5 cursor-pointer font-medium transition-all duration-150 inline-block focus:outline-none focus:ring-2 focus:ring-blue ${statusStyle} ${
                isHovered
                  ? 'ring-2 ring-blue scale-105 shadow-md font-bold animate-pulse'
                  : 'hover:brightness-95'
              }`}
              title={`${field.label || field.type}: ${field.value} (${field.status})`}
            >
              {seg.content}
            </mark>
          );
        })}
        <span className="text-grey-400 font-serif ml-1 text-lg">&rdquo;</span>
      </div>

      {/* Footer Metadata */}
      <div className="pt-2 text-[11px] text-grey-500 flex items-center justify-between font-mono">
        <span>Verified Quotes: {fields.length}</span>
        <span>Offsets: [start, end)</span>
      </div>
    </div>
  );
}
