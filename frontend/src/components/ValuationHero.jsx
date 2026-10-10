import React from 'react';
import { MapPin } from 'lucide-react';
import { formatINR, formatFullINR, getPriceTier } from '../utils/formatters';

export default function ValuationHero({ estimate, form }) {
  if (!estimate) return null;

  const { predicted_price, rate_per_sqft, finance } = estimate;
  const tier = getPriceTier(predicted_price);
  const ltvPercent = Math.round((finance?.ltv_ratio || 0.75) * 100);

  return (
    <div className="glass-panel rounded-2xl p-6 sm:p-7 shadow-2xl relative overflow-hidden gradient-border-emerald">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 text-xs text-slate-400 mb-1">
            <MapPin className="h-3.5 w-3.5 text-emerald-400" />
            <span>
              {form.bhk} BHK • {form.locality}, {form.city} • {form.area_sqft} sq.ft
            </span>
          </div>
          <span className="text-xs uppercase tracking-wider font-semibold text-emerald-400">
            Estimated Fair Market Value
          </span>
          <div className="flex items-baseline gap-3 mt-1">
            <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              {formatINR(predicted_price)}
            </h1>
            <span className="text-xs sm:text-sm text-slate-400 font-medium">
              ({formatFullINR(predicted_price)})
            </span>
          </div>
        </div>

        <div className="flex sm:flex-col items-start sm:items-end gap-2">
          <span className={`text-xs font-semibold px-3 py-1 rounded-full border ${tier.color}`}>
            {tier.label}
          </span>
          <div className="text-right">
            <span className="text-[11px] text-slate-400 block">Unit Rate</span>
            <span className="text-sm font-bold text-slate-200">
              ₹{Math.round(rate_per_sqft).toLocaleString('en-IN')}{' '}
              <span className="text-xs font-normal text-slate-400">/ sq.ft</span>
            </span>
          </div>
        </div>
      </div>

      {/* Key metric cards grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6">
        <div className="bg-slate-900/80 rounded-xl p-3.5 border border-slate-800">
          <span className="text-[11px] text-slate-400 block mb-1">Monthly EMI</span>
          <span className="text-base sm:text-lg font-bold text-emerald-400">
            {formatINR(finance.monthly_emi)}
          </span>
          <span className="text-[10px] text-slate-500 block mt-0.5">
            @{form.annual_rate_pct}% for {form.tenure_years} yrs
          </span>
        </div>

        <div className="bg-slate-900/80 rounded-xl p-3.5 border border-slate-800">
          <span className="text-[11px] text-slate-400 block mb-1">Upfront Down Payment</span>
          <span className="text-base sm:text-lg font-bold text-slate-200">
            {formatINR(finance.down_payment)}
          </span>
          <span className="text-[10px] text-slate-500 block mt-0.5">
            {Math.round((finance.down_payment / predicted_price) * 100)}% of valuation
          </span>
        </div>

        <div className="bg-slate-900/80 rounded-xl p-3.5 border border-slate-800">
          <span className="text-[11px] text-slate-400 block mb-1">Sanctioned Loan</span>
          <span className="text-base sm:text-lg font-bold text-blue-400">
            {formatINR(finance.loan_amount)}
          </span>
          <span className="text-[10px] text-slate-500 block mt-0.5">
            Max LTV: {ltvPercent}%
          </span>
        </div>

        <div className="bg-slate-900/80 rounded-xl p-3.5 border border-slate-800">
          <span className="text-[11px] text-slate-400 block mb-1">Total Acquisition Cost</span>
          <span className="text-base sm:text-lg font-bold text-amber-300">
            {formatINR(finance.total_acquisition_cost)}
          </span>
          <span className="text-[10px] text-slate-500 block mt-0.5">
            Incl. Stamp Duty & Taxes
          </span>
        </div>
      </div>
    </div>
  );
}
