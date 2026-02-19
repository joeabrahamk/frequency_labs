import RankingCard from './RankingCard'

export default function ResultsSection({ results, useCases }) {
  if (!results) {
    return null
  }

  return (
    <section className="py-20 px-6 bg-neutral-50">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-4xl font-bold text-neutral-900 mb-2">Your Results</h2>
        <p className="text-lg text-neutral-600 mb-10">
          Ranked for: <span className="font-medium">{useCases.map(u => u.name).join(', ')}</span>
        </p>

        <div className="space-y-6 mb-12">
          {results.ranked_headphones && results.ranked_headphones.length > 0 ? (
            results.ranked_headphones.map((hp, index) => (
              <RankingCard
                key={index}
                rank={index + 1}
                headphone={hp}
                score={hp.score}
                contributions={hp.contributions}
              />
            ))
          ) : (
            <div className="card-base text-center py-12">
              <p className="text-neutral-600">No results available</p>
            </div>
          )}
        </div>

        {results.explanation && (
          <div className="card-base bg-neutral-100 border-neutral-200">
            <p className="text-sm font-medium text-neutral-600 mb-3">How This Works</p>
            <p className="text-neutral-800 leading-relaxed">
              {results.explanation.reasoning ||
                'Each headphone was evaluated against your selected use cases using transparent, rule-based scoring. Scores are normalized and weighted by your use case preferences.'}
            </p>
          </div>
        )}
      </div>
    </section>
  )
}
