/** @returns {string} API base URL (no trailing slash) */
export function getApiBase() {
  const raw = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  return raw.replace(/\/$/, '');
}
