import { useState } from 'react'

const USE_CASES = [
  { id: 'gaming', label: 'Gaming' },
  { id: 'gym', label: 'Gym' },
  { id: 'work_calls', label: 'Work Calls' },
  { id: 'travel', label: 'Travel' },
  { id: 'casual_music', label: 'Casual Music' },
]

export default function UseCaseSelector({ onUseCasesChange }) {
  const [selectedCases, setSelectedCases] = useState({})
  const [weights, setWeights] = useState({})

  const handleToggleCase = (caseId) => {
    setSelectedCases((prev) => {
      const updated = { ...prev }
      if (updated[caseId]) {
        delete updated[caseId]
        const newWeights = { ...weights }
        delete newWeights[caseId]
        setWeights(newWeights)
      } else {
        updated[caseId] = true
      }
      return updated
    })
  }

  const handleWeightChange = (caseId, value) => {
    setWeights((prev) => ({
      ...prev,
      [caseId]: Math.min(100, Math.max(0, parseInt(value) || 0)),
    }))
  }

  const handleApply = () => {
    const useCasesArray = Object.keys(selectedCases).map((caseId) => ({
      name: caseId,
      percentage: weights[caseId] || 100 / Object.keys(selectedCases).length,
    }))
    onUseCasesChange(useCasesArray)
  }

  const totalWeight = Object.values(weights).reduce((a, b) => a + b, 0)

  return (
    <section className="py-20 px-6 bg-neutral-50">
      <div className="max-w-3xl mx-auto">
        <h2 className="text-4xl font-bold text-neutral-900 mb-4">Select Your Use Cases</h2>
        <p className="text-lg text-neutral-600 mb-10">Choose one or more scenarios that matter to you.</p>

        <div className="space-y-4 mb-8">
          {USE_CASES.map((useCase) => (
            <div
              key={useCase.id}
              className={`p-4 rounded-lg border-2 transition-all duration-300 cursor-pointer ${
                selectedCases[useCase.id]
                  ? 'border-black bg-white'
                  : 'border-neutral-200 bg-white hover:border-neutral-300'
              }`}
              onClick={() => handleToggleCase(useCase.id)}
            >
              <div className="flex items-center justify-between">
                <label className="flex items-center gap-3 cursor-pointer flex-1">
                  <input
                    type="checkbox"
                    checked={selectedCases[useCase.id] || false}
                    onChange={() => {}}
                    className="w-5 h-5 rounded border-neutral-300 cursor-pointer"
                  />
                  <span className="text-lg font-medium">{useCase.label}</span>
                </label>

                {selectedCases[useCase.id] && (
                  <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      value={weights[useCase.id] || ''}
                      onChange={(e) => handleWeightChange(useCase.id, e.target.value)}
                      className="input-base w-20 text-center"
                      placeholder="Weight"
                    />
                    <span className="text-sm text-neutral-600">%</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="flex items-center justify-between mb-8">
          <p className={`text-sm font-medium ${totalWeight === 100 ? 'text-green-600' : 'text-neutral-600'}`}>
            Total Weight: {totalWeight}%
          </p>
        </div>

        <button onClick={handleApply} className="btn-primary w-full">
          Continue
        </button>
      </div>
    </section>
  )
}
