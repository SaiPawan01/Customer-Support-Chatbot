import React from 'react'

import features from '../../data/features.jsx'

function Features(){
    return <>
    {/* Features Section */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">Powerful Features</h2>
            <p className="text-lg text-slate-400 max-w-2xl mx-auto">
              Everything you need to provide exceptional customer support powered by AI
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="p-8 rounded-xl border transition-all duration-300 bg-slate-800/50 border-slate-700 hover:border-blue-500 hover:bg-blue-600/20 hover:shadow-lg hover:shadow-blue-500/20 hover:scale-105 transform"
              >
                <div className="text-blue-400 mb-4">{feature.icon}</div>
                <h3 className="text-xl font-bold text-white mb-3">{feature.title}</h3>
                <p className="text-slate-400">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
}

export default Features