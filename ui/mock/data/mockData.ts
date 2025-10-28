// Define types for the mock data
export interface LogEntry {
  type: "log";
  content: string;
}

export interface ScreenshotEntry {
  type: "screenshot";
  content: string;
}

export type MockDataEntry = LogEntry | ScreenshotEntry;

// Mock data for E2E testing scenarios
export const mockData: MockDataEntry[] = [
  {
    "type": "screenshot",
    "content": "step1_goto.png"
  },
  {
    "type": "log",
    "content": "Screenshot taken: step1_goto"
  },
  {
    "type": "log",
    "content": "Highlighted username input"
  },
  {
    "type": "log",
    "content": "Filled username"
  },
  {
    "type": "log",
    "content": "Highlighted password input"
  },
  {
    "type": "log",
    "content": "Filled password"
  },
  {
    "type": "screenshot",
    "content": "step2_filled.png"
  },
  {
    "type": "log",
    "content": "Screenshot taken: step2_filled"
  },
  {
    "type": "log",
    "content": "Highlighted login button"
  },
  {
    "type": "log",
    "content": "Clicked login button"
  },
  {
    "type": "screenshot",
    "content": "step3_loggedin.png"
  },
  {
    "type": "log",
    "content": "Screenshot taken: step3_loggedin"
  },
  {
    "type": "log",
    "content": "Products text is visible"
  }
];

// Helper functions
export function getEntriesByType(type: "log" | "screenshot"): MockDataEntry[] {
  return mockData.filter(entry => entry.type === type);
}

export function getMockDataAsJSON(): string {
  return JSON.stringify(mockData, null, 2);
}

export function getTotalEntries(): number {
  return mockData.length;
}

export function getLogCount(): number {
  return getEntriesByType("log").length;
}

export function getScreenshotCount(): number {
  return getEntriesByType("screenshot").length;
}
