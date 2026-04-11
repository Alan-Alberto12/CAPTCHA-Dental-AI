import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { usePresignedImages } from "../hooks/usePresignedImages";
import PresignedImage from "../components/PresignedImage";
import { API_URL } from '../config';


export default function PlayPage() {
    const navigate = useNavigate();

    const [sessionFromAPI, setSessionFromAPI] = useState(null);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [selectedImages, setSelectedImages] = useState([]);
    const [answeredQuestions, setAnsweredQuestions] = useState(new Set());

    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [message, setMessage] = useState(null);
    const [questionStartTime, setQuestionStartTime] = useState(null);


    // Session completion
    const [sessionCompleted, setSessionCompleted] = useState(false);
    const [sessionTitle, setSessionTitle] = useState("");
    const [isSavingTitle, setIsSavingTitle] = useState(false);
    const [titleSaved, setTitleSaved] = useState(false);
    const [leaderboardPoints, setLeaderboardPoints] = useState(null);

    // Prevent duplicate session fetches (React StrictMode protection)
    const hasFetchedSession = useRef(false);

    // Presigned URL management with auto-refresh
    const { session, isRefreshing, refreshError, handleImageError } = usePresignedImages(
        sessionFromAPI,
        async () => {
            // Refresh callback: fetch current session to get new presigned URLs
            const token = localStorage.getItem("token");
            if (!token) return null;

            const response = await fetch(`${API_URL}/auth/sessions/current`, {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });

            if (response.ok) {
                const data = await response.json();
                // sync fresh image URLs received from the API, so it can be back into state.
                setSessionFromAPI(data);
                return data;
            }
            return null;
        }
    );

    // Fetch new session on mount
    useEffect(() => {
        if (!hasFetchedSession.current) {
            hasFetchedSession.current = true;
            fetchNewSession();
        }
    }, []);

    // Start timer when question changes
    useEffect(() => {
        if (session && !sessionCompleted) {
            setQuestionStartTime(new Date().toISOString());
        }
    }, [currentQuestionIndex, session]);

    const fetchNewSession = async (forceNew = false) => {
        setIsLoading(true);
        setError(null);
        setMessage(null);

        try {
            const token = localStorage.getItem("token");
            if (!token) {
                navigate("/login");
                return;
            }

            const url = forceNew
                ? `${API_URL}/auth/sessions/next?force_new=true`
                : `${API_URL}/auth/sessions/next`;

            const response = await fetch(url, {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`,
                },
            });

            if (response.ok) {
                const data = await response.json();


                setSessionFromAPI(data);

                // Initialize answered questions from backend
                const answeredSet = new Set(data.answered_question_ids || []);
                setAnsweredQuestions(answeredSet);

                // Find first unanswered question
                let firstUnansweredIndex = 0;
                for (let i = 0; i < data.questions.length; i++) {
                    if (!answeredSet.has(data.questions[i].id)) {
                        firstUnansweredIndex = i;
                        break;
                    }
                }

                setCurrentQuestionIndex(firstUnansweredIndex);
                setSelectedImages([]);
                setSessionCompleted(answeredSet.size === data.questions.length);
                setQuestionStartTime(new Date().toISOString());
            } else {
                const errorData = await response.json();
                setError(errorData.detail || "Failed to load session");

                // If unauthorized, redirect to login
                if (response.status === 401) {
                    localStorage.removeItem("token");
                    navigate("/login");
                }
            }
        } catch (err) {
            console.error("Error fetching session:", err);
            setError("Network error. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleImageClick = (imageId) => {
        if (sessionCompleted) return;

        setSelectedImages(prev => {
            if (prev.includes(imageId)) {
                // Deselect image
                return prev.filter(id => id !== imageId);
            } else {
                // Select image
                return [...prev, imageId];
            }
        });
    };

    const handleSubmitAnswer = async () => {
        if (!session || sessionCompleted) return;

        const currentQuestion = session.questions[currentQuestionIndex];
        const timeSpent = (Date.now() - new Date(questionStartTime).getTime()) / 1000;

        setIsLoading(true);
        setError(null);
        setMessage(null);

        try {
            const token = localStorage.getItem("token");

            const response = await fetch(`${API_URL}/auth/annotations`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    session_id: session.session_id,
                    question_id: currentQuestion.id,
                    selected_image_ids: selectedImages,
                    time_spent: timeSpent,
                }),
            });

            if (response.ok) {
                const data = await response.json();

                // Mark question as answered
                const newAnsweredQuestions = new Set(answeredQuestions);
                newAnsweredQuestions.add(currentQuestion.id);
                setAnsweredQuestions(newAnsweredQuestions);

                // Check if all questions answered
                if (newAnsweredQuestions.size === session.questions.length) {
                    //Finalize session if session has been completed
                    setSessionCompleted(true);
                    setError(null);
                    awardPoints(session.session_id);
                } else {
                    //Go to next question if there's still any left
                    handleNextQuestion();
                    // setMessage("Answer submitted!");
                    // // Auto-advance to next unanswered question after 1 second
                    // setTimeout(() => {
                    //     handleNextQuestion();
                    // }, 1000);
                }
                // Clear selected images
                setSelectedImages([]);
            } else {
                const errorData = await response.json();
                setError(errorData.detail || "Failed to submit answer");
            }
        } catch (err) {
            console.error("Error submitting annotation:", err);
            setError("Network error. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleNextQuestion = () => {
        if (!session) return;

        setMessage(null);
        setError(null);

        // Find next unanswered question
        let nextIndex = currentQuestionIndex;
        for (let i = 0; i < session.questions.length; i++) {
            const checkIndex = (currentQuestionIndex + i + 1) % session.questions.length;
            if (!answeredQuestions.has(session.questions[checkIndex].id)) {
                nextIndex = checkIndex;
                break;
            }
        }

        setCurrentQuestionIndex(nextIndex);
        setSelectedImages([]);
    };

    const handlePreviousQuestion = () => {
        if (!session) return;

        setMessage(null);
        setError(null);

        // Go to previous question (circular)
        const prevIndex = (currentQuestionIndex - 1 + session.questions.length) % session.questions.length;
        setCurrentQuestionIndex(prevIndex);
        setSelectedImages([]);
    };

    const handleSaveTitle = async () => {
        if (!sessionTitle.trim() || !session) return;

        setIsSavingTitle(true);
        try {
            const token = localStorage.getItem("token");
            const response = await fetch(`${API_URL}/auth/sessions/${session.session_id}/title`, {
                method: "PATCH",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ title: sessionTitle.trim() }),
            });

            if (response.ok) {
                setTitleSaved(true);
                setMessage("Session title saved!");
            } else {
                const errorData = await response.json();
                setError(errorData.detail || "Failed to save title");
            }
        } catch (err) {
            console.error("Error saving title:", err);
            setError("Network error. Please try again.");
        } finally {
            setIsSavingTitle(false);
        }
    };

    const awardPoints = async (sessionId) => {
        try {
            const token = localStorage.getItem("token");
            if (!token) return;

            const response = await fetch(`${API_URL}/leaderboard/session/complete/${sessionId}`, {
                method: "POST",
                headers: { Authorization: `Bearer ${token}` },
            });

            if (response.ok) {
                const data = await response.json();
                setLeaderboardPoints(data);
                console.log("Points awarded:", data);
            }
        } catch (err) {
            console.error("Error awarding points:", err);
        }
    };

    const handleNewSession = () => {
        hasFetchedSession.current = false;
        setSessionTitle("");
        setTitleSaved(false);
        fetchNewSession(true); // Force new session
        setLeaderboardPoints(null);
    };

    // Loading state
    if (isLoading && !session) {
        return (
            <div className="min-h-screen bg-[#98A1BC] flex items-center justify-center">
                <div className="text-[#F5EEDC] text-xl font-semibold">
                    Loading Session...
                </div>
            </div>
        );
    }

    // Error state
    if (error && !session) {
        return (
            <div className="min-h-screen bg-[#98A1BC] flex items-center justify-center">
                <div className="bg-[#525470] rounded-xl p-6 max-w-md mx-4">
                    <h2 className="text-[#F5EEDC] text-xl font-semibold mb-4">Error</h2>
                    <p className="text-[#F5EEDC] mb-4">{error}</p>
                    <button
                        onClick={fetchNewSession}
                        className="w-full rounded-lg bg-[#F5EEDC] px-4 py-2 font-medium text-[#525470]"
                    >
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    if (!session) return null;

    // Safety check: ensure questions exist and currentQuestionIndex is valid
    if (!session.questions || session.questions.length === 0) {
        return (
            <div className="min-h-screen bg-[#98A1BC] flex items-center justify-center">
                <div className="bg-[#525470] rounded-xl p-6 max-w-md mx-4">
                    <h2 className="text-[#F5EEDC] text-xl font-semibold mb-4">No Questions Available</h2>
                    <p className="text-[#F5EEDC] mb-4">There are no questions available for this session.</p>
                    <button
                        onClick={() => navigate("/dashboard")}
                        className="w-full rounded-lg bg-[#F5EEDC] px-4 py-2 font-medium text-[#525470]"
                    >
                        Back to Dashboard
                    </button>
                </div>
            </div>
        );
    }

    const currentQuestion = session.questions[currentQuestionIndex];

    // Additional safety check for currentQuestion
    if (!currentQuestion) {
        return (
            <div className="min-h-screen bg-[#98A1BC] flex items-center justify-center">
                <div className="bg-[#525470] rounded-xl p-6 max-w-md mx-4">
                    <h2 className="text-[#F5EEDC] text-xl font-semibold mb-4">Error Loading Question</h2>
                    <p className="text-[#F5EEDC] mb-4">Unable to load the current question.</p>
                    <button
                        onClick={() => navigate("/dashboard")}
                        className="w-full rounded-lg bg-[#F5EEDC] px-4 py-2 font-medium text-[#525470]"
                    >
                        Back to Dashboard
                    </button>
                </div>
            </div>
        );
    }

    const progress = `${answeredQuestions.size}/${session.questions.length}`;

    return (
        <div className="min-h-screen bg-[#98A1BC] pb-8">
            <div className="mx-auto w-full max-w-6xl px-3 md:px-4 lg:px-8 pt-6">

                {/* Header with Progress */}
                <div className="mb-4 flex items-center justify-between">
                    <div className="text-[#F5EEDC]">
                        <p className="text-sm font-medium">Session {session.session_number ?? 1}</p>
                    </div>
                </div>

                {!sessionCompleted && (
                    <>
                    {/* Question Prompt */}
                    <div className="mb-3 rounded-lg bg-[#525470] px-6 py-4">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-[#F5EEDC] text-sm opacity-80">
                                Question {currentQuestionIndex + 1} of {session.questions.length}
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

                    {/* Image Grid (2x2) */}
                    <div className="grid grid-cols-2 gap-4 mb-6 max-w-xl mx-auto">
                        {session.images.map((image) => {
                            const isSelected = selectedImages.includes(image.id);
                            return (
                                <div
                                    key={image.id}
                                    onClick={() => handleImageClick(image.id)}
                                    className={`
                                        relative rounded-lg overflow-hidden cursor-pointer
                                        transition-all duration-200 transform hover:scale-105
                                        ${isSelected
                                            ? 'ring-4 ring-[#F5EEDC] ring-offset-2 ring-offset-[#98A1BC]'
                                            : 'ring-2 ring-[#525470] hover:ring-[#F5EEDC]/50'
                                        }
                                    `}
                                >
                                    <PresignedImage
                                        src={image.image_url}
                                        alt={image.filename}
                                        className="w-full h-full object-contain"
                                        onError={() => handleImageError(image.id)}
                                        isRefreshing={isRefreshing}
                                    />
                                    {isSelected && (
                                        <div className="absolute inset-0 bg-[#F5EEDC]/20 flex items-center justify-center">
                                            <div className="bg-[#525470] text-[#F5EEDC] rounded-full w-12 h-12 flex items-center justify-center text-2xl font-bold">
                                                ✓
                                            </div>
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                    </>
                )}

                {/* Messages */}
                {isRefreshing && (
                    <div className="mb-4 rounded-lg bg-blue-500/20 border border-blue-500 px-4 py-3">
                        <p className="text-[#F5EEDC] font-medium">Refreshing images...</p>
                    </div>
                )}

                {refreshError && (
                    <div className="mb-4 rounded-lg bg-red-500/20 border border-red-500 px-4 py-3">
                        <p className="text-[#F5EEDC] font-medium">{refreshError}</p>
                    </div>
                )}

                {message && (
                    <div className="mb-4 rounded-lg bg-[#525470] border border-[#525470] px-4 py-3">
                        <p className="text-[#F5EEDC] font-medium">{message}</p>
                    </div>
                )}

                {error && (
                    <div className="mb-4 rounded-lg bg-red-500/20 border border-red-500 px-4 py-3">
                        <p className="text-[#F5EEDC] font-medium">{error}</p>
                    </div>
                )}

                {/* Action Buttons */}
                {!sessionCompleted ? (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 max-w-lg mx-auto">
                        <button
                            onClick={handlePreviousQuestion}
                            className="rounded-lg border-2 border-[#525470] px-4 py-3 font-medium text-[#F5EEDC] hover:bg-[#525470]/30"
                        >
                            ← Previous
                        </button>
                        <button
                            onClick={handleSubmitAnswer}
                            disabled={isLoading || answeredQuestions.has(currentQuestion.id)}
                            className={`
                                rounded-lg px-4 py-3 font-medium
                                ${answeredQuestions.has(currentQuestion.id)
                                    ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                                    : 'bg-[#F5EEDC] text-[#525470] hover:bg-[#F5EEDC]/90'
                                }
                            `}
                        >
                            {isLoading ? 'Submitting...' : answeredQuestions.has(currentQuestion.id) ? 'Already Answered' : 'Submit Answer'}
                        </button>
                        <button
                            onClick={handleNextQuestion}
                            className="rounded-lg border-2 border-[#525470] py-3 py-2 font-medium text-[#F5EEDC] hover:bg-[#525470]/30"
                        >
                            Next →
                        </button>
                    </div>
                ) : (
                    <div className="max-w-lg mx-auto">
                        <div className="mb-6 rounded-xl bg-[#525470] px-6 py-8 text-center">
                            <h2 className="text-2xl font-bold text-[#F5EEDC] mb-2">Session Completed!</h2>
                            <p className="text-[#F5EEDC] opacity-80 mb-4">
                                You answered all {session.questions.length} questions.
                            </p>

                            {/* Points Awarded Banner */}
                            {leaderboardPoints && (
                                <div className="mb-4 bg-yellow-400/20 border border-yellow-400 rounded-xl px-4 py-4">
                                    <p className="text-yellow-300 font-bold text-lg mb-2">
                                        +{leaderboardPoints.total_awarded} pts earned!
                                    </p>
                                    <div className="space-y-1">
                                        {leaderboardPoints.breakdown.map((item, i) => (
                                            <p key={i} className="text-[#F5EEDC] text-xs">
                                                +{item.points} — {item.reason.replace(/_/g, ' ')}
                                            </p>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Session Title Input */}
                            <div className="mt-4 text-left">
                                <label className="block text-[#F5EEDC] text-sm font-medium mb-2">
                                    Enter New Session Title (Optional):
                                </label>
                                <div className="flex gap-2">
                                    <input
                                        type="text"
                                        value={sessionTitle}
                                        onChange={(e) => setSessionTitle(e.target.value)}
                                        maxLength={100}
                                        disabled={titleSaved}
                                        className="flex-1 px-4 py-2 rounded-lg bg-white/90 text-[#525470] placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#F5EEDC] disabled:opacity-60"
                                    />
                                    <button
                                        onClick={handleSaveTitle}
                                        disabled={!sessionTitle.trim() || isSavingTitle || titleSaved}
                                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                                            titleSaved
                                                ? 'bg-[#525470] text-white'
                                                : 'bg-[#F5EEDC] text-[#525470] hover:bg-[#F5EEDC]/90 disabled:opacity-50 disabled:cursor-not-allowed'
                                        }`}
                                    >
                                        {isSavingTitle ? '...' : titleSaved ? '✓' : 'Save'}
                                    </button>
                                </div>
                            </div>
                        </div>
                        <button
                            onClick={handleNewSession}
                            className="w-full rounded-lg bg-[#F5EEDC] px-6 py-3 font-semibold text-[#525470] hover:bg-[#F5EEDC]/90"
                        >
                            Start New Session
                        </button>
                    </div>
                )}

                {/* Question Navigation Dots */}
                {!sessionCompleted && (
                    <div className="mt-8 flex justify-center gap-2">
                        {session.questions.map((q, idx) => (
                            <button
                                key={q.id}
                                onClick={() => {
                                    setCurrentQuestionIndex(idx);
                                    setSelectedImages([]);
                                    setMessage(null);
                                    setError(null);
                                }}
                                className={`
                                    w-3 h-3 rounded-full transition-all
                                    ${idx === currentQuestionIndex
                                        ? 'bg-[#F5EEDC] w-8'
                                        : answeredQuestions.has(q.id)
                                            ? 'bg-[#525470]'
                                            : 'bg-[#525470]'
                                    }
                                `}
                                title={`Question ${idx + 1}${answeredQuestions.has(q.id) ? ' (Answered)' : ''}`}
                            />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}