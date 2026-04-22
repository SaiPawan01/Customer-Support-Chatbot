import React from 'react'
import { CheckCircle, ArrowRight } from 'lucide-react'

function Benefits(){
    return <>
    {/* Benefits Section */}
      <section id="benefits" className="py-20 px-4 sm:px-6 lg:px-8 bg-slate-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold text-white mb-6">Why Choose SupportBot AI?</h2>
              <ul className="space-y-4">
                {[
                  "Reduce support costs by up to 70%",
                  "Improve customer satisfaction scores",
                  "24/7 instant support availability",
                  "Seamless escalation workflow",
                  "Easy integration with existing systems",
                  "Continuous AI model improvement"
                ].map((benefit) => (
                  <li key={benefit} className="flex items-center gap-3 text-slate-300">
                    <CheckCircle className="w-5 h-5 text-green-400 shrink-0" />
                    {benefit}
                  </li>
                ))}

              </ul>
            </div>
            <div className="bg-linear-to-br from-blue-600/20 to-cyan-600/20 rounded-xl p-8 border border-blue-500/30">
              <div className="space-y-4">
                <div className="bg-slate-700/50 rounded-lg p-4">
                  <p className="text-slate-300 text-sm">User Query</p>
                  <p className="text-white font-semibold">How do I reset my password?</p>
                </div>
                <div className="flex justify-center">
                  <ArrowRight className="w-6 h-6 text-blue-400 rotate-90" />
                </div>
                <div className="bg-slate-700/50 rounded-lg p-4">
                  <p className="text-slate-300 text-sm">AI Processing</p>
                  <p className="text-white font-semibold">Semantic Search + RAG Pipeline</p>
                </div>
                <div className="flex justify-center">
                  <ArrowRight className="w-6 h-6 text-blue-400 rotate-90" />
                </div>
                <div className="bg-green-600/20 border border-green-500/50 rounded-lg p-4">
                  <p className="text-slate-300 text-sm">Instant Response</p>
                  <p className="text-white font-semibold">Step-by-step guide provided (95% confidence)</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
}

export default Benefits