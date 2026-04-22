import React from 'react';

function StatsSection() {
    const stats = [
        { number: "90%", label: "Query Resolution Rate" },
        { number: "24/7", label: "Availability" },
        { number: "<2sec", label: "Average Response Time" },
        { number: "99.9%", label: "Uptime SLA" }
    ];

    return <>
        {/* Stats Section */}
        <section className="py-12 px-4 sm:px-6 lg:px-8 border-y border-slate-700/50">
            <div className="max-w-7xl mx-auto">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                    {stats.map((stat) => (
                        <div key={stat.label} className="text-center">
                            <div className="text-3xl md:text-4xl font-bold text-blue-400 mb-2">{stat.number}</div>
                            <div className="text-slate-400">{stat.label}</div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    </>
}

export default StatsSection