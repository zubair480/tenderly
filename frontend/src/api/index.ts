import { realApi } from './client';
import { mockApi } from './mock';

// Keep mock mode safe by default so the app remains demoable before API deployment.
export const usingMockApi = import.meta.env.VITE_USE_MOCK !== 'false';
export const tenderlyApi = usingMockApi ? mockApi : realApi;

export type * from './types';
