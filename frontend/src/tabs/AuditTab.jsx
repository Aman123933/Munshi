import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  Clock,
  User,
  MessageSquare,
  FileText,
  X,
  CheckCircle2,
  AlertTriangle,
  Lock,
  ChevronRight,
  RefreshCw,
  AlertCircle,
  Eye,
  Check,
} from 'lucide-react';
import { apiClient } from '../api/client';

export default function AuditTab() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedLog, setSelectedLog] = useState(null);

  const fetchAuditLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.getAuditLogs();
      setLogs(data || []);
    } catch (err) {
      console.error('Failed to load audit logs:', err);
      setError(err.message || 'Failed to load audit logs. Principal access required.');
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAuditLogs();
  }, []);

  // Close modal on Escape key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && selectedLog) {
        setSelectedLog(null);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedLog]);

  return (
    <div className="space-y-6">
      {/* 1. Header Banner */}
      <section className="bg-white rounded-xl border border-line p-5 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-xl bg-amber-100 text-amber-dark flex items-center justify-center flex-shrink-0">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h2 className="font-heading text-base tracking-wide uppercase text-ink">
              Principal Audit Trail &amp; Confirmation Ledger
            </h2>
            <p className="text-xs text-grey font-medium">
              Permanent immutable transaction ledger. Click any confirmation row to inspect the original message and extracted fields.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 self-start sm:self-center">
          <span className="px-2.5 py-1 rounded-md text-xs font-mono font-bold bg-amber-50 text-amber-dark border border-amber/30">
            Role: Principal Only
          </span>
          <button
            onClick={fetchAuditLogs}
            disabled={loading}
            className="p-1.5 rounded-lg border border-line hover:bg-grey-50 text-grey transition"
            title="Refresh logs"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue' : ''}`} />
          </button>
        </div>
      </section>

      {/* 2. Main Audit Confirmations Table */}
      <section className="bg-white rounded-xl border border-line shadow-sm overflow-hidden">
        {/* Error State */}
        {error && (
          <div className="p-8 text-center space-y-3">
            <AlertCircle className="w-8 h-8 text-status-block mx-auto" />
            <div className="text-sm font-bold text-status-block">{error}</div>
            <button
              onClick={fetchAuditLogs}
              className="px-4 py-1.5 rounded-lg bg-blue text-white text-xs font-semibold hover:bg-blue-700 transition"
            >
              Retry
            </button>
          </div>
        )}

        {/* Loading State */}
        {loading && !error && (
          <div className="p-8 space-y-3 animate-pulse">
            <div className="h-4 bg-grey-200 rounded w-1/4 mb-4" />
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-16 bg-grey-100 rounded-lg" />
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && logs.length === 0 && (
          <div className="p-12 text-center space-y-2">
            <ShieldAlert className="w-10 h-10 text-grey-300 mx-auto" />
            <h3 className="font-heading text-sm text-ink uppercase">No Audit Confirmations Yet</h3>
            <p className="text-xs text-grey">
              Confirmed attendance, diary, and homework transactions will appear in this ledger.
            </p>
          </div>
        )}

        {/* Populated Table */}
        {!loading && !error && logs.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse min-w-[650px]">
              <thead className="bg-[#F9FAFB] text-grey uppercase tracking-wider font-semibold border-b border-line text-[11px]">
                <tr>
                  <th className="py-3 px-4">Time</th>
                  <th className="py-3 px-4">Teacher</th>
                  <th className="py-3 px-4">Action</th>
                  <th className="py-3 px-4">Message Excerpt</th>
                  <th className="py-3 px-4">Confirmation Summary</th>
                  <th className="py-3 px-3 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {logs.map((log) => (
                  <tr
                    key={log.id}
                    onClick={() => setSelectedLog(log)}
                    tabIndex={0}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        setSelectedLog(log);
                      }
                    }}
                    className="hover:bg-blue-50/50 cursor-pointer transition focus:outline-none focus:ring-1 focus:ring-blue group"
                  >
                    {/* Time */}
                    <td className="py-3.5 px-4 font-mono text-grey whitespace-nowrap align-top">
                      <div className="flex items-center space-x-1.5 text-ink font-semibold">
                        <Clock className="w-3.5 h-3.5 text-grey" />
                        <span>
                          {log.time ? new Date(log.time).toLocaleTimeString() : 'N/A'}
                        </span>
                      </div>
                      <div className="text-[10px] text-grey-400">
                        {log.time ? new Date(log.time).toLocaleDateString() : ''}
                      </div>
                    </td>

                    {/* Teacher */}
                    <td className="py-3.5 px-4 font-semibold text-ink whitespace-nowrap align-top">
                      <div className="flex items-center space-x-1.5">
                        <User className="w-3.5 h-3.5 text-blue" />
                        <span>{log.teacher}</span>
                      </div>
                    </td>

                    {/* Action */}
                    <td className="py-3.5 px-4 whitespace-nowrap align-top">
                      <span className="inline-block px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase bg-tint text-blue border border-blue/20">
                        {log.action}
                      </span>
                    </td>

                    {/* Message Excerpt */}
                    <td className="py-3.5 px-4 max-w-xs align-top">
                      <div className="font-mono text-grey-700 truncate text-[11px] bg-grey-50 px-2 py-1 rounded border border-line/60">
                        &quot;{log.text || log.message_id}&quot;
                      </div>
                    </td>

                    {/* Summary */}
                    <td className="py-3.5 px-4 text-grey-800 font-medium leading-relaxed align-top">
                      {log.summary}
                    </td>

                    {/* Action Icon */}
                    <td className="py-3.5 px-3 text-right whitespace-nowrap align-top">
                      <span className="inline-flex items-center space-x-1 text-xs text-blue group-hover:translate-x-0.5 transition font-semibold">
                        <span>Inspect</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* 3. Detailed Audit Inspection Modal (Opens on row click) */}
      {selectedLog && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="audit-modal-title"
          className="fixed inset-0 z-50 bg-ink/50 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto animate-fadeIn"
          onClick={() => setSelectedLog(null)}
        >
          <div
            className="bg-white rounded-2xl border border-line shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 space-y-5"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-start justify-between pb-3 border-b border-line">
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono uppercase bg-tint text-blue border border-blue/20">
                    {selectedLog.action}
                  </span>
                  <span className="text-xs font-mono text-grey">
                    Audit ID: {selectedLog.id}
                  </span>
                </div>
                <h3 id="audit-modal-title" className="font-heading text-lg text-ink uppercase tracking-wide">
                  Confirmed Transaction Inspection
                </h3>
              </div>

              <button
                type="button"
                onClick={() => setSelectedLog(null)}
                className="p-1 rounded-lg text-grey hover:text-ink hover:bg-grey-100 transition focus:outline-none focus:ring-2 focus:ring-blue"
                title="Close dialog (Escape)"
                aria-label="Close dialog"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Metadata Strip */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 p-3 bg-[#F9FAFB] rounded-xl border border-line text-xs font-mono">
              <div>
                <span className="text-grey block text-[10px] uppercase font-bold">Confirmed By</span>
                <span className="text-ink font-bold">{selectedLog.teacher}</span>
              </div>
              <div>
                <span className="text-grey block text-[10px] uppercase font-bold">Timestamp</span>
                <span className="text-ink font-bold">
                  {selectedLog.time ? new Date(selectedLog.time).toLocaleString() : 'N/A'}
                </span>
              </div>
              <div>
                <span className="text-grey block text-[10px] uppercase font-bold">Message Ref</span>
                <span className="text-ink font-bold truncate block">{selectedLog.message_id}</span>
              </div>
            </div>

            {/* Original Teacher Message */}
            <div className="space-y-1.5">
              <div className="flex items-center space-x-2 text-ink">
                <MessageSquare className="w-4 h-4 text-blue" />
                <h4 className="font-heading text-xs uppercase tracking-wider text-grey">
                  Original Teacher Message
                </h4>
              </div>
              <div className="p-3.5 bg-grey-50 rounded-xl border border-line font-body text-ink text-sm leading-relaxed">
                &quot;{selectedLog.text || selectedLog.summary}&quot;
              </div>
            </div>

            {/* Extracted Fields Table */}
            <div className="space-y-2">
              <div className="flex items-center space-x-2 text-ink">
                <FileText className="w-4 h-4 text-status-ok" />
                <h4 className="font-heading text-xs uppercase tracking-wider text-grey">
                  Verified Extraction Fields ({selectedLog.fields?.length || 0})
                </h4>
              </div>

              {selectedLog.fields && selectedLog.fields.length > 0 ? (
                <div className="border border-line rounded-xl overflow-hidden">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-[#F9FAFB] text-grey uppercase font-semibold border-b border-line text-[10px]">
                      <tr>
                        <th className="py-2.5 px-3">Field</th>
                        <th className="py-2.5 px-3">Verified Value</th>
                        <th className="py-2.5 px-3">Quote</th>
                        <th className="py-2.5 px-3">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-line">
                      {selectedLog.fields.map((f, idx) => (
                        <tr key={f.id || idx} className="hover:bg-grey-50">
                          <td className="py-2.5 px-3 font-bold text-ink">
                            {f.label || f.type}
                          </td>
                          <td className="py-2.5 px-3 font-semibold text-ink">
                            {f.value}
                          </td>
                          <td className="py-2.5 px-3 font-mono text-grey text-[11px]">
                            &quot;{f.quote}&quot;
                          </td>
                          <td className="py-2.5 px-3">
                            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-status-ok">
                              <CheckCircle2 className="w-3 h-3" />
                              <span>OK</span>
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="p-3 bg-grey-50 rounded-lg text-xs text-grey">
                  No individual field breakdown recorded for this legacy transaction.
                </div>
              )}
            </div>

            {/* Transaction Summary */}
            <div className="p-3 bg-tint/60 border border-blue/20 rounded-xl space-y-1">
              <div className="text-[10px] font-bold uppercase tracking-wider text-blue">
                Transaction Commit Summary
              </div>
              <p className="text-xs text-ink leading-relaxed">
                {selectedLog.summary}
              </p>
            </div>

            {/* Modal Actions */}
            <div className="pt-2 border-t border-line flex justify-end">
              <button
                type="button"
                onClick={() => setSelectedLog(null)}
                className="px-4 py-2 rounded-lg bg-blue text-white text-xs font-semibold hover:bg-blue-700 transition"
              >
                Close Inspection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
