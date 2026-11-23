import React from 'react';
import { Activity, ShieldCheck, Search, Cpu } from 'lucide-react';

export default function LoadingSkeleton() {
  return (
    <div className="bg-white rounded-xl border border-line p-6 shadow-sm space-y-6 animate-pulse">
      {/* Pipeline Status Indicator */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-line gap-2">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-tint text-blue flex items-center justify-center">
            <Activity className="w-5 h-5 animate-spin" />
          </div>
          <div>
            <h2 className="font-heading text-sm text-ink uppercase tracking-wide">
              Processing Pipeline in Progress...
            </h2>
            <p className="text-xs text-grey">
              Extracting structured entities, computing span offsets, and running rules R1 to R9
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2 text-xs font-mono text-grey">
          <span className="w-2.5 h-2.5 rounded-full bg-[#FFB020] animate-ping" />
          <span>Evaluating rules...</span>
        </div>
      </div>

      {/* Pipeline Stages Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
        {[
          { icon: Cpu, label: 'LLM Extraction' },
          { icon: Search, label: 'Span Verifier' },
          { icon: Search, label: 'Roster Match' },
          { icon: ShieldCheck, label: 'Rules R1-R9' },
        ].map((stage, idx) => {
          const Icon = stage.icon;
          return (
            <div
              key={idx}
              className="p-3 bg-grey-50 rounded-lg border border-line/60 flex items-center space-x-2.5"
            >
              <Icon className="w-4 h-4 text-blue animate-bounce" />
              <div className="flex-1">
                <div className="text-[10px] text-grey font-bold uppercase tracking-wider">
                  Step {idx + 1}
                </div>
                <div className="text-xs font-semibold text-ink">{stage.label}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Shimmer Placeholder Fields */}
      <div className="space-y-3 pt-2">
        <div className="h-4 bg-grey-200 rounded w-1/4" />
        <div className="h-20 bg-grey-100 rounded-xl border border-line/50 p-4 space-y-2">
          <div className="h-4 bg-grey-200 rounded w-3/4" />
          <div className="h-3 bg-grey-200 rounded w-1/2" />
        </div>
        <div className="h-20 bg-grey-100 rounded-xl border border-line/50 p-4 space-y-2">
          <div className="h-4 bg-grey-200 rounded w-2/3" />
          <div className="h-3 bg-grey-200 rounded w-1/3" />
        </div>
        <div className="h-20 bg-grey-100 rounded-xl border border-line/50 p-4 space-y-2">
          <div className="h-4 bg-grey-200 rounded w-4/5" />
          <div className="h-3 bg-grey-200 rounded w-2/5" />
        </div>
      </div>
    </div>
  );
}
