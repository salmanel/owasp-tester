import { create } from 'zustand';

export type TestMode = 'soft' | 'advanced';

export interface VulnerabilityResult {
  id: string;
  url: string;
  vulnerability: string;
  payload?: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  timestamp: string;
}

interface AppState {
  mode: TestMode;
  sidebarCollapsed: boolean;
  results: VulnerabilityResult[];
  isTestRunning: boolean;
  setMode: (mode: TestMode) => void;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  addResults: (results: VulnerabilityResult[]) => void;
  clearResults: () => void;
  setTestRunning: (running: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  mode: 'soft',
  sidebarCollapsed: false,
  results: [],
  isTestRunning: false,
  setMode: (mode) => set({ mode }),
  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
  setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
  addResults: (results) => set((state) => ({ results: [...state.results, ...results] })),
  clearResults: () => set({ results: [] }),
  setTestRunning: (running) => set({ isTestRunning: running }),
}));
