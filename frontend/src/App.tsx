import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/layout/Layout';
import { Overview } from './pages/Overview';
import { LiveMonitor } from './pages/LiveMonitor';
import { AttackAnalysis } from './pages/AttackAnalysis';
import { NetworkIntelligence } from './pages/NetworkIntelligence';
import { Assets } from './pages/Assets';
import { ThreatIntelligence } from './pages/ThreatIntelligence';
import { Reports } from './pages/Reports';
import { Settings } from './pages/Settings';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 3000,
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Overview />} />
            <Route path="live" element={<LiveMonitor />} />
            <Route path="attacks" element={<AttackAnalysis />} />
            <Route path="network" element={<NetworkIntelligence />} />
            <Route path="assets" element={<Assets />} />
            <Route path="intelligence" element={<ThreatIntelligence />} />
            <Route path="reports" element={<Reports />} />
            <Route path="settings" element={<Settings />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

export default App;
