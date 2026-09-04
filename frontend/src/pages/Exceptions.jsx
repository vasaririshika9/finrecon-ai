import React, { useEffect, useState } from 'react';
import ExceptionTable from '../components/ExceptionTable';
import MetricCard from '../components/MetricCard';
import { api } from '../services/api';
import { Loader2, DollarSign, Calendar, FileQuestion, Users, RefreshCw } from 'lucide-react';

export default function Exceptions() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchExceptions = async () => {
    setLoading(true);
    try {
      const res = await api.getExceptions();
      setData(Array.isArray(res) ? res : []);
    } catch (err) {
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExceptions();
  }, []);

  // Compute live counts from exceptions data
  const amtMismatches = data.filter(r => r.status === 'AMOUNT_MISMATCH' || r.issue_type === 'Amount Mismatch').length;
  const dateMismatches = data.filter(r => r.status === 'DATE_MISMATCH' || r.issue_type === 'Date Mismatch').length;
  const missingRecords = data.filter(r => r.status === 'MISSING_BANK_RECORD' || r.issue_type === 'Missing Record').length;
  const reviewRequired = data.length;

  return (
    <div className="space-y-6">
      {/* Metric Cards dynamically reflecting exceptions */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Amount Mismatches"
          value={amtMismatches}
          icon={DollarSign}
          color="text-orange-400"
          bg="bg-orange-400/10"
        />
        <MetricCard
          title="Date Mismatches"
          value={dateMismatches}
          icon={Calendar}
          color="text-yellow-400"
          bg="bg-yellow-400/10"
        />
        <MetricCard
          title="Missing Records"
          value={missingRecords}
          icon={FileQuestion}
          color="text-pink-400"
          bg="bg-pink-400/10"
        />
        <MetricCard
          title="Total In Review"
          value={reviewRequired}
          icon={Users}
          color="text-brand-purple"
          bg="bg-brand-purple/10"
        />
      </div>

      {/* Banner */}
      <div className="bg-red-500/10 border border-red-500/20 p-4 rounded-xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xl">⚠️</span>
          <div>
            <p className="text-red-400 text-sm font-semibold">
              Autonomous Exception Quarantine
            </p>
            <p className="text-xs text-slate-400 mt-0.5">
              These {data.length} transactions have discrepancies exceeding tolerance limits and have been flagged for manual finance controller review.
            </p>
          </div>
        </div>
        <button
          onClick={fetchExceptions}
          className="flex items-center gap-2 bg-dark-800 hover:bg-dark-700 text-slate-300 px-3 py-1.5 rounded-lg text-xs font-medium border border-dark-700 transition-colors"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh
        </button>
      </div>

      {/* Table */}
      {loading ? (
        <div className="flex flex-col items-center justify-center p-16 space-y-3 bg-dark-800 rounded-xl border border-dark-700">
          <Loader2 className="animate-spin text-brand-blue" size={36} />
          <span className="text-sm text-slate-400">Auditing exceptions...</span>
        </div>
      ) : (
        <ExceptionTable data={data} />
      )}
    </div>
  );
}
