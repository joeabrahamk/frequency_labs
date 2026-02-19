const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function evaluateDecision(payload) {
  try {
    const response = await fetch(`${API_BASE_URL}/evaluate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Evaluation error:', error)
    throw error
  }
}
