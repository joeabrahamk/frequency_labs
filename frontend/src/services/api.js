const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function pingBackend() {
  try {
    await fetch(`${API_BASE_URL}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
  } catch (error) {
    // Silently fail - this is just a keep-alive ping
    console.debug('Backend ping failed (expected on cold start)')
  }
}

export async function evaluateDecision(payload) {
  try {
    const endpoint = payload?.amazon_urls ? '/evaluate-amazon' : '/evaluate'
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      let detail = ''
      try {
        const errData = await response.json()
        detail = errData?.detail || ''
      } catch {
        // ignore JSON parse errors for non-JSON error responses
      }
      throw new Error(detail ? `API Error: ${response.status} - ${detail}` : `API Error: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Evaluation error:', error)
    throw error
  }
}
