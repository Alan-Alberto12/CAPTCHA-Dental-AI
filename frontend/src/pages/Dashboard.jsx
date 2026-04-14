import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { API_URL } from '../config';


export default function Dashboard() {
  const navigate = useNavigate();

  const [completedSessions, setCompletedSessions] = useState([]);
  const [hasInProgressSession, setHasInProgressSession] = useState(false);
  const [userStats, setUserStats] = useState(null);
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
      const [completedCase, currentCase, statsCase] = await Promise.all([
        fetch(`${API_URL}/auth/sessions/completed`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API_URL}/auth/sessions/current`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API_URL}/leaderboard/me`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
      ]);

      if(completedCase.ok) {
        const completedData = await completedCase.json();
        setCompletedSessions(completedData);
        completedData.forEach(session => {
          if (session.thumbnail_url) {
            const img = new window.Image();
            img.src = session.thumbnail_url;
          }
        });
      }

      if(currentCase.ok) {
        const currentData = await currentCase.json();
        setHasInProgressSession(currentData !== null);
      }

      if(statsCase.ok) {
        setUserStats(await statsCase.json());
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
      const data = await response.json();
      data.questions.forEach(question => {
        question.images.forEach(image => {
          const img = new window.Image();
          img.src = image.image_url;
        });
      });
      setQuestionOverviewCount(0);
      setSelectedSession(data);
    }
  }
  
   //Search bar functionality - search by title or session id
  const filteredCases = completedSessions.filter(session => {
    const searchLower = searchTerm.toLowerCase();
    const titleMatch = session.title?.toLowerCase().includes(searchLower);
    const idMatch = `Session ${session.session_id}`.toLowerCase().includes(searchLower);
    return titleMatch || idMatch;
  });

  if (isLoading) {
    return (
        <div className="min-h-screen bg-[#98A1BC] flex items-center justify-center">
            <div className="text-[#F5EEDC] text-xl font-semibold">Loading Completed Sessions...</div>
        </div>
    );
  }
 
  if (selectedSession) {
    const currentQuestion = selectedSession.questions[questionOverviewCount]
    const selectedImages = selectedSession.selected_images_per_question[currentQuestion.id] ?? []

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
              Selected: {selectedImages.length}
            </p>
          </div>

          {/* Image grid (2x2)*/}
          <div className="grid grid-cols-2 gap-4 mb-6 max-w-xl mx-auto">
            {currentQuestion.images.map((image) => {
              const isSelected = selectedImages.includes(image.id)
              return (
                <div
                  key={image.id}
                  className={`
                    relative rounded-lg overflow-hidden
                    ${isSelected
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
                  {isSelected && (
                    <div className="absolute inset-0 bg-[#F5EEDC]/20 flex items-center justify-center">
                      <div className="bg-[#525470] text-[#F5EEDC] rounded-full w-12 h-12 flex items-center justify-center text-2xl font-bold">
                        ✓
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
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
        
        {/* In-Progress Session Banner */}
        {hasInProgressSession && (
          <Link
            to="/play"
            className="group flex items-center justify-between mb-6 px-5 py-4 rounded-2xl bg-[#525470] hover:bg-[#3f4157] hover:-translate-y-0.5 hover:shadow-lg transition-all duration-200 shadow-md cursor-pointer"
          >
            <div className="flex items-center gap-3">
              <span className="shrink-0 w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse" />
              <div>
                <p className="text-[#F5EEDC] font-semibold text-lg">Session in progress</p>
                <p className="text-[#F5EEDC]/60 text-xs">Click to continue where you left off</p>
              </div>
            </div>
            <span className="text-[#F5EEDC]/70 group-hover:text-[#F5EEDC] text-lg transition-colors">→</span>
          </Link>
        )}

        {/* Stat cards + searchbar */}
        <div className="flex items-center gap-3 mb-8">
          <div className="bg-[#F4EBD3] rounded-3xl p-4 text-center shadow-md min-w-[100px]">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Sessions Completed</h3>
            <p className="text-4xl font-bold text-[#525470]">{completedSessions.length}</p>
          </div>

          <div className="bg-[#F4EBD3] rounded-3xl p-4 text-center shadow-md min-w-[100px]">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Daily Streak</h3>
            <p className="text-4xl font-bold text-orange-400">
              {userStats ? userStats.daily_streak : '—'}
              <span className="text-4xl ml-0.5">🔥</span>
            </p>
          </div>

          <div className="bg-[#F4EBD3] rounded-3xl p-4 text-center shadow-md min-w-[110px]">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Lifetime Points</h3>
            <p className="text-4xl font-bold text-yellow-500">
              {userStats ? userStats.total_points.toLocaleString() : '—'}
            </p>
          </div>

          {/* Searchbar */}
          <div className="flex-1 bg-[#F4EBD3] rounded-2xl px-2 py-4 shadow-md">
            <div className="bg-white rounded-2xl px-4 py-4">
              <input
                type="text"
                placeholder="Search sessions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-transparent text-base focus:outline-none placeholder-gray-500"
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
                className="bg-[#F4EBD3] rounded-2xl shadow-md overflow-hidden hover:bg-[#DED3C4] hover:-translate-y-1 hover:shadow-xl transition-all duration-200 cursor-pointer"
              >
                <div className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="font-bold text-lg truncate" title={session.title || `Session ${session.session_id}`}>
                      {session.title || `Session ${session.session_number}`}
                    </h3>
                    {session.points_earned > 0 && (
                      <span className="bg-green-400 text-green-900 px-2 py-1 rounded-md font-bold text-xs shrink-0 whitespace-nowrap">
                        +{session.points_earned} pts
                      </span>
                    )}
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
