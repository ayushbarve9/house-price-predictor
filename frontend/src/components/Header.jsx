import React from 'react';
import { Home, ShieldCheck, Cpu } from 'lucide-react';

export default function Header({ meta, loading }) {
  return (
    <header className="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-18 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20 ring-1 ring-emerald-400/30">
            <Home className="h-5 w-5 text-slate-950 font-black stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                GrihaValue
              </span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                गृहValue AI
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              Institutional-Grade Indian Real Estate Valuation & Acquisition Intelligence
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden md:flex items-center gap-2 text-xs text-slate-300 bg-slate-900/90 border border-slate-800 px-3 py-1.5 rounded-lg shadow-sm">
            <Cpu className="h-3.5 w-3.5 text-emerald-400" />
            <span>
              {loading ? (
                'Loading model...'
              ) : meta ? (
                <>
                  <span className="text-slate-400">Model:</span>{' '}
                  <strong className="text-emerald-300">{meta.model_name || 'Ensemble RF'}</strong>{' '}
                  {meta.r2_score && (
                    <span className="text-slate-400 ml-1">
                      (R²: <span className="text-emerald-400">{(meta.r2_score * 100).toFixed(1)}%</span>)
                    </span>
                  )}
                </>
              ) : (
                <span className="text-amber-400">Model offline</span>
              )}
            </span>
          </div>

          <div className="flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-950/40 border border-emerald-800/50 px-2.5 py-1.5 rounded-lg">
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
            <span className="font-medium hidden sm:inline">RBI LTV & State Acts Compliant</span>
            <span className="font-medium sm:hidden">RBI Verified</span>
          </div>
        </div>
      </div>
    </header>
  );
}
