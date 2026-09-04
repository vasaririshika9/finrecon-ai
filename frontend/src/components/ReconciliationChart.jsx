import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

export default function ReconciliationChart({ data }) {
  if (!data) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-500">
        No reconciliation data available
      </div>
    );
  }

  // Support both backend schema and fallback schema
  const exact = data.exact_matches ?? data.matched ?? 0;
  const fuzzy = data.fuzzy_matches ?? data.fuzzy_matched ?? 0;
  const amtMismatch = data.amount_mismatches ?? 0;
  const dateMismatch = data.date_mismatches ?? 0;
  const missing = data.missing_records ?? 0;
  const dups = data.duplicates ?? 0;
  const unresolved = data.unresolved_exceptions ?? data.unresolved ?? 0;

  const chartData = [
    { name: 'Exact Match', value: exact, color: '#22c55e' },
    { name: 'Fuzzy Match', value: fuzzy, color: '#3b82f6' },
    { name: 'Amount Mismatch', value: amtMismatch, color: '#f97316' },
    { name: 'Date Mismatch', value: dateMismatch, color: '#eab308' },
    { name: 'Missing Bank', value: missing, color: '#ec4899' },
    { name: 'Duplicates', value: dups, color: '#a855f7' },
    { name: 'Unresolved', value: unresolved, color: '#ef4444' },
  ].filter(item => item.value > 0);

  return (
    <div className="bg-dark-800 p-6 rounded-xl border border-dark-700 shadow-lg h-96 flex flex-col">
      <h3 className="text-lg font-semibold text-white mb-2">Reconciliation Distribution</h3>
      <div className="flex-1 w-full min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              innerRadius={65}
              outerRadius={100}
              paddingAngle={4}
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                borderColor: '#334155',
                borderRadius: '8px',
                color: '#fff',
              }}
            />
            <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
