import { useState, useRef } from 'react'
import HeroSection from './components/HeroSection'
import UseCaseSelector from './components/UseCaseSelector'
import HeadphoneForm from './components/HeadphoneForm'
import ResultsSection from './components/ResultsSection'
import { evaluateDecision } from './services/api'

export default function App() {
  const [currentSection, setCurrentSection] = useState('hero')
  const [selectedUseCases, setSelectedUseCases] = useState([])
  const [results, setResults] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const resultsRef = useRef(null)

  const handleStartClick = () => {
    setCurrentSection('use-cases')
    setTimeout(() => {
      document.querySelector('[data-section="use-cases"]')?.scrollIntoView({ behavior: 'smooth' })
    }, 100)
  }

  const handleUseCasesChange = (useCases) => {
    setSelectedUseCases(useCases)
    setCurrentSection('headphones')
    setTimeout(() => {
      document.querySelector('[data-section="headphones"]')?.scrollIntoView({ behavior: 'smooth' })
    }, 100)
  }

  const handleEvaluate = async (payload) => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await evaluateDecision(payload)
      setResults(response)
      setCurrentSection('results')
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth' })
      }, 100)
    } catch (err) {
      setError(err.message || 'Failed to evaluate. Please check your input and try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-white">
      <HeroSection onStartClick={handleStartClick} />

      <div data-section="use-cases">
        {currentSection === 'use-cases' && (
          <UseCaseSelector onUseCasesChange={handleUseCasesChange} />
        )}
      </div>

      <div data-section="headphones">
        {currentSection === 'headphones' && (
          <HeadphoneForm
            useCases={selectedUseCases}
            onEvaluate={handleEvaluate}
            isLoading={isLoading}
          />
        )}
      </div>

      {error && (
        <section className="py-8 px-6 bg-red-50 border-b border-red-200">
          <div className="max-w-4xl mx-auto">
            <p className="text-red-800 font-medium">{error}</p>
          </div>
        </section>
      )}

      <div ref={resultsRef}>
        {currentSection === 'results' && (
          <ResultsSection results={results} useCases={selectedUseCases} />
        )}
      </div>
    </div>
  )
}
