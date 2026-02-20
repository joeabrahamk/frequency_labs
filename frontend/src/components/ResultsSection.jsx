import { useState } from 'react'
import RankingCard from './RankingCard'

export default function ResultsSection({ results, useCases }) {
  const [activeTab, setActiveTab] = useState('performance')
  const [isExpanded, setIsExpanded] = useState(false)
  
  if (!results) {
    return null
  }

  const displayedRankings = activeTab === 'performance' 
    ? results.ranked_headphones 
    : results.value_ranked_headphones

  return (
    <section className="py-20 px-6 bg-neutral-50">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-10">
          <h2 className="text-4xl font-bold text-neutral-900 mb-3">Your Rankings</h2>
          <p className="text-lg text-neutral-600">
            Evaluated for: <span className="font-medium">{useCases.map(u => u.name.replace('_', ' ')).join(', ')}</span>
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-2 mb-8 border-b border-neutral-200">
          <button
            onClick={() => setActiveTab('performance')}
            className={`px-6 py-3 font-medium transition-all duration-200 border-b-2 ${
              activeTab === 'performance'
                ? 'border-black text-black'
                : 'border-transparent text-neutral-500 hover:text-neutral-700'
            }`}
          >
            Performance Ranking
          </button>
          <button
            onClick={() => setActiveTab('value')}
            className={`px-6 py-3 font-medium transition-all duration-200 border-b-2 ${
              activeTab === 'value'
                ? 'border-black text-black'
                : 'border-transparent text-neutral-500 hover:text-neutral-700'
            }`}
          >
            Value Ranking
          </button>
        </div>

        {/* Tab Description */}
        <div className="mb-8 px-1">
          {activeTab === 'performance' ? (
            <p className="text-sm text-neutral-600">
              Ranked by best specifications for your selected use cases
            </p>
          ) : (
            <p className="text-sm text-neutral-600">
              Ranked by best performance per rupee spent (value for money)
            </p>
          )}
        </div>

        {/* Column Grid Display */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {displayedRankings && displayedRankings.length > 0 ? (
            displayedRankings.map((hp, index) => (
              <RankingCard
                key={`${activeTab}-${index}`}
                rank={index + 1}
                headphone={hp}
                score={hp.score}
                valueScore={hp.value_score}
                price={hp.price}
                contributions={hp.contributions}
                viewMode={activeTab}
                isExpanded={isExpanded}
                setIsExpanded={setIsExpanded}
              />
            ))
          ) : (
            <div className="col-span-full bg-white rounded-2xl shadow-sm border border-neutral-200 text-center py-16">
              <p className="text-neutral-500">No results available</p>
            </div>
          )}
        </div>

        {/* Explanation */}
        {results.explanation && (
          <div className="mt-12 bg-neutral-100 rounded-2xl p-6 border border-neutral-200">
            <p className="text-sm font-semibold text-neutral-700 mb-2">How Rankings Work</p>
            <p className="text-neutral-700 leading-relaxed">
              {results.explanation.reasoning}
            </p>
          </div>
        )}
      </div>
    </section>
  )
}
