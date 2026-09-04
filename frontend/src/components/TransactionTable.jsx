import React from 'react';
import { AlertCircle, CheckCircle } from 'lucide-react';

export default function TransactionTable({ data = [] }) {
  return (
    <div className="bg-dark-800 rounded-xl border border-dark-700 overflow-hidden shadow-lg">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-dark-700 text-slate-200 uppercase text-xs font-semibold">
            <tr>
              <th className="px-6 py-4">Txn ID</th>
              <th className="px-6 py-4">Vendor</th>
              <th className="px-6 py-4">Ledger Amount</th>
              <th className="px-6 py-4">Bank Vendor</th>
              <th className="px-6 py-4">Bank Amount</th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4">Confidence</th>
              <th className="px-6 py-4">Review</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-dark-700">
            {data.map((row, i) => {
              const txnId = row.transaction_id || row.id || `TXN-${i + 1}`;
              const vendor = row.ledger_vendor || row.vendor || 'N/A';
              const bankVendor = row.bank_vendor || '—';
              const lAmt = row.ledger_amount != null ? parseFloat(row.ledger_amount).toFixed(2) : '—';
              const bAmt = row.bank_amount != null ? parseFloat(row.bank_amount).toFixed(2) : '—';
              const status = row.status || 'Unknown';
              const isMatched = status === 'MATCHED' || status === 'FUZZY_MATCHED' || status === 'Matched';
              const conf = row.confidence != null ? Number(row.confidence).toFixed(1) : '—';
              const needsReview = row.requires_human_review ?? row.human_review ?? false;

              let statusColor = 'bg-slate-700 text-slate-300';
              if (status === 'MATCHED') statusColor = 'bg-green-500/10 text-green-400 border border-green-500/20';
              else if (status === 'FUZZY_MATCHED') statusColor = 'bg-blue-500/10 text-blue-400 border border-blue-500/20';
              else if (status === 'AMOUNT_MISMATCH') statusColor = 'bg-orange-500/10 text-orange-400 border border-orange-500/20';
              else if (status === 'DATE_MISMATCH') statusColor = 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20';
              else if (status === 'MISSING_BANK_RECORD') statusColor = 'bg-pink-500/10 text-pink-400 border border-pink-500/20';
              else if (status === 'DUPLICATE') statusColor = 'bg-purple-500/10 text-purple-400 border border-purple-500/20';
              else if (status === 'UNRESOLVED') statusColor = 'bg-red-500/10 text-red-400 border border-red-500/20';

              return (
                <tr key={i} className="hover:bg-dark-700/50 transition-colors">
                  <td className="px-6 py-4 font-mono text-xs text-brand-blue font-medium">{txnId}</td>
                  <td className="px-6 py-4 font-medium text-white">{vendor}</td>
                  <td className="px-6 py-4 font-mono text-slate-200">₹{lAmt}</td>
                  <td className="px-6 py-4 text-slate-300">{bankVendor}</td>
                  <td className="px-6 py-4 font-mono text-slate-200">₹{bAmt}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${statusColor}`}>
                      {status}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-mono text-xs">{conf}%</td>
                  <td className="px-6 py-4">
                    {needsReview ? (
                      <span className="flex items-center gap-1.5 text-xs text-red-400 font-medium">
                        <AlertCircle size={16} /> Required
                      </span>
                    ) : (
                      <span className="flex items-center gap-1.5 text-xs text-green-400 font-medium">
                        <CheckCircle size={16} /> Verified
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {data.length === 0 && (
          <div className="p-8 text-center text-slate-500">
            No transactions found.
          </div>
        )}
      </div>
    </div>
  );
}
