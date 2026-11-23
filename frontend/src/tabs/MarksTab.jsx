import React, { useState, useEffect, useMemo } from 'react';
import {
  Upload,
  FileSpreadsheet,
  AlertTriangle,
  Lock,
  CheckCircle2,
  Sparkles,
  Filter,
  Check,
  Search,
  RefreshCw,
  Lightbulb,
  FileText,
  AlertCircle,
  ShieldCheck,
} from 'lucide-react';
import { apiClient } from '../api/client';

export default function MarksTab() {
  const [flags, setFlags] = useState([]);
  const [rowsChecked, setRowsChecked] = useState(0);
  const [uploadId, setUploadId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);

  // Local-only "Mark as checked" state
  const [checkedFlagIds, setCheckedFlagIds] = useState(new Set());

  // Filters
  const [severityFilter, setSeverityFilter] = useState('all'); // 'all' | 'block' | 'review' | 'unchecked'
  const [classFilter, setClassFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Load demo marks by default on mount so the screen has realistic data immediately
  useEffect(() => {
    handleUseDemoFile();
  }, []);

  const handleUseDemoFile = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.getMarksDemo();
      setFlags(res.flags || []);
      setRowsChecked(res.rows || 703);
      setUploadId(res.upload_id || 'demo_error_test');
    } catch (err) {
      console.error('Failed to load marks demo:', err);
      setError(err.message || 'Failed to run marks pre-flight check on demo file.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file) => {
    if (!file) return;
    if (!file.name.endsWith('.csv')) {
      alert('Please select a valid CSV file.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await apiClient.uploadMarks(formData);
      setFlags(res.flags || []);
      setRowsChecked(res.rows || 0);
      setUploadId(res.upload_id || `upload-${Date.now()}`);
      setCheckedFlagIds(new Set()); // reset local checked states for new upload
    } catch (err) {
      console.error('Upload failed:', err);
      setError(err.message || 'CSV upload and verification failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleChecked = (flagId) => {
    setCheckedFlagIds((prev) => {
      const next = new Set(prev);
      if (next.has(flagId)) {
        next.delete(flagId);
      } else {
        next.add(flagId);
      }
      return next;
    });
  };

  // Derive class options from loaded flags
  const availableClasses = useMemo(() => {
    const set = new Set();
    flags.forEach((f) => {
      if (f.class) set.add(f.class);
    });
    return Array.from(set).sort();
  }, [flags]);

  // Filtered flags
  const filteredFlags = useMemo(() => {
    return flags.filter((f) => {
      const flagKey = f.id || f.record_id || `${f.student_name}-${f.column}`;
      const isChecked = checkedFlagIds.has(flagKey);

      // Severity filter
      if (severityFilter === 'block' && f.severity !== 'block') return false;
      if (severityFilter === 'review' && f.severity !== 'review') return false;
      if (severityFilter === 'unchecked' && isChecked) return false;

      // Class filter
      if (classFilter !== 'all' && f.class !== classFilter) return false;

      // Text search
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesName = (f.student_name || '').toLowerCase().includes(q);
        const matchesRec = (f.record_id || '').toLowerCase().includes(q);
        const matchesSub = (f.subject || '').toLowerCase().includes(q);
        const matchesCol = (f.column || '').toLowerCase().includes(q);
        if (!matchesName && !matchesRec && !matchesSub && !matchesCol) return false;
      }

      return true;
    });
  }, [flags, severityFilter, classFilter, searchQuery, checkedFlagIds]);

  // Group by severity
  const blockFlags = filteredFlags.filter((f) => f.severity === 'block');
  const reviewFlags = filteredFlags.filter((f) => f.severity === 'review');

  // Summary counts
  const totalFlagsCount = flags.length;
  const totalBlocksCount = flags.filter((f) => f.severity === 'block').length;
  const totalReviewsCount = flags.filter((f) => f.severity === 'review').length;
  const checkedCount = checkedFlagIds.size;

  return (
    <div className="space-y-6">
      {/* 1. Top Section: Dropzone & Demo File Button */}
      <section className="bg-white rounded-xl border border-line p-5 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-line gap-3">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-blue/10 text-blue flex items-center justify-center flex-shrink-0">
              <FileSpreadsheet className="w-5 h-5" />
            </div>
            <div>
              <h2 className="font-heading text-base tracking-wide uppercase text-ink">
                Marks Pre-Flight Checker (Module A)
              </h2>
              <p className="text-xs text-grey font-medium">
                Rule R8 pre-flight verification: bounds checking, negative scores, missing totals, and duplicate records.
              </p>
            </div>
          </div>

          {/* "Use the demo file" button */}
          <button
            type="button"
            onClick={handleUseDemoFile}
            disabled={loading}
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-blue text-white text-xs font-semibold hover:bg-blue-700 transition cursor-pointer shadow-xs focus:outline-none focus:ring-2 focus:ring-blue disabled:opacity-50 self-start sm:self-center"
          >
            {loading ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Sparkles className="w-3.5 h-3.5 text-amber" />
            )}
            <span>Use the demo file (GET /api/marks/demo)</span>
          </button>
        </div>

        {/* Drag and Drop Dropzone */}
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragOver(true);
          }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setIsDragOver(false);
            const file = e.dataTransfer.files?.[0];
            if (file) handleFileUpload(file);
          }}
          className={`border-2 border-dashed rounded-xl p-6 text-center transition cursor-pointer ${
            isDragOver
              ? 'border-blue bg-blue-50/50 scale-[1.005]'
              : 'border-line/80 hover:border-blue/50 hover:bg-grey-50/50 bg-[#F9FAFB]'
          }`}
        >
          <label className="cursor-pointer block space-y-2">
            <Upload className="w-8 h-8 text-blue mx-auto" />
            <div className="text-xs font-bold text-ink">
              Drag &amp; drop a marks CSV file here, or <span className="text-blue underline">browse to upload</span>
            </div>
            <p className="text-[11px] text-grey">
              Supported format: CSV with student_id, roll_no, class, subject, theory_marks, internal_marks, total_marks
            </p>
            <input
              type="file"
              accept=".csv"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) handleFileUpload(file);
              }}
              className="hidden"
            />
          </label>
        </div>
      </section>

      {/* 2. Summary Strip */}
      <section className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        <div className="p-3.5 bg-white rounded-xl border border-line shadow-xs">
          <div className="text-[10px] font-bold uppercase tracking-wider text-grey">Rows Checked</div>
          <div className="text-2xl font-heading font-black text-ink mt-0.5">{rowsChecked}</div>
        </div>

        <div className="p-3.5 bg-white rounded-xl border border-line shadow-xs">
          <div className="text-[10px] font-bold uppercase tracking-wider text-grey">Total Flags</div>
          <div className="text-2xl font-heading font-black text-ink mt-0.5">{totalFlagsCount}</div>
        </div>

        <div className="p-3.5 bg-red-50/60 rounded-xl border border-status-block/30 shadow-xs">
          <div className="text-[10px] font-bold uppercase tracking-wider text-status-block flex items-center space-x-1">
            <Lock className="w-3 h-3" />
            <span>Blocks</span>
          </div>
          <div className="text-2xl font-heading font-black text-status-block mt-0.5">{totalBlocksCount}</div>
        </div>

        <div className="p-3.5 bg-amber-50/60 rounded-xl border border-status-review/30 shadow-xs">
          <div className="text-[10px] font-bold uppercase tracking-wider text-status-review flex items-center space-x-1">
            <AlertTriangle className="w-3 h-3" />
            <span>Reviews</span>
          </div>
          <div className="text-2xl font-heading font-black text-status-review mt-0.5">{totalReviewsCount}</div>
        </div>

        <div className="p-3.5 bg-emerald-50/60 rounded-xl border border-status-ok/30 shadow-xs col-span-2 sm:col-span-1">
          <div className="text-[10px] font-bold uppercase tracking-wider text-status-ok flex items-center space-x-1">
            <CheckCircle2 className="w-3 h-3" />
            <span>Checked</span>
          </div>
          <div className="text-2xl font-heading font-black text-status-ok mt-0.5">
            {checkedCount}/{totalFlagsCount}
          </div>
        </div>
      </section>

      {/* 3. Filter Controls Bar */}
      <section className="bg-white rounded-xl border border-line p-4 shadow-xs flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3">
          {/* Severity Filter Pills */}
          <div className="inline-flex rounded-lg border border-line bg-grey-50 p-0.5 text-xs">
            {[
              { id: 'all', label: `All (${totalFlagsCount})` },
              { id: 'block', label: `Blocks (${totalBlocksCount})` },
              { id: 'review', label: `Reviews (${totalReviewsCount})` },
              { id: 'unchecked', label: `Pending (${totalFlagsCount - checkedCount})` },
            ].map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setSeverityFilter(tab.id)}
                className={`px-2.5 py-1 rounded-md font-semibold transition cursor-pointer ${
                  severityFilter === tab.id
                    ? 'bg-white text-ink shadow-xs font-bold'
                    : 'text-grey hover:text-ink'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Class Filter Dropdown */}
          <div className="flex items-center space-x-1.5 text-xs">
            <Filter className="w-3.5 h-3.5 text-grey" />
            <select
              aria-label="Filter by Class"
              value={classFilter}
              onChange={(e) => setClassFilter(e.target.value)}
              className="px-2.5 py-1 rounded-lg border border-line bg-grey-50 font-semibold text-ink text-xs focus:outline-none focus:ring-1 focus:ring-blue cursor-pointer"
            >
              <option value="all">All Classes</option>
              {availableClasses.map((cls) => (
                <option key={cls} value={cls}>
                  Class {cls}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Search Input */}
        <div className="relative">
          <Search className="w-3.5 h-3.5 text-grey absolute left-2.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search student or record ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-8 pr-3 py-1 border border-line rounded-lg text-xs bg-grey-50 focus:outline-none focus:ring-1 focus:ring-blue w-48 sm:w-60"
          />
        </div>
      </section>

      {/* 4. Flag List Grouped by Severity */}
      <section className="space-y-6">
        {/* Error State */}
        {error && (
          <div className="p-6 bg-red-50 border border-status-block/30 rounded-xl text-center space-y-2">
            <AlertCircle className="w-8 h-8 text-status-block mx-auto" />
            <div className="text-sm font-bold text-status-block">{error}</div>
            <button
              onClick={handleUseDemoFile}
              className="px-4 py-1.5 rounded-lg bg-blue text-white text-xs font-semibold hover:bg-blue-700 transition"
            >
              Load Demo File
            </button>
          </div>
        )}

        {/* Loading State */}
        {loading && !error && (
          <div className="p-8 bg-white rounded-xl border border-line text-center space-y-3 animate-pulse">
            <RefreshCw className="w-8 h-8 text-blue animate-spin mx-auto" />
            <div className="text-sm font-bold text-ink">Running Pre-Flight Checks...</div>
            <p className="text-xs text-grey">Verifying limits, checking formulas, and evaluating statistical outliers.</p>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && filteredFlags.length === 0 && (
          <div className="p-12 bg-white rounded-xl border border-line text-center space-y-2">
            <CheckCircle2 className="w-10 h-10 text-status-ok mx-auto" />
            <h3 className="font-heading text-sm text-ink uppercase">No Discrepancies Found</h3>
            <p className="text-xs text-grey">
              All marks in the selected filter match validation rules.
            </p>
          </div>
        )}

        {/* Populated Groups */}
        {!loading && !error && filteredFlags.length > 0 && (
          <div className="space-y-6">
            {/* Group A: Block Flags */}
            {blockFlags.length > 0 && (
              <div className="space-y-3">
                <div className="flex items-center space-x-2 text-status-block pb-1 border-b border-status-block/20">
                  <Lock className="w-4 h-4" />
                  <h3 className="font-heading text-xs tracking-wider uppercase">
                    Block Discrepancies ({blockFlags.length})
                  </h3>
                  <span className="text-[11px] text-grey-500 font-normal">
                    &bull; Cannot be submitted to records until resolved
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {blockFlags.map((flag) => {
                    const flagKey = flag.id || flag.record_id || `${flag.student_name}-${flag.column}`;
                    const isChecked = checkedFlagIds.has(flagKey);

                    return (
                      <div
                        key={flagKey}
                        className={`p-4 rounded-xl border transition flex flex-col justify-between space-y-3 ${
                          isChecked
                            ? 'bg-grey-50/70 border-line opacity-80'
                            : 'bg-white border-status-block/30 shadow-xs hover:border-status-block/60'
                        }`}
                      >
                        {/* Evidence Card Header */}
                        <div className="space-y-1.5">
                          <div className="flex items-center justify-between gap-2">
                            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-bold uppercase font-mono bg-red-100 text-status-block border border-status-block/30">
                              <Lock className="w-3 h-3" />
                              <span>Block</span>
                            </span>
                            <span className="text-[10px] font-mono text-grey">
                              ID: {flag.record_id || 'N/A'}
                            </span>
                          </div>

                          <div className="flex items-center space-x-2">
                            <span className="font-bold text-ink text-sm">
                              {flag.student_name}
                            </span>
                            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-grey-100 text-grey-700 font-mono">
                              Class {flag.class}
                            </span>
                          </div>

                          <div className="text-xs text-grey font-medium">
                            Subject: <span className="font-bold text-ink">{flag.subject}</span>
                          </div>
                        </div>

                        {/* Evidence Card Body */}
                        <div className="bg-red-50/40 rounded-lg p-2.5 border border-status-block/15 space-y-1.5 text-xs">
                          <div className="flex items-center justify-between text-[11px] font-mono">
                            <span className="text-grey">Column:</span>
                            <span className="font-bold text-ink">{flag.column}</span>
                          </div>
                          <div className="flex items-center justify-between text-[11px] font-mono">
                            <span className="text-grey">Observed:</span>
                            <span className="font-bold text-status-block bg-red-100 px-1.5 py-0.5 rounded">
                              {flag.observed}
                            </span>
                          </div>
                          <div className="flex items-center justify-between text-[11px] font-mono">
                            <span className="text-grey">Expected:</span>
                            <span className="font-bold text-status-ok bg-emerald-100 px-1.5 py-0.5 rounded">
                              {flag.expected}
                            </span>
                          </div>

                          <p className="text-xs text-grey-800 font-medium pt-1 leading-snug">
                            {flag.evidence}
                          </p>

                          {flag.hint && (
                            <div className="mt-1 pt-1 border-t border-status-block/15 flex items-start space-x-1.5 text-[11px] text-amber-dark font-medium">
                              <Lightbulb className="w-3.5 h-3.5 flex-shrink-0 mt-0.5 text-amber" />
                              <span>Hint: {flag.hint}</span>
                            </div>
                          )}
                        </div>

                        {/* Evidence Card Footer: Local "Mark as checked" Toggle */}
                        <div className="pt-2 border-t border-line/60 flex items-center justify-between">
                          <span className="text-[10px] text-grey font-mono">
                            Rule: {flag.rule}
                          </span>

                          <button
                            type="button"
                            onClick={() => handleToggleChecked(flagKey)}
                            className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md text-xs font-semibold border transition cursor-pointer ${
                              isChecked
                                ? 'bg-emerald-50 text-status-ok border-status-ok/30 font-bold'
                                : 'bg-white text-grey-700 border-line hover:border-grey hover:bg-grey-50'
                            }`}
                          >
                            <Check className={`w-3.5 h-3.5 ${isChecked ? 'text-status-ok' : 'text-grey'}`} />
                            <span>{isChecked ? 'Checked by teacher' : 'Mark as checked'}</span>
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Group B: Review Flags */}
            {reviewFlags.length > 0 && (
              <div className="space-y-3">
                <div className="flex items-center space-x-2 text-status-review pb-1 border-b border-status-review/20">
                  <AlertTriangle className="w-4 h-4" />
                  <h3 className="font-heading text-xs tracking-wider uppercase">
                    Review Discrepancies ({reviewFlags.length})
                  </h3>
                  <span className="text-[11px] text-grey-500 font-normal">
                    &bull; Flagged for verification (absent codes, component mismatches, outliers)
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {reviewFlags.map((flag) => {
                    const flagKey = flag.id || flag.record_id || `${flag.student_name}-${flag.column}`;
                    const isChecked = checkedFlagIds.has(flagKey);

                    return (
                      <div
                        key={flagKey}
                        className={`p-4 rounded-xl border transition flex flex-col justify-between space-y-3 ${
                          isChecked
                            ? 'bg-grey-50/70 border-line opacity-80'
                            : 'bg-white border-status-review/30 shadow-xs hover:border-status-review/60'
                        }`}
                      >
                        {/* Evidence Card Header */}
                        <div className="space-y-1.5">
                          <div className="flex items-center justify-between gap-2">
                            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-bold uppercase font-mono bg-amber-100 text-status-review border border-status-review/30">
                              <AlertTriangle className="w-3 h-3" />
                              <span>Review</span>
                            </span>
                            <span className="text-[10px] font-mono text-grey">
                              ID: {flag.record_id || 'N/A'}
                            </span>
                          </div>

                          <div className="flex items-center space-x-2">
                            <span className="font-bold text-ink text-sm">
                              {flag.student_name}
                            </span>
                            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-grey-100 text-grey-700 font-mono">
                              Class {flag.class}
                            </span>
                          </div>

                          <div className="text-xs text-grey font-medium">
                            Subject: <span className="font-bold text-ink">{flag.subject}</span>
                          </div>
                        </div>

                        {/* Evidence Card Body */}
                        <div className="bg-amber-50/40 rounded-lg p-2.5 border border-status-review/15 space-y-1.5 text-xs">
                          <div className="flex items-center justify-between text-[11px] font-mono">
                            <span className="text-grey">Column:</span>
                            <span className="font-bold text-ink">{flag.column}</span>
                          </div>
                          <div className="flex items-center justify-between text-[11px] font-mono">
                            <span className="text-grey">Observed:</span>
                            <span className="font-bold text-status-review bg-amber-100 px-1.5 py-0.5 rounded">
                              {flag.observed}
                            </span>
                          </div>
                          <div className="flex items-center justify-between text-[11px] font-mono">
                            <span className="text-grey">Expected:</span>
                            <span className="font-bold text-status-ok bg-emerald-100 px-1.5 py-0.5 rounded">
                              {flag.expected}
                            </span>
                          </div>

                          <p className="text-xs text-grey-800 font-medium pt-1 leading-snug">
                            {flag.evidence}
                          </p>

                          {flag.hint && (
                            <div className="mt-1 pt-1 border-t border-status-review/15 flex items-start space-x-1.5 text-[11px] text-amber-dark font-medium">
                              <Lightbulb className="w-3.5 h-3.5 flex-shrink-0 mt-0.5 text-amber" />
                              <span>Hint: {flag.hint}</span>
                            </div>
                          )}
                        </div>

                        {/* Evidence Card Footer: Local "Mark as checked" Toggle */}
                        <div className="pt-2 border-t border-line/60 flex items-center justify-between">
                          <span className="text-[10px] text-grey font-mono">
                            Rule: {flag.rule}
                          </span>

                          <button
                            type="button"
                            onClick={() => handleToggleChecked(flagKey)}
                            className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md text-xs font-semibold border transition cursor-pointer ${
                              isChecked
                                ? 'bg-emerald-50 text-status-ok border-status-ok/30 font-bold'
                                : 'bg-white text-grey-700 border-line hover:border-grey hover:bg-grey-50'
                            }`}
                          >
                            <Check className={`w-3.5 h-3.5 ${isChecked ? 'text-status-ok' : 'text-grey'}`} />
                            <span>{isChecked ? 'Checked by teacher' : 'Mark as checked'}</span>
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </section>
    </div>
  );
}
