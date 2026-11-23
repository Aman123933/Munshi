import React, { useState, useEffect } from 'react';
import {
  Download,
  Calendar,
  Users,
  Check,
  X,
  RefreshCw,
  AlertCircle,
  FileSpreadsheet,
  CheckCircle2,
  XCircle,
} from 'lucide-react';
import { apiClient } from '../api/client';

export default function RecordsTab() {
  const [classLabel, setClassLabel] = useState('8A');
  const [dateVal, setDateVal] = useState('2026-11-23');
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [exportingFormat, setExportingFormat] = useState(null);
  const [exportSuccess, setExportSuccess] = useState(null);

  const availableClasses = ['6A', '7A', '7B', '8A', '8B', '9A', '10A', '11A', '12A'];

  const fetchAttendance = async () => {
    setLoading(true);
    setError(null);
    setExportSuccess(null);
    try {
      const data = await apiClient.getAttendance(classLabel, dateVal);
      setRecords(data || []);
    } catch (err) {
      console.error('Failed to load attendance:', err);
      setError(err.message || 'Failed to load attendance records.');
      setRecords([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAttendance();
  }, [classLabel, dateVal]);

  const handleExport = async (format) => {
    try {
      setExportingFormat(format);
      setExportSuccess(null);
      const blob = await apiClient.exportAttendance(classLabel, dateVal, format);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `attendance_${classLabel}_${dateVal}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      setExportSuccess(`Exported ${format.toUpperCase()} successfully.`);
      setTimeout(() => setExportSuccess(null), 3500);
    } catch (err) {
      console.error('Export failed:', err);
      alert('Export failed: ' + err.message);
    } finally {
      setExportingFormat(null);
    }
  };

  const presentCount = records.filter((r) => r.present).length;
  const absentCount = records.filter((r) => !r.present).length;
  const totalCount = records.length;
  const attendanceRate = totalCount > 0 ? Math.round((presentCount / totalCount) * 100) : 0;

  return (
    <div className="space-y-6">
      {/* 1. Header & Filter Controls Bar */}
      <section className="bg-white rounded-xl border border-line p-4 sm:p-5 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-line gap-3">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-tint text-blue flex items-center justify-center flex-shrink-0">
              <Users className="w-5 h-5" />
            </div>
            <div>
              <h2 className="font-heading text-base tracking-wide uppercase text-ink">
                Class Attendance Records
              </h2>
              <p className="text-xs text-grey font-medium">
                Verified attendance registers with roll numbers and export utilities (GET /api/attendance).
              </p>
            </div>
          </div>

          {/* Export Buttons */}
          <div className="flex items-center space-x-2 self-start sm:self-center">
            <button
              onClick={() => handleExport('csv')}
              disabled={exportingFormat !== null || loading || records.length === 0}
              className="inline-flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs font-semibold border border-line bg-white hover:bg-grey-50 text-grey-700 transition cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue disabled:opacity-50"
              title="Download attendance sheet as CSV"
            >
              {exportingFormat === 'csv' ? (
                <RefreshCw className="w-3.5 h-3.5 animate-spin text-blue" />
              ) : (
                <Download className="w-3.5 h-3.5 text-blue" />
              )}
              <span>Export CSV</span>
            </button>

            <button
              onClick={() => handleExport('xlsx')}
              disabled={exportingFormat !== null || loading || records.length === 0}
              className="inline-flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs font-semibold border border-line bg-white hover:bg-grey-50 text-grey-700 transition cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue disabled:opacity-50"
              title="Download formatted Excel XLSX workbook"
            >
              {exportingFormat === 'xlsx' ? (
                <RefreshCw className="w-3.5 h-3.5 animate-spin text-status-ok" />
              ) : (
                <FileSpreadsheet className="w-3.5 h-3.5 text-status-ok" />
              )}
              <span>Export XLSX</span>
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-3">
            {/* Class-Section Selector */}
            <div className="flex items-center space-x-2">
              <label htmlFor="records-class-select" className="text-xs font-bold text-grey uppercase tracking-wider">
                Class:
              </label>
              <select
                id="records-class-select"
                aria-label="Select Class-Section"
                value={classLabel}
                onChange={(e) => setClassLabel(e.target.value)}
                className="px-3 py-1.5 rounded-lg border border-line text-xs font-bold text-ink bg-grey-50 focus:outline-none focus:ring-2 focus:ring-blue cursor-pointer"
              >
                {availableClasses.map((c) => (
                  <option key={c} value={c}>
                    Class {c}
                  </option>
                ))}
              </select>
            </div>

            {/* Date Selector */}
            <div className="flex items-center space-x-2">
              <Calendar className="w-4 h-4 text-grey" />
              <label htmlFor="records-date-input" className="text-xs font-bold text-grey uppercase tracking-wider">
                Date:
              </label>
              <input
                id="records-date-input"
                aria-label="Select Attendance Date"
                type="date"
                value={dateVal}
                onChange={(e) => setDateVal(e.target.value)}
                className="px-3 py-1.5 rounded-lg border border-line text-xs font-mono font-medium text-ink bg-grey-50 focus:outline-none focus:ring-2 focus:ring-blue"
              />
            </div>
          </div>

          {/* Quick Refresh */}
          <button
            onClick={fetchAttendance}
            disabled={loading}
            className="p-1.5 rounded-lg text-grey hover:text-ink hover:bg-grey-50 border border-line transition cursor-pointer"
            title="Refresh attendance records"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue' : ''}`} />
          </button>
        </div>

        {exportSuccess && (
          <div className="p-2.5 bg-emerald-50 border border-status-ok/30 rounded-lg text-xs text-status-ok flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
            <span>{exportSuccess}</span>
          </div>
        )}
      </section>

      {/* 2. Summary Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-3.5 bg-white rounded-xl border border-line shadow-xs">
          <div className="text-[10px] font-bold uppercase tracking-wider text-grey">Total Roster</div>
          <div className="text-2xl font-heading font-black text-ink mt-0.5">{totalCount}</div>
        </div>

        <div className="p-3.5 bg-emerald-50/60 rounded-xl border border-status-ok/30 shadow-xs">
          <div className="text-[10px] font-bold uppercase tracking-wider text-status-ok">Present</div>
          <div className="text-2xl font-heading font-black text-status-ok mt-0.5">{presentCount}</div>
        </div>

        <div className="p-3.5 bg-red-50/60 rounded-xl border border-status-block/30 shadow-xs">
          <div className="text-[10px] font-bold uppercase tracking-wider text-status-block">Absent</div>
          <div className="text-2xl font-heading font-black text-status-block mt-0.5">{absentCount}</div>
        </div>

        <div className="p-3.5 bg-blue-50/60 rounded-xl border border-blue/30 shadow-xs">
          <div className="text-[10px] font-bold uppercase tracking-wider text-blue">Turnout</div>
          <div className="text-2xl font-heading font-black text-blue mt-0.5">{attendanceRate}%</div>
        </div>
      </div>

      {/* 3. Main Roster Table */}
      <section className="bg-white rounded-xl border border-line shadow-sm overflow-hidden">
        {/* Error State */}
        {error && (
          <div className="p-6 text-center space-y-3">
            <AlertCircle className="w-8 h-8 text-status-block mx-auto" />
            <div className="text-sm font-bold text-status-block">{error}</div>
            <button
              onClick={fetchAttendance}
              className="px-4 py-1.5 rounded-lg bg-blue text-white text-xs font-semibold hover:bg-blue-700 transition"
            >
              Retry
            </button>
          </div>
        )}

        {/* Loading State Skeleton */}
        {loading && !error && (
          <div className="p-6 space-y-3 animate-pulse">
            <div className="h-4 bg-grey-200 rounded w-1/4" />
            <div className="space-y-2">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div key={i} className="h-10 bg-grey-100 rounded-lg" />
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && records.length === 0 && (
          <div className="p-12 text-center space-y-2">
            <Users className="w-10 h-10 text-grey-300 mx-auto" />
            <h3 className="font-heading text-sm text-ink uppercase">No Records Found</h3>
            <p className="text-xs text-grey">
              No attendance data recorded for Class {classLabel} on {dateVal}.
            </p>
          </div>
        )}

        {/* Populated Table */}
        {!loading && !error && records.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-[#F9FAFB] text-grey uppercase tracking-wider font-semibold border-b border-line text-[11px]">
                <tr>
                  <th className="py-3 px-4">Roll No</th>
                  <th className="py-3 px-4">Student Name</th>
                  <th className="py-3 px-4">Student ID</th>
                  <th className="py-3 px-4">Attendance Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {records.map((r) => (
                  <tr key={r.student_id} className="hover:bg-grey-50/80 transition">
                    <td className="py-3.5 px-4 font-mono font-bold text-ink">
                      {r.roll_no}
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-ink">
                      {r.name}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-grey">
                      {r.student_id}
                    </td>
                    <td className="py-3.5 px-4">
                      {r.present ? (
                        <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-100 text-status-ok border border-status-ok/30">
                          <Check className="w-3.5 h-3.5" />
                          <span>Present</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold bg-red-100 text-status-block border border-status-block/30">
                          <X className="w-3.5 h-3.5" />
                          <span>Absent</span>
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
