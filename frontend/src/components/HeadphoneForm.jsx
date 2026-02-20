import { useState } from 'react'
import HeadphoneCard from './HeadphoneCard'

export default function HeadphoneForm({ useCases, onEvaluate, isLoading }) {
  const [headphones, setHeadphones] = useState([])

  const addHeadphone = () => {
    setHeadphones((prev) => [
      ...prev,
      {
        id: Date.now(),
        price: '',
        battery_life: '',
        latency: '',
        num_mics: 2,
        device_type: 'Wireless Earbuds',
        water_resistance: 'IPX4',
      },
    ])
  }

  const removeHeadphone = (id) => {
    setHeadphones((prev) => prev.filter((h) => h.id !== id))
  }

  const updateHeadphone = (id, field, value) => {
    setHeadphones((prev) =>
      prev.map((h) =>
        h.id === id
          ? { ...h, [field]: field === 'id' ? h.id : value }
          : h
      )
    )
  }

  const handleEvaluate = () => {
    const payload = {
      headphones: headphones.map(({ id, ...rest }) => rest),
      use_cases: useCases,
    }
    onEvaluate(payload)
  }

  const isFormValid = headphones.length > 0

  return (
    <section className="py-20 px-6 bg-white">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-4xl font-bold text-neutral-900 mb-4">Add Headphones</h2>
        <p className="text-lg text-neutral-600 mb-12">
          Input the specifications for each headphone model you want to compare.
        </p>

        <div className="space-y-6 mb-10">
          {headphones.map((headphone) => (
            <HeadphoneCard
              key={headphone.id}
              headphone={headphone}
              onUpdate={updateHeadphone}
              onRemove={removeHeadphone}
            />
          ))}
        </div>

        <button onClick={addHeadphone} className="btn-secondary mb-10 w-full">
          + Add Headphone
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
