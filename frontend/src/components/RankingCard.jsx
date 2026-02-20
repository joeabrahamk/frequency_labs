import { useState } from 'react'

// Map of common weight levels for reference
const WEIGHT_LEVELS = {
  'price': 'important',
  'latency': 'critical',
  'num_mics': 'critical',
  'battery_life': 'critical',
  'device_type': 'critical',
  'water_resistance': 'important',
  'driver_size': 'secondary'
}

const getWeightBadge = (spec) => {
  const level = WEIGHT_LEVELS[spec] || 'secondary'
  const colors = {
    critical: 'bg-red-50 text-red-700 border-red-200',
    important: 'bg-amber-50 text-amber-700 border-amber-200',
    secondary: 'bg-blue-50 text-blue-700 border-blue-200'
  }
  return {
    label: level.charAt(0).toUpperCase() + level.slice(1),
    classes: colors[level]
  }
}

export default function RankingCard({ 
  rank, 
  headphone, 
  score, 
  valueScore, 
  price, 
  contributions,
  viewMode = 'performance',
  isExpanded,
  setIsExpanded
}) {
  const scorePercentage = Math.round(score * 100)
  const isValueMode = viewMode === 'value'

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-neutral-200 hover:shadow-lg transition-all duration-200 flex flex-col h-full">
      {/* Rank Badge */}
      <div className="p-4 pb-0">
        <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm ${
          rank === 1 ? 'bg-yellow-100 text-yellow-700' :
          rank === 2 ? 'bg-neutral-100 text-neutral-600' :
          'bg-neutral-50 text-neutral-500'
        }`}>
          #{rank}
        </div>
      </div>

      {/* Headphone Name & Price */}
      <div className="px-6 pt-3 pb-4">
        <h3 className="text-xl font-bold text-neutral-900 mb-2 line-clamp-2 min-h-[3.5rem]">
          {headphone.model || headphone.details?.name || `Headphone ${rank}`}
        </h3>
        <p className="text-sm font-medium text-neutral-600">
          ₹{price?.toLocaleString('en-IN') || 'N/A'}
        </p>
      </div>

      {/* Scores Section */}
      <div className="px-6 pb-5 space-y-4">
        {/* Performance Score */}
        <div>
          <div className="flex items-baseline justify-between mb-2">
            <span className="text-xs font-medium text-neutral-500 uppercase tracking-wide">Performance</span>
            <span className={`text-2xl font-bold ${isValueMode ? 'text-neutral-300' : 'text-black'}`}>
              {scorePercentage}%
            </span>
          </div>
          <div className="w-full bg-neutral-100 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-300 ${
                isValueMode ? 'bg-neutral-300' : 'bg-black'
              }`}
              style={{ width: `${scorePercentage}%` }}
            />
          </div>
        </div>

        {/* Value Score */}
        {valueScore && (
          <div>
            <div className="flex items-baseline justify-between mb-2">
              <span className="text-xs font-medium text-neutral-500 uppercase tracking-wide">Value (performance/cost)</span>
              <span className={`text-2xl font-bold ${isValueMode ? 'text-green-600' : 'text-neutral-300'}`}>
                {valueScore.toFixed(1)}
              </span>
            </div>
            <div className="w-full bg-neutral-100 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-300 ${
                  isValueMode ? 'bg-green-500' : 'bg-neutral-300'
                }`}
                style={{ width: `${Math.min(100, (valueScore / 10) * 100)}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Expandable Details */}
      {isExpanded && contributions && (
        <div className="px-6 pb-5 border-t border-neutral-100 pt-5">
          <p className="text-xs font-semibold text-neutral-700 uppercase tracking-wide mb-4">Breakdown</p>
          <div className="space-y-3">
            {Object.entries(contributions)
              .sort((a, b) => b[1] - a[1])
              .map(([criterion, value]) => {
                const contribution = Math.round(value * 100)
                const isPrice = criterion === 'price'
                const weightBadge = getWeightBadge(criterion)
                return (
                  <div key={criterion}>
                    <div className="flex justify-between items-center mb-1.5">
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-neutral-600 capitalize">
                          {criterion.replace(/_/g, ' ')}
                          {isPrice && <span className="text-neutral-400 ml-1">(lower is better)</span>}
                        </span>
                        <span className={`text-xs px-2 py-0.5 rounded border ${weightBadge.classes}`}>
                          {weightBadge.label}
                        </span>
                      </div>
                      <span className="text-xs font-semibold text-neutral-900">
                        {contribution}%
                      </span>
                    </div>
                    <div className="w-full bg-neutral-100 rounded-full h-1.5">
                      <div
                        className="bg-neutral-500 h-1.5 rounded-full transition-all"
                        style={{ width: `${contribution}%` }}
                      />
                    </div>
                  </div>
                )
              })}
          </div>
        </div>
      )}

      {/* Toggle Button */}
      <div className="mt-auto px-6 pb-5">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full text-sm font-medium text-neutral-600 hover:text-black transition-colors py-2"
        >
          {isExpanded ? '↑ Hide Details' : '↓ Show Details'}
        </button>
      </div>
    </div>
  )
}
