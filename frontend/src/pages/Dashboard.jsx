import React from 'react';

export default function DentalDashboard() {
  const currentPage = 'dashboard'; // Track which page we're on

  // Mock data for cases
  const cases = [
    { id: 1, title: 'Case 1 Title', status: 'completed', statusLabel: 'C' },
    { id: 2, title: 'Case 2 Title', status: 'in-progress', statusLabel: 'IP' },
    { id: 3, title: 'Case 3 Title', status: 'on-hold', statusLabel: 'OH' },
    { id: 4, title: 'Case 4 Title', status: "completed", statusLabel: 'C' },
    { id: 5, title: 'Case 5 Title', status: null, statusLabel: null },
    { id: 6, title: 'Case 6 Title', status: null, statusLabel: null },
    { id: 7, title: 'Case 7 Title', status: null, statusLabel: null },
    { id: 8, title: 'Case 8 Title', status: null, statusLabel: null },
  ];

  const stats = [
    { label: 'Total', value: '8' },
    { label: 'Completed', value: '5' },
    { label: 'In Progress', value: '2' },
    { label: 'On Hold', value: '1' },
  ];

  const getStatusColor = (status) => {
    switch(status) {
      case 'completed': return 'bg-green-400';
      case 'in-progress': return 'bg-orange-400';
      case 'on-hold': return 'bg-yellow-400';
      default: return '';
    }
  };

  return (
    <div className="min-h-screen bg-[#98A1BC]">
      {/* Top Navigation */}
      <nav className="bg-[#555879] text-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-center gap-12 py-4">
            <a
              href="#"
              className={`text-xl text-[#F4EBD3] font-semibold hover:text-gray-300 px-4 py-2 rounded-lg transition-all ${
                currentPage === 'dashboard' ? 'border-2 border-[#F4EBD3] bg-[#555879]/50' : 'hover:border-2 hover:border-[#F4EBD3]/50'
              }`}
            >
              Dashboard
            </a>
            <a
              href="#"
              className={`text-xl text-[#F4EBD3] font-semibold hover:text-gray-300 px-4 py-2 rounded-lg transition-all ${
                currentPage === 'play' ? 'border-2 border-[#F4EBD3] bg-[#555879]/50' : 'hover:border-2 hover:border-[#F4EBD3]/50'
              }`}
            >
              Play
            </a>
            <a
              href="#"
              className={`text-xl text-[#F4EBD3] font-semibold hover:text-gray-300 px-4 py-2 rounded-lg transition-all ${
                currentPage === 'leaderboard' ? 'border-2 border-[#F4EBD3] bg-[#555879]/50' : 'hover:border-2 hover:border-[#F4EBD3]/50'
              }`}
            >
              Leaderboard
            </a>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-4 gap-6 mb-8">
          {stats.map((stat, idx) => (
            <div key={idx} className="bg-yellow-100 rounded-3xl p-8 text-center shadow-md">
              <h3 className="text-xl font-bold mb-4">{stat.label}</h3>
              <p className="text-6xl font-bold">{stat.value}</p>
            </div>
          ))}
        </div>

        {/* Search and Filter */}
        <div className="flex items-center gap-4 mb-6">
          <div className="flex-1 bg-yellow-100 rounded-2xl px-6 py-4 shadow-md">
            <input
              type="text"
              placeholder="Search cases..."
              className="w-full bg-transparent text-lg focus:outline-none placeholder-gray-600"
            />
          </div>
          <button className="bg-white rounded-2xl px-8 py-4 shadow-md flex items-center gap-2 font-semibold text-lg hover:bg-gray-50">
            <span className="text-xl">⏷</span>
            Filter
          </button>
        </div>

        {/* Cases Grid */}
        <div className="grid grid-cols-4 gap-6">
          {cases.map((case_) => (
            <div key={case_.id} className="bg-yellow-100 rounded-2xl shadow-md overflow-hidden hover:shadow-lg transition-shadow">
              <div className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="font-bold text-lg">{case_.title}</h3>
                  {case_.statusLabel && (
                    <span className={`${getStatusColor(case_.status)} px-3 py-1 rounded-md font-bold text-sm`}>
                      {case_.statusLabel}
                    </span>
                  )}
                </div>

                <div className="bg-white rounded-xl h-40 flex items-center justify-center">
                  <svg
                    className="w-24 h-24 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" strokeWidth="2"/>
                    <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor"/>
                    <path d="M21 15l-5-5L5 21" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
