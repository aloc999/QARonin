export interface FetchWithRetryOptions {
  maxAttempts?: number;
  initialDelayMs?: number;
  backoffFactor?: number;
}

export async function fetchWithRetry(
  url: string,
  options: RequestInit = {},
  retryOptions: FetchWithRetryOptions = {}
): Promise<Response> {
  const { maxAttempts = 5, initialDelayMs = 200, backoffFactor = 2 } = retryOptions;
  let lastResponse: Response | null = null;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    const response = await fetch(url, options);
    if (response.ok) return response;
    lastResponse = response;

    if (attempt < maxAttempts) {
      await new Promise((resolve) => setTimeout(resolve, initialDelayMs * Math.pow(backoffFactor, attempt - 1)));
    }
  }

  throw new Error(`fetchWithRetry: all ${maxAttempts} attempts failed, last status ${lastResponse?.status}`);
}
