import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { usePresignedImages } from "../hooks/usePresignedImages";
import PresignedImage from "../components/PresignedImage";

/**
 * PlayPage - Image Selection/Annotation System
 * - Fetches session with 4 images and 1-5 random questions
 * - Allows users to select images for each question
 * - Submits annotations to backend
 * - Tracks time spent per question
 * - Auto-refreshes expired presigned URLs
 */
export default function PlayPage() {
    const navigate = useNavigate();

    // Session data (raw from API)
    const [rawSession, setRawSession] = useState(null);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [selectedImages, setSelectedImages] = useState([]);
    const [answeredQuestions, setAnsweredQuestions] = useState(new Set());

    // UI states
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [message, setMessage] = useState(null);
    const [questionStartTime, setQuestionStartTime] = useState(null);

    // Session completion
    const [sessionCompleted, setSessionCompleted] = useState(false);

    // Prevent duplicate session fetches (React StrictMode protection)
    const hasFetchedSession = useRef(false);

    // Presigned URL management with auto-refresh
    const { session, isRefreshing, refreshError, handleImageError } = usePresignedImages(
        rawSession,
        async () => {
            // Refresh callback: fetch current session to get new presigned URLs
            const token = localStorage.getItem("token");
            if (!token) return null;

            const response = await fetch("http://127.0.0.1:8000/auth/sessions/current", {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });

            if (response.ok) {
                const data = await response.json();
                setRawSession(data); // Update raw session
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
            setQuestionStartTime(Date.now());
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
                ? "http://127.0.0.1:8000/auth/sessions/next?force_new=true"
                : "http://127.0.0.1:8000/auth/sessions/next";

            const response = await fetch(url, {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`,
                },
            });

            if (response.ok) {
                const data = await response.json();
                console.log("Session loaded:", data);

                // Check if this is a resumed session
                if (data.resumed) {
                    setMessage("📍 Resuming your previous session...");
                    // Clear message after 3 seconds
                    setTimeout(() => setMessage(null), 3000);
                }

                setRawSession(data);

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
                setQuestionStartTime(Date.now());
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
        const timeSpent = (Date.now() - questionStartTime) / 1000; // Convert to seconds

        setIsLoading(true);
        setError(null);
        setMessage(null);

        try {
            const token = localStorage.getItem("token");

            const response = await fetch("http://127.0.0.1:8000/auth/annotations", {
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
                console.log("Annotation submitted:", data);

                // Mark question as answered
                const newAnsweredQuestions = new Set(answeredQuestions);
                newAnsweredQuestions.add(currentQuestion.id);
                setAnsweredQuestions(newAnsweredQuestions);

                // Check if all questions answered
                if (newAnsweredQuestions.size === session.questions.length) {
                    setSessionCompleted(true);
                    setMessage("🎉 Session completed! All questions answered.");
                } else {
                    setMessage("✅ Answer submitted!");
                    // Auto-advance to next unanswered question after 1 second
                    setTimeout(() => {
                        handleNextQuestion();
                    }, 1000);
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

    const handleNewSession = () => {
        hasFetchedSession.current = false;
        fetchNewSession(true); // Force new session
    };

    // Loading state
    if (isLoading && !session) {
        return (
            <div className="min-h-screen bg-[#98A1BC] flex items-center justify-center">
                <div className="text-[#F5EEDC] text-xl font-semibold">Loading session...</div>
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

    const currentQuestion = session.questions[currentQuestionIndex];
    const progress = `${answeredQuestions.size}/${session.questions.length}`;

    return (
        <div className="min-h-screen bg-[#98A1BC] pb-8">
            <div className="mx-auto w-full max-w-6xl px-3 md:px-4 lg:px-8 pt-6">

                {/* Header with Progress */}
                <div className="mb-4 flex items-center justify-between">
                    <div className="text-[#F5EEDC]">
                        <p className="text-sm font-medium">Session {session.session_id}</p>
                        <p className="text-xs opacity-80">Progress: {progress} questions answered</p>
                    </div>
                    <button
                        onClick={() => navigate("/")}
                        className="text-[#F5EEDC] hover:text-white text-sm underline"
                    >
                        Exit
                    </button>
                </div>

                {/* Question Prompt */}
                <div className="mb-6 rounded-xl bg-[#525470] px-6 py-4">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-[#F5EEDC] text-sm opacity-80">
                            Question {currentQuestionIndex + 1} of {session.questions.length}
                        </span>
                        {answeredQuestions.has(currentQuestion.id) && (
                            <span className="text-green-400 text-sm font-medium">✓ Answered</span>
                        )}
                    </div>
                    <h1 className="text-xl md:text-2xl font-semibold text-[#F5EEDC]">
                        {currentQuestion.question_text}
                    </h1>
                    <p className="text-[#F5EEDC] text-sm opacity-70 mt-2">
                        Type: {currentQuestion.question_type.replace('_', ' ')}
                    </p>
                </div>

                {/* Instructions */}
                <div className="mb-4 bg-white/10 rounded-lg px-4 py-2">
                    <p className="text-[#F5EEDC] text-sm">
                        💡 Click images to select/deselect • Selected: {selectedImages.length}
                    </p>
                </div>

                {/* Image Grid (4 images) */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    {session.images.map((image) => {
                        const isSelected = selectedImages.includes(image.id);
                        return (
                            <div
                                key={image.id}
                                onClick={() => handleImageClick(image.id)}
                                className={`
                                    relative aspect-square rounded-lg overflow-hidden cursor-pointer
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
                                    className="w-full h-full object-cover"
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
                                <div className="absolute bottom-0 left-0 right-0 bg-black/60 px-2 py-1">
                                    <p className="text-white text-xs truncate">{image.filename}</p>
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Messages */}
                {isRefreshing && (
                    <div className="mb-4 rounded-lg bg-blue-500/20 border border-blue-500 px-4 py-3">
                        <p className="text-[#F5EEDC] font-medium">🔄 Refreshing images...</p>
                    </div>
                )}

                {refreshError && (
                    <div className="mb-4 rounded-lg bg-red-500/20 border border-red-500 px-4 py-3">
                        <p className="text-[#F5EEDC] font-medium">{refreshError}</p>
                    </div>
                )}

                {message && (
                    <div className="mb-4 rounded-lg bg-green-500/20 border border-green-500 px-4 py-3">
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
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 max-w-2xl mx-auto">
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
                            className="rounded-lg border-2 border-[#525470] px-4 py-3 font-medium text-[#F5EEDC] hover:bg-[#525470]/30"
                        >
                            Next →
                        </button>
                    </div>
                ) : (
                    <div className="max-w-md mx-auto">
                        <div className="mb-6 rounded-xl bg-[#525470] px-6 py-8 text-center">
                            <div className="text-6xl mb-4">🎉</div>
                            <h2 className="text-2xl font-bold text-[#F5EEDC] mb-2">Session Complete!</h2>
                            <p className="text-[#F5EEDC] opacity-80 mb-4">
                                You answered all {session.questions.length} questions.
                            </p>
                            <div className="bg-white/10 rounded-lg px-4 py-3">
                                <p className="text-[#F5EEDC] text-sm">
                                    💡 Click "Start New Session" to begin a fresh session. Your progress is saved!
                                </p>
                            </div>
                        </div>
                        <button
                            onClick={handleNewSession}
                            className="w-full rounded-lg bg-[#F5EEDC] px-6 py-3 font-semibold text-[#525470] hover:bg-[#F5EEDC]/90"
                        >
                            Start New Session
                        </button>
                        <button
                            onClick={() => navigate("/")}
                            className="w-full mt-3 rounded-lg border-2 border-[#525470] px-6 py-3 font-medium text-[#F5EEDC] hover:bg-[#525470]/30"
                        >
                            Back to Home
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
                                            ? 'bg-green-400'
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
