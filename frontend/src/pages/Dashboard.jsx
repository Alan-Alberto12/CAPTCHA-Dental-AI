import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { API_URL } from '../config';


export default function Dashboard() {
  const navigate = useNavigate();

  const [completedSessions, setCompletedSessions] = useState([]);
  const [hasInProgressSession, setHasInProgressSession] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSession, setSelectedSession] = useState(null);
  const [questionOverviewCount, setQuestionOverviewCount] = useState(0);


  //fetch data on mount
  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    try {
      //fetch both completed_sessions and current_session endpoints
      const [completedCase, currentCase] = await Promise.all([
        fetch(`${API_URL}/auth/sessions/completed`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API_URL}/auth/sessions/current`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      if(completedCase.ok) {
        const completedData = await completedCase.json();
        setCompletedSessions(completedData);
      }
      
      if(currentCase.ok) {
        const currentData = await currentCase.json();
        setHasInProgressSession(currentData !== null);
      }
    } catch (error) {
      console.error('Error fetching dashboard cases:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const sessionOverviewDisplay = async (sessionId) => {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_URL}/auth/sessions/${sessionId}/overview`, {
      headers: {'Authorization': `Bearer ${token}` }
    })
    if(response.ok) {
      setQuestionOverviewCount(0)
      setSelectedSession(await response.json())
    }
  }
  
   //Search bar functionality - search by title or session id
  const filteredCases = completedSessions.filter(session => {
    const searchLower = searchTerm.toLowerCase();
    const titleMatch = session.title?.toLowerCase().includes(searchLower);
    const idMatch = `Session ${session.session_id}`.toLowerCase().includes(searchLower);
    return titleMatch || idMatch;
  });
 
  if (selectedSession) {
    const currentQuestion = selectedSession.questions[questionOverviewCount]
    const selectedCount = currentQuestion.images.filter(img => img.selected).length

    return (
      <div className="min-h-screen bg-[#98A1BC] pb-8">
        <div className="mx-auto w-full max-w-6xl px-3 md:px-4 lg:px-8 pt-6">

          {/* Back button */}
          <button
            onClick={() => setSelectedSession(null)}
            className="text-[#F5EEDC] text-md hover:underline mb-4 inline-block"
          >
            ← Back to Dashboard
          </button>

          {/* Question Prompt */}
          <div className="mb-3 rounded-lg bg-[#525470] px-6 py-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[#F5EEDC] text-sm opacity-80">
                Question {questionOverviewCount + 1} of {selectedSession.questions.length}
              </span>
            </div>
            <h1 className="text-xl md:text-xl font-semibold text-[#F5EEDC]">
              {currentQuestion.question_text}
            </h1>
          </div>

          {/* Instructions */}
          <div className="mb-4 bg-white/10 rounded-md px-4 py-2">
            <p className="text-[#F5EEDC] text-sm">
              Selected: {selectedCount}
            </p>
          </div>

          {/* Image grid (2x2) — only the 4 images for this question */}
          <div className="grid grid-cols-2 gap-4 mb-6 max-w-xl mx-auto">
            {currentQuestion.images.map((image) => (
              <div
                key={image.id}
                className={`
                  relative rounded-lg overflow-hidden
                  ${image.selected
                    ? 'ring-4 ring-[#F5EEDC] ring-offset-2 ring-offset-[#98A1BC]'
                    : 'ring-2 ring-[#525470]'
                  }
                `}
              >
                <img
                  src={image.image_url}
                  alt={image.filename}
                  className="w-full h-full object-contain"
                />
                {image.selected && (
                  <div className="absolute inset-0 bg-[#F5EEDC]/20 flex items-center justify-center">
                    <div className="bg-[#525470] text-[#F5EEDC] rounded-full w-12 h-12 flex items-center justify-center text-2xl font-bold">
                      ✓
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 max-w-lg mx-auto">
          <button
            onClick={() => setQuestionOverviewCount(i => Math.max(0, i - 1))}
            className="rounded-lg border-2 border-[#525470] px-4 py-3 font-medium text-[#F5EEDC] hover:bg-[#525470]/30"
          >
            ← Previous
          </button>
          <button
            disabled
            className="rounded-lg px-4 py-3 font-medium bg-gray-400 text-gray-200 cursor-not-allowed"
          >
            Already Submitted
          </button>
          <button
            onClick={() => setQuestionOverviewCount(i => Math.min(selectedSession.questions.length - 1, i + 1))}
            className="rounded-lg border-2 border-[#525470] px-4 py-3 font-medium text-[#F5EEDC] hover:bg-[#525470]/30"
          >
            Next →
          </button>
        </div>

        {/* Navigation Dots */}
        <div className="mt-8 flex justify-center gap-2">
          {selectedSession.questions.map((q, idx) => (
            <button
              key={q.id}
              onClick={() => setQuestionOverviewCount(idx)}
              className={`w-3 h-3 rounded-full transition-all ${
                idx === questionOverviewCount ? 'bg-[#F5EEDC] w-8' : 'bg-[#525470]'
              }`}
            />
          ))}
        </div>

      </div>
    </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#98A1BC] pb-20 md:pb-6">
      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        
        {/* In-Progress Warning Banner */}
        {hasInProgressSession && (
          <Link 
            to="/play" 
            className="block mb-6 text-center text-red-600 font-bold text-lg hover:text-red-700 hover:underline cursor-pointer"
          >
            You currently have 1 session In Progress. To complete it, please redirect to the Play tab.
          </Link>
        )}

        {/*stat card and searchbar */}
        <div className="flex items-center gap-6 mb-8">
          {/*Completed card*/}
          <div className="bg-[#F4EBD3] rounded-3xl p-6 text-center shadow-md min-w-[150px]">
            <h3 className="text-lg font-bold mb-2">Completed</h3>
            {/*gives the number of completed sessions registered in the db*/}
            <p className="text-5xl font-bold">{completedSessions.length}</p> 
          </div>

          {/*Searchbar */}
          <div className="flex-1 bg-[#F4EBD3] rounded-2xl px-6 py-2 shadow-md">
            <div className="flex-1 bg-white rounded-2xl px-6 py-2">
              <input
                type="text"
                placeholder="Search cases..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-transparent text-lg focus:outline-none placeholder-gray-600"
              />
            </div>
          </div>
        </div>

        {/*Sessions Grid OR Empty State */}
        {filteredCases.length === 0 ? (
          <div className="text-center py-16">
            <p className="text-white text-xl font-semibold">
              {completedSessions.length === 0 
                ? 'No sessions completed' 
                : 'No sessions match your search'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {filteredCases.map((session) => (
              <div 
                key={session.session_id} 
                onClick={() => sessionOverviewDisplay(session.session_id)}
                className="bg-[#F4EBD3] rounded-2xl shadow-md overflow-hidden hover:bg-[#DED3C4] transition-colors cursor-pointer"
              >
                <div className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="font-bold text-lg truncate" title={session.title || `Session ${session.session_id}`}>
                      {session.title || `Session ${session.session_number}`}
                    </h3>
                    <span className="bg-green-400 px-3 py-1 rounded-md font-bold text-sm flex-shrink-0">
                      C
                    </span>
                  </div>

                  {/* Thumbnail Image */}
                  <div className="bg-white rounded-xl h-40 flex items-center justify-center overflow-hidden">
                    {session.thumbnail_url ? (
                      <img
                        src={session.thumbnail_url}
                        alt={`Session ${session.session_id} thumbnail`}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <svg
                        className="w-16 h-16 text-gray-400"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2" strokeWidth="2"/>
                        <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor"/>
                        <path d="M21 15l-5-5L5 21" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    )}
                  </div>

                  {/* Session Info */}
                  <div className="mt-3 text-sm text-gray-600">
                    <p>{session.question_count} questions</p>
                    <p>{new Date(session.completed_at).toLocaleDateString()}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
