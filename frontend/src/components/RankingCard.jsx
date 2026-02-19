import { useState } from 'react'

export default function RankingCard({ rank, headphone, score, contributions }) {
  const [isExpanded, setIsExpanded] = useState(false)

  const scorePercentage = Math.round(score * 100)

  return (
    <div className="card-base space-y-4">
      <div
        className="cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-start justify-between mb-4">
          <div>
            <p className="text-sm font-medium text-neutral-600">#{rank}</p>
            <h3 className="text-2xl font-bold text-neutral-900">
              {headphone.model || headphone.details?.name || `Headphone ${rank}`}
            </h3>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold text-neutral-900">{scorePercentage}%</p>
            <p className="text-xs text-neutral-600">Match Score</p>
          </div>
        </div>

        <div className="w-full bg-neutral-100 rounded-full h-2">
          <div
            className="bg-black h-2 rounded-full transition-all duration-300"
            style={{ width: `${scorePercentage}%` }}
          />
        </div>
      </div>

      {isExpanded && contributions && (
        <div className="pt-4 border-t border-neutral-100 space-y-4">
          <p className="text-sm font-medium text-neutral-600">Contribution Breakdown</p>
          <div className="space-y-3">
            {Object.entries(contributions).map(([criterion, value]) => {
              const contribution = Math.round(value * 100)
              return (
                <div key={criterion}>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm text-neutral-700 capitalize">
                      {criterion.replace(/_/g, ' ')}
                    </span>
                    <span className="text-sm font-medium text-neutral-900">
                      {contribution}%
                    </span>
                  </div>
                  <div className="w-full bg-neutral-100 rounded-full h-1.5">
                    <div
                      className="bg-neutral-400 h-1.5 rounded-full"
                      style={{ width: `${contribution}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="text-sm font-medium text-neutral-600 hover:text-neutral-900 transition-colors duration-200"
      >
        {isExpanded ? 'Hide Details' : 'Show Details'}
      </button>
    </div>
  )
}
