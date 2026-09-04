import React from 'react';
import { AlertOctagon, CheckCircle } from 'lucide-react';

export default function ExceptionTable({ data = [] }) {
  return (
    <div className="bg-dark-800 rounded-xl border border-dark-700 overflow-hidden shadow-lg">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-dark-700 text-slate-200 uppercase text-xs font-semibold">
            <tr>
              <th className="px-6 py-4">Transaction ID</th>
              <th className="px-6 py-4">Ledger Vendor</th>
              <th className="px-6 py-4">Issue Type</th>
              <th className="px-6 py-4">Ledger Amount</th>
              <th className="px-6 py-4">Bank Amount</th>
              <th className="px-6 py-4">Difference</th>
              <th className="px-6 py-4">Confidence</th>
              <th className="px-6 py-4">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-dark-700">
            {data.map((row, i) => {
              const txnId = row.transaction_id || row.id || `EXC-${i + 1}`;
              const vendor = row.ledger_vendor || row.vendor || 'N/A';
              const status = row.status || row.issue_type || 'EXCEPTION';
              const lAmt = row.ledger_amount != null ? `₹${parseFloat(row.ledger_amount).toFixed(2)}` : '—';
              const bAmt = row.bank_amount != null ? `₹${parseFloat(row.bank_amount).toFixed(2)}` : '—';
              
              let diffText = '—';
              if (row.amount_difference != null) {
                diffText = `₹${parseFloat(row.amount_difference).toFixed(2)}`;
              } else if (row.date_difference_days != null) {
                diffText = `${row.date_difference_days} days`;
              } else if (row.difference != null) {
                diffText = `₹${parseFloat(row.difference).toFixed(2)}`;
              }

              const conf = row.confidence != null ? Number(row.confidence).toFixed(1) : '30.0';

              let badgeStyle = 'bg-red-500/10 text-red-400 border border-red-500/20';
              if (status === 'AMOUNT_MISMATCH') badgeStyle = 'bg-orange-500/10 text-orange-400 border border-orange-500/20';
              else if (status === 'DATE_MISMATCH') badgeStyle = 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20';
              else if (status === 'MISSING_BANK_RECORD') badgeStyle = 'bg-pink-500/10 text-pink-400 border border-pink-500/20';
              else if (status === 'DUPLICATE') badgeStyle = 'bg-purple-500/10 text-purple-400 border border-purple-500/20';

              return (
                <tr key={i} className="hover:bg-dark-700/50 transition-colors">
                  <td className="px-6 py-4 font-mono text-xs text-red-400 font-semibold">{txnId}</td>
                  <td className="px-6 py-4 font-medium text-white">{vendor}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${badgeStyle}`}>
                      {status}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-mono text-slate-300">{lAmt}</td>
                  <td className="px-6 py-4 font-mono text-slate-300">{bAmt}</td>
                  <td className="px-6 py-4 font-mono text-amber-400 font-medium">{diffText}</td>
                  <td className="px-6 py-4 font-mono text-xs">{conf}%</td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => alert(`Reviewing exception: ${txnId}\nVendor: ${vendor}\nStatus: ${status}\nNotes: ${row.notes || 'Discrepancy flagged for human audit.'}`)}
                      className="flex items-center gap-1.5 text-brand-blue hover:text-blue-400 transition-colors text-xs font-semibold uppercase tracking-wider bg-brand-blue/10 px-3 py-1.5 rounded-lg border border-brand-blue/20"
                    >
                      <AlertOctagon size={14} /> Review
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {data.length === 0 && (
          <div className="p-8 text-center text-slate-500">
            No exceptions found.
          </div>
        )}
      </div>
    </div>
  );
}
