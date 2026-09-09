import { useEffect } from 'react';

const DEFAULT_TIMEOUT_MS = 5000;

const useAutoDismiss = (value, clearFn, timeoutMs = DEFAULT_TIMEOUT_MS) => {
  useEffect(() => {
    if (!value) return undefined;

    const timer = setTimeout(() => {
      clearFn('');
    }, timeoutMs);

    return () => clearTimeout(timer);
  }, [value, clearFn, timeoutMs]);
};

export default useAutoDismiss;
