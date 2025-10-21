import React from 'react';

export default function Play() {
  const currentPage = 'play';

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
    </div>
    )
}
