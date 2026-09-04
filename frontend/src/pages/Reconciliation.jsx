import React, { useEffect, useState } from 'react';
import TransactionTable from '../components/TransactionTable';
import { api } from '../services/api';
import { Loader2, Search, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';

export default function Reconciliation() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await api.getResults();
      setData(Array.isArray(res) ? res : []);
    } catch (err) {
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const filteredData = data.filter((row) => {
    const term = searchTerm.toLowerCase();
    const vendor = (row.ledger_vendor || row.vendor || '').toLowerCase();
    const bankVendor = (row.bank_vendor || '').toLowerCase();
    const txnId = (row.transaction_id || row.id || '').toLowerCase();
    const matchesSearch = vendor.includes(term) || bankVendor.includes(term) || txnId.includes(term);

    if (statusFilter === 'ALL') return matchesSearch;
    if (statusFilter === 'MATCHED') return matchesSearch && (row.status === 'MATCHED' || row.status === 'FUZZY_MATCHED');
    if (statusFilter === 'EXCEPTIONS') return matchesSearch && row.status !== 'MATCHED' && row.status !== 'FUZZY_MATCHED';
    return matchesSearch && row.status === statusFilter;
  });

  const matchedCount = data.filter(r => r.status === 'MATCHED' || r.status === 'FUZZY_MATCHED').length;
  const exceptionCount = data.length - matchedCount;

  return (
    <div className="space-y-6">
      {/* Top Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-dark-800 p-6 rounded-xl border border-dark-700 shadow-lg">
        <div>
          <h2 className="text-xl font-bold text-white">Reconciliation Hub</h2>
          <p className="text-sm text-slate-400 mt-1">
            Displaying {filteredData.length} of {data.length} transactions.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 text-slate-400" size={16} />
            <input 
              type="text" 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search vendor or ID..." 
              className="bg-dark-900 border border-dark-700 rounded-lg pl-9 pr-4 py-2 text-sm text-white focus:border-brand-blue outline-none placeholder:text-slate-500 w-52"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-dark-900 border border-dark-700 rounded-lg px-3 py-2 text-sm text-white focus:border-brand-blue outline-none"
          >
            <option value="ALL">All Statuses</option>
            <option value="MATCHED">Matched Only</option>
            <option value="EXCEPTIONS">Exceptions Only</option>
            <option value="AMOUNT_MISMATCH">Amount Mismatch</option>
            <option value="DATE_MISMATCH">Date Mismatch</option>
            <option value="MISSING_BANK_RECORD">Missing Bank</option>
            <option value="DUPLICATE">Duplicate</option>
            <option value="UNRESOLVED">Unresolved</option>
          </select>

          <button
            onClick={fetchData}
            className="p-2 bg-dark-700 hover:bg-dark-600 text-slate-300 rounded-lg border border-dark-600 transition-colors"
            title="Refresh transactions"
          >
            <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* Summary Chips */}
      <div className="flex gap-4">
        <div className="flex items-center gap-2 bg-dark-800 px-4 py-2 rounded-lg border border-dark-700 text-sm">
          <CheckCircle2 size={16} className="text-green-400" />
          <span className="text-slate-400">Total Matched:</span>
          <strong className="text-white">{matchedCount}</strong>
        </div>
        <div className="flex items-center gap-2 bg-dark-800 px-4 py-2 rounded-lg border border-dark-700 text-sm">
          <AlertCircle size={16} className="text-orange-400" />
          <span className="text-slate-400">Total Exceptions:</span>
          <strong className="text-white">{exceptionCount}</strong>
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex flex-col items-center justify-center p-16 space-y-3 bg-dark-800 rounded-xl border border-dark-700">
          <Loader2 className="animate-spin text-brand-blue" size={36} />
          <span className="text-sm text-slate-400">Loading reconciliation results...</span>
        </div>
      ) : (
        <TransactionTable data={filteredData} />
      )}
    </div>
  );
}
