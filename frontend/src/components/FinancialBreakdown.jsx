import React from 'react';
import { 
  CreditCard, 
  Receipt, 
  Coins, 
  Building 
} from 'lucide-react';
import { formatINR, formatFullINR } from '../utils/formatters';

export default function FinancialBreakdown({ finance, city }) {
  if (!finance) return null;

  const total = finance.total_acquisition_cost || (finance.property_value + finance.stamp_duty + finance.gst);
  const loanPct = Math.round((finance.loan_amount / total) * 100);
  const downPct = Math.round((finance.down_payment / total) * 100);
  const stampPct = Math.round((finance.stamp_duty / total) * 100);
  const gstPct = Math.round((finance.gst / total) * 100);

  // Total cash needed upfront (down payment + stamp duty + GST)
  const initialCashNeeded = finance.down_payment + finance.stamp_duty + finance.gst;

  return (
    <div className="glass-panel rounded-2xl p-6 sm:p-7 shadow-2xl">
      <div className="flex items-center justify-between pb-5 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <Coins className="h-5 w-5 text-emerald-400" />
            Complete Acquisition Cost & Financing Architecture
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Grounded in RBI Master Direction & State Stamp Duty Schedules (October 2026)
          </p>
        </div>
      </div>

      {/* Visual capital split bar */}
      <div className="mt-6">
        <div className="flex justify-between items-center text-xs mb-2">
          <span className="font-semibold text-slate-300">Capital Structure</span>
          <span className="text-slate-400">Total: {formatINR(total)}</span>
        </div>
        <div className="h-3 w-full bg-slate-900 rounded-full overflow-hidden flex">
          <div 
            style={{ width: `${loanPct}%` }} 
            className="bg-blue-500 transition-all duration-500" 
            title={`Bank Loan: ${loanPct}%`}
          />
          <div 
            style={{ width: `${downPct}%` }} 
            className="bg-emerald-500 transition-all duration-500" 
            title={`Down Payment: ${downPct}%`}
          />
          <div 
            style={{ width: `${stampPct}%` }} 
            className="bg-amber-500 transition-all duration-500" 
            title={`Stamp Duty: ${stampPct}%`}
          />
          {gstPct > 0 && (
            <div 
              style={{ width: `${gstPct}%` }} 
              className="bg-rose-500 transition-all duration-500" 
              title={`GST: ${gstPct}%`}
            />
          )}
        </div>
        <div className="flex flex-wrap items-center gap-4 text-[11px] text-slate-300 mt-2">
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-blue-500" /> Bank Loan ({loanPct}%)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-emerald-500" /> Down Payment ({downPct}%)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-amber-500" /> Stamp Duty & Reg ({stampPct}%)
          </span>
          {gstPct > 0 && (
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-rose-500" /> GST ({gstPct}%)
            </span>
          )}
        </div>
      </div>

      {/* Itemized Table */}
      <div className="mt-6 divide-y divide-slate-800/80">
        <div className="py-3 flex justify-between items-center text-sm">
          <div className="flex items-center gap-2">
            <Building className="h-4 w-4 text-slate-400" />
            <span className="text-slate-300">Base Property Value (Model Output)</span>
          </div>
          <span className="font-semibold text-slate-100">{formatINR(finance.property_value)}</span>
        </div>

        <div className="py-3 flex justify-between items-center text-sm">
          <div className="flex items-center gap-2">
            <CreditCard className="h-4 w-4 text-blue-400" />
            <div>
              <span className="text-slate-300">Eligible Bank Home Loan</span>
              <span className="text-[11px] text-slate-500 block">
                RBI Cap applied: {(finance.ltv_ratio * 100).toFixed(0)}% LTV
              </span>
            </div>
          </div>
          <span className="font-semibold text-blue-400">{formatINR(finance.loan_amount)}</span>
        </div>

        <div className="py-3 flex justify-between items-center text-sm">
          <div className="flex items-center gap-2">
            <Coins className="h-4 w-4 text-emerald-400" />
            <div>
              <span className="text-slate-300">Buyer Equity (Down Payment)</span>
              <span className="text-[11px] text-slate-500 block">
                Paid directly to seller / builder
              </span>
            </div>
          </div>
          <span className="font-semibold text-emerald-400">{formatINR(finance.down_payment)}</span>
        </div>

        <div className="py-3 flex justify-between items-center text-sm">
          <div className="flex items-center gap-2">
            <Receipt className="h-4 w-4 text-amber-400" />
            <div>
              <span className="text-slate-300">State Stamp Duty & Registration</span>
              <span className="text-[11px] text-slate-500 block">
                Statutory fees for {city}
              </span>
            </div>
          </div>
          <span className="font-semibold text-amber-400">{formatINR(finance.stamp_duty)}</span>
        </div>

        <div className="py-3 flex justify-between items-center text-sm">
          <div className="flex items-center gap-2">
            <Receipt className="h-4 w-4 text-rose-400" />
            <div>
              <span className="text-slate-300">GST on Property</span>
              <span className="text-[11px] text-slate-500 block">
                {finance.gst === 0 
                  ? 'Exempt (Ready to move with completion cert)' 
                  : '5% (or 1% affordable) for Under Construction'}
              </span>
            </div>
          </div>
          <span className="font-semibold text-slate-300">
            {finance.gst === 0 ? '₹0 (Exempt)' : formatINR(finance.gst)}
          </span>
        </div>

        <div className="py-4 flex justify-between items-center bg-slate-900/50 px-3 rounded-xl mt-3 border border-slate-800">
          <div>
            <span className="text-sm font-bold text-slate-100 block">
              Upfront Out-of-Pocket Cash Required
            </span>
            <span className="text-xs text-slate-400">
              Down Payment + Stamp Duty + GST
            </span>
          </div>
          <div className="text-right">
            <span className="text-base font-extrabold text-emerald-400">
              {formatINR(initialCashNeeded)}
            </span>
            <span className="text-[11px] text-slate-500 block">
              {formatFullINR(initialCashNeeded)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
