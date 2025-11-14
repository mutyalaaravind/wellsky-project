// Simple auth utility
export const getAuthToken = (): string => {
  const tokenStorage = localStorage.getItem('okta-token-storage')
  if (tokenStorage) {
    const tokenData = JSON.parse(tokenStorage)
    return tokenData.accessToken?.accessToken || ''
  }
  return ''
}