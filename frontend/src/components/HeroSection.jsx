import { useState } from 'react'
import bgimg from '../assets/applle.png'

export default function HeroSection({ onStartClick }) {
  return (
    <section className="min-h-screen w-100vw flex flex-col items-center justify-center px-6 py-20 text-center relative">
      <div 
        className="absolute inset-0 bg-contain bg-center bg-no-repeat opacity-50"
        style={{ backgroundImage: `url(${bgimg})` }}
      ></div>
      <div className="absolute inset-0 bg-black/40"></div>
      <div className="max-w-2xl mx-auto relative z-10">
        <h1 className="text-6xl md:text-7xl font-bold text-neutral-900 mb-6 leading-tight">
          Find the Right
          <span className="block">Headphones for You</span>
        </h1>
        
        <p className="text-xl text-white mb-12 leading-relaxed">
          Our intelligent decision system helps you choose the perfect headphones based on your use cases and requirements. Transparent, rule-based, and explainable.
        </p>

        <button
          onClick={onStartClick}
          className="btn-primary text-lg"
        >
          Start Evaluation
        </button>
      </div>
    </section>
  )
}
