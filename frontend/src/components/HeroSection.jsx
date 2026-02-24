import { useState } from 'react'
import bgimg from '../assets/applle.png'

export default function HeroSection({ onStartClick }) {
  return (
    <section className="h-screen w-100vw flex flex-col items-center justify-center px-6 py-20 relative">
      <div 
        className="absolute inset-0 bg-contain bg-center bg-no-repeat opacity-40 scale-90"
        style={{ backgroundImage: `url(${bgimg})` }}
      ></div>
      <div className="absolute inset-0 bg-black/40"></div>
      
      <div className="max-w-5xl mx-auto text-center relative z-10">
        {/* Tag */}
        <div className="inline-block px-3 py-1 border border-white/30 rounded-full text-white/80 text-xs font-medium mb-8 tracking-wide">
          SMART DECISION SYSTEM
        </div>
        
        {/* Main heading */}
        <h1 className="text-5xl md:text-7xl font-light text-white mb-6 leading-tight tracking-tight">
          Find Your Perfect
          <span className="block font-normal">Headphones</span>
        </h1>
        
        <p className="text-lg md:text-xl text-white/90 mb-12 max-w-2xl mx-auto leading-relaxed">
          Make confident choices with our intelligent, transparent scoring system tailored to your use case.
        </p>

        {/* CTA Button */}
        <button
          onClick={onStartClick}
          className="group inline-flex items-center gap-2 px-8 py-3 bg-black/80 text-white text-base font-medium rounded-md hover:bg-black/90 transition-colors duration-200"
        >
          <span>Start Evaluation</span>
          <svg 
            className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>

        {/* Feature list */}
        <div className="grid grid-cols-3 gap-4 md:gap-8 mt-24 max-w-4xl mx-auto">
          <div className="text-center">
            <div className="w-10 h-10 border border-white/30 rounded-lg flex items-center justify-center mb-4 mx-auto">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-white font-medium mb-2 text-sm">Smart Scoring</h3>
            <p className="text-white/70 text-xs md:text-sm leading-relaxed">Use-case specific weights for accurate rankings</p>
          </div>

          <div className="text-center">
            <div className="w-10 h-10 border border-white/30 rounded-lg flex items-center justify-center mb-4 mx-auto">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-white font-medium mb-2 text-sm">Transparent</h3>
            <p className="text-white/70 text-xs md:text-sm leading-relaxed">See exactly why each headphone ranks where it does</p>
          </div>

          <div className="text-center">
            <div className="w-10 h-10 border border-white/30 rounded-lg flex items-center justify-center mb-4 mx-auto">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-white font-medium mb-2 text-sm">Value Focused</h3>
            <p className="text-white/70 text-xs md:text-sm leading-relaxed">Find the best performance per rupee spent</p>
          </div>
        </div>
      </div>
    </section>
  )
}
