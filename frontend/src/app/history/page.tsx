'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { History, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import HistoryList from '@/components/history/HistoryList';
import HistoryFilters from '@/components/history/HistoryFilters';
import { InvestigationSummary } from '@/types/graph';
import { getHistory, HistoryFilters as HistoryFiltersType } from '@/lib/api';

const PAGE_SIZE = 20;

export default function HistoryPage() {
  // State
  const [investigations, setInvestigations] = useState<InvestigationSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  // Filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStatuses, setSelectedStatuses] = useState<('completed' | 'failed' | 'running')[]>([]);
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');

  // Load investigations
  const loadInvestigations = useCallback(
    async (pageNum: number = 1, append: boolean = false) => {
      if (pageNum === 1) {
        setLoading(true);
      } else {
        setLoadingMore(true);
      }
      setError(null);

      try {
        const filters: HistoryFiltersType = {
          page: pageNum,
          limit: PAGE_SIZE,
        };

        if (searchQuery) filters.search = searchQuery;
        if (selectedStatuses.length > 0) filters.status = selectedStatuses;
        if (startDate) filters.startDate = startDate;
        if (endDate) filters.endDate = endDate;

        const data = await getHistory(filters);

        if (append) {
          setInvestigations((prev) => [...prev, ...data.items]);
        } else {
          setInvestigations(data.items);
        }
        setPage(data.page);
        setTotalPages(data.totalPages);
        setTotal(data.total);
      } catch (err) {
        console.error('Failed to load history:', err);
        // Use mock data for development
        const mockData: InvestigationSummary[] = [
          {
            id: '1',
            query: 'APT28 ransomware campaign analysis',
            status: 'completed',
            createdAt: new Date(Date.now() - 3600000).toISOString(),
            duration_ms: 45000,
            toolsUsed: 5,
          },
          {
            id: '2',
            query: 'Dark web marketplace vendor investigation',
            status: 'completed',
            createdAt: new Date(Date.now() - 7200000).toISOString(),
            duration_ms: 32000,
            toolsUsed: 3,
          },
          {
            id: '3',
            query: 'CVE-2024-1234 exploitation research',
            status: 'failed',
            createdAt: new Date(Date.now() - 86400000).toISOString(),
            duration_ms: 12000,
            toolsUsed: 2,
          },
          {
            id: '4',
            query: 'Threat actor infrastructure mapping',
            status: 'running',
            createdAt: new Date(Date.now() - 300000).toISOString(),
            toolsUsed: 4,
          },
          {
            id: '5',
            query: 'Malware family attribution analysis',
            status: 'completed',
            createdAt: new Date(Date.now() - 172800000).toISOString(),
            duration_ms: 67000,
            toolsUsed: 6,
          },
          {
            id: '6',
            query: 'Cryptocurrency wallet tracking',
            status: 'completed',
            createdAt: new Date(Date.now() - 259200000).toISOString(),
            duration_ms: 89000,
            toolsUsed: 4,
          },
          {
            id: '7',
            query: 'Phishing campaign infrastructure',
            status: 'completed',
            createdAt: new Date(Date.now() - 345600000).toISOString(),
            duration_ms: 54000,
            toolsUsed: 5,
          },
          {
            id: '8',
            query: 'Data breach source identification',
            status: 'failed',
            createdAt: new Date(Date.now() - 432000000).toISOString(),
            duration_ms: 8000,
            toolsUsed: 1,
          },
        ];

        // Apply mock filtering
        let filtered = mockData;

        if (searchQuery) {
          const query = searchQuery.toLowerCase();
          filtered = filtered.filter((inv) => inv.query.toLowerCase().includes(query));
        }

        if (selectedStatuses.length > 0) {
          filtered = filtered.filter((inv) => selectedStatuses.includes(inv.status));
        }

        setInvestigations(append ? [...investigations, ...filtered] : filtered);
        setPage(1);
        setTotalPages(1);
        setTotal(filtered.length);
      } finally {
        setLoading(false);
        setLoadingMore(false);
      }
    },
    [searchQuery, selectedStatuses, startDate, endDate, investigations]
  );

  // Initial load and filter changes
  useEffect(() => {
    loadInvestigations(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchQuery, selectedStatuses, startDate, endDate]);

  const handleLoadMore = () => {
    if (page < totalPages && !loadingMore) {
      loadInvestigations(page + 1, true);
    }
  };

  const handleRefresh = () => {
    loadInvestigations(1);
  };

  const handleClearFilters = () => {
    setSearchQuery('');
    setSelectedStatuses([]);
    setStartDate('');
    setEndDate('');
  };

  const hasActiveFilters = searchQuery || selectedStatuses.length > 0 || startDate || endDate;

  return (
    <div className="min-h-screen bg-slate-950 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <History className="h-7 w-7 text-blue-500" />
            <div>
              <h1 className="text-2xl font-bold text-slate-100">Investigation History</h1>
              <p className="text-slate-400">Browse and search past investigations</p>
            </div>
          </div>
          <Button
            variant="outline"
            onClick={handleRefresh}
            disabled={loading}
            className="border-slate-700 text-slate-300 hover:bg-slate-800"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {/* Filters */}
        <HistoryFilters
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          selectedStatuses={selectedStatuses}
          onStatusChange={setSelectedStatuses}
          startDate={startDate}
          onStartDateChange={setStartDate}
          endDate={endDate}
          onEndDateChange={setEndDate}
          onClearFilters={handleClearFilters}
          hasActiveFilters={hasActiveFilters}
        />

        {/* Results Summary */}
        {!loading && (
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-slate-400">
              {total === 0 ? (
                'No investigations found'
              ) : (
                <>
                  Showing <span className="text-slate-200">{investigations.length}</span> of{' '}
                  <span className="text-slate-200">{total}</span> investigations
                </>
              )}
            </p>
          </div>
        )}

        {/* Investigation List */}
        <HistoryList
          investigations={investigations}
          loading={loading}
          error={error}
          hasMore={page < totalPages}
          loadingMore={loadingMore}
          onLoadMore={handleLoadMore}
          onRetry={handleRefresh}
        />
      </div>
    </div>
  );
}
