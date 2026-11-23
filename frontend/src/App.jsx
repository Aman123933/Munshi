import React, { useState, useEffect } from 'react';
import { Activity, CheckCircle2, AlertCircle, RefreshCw, Server, ShieldCheck, BookOpen } from 'lucide-react';

export default function App() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastChecked, setLastChecked] = useState(null);

  const checkHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/health');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setHealth(data);
      setLastChecked(new Date().toLocaleTimeString());
    } catch (err) {
      console.error('Failed to fetch /api/health:', err);
      setError(err.message || 'Failed to connect to backend proxy');
      setHealth(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  return (
    <div className="min-h-screen bg-[#EAF0FF] text-[#0B1220] flex flex-col">
      {/* Header */}
      <header className="border-b border-[#D0D5DD] bg-white px-6 py-4 shadow-sm">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-[#1F4FD8] flex items-center justify-center text-white font-black text-xl font-heading">
              M
            </div>
            <div>
              <h1 className="text-xl font-heading text-[#0B1220] tracking-wide">MUNSHI</h1>
              <p className="text-xs text-[#475467] font-medium">AI proposes. Rules verify. Teacher confirms.</p>
            </div>
          </div>
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#EAF0FF] text-[#1F4FD8] border border-[#1F4FD8]/20">
            Hackathon Prototype v0.1
          </span>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-6xl mx-auto w-full p-6 space-y-6">
        {/* API Health Card */}
        <section className="bg-white rounded-xl border border-[#D0D5DD] p-6 shadow-sm">
          <div className="flex items-center justify-between pb-4 border-b border-[#D0D5DD]">
            <div className="flex items-center space-x-3">
              <Server className="w-5 h-5 text-[#1F4FD8]" />
              <div>
                <h2 className="text-lg font-heading text-[#0B1220]">Backend Proxy Health Check</h2>
                <p className="text-sm text-[#475467]">
                  Frontend querying <code className="bg-[#EAF0FF] text-[#1F4FD8] px-1.5 py-0.5 rounded text-xs font-mono font-semibold">/api/health</code> via Vite proxy to port 8000
                </p>
              </div>
            </div>
            <button
              onClick={checkHealth}
              disabled={loading}
              className="inline-flex items-center space-x-2 px-3.5 py-2 rounded-lg bg-[#1F4FD8] text-white text-sm font-semibold hover:bg-[#1A43B8] transition duration-150 disabled:opacity-50 cursor-pointer"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>{loading ? 'Checking...' : 'Recheck'}</span>
            </button>
          </div>

          <div className="mt-5">
            {loading && !health && !error ? (
              <div className="flex items-center space-x-3 text-[#475467] p-4 bg-slate-50 rounded-lg">
                <Activity className="w-5 h-5 animate-pulse text-[#1F4FD8]" />
                <span className="text-sm">Connecting to backend server at port 8000...</span>
              </div>
            ) : health ? (
              <div className="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-emerald-50 border border-[#067647]/20 rounded-lg">
                <div className="flex items-center space-x-3">
                  <CheckCircle2 className="w-6 h-6 text-[#067647] flex-shrink-0" />
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-bold text-[#067647]">Backend Online & Healthy</span>
                      <span className="px-2 py-0.5 text-xs rounded font-mono font-semibold bg-[#067647]/10 text-[#067647]">
                        status: OK (200)
                      </span>
                    </div>
                    <p className="text-xs text-[#067647]/80 mt-0.5 font-mono">
                      Payload: {JSON.stringify(health)}
                    </p>
                  </div>
                </div>
                {lastChecked && (
                  <span className="text-xs text-[#475467] mt-2 sm:mt-0 font-medium">
                    Last response: {lastChecked}
                  </span>
                )}
              </div>
            ) : (
              <div className="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-red-50 border border-[#B42318]/20 rounded-lg">
                <div className="flex items-center space-x-3">
                  <AlertCircle className="w-6 h-6 text-[#B42318] flex-shrink-0" />
                  <div>
                    <span className="text-sm font-bold text-[#B42318]">Connection Failed</span>
                    <p className="text-xs text-[#B42318]/80 mt-0.5 font-mono">
                      {error || 'Make sure uvicorn backend is running on http://127.0.0.1:8000'}
                    </p>
                  </div>
                </div>
                <span className="text-xs text-[#B42318] font-semibold mt-2 sm:mt-0">
                  Status: Blocked
                </span>
              </div>
            )}
          </div>
        </section>

        {/* System Architecture Overview */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-xl border border-[#D0D5DD] p-5 shadow-sm space-y-2">
            <div className="flex items-center space-x-2 text-[#1F4FD8]">
              <BookOpen className="w-5 h-5" />
              <h3 className="font-heading text-sm text-[#0B1220]">Core Principle</h3>
            </div>
            <p className="text-xs text-[#475467] leading-relaxed">
              AI proposes. Rules verify. The teacher confirms. The language model never writes directly to the record tables.
            </p>
          </div>

          <div className="bg-white rounded-xl border border-[#D0D5DD] p-5 shadow-sm space-y-2">
            <div className="flex items-center space-x-2 text-[#067647]">
              <ShieldCheck className="w-5 h-5" />
              <h3 className="font-heading text-sm text-[#0B1220]">Rule Verification (R1-R9)</h3>
            </div>
            <p className="text-xs text-[#475467] leading-relaxed">
              Span verifier computes exact substring offsets. RapidFuzz resolves rosters. Rules enforce assignments, dates, topics, and marks limits.
            </p>
          </div>

          <div className="bg-white rounded-xl border border-[#D0D5DD] p-5 shadow-sm space-y-2">
            <div className="flex items-center space-x-2 text-[#FFB020]">
              <Server className="w-5 h-5 text-[#B54708]" />
              <h3 className="font-heading text-sm text-[#0B1220]">Atomic Confirm</h3>
            </div>
            <p className="text-xs text-[#475467] leading-relaxed">
              Teacher reviews and resolves ambiguities. All record tables and audit logs are committed in a single transaction.
            </p>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-[#D0D5DD] bg-white px-6 py-4 mt-auto">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between text-xs text-[#475467]">
          <span>Munshi &copy; 2026. Built with FastAPI, React, Vite & Tailwind CSS.</span>
          <span className="mt-1 sm:mt-0 font-medium">Design tokens: Ink #0B1220 &bull; Blue #1F4FD8 &bull; Amber #FFB020 &bull; Tint #EAF0FF</span>
        </div>
      </footer>
    </div>
  );
}
