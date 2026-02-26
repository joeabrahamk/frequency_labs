import { useState } from 'react'

const createUrlEntry = () => ({
  id: Date.now() + Math.random(),
  url: '',
})

const isValidAmazonUrl = (value) => {
  if (!value || typeof value !== 'string') {
    return false
  }

  try {
    const parsed = new URL(value.trim())
    const hostname = parsed.hostname.toLowerCase()
    return hostname.includes('amazon.') || hostname.startsWith('amzn.')
  } catch (error) {
    return false
  }
}

export default function AmazonUrlForm({ useCases, onEvaluate, isLoading, modeToggle }) {
  const [urls, setUrls] = useState([createUrlEntry()])

  const addUrl = () => {
    setUrls((prev) => [...prev, createUrlEntry()])
  }

  const removeUrl = (id) => {
    setUrls((prev) => prev.filter((entry) => entry.id !== id))
  }

  const updateUrl = (id, value) => {
    setUrls((prev) =>
      prev.map((entry) => (entry.id === id ? { ...entry, url: value } : entry))
    )
  }

  const getUrlError = (value) => {
    if (!value) {
      return 'Please add an Amazon product link.'
    }
    if (!isValidAmazonUrl(value)) {
      return 'Enter a valid Amazon product URL.'
    }
    return ''
  }

  const isFormValid = urls.length > 0 && urls.every((entry) => isValidAmazonUrl(entry.url))

  const handleEvaluate = () => {
    const payload = {
      amazon_urls: urls.map((entry) => entry.url.trim()),
      use_cases: useCases,
    }
    onEvaluate(payload)
  }

  return (
    <section className="py-20 px-6 bg-white">
      <div className="max-w-4xl mx-auto">
        {modeToggle}
        <h2 className="text-4xl font-bold text-neutral-900 mb-4">Compare from Amazon</h2>
        <p className="text-lg text-neutral-600 mb-12">
          Paste Amazon product links and we will extract the specs for you.
        </p>

        <div className="space-y-6 mb-10">
          {urls.map((entry, index) => {
            const errorText = getUrlError(entry.url)
            return (
              <div key={entry.id} className="card-base space-y-3">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <label className="input-label">Amazon URL {index + 1}</label>
                    <input
                      type="url"
                      placeholder="https://www.amazon.in/dp/..."
                      value={entry.url}
                      onChange={(event) => updateUrl(entry.id, event.target.value)}
                      className="input-base"
                    />
                    {errorText && (
                      <p className="mt-2 text-sm text-red-600">{errorText}</p>
                    )}
                  </div>
                  {urls.length > 1 && (
                    <button
                      onClick={() => removeUrl(entry.id)}
                      className="text-red-600 hover:text-red-800 font-medium text-sm mt-8"
                    >
                      Remove
                    </button>
                  )}
                </div>
              </div>
            )
          })}
        </div>

        <button onClick={addUrl} className="btn-secondary mb-10 w-full">
          + Add Another URL
        </button>

        <button
          onClick={handleEvaluate}
          disabled={!isFormValid || isLoading}
          className="btn-primary w-full text-lg"
        >
          {isLoading ? 'Evaluating...' : 'Evaluate'}
        </button>
      </div>
    </section>
  )
}
