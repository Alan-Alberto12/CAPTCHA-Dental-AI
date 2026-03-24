import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";

function Login() {
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [message, setMessage] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [emailError, setEmailError] = useState(false);
    const [passwordError, setPasswordError] = useState(false);
    const [showForgotPassword, setShowForgotPassword] = useState(false);
    const [forgotPasswordEmail, setForgotPasswordEmail] = useState("");
    const [forgotPasswordMessage, setForgotPasswordMessage] = useState("");
    const [isEmailSent, setIsEmailSent] = useState(false);

    // Email confirmation states
    const [showEmailConfirmation, setShowEmailConfirmation] = useState(false);
    const [emailConfirmationStatus, setEmailConfirmationStatus] = useState(null); // 'success' or 'error'

    // Prevent duplicate confirmation attempts (React StrictMode runs effects twice)
    const confirmationAttempted = useRef(false);

    // Check for email confirmation token on component mount
    useEffect(() => {
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token');

        if (token && !confirmationAttempted.current) {
            confirmationAttempted.current = true;
            handleEmailConfirmation(token);
        }
    }, []);

    const handleEmailConfirmation = async (token) => {
        console.log("Attempting email confirmation with token:", token);
        try {
            const response = await fetch("http://127.0.0.1:8000/auth/confirm-email", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ token }),
            });

            console.log("Email confirmation response status:", response.status);

            if (response.ok) {
                const data = await response.json();
                console.log("Email confirmation success:", data);
                setEmailConfirmationStatus('success');
                setShowEmailConfirmation(true);
            } else {
                const errorData = await response.json();
                console.log("Email confirmation error response:", errorData);
                setEmailConfirmationStatus('error');
                setShowEmailConfirmation(true);
            }
        } catch (error) {
            console.error("Error confirming email:", error);
            setEmailConfirmationStatus('error');
            setShowEmailConfirmation(true);
        }

        // Clean up URL by removing the token parameter
        window.history.replaceState({}, document.title, window.location.pathname);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setMessage("");
        setEmailError(false);
        setPasswordError(false);

        // Validate fields
        if (!email) {
            setEmailError(true);
        }
        if (!password) {
            setPasswordError(true);
        }
        if (!email || !password) {
            setIsLoading(false);
            return;
        }

        try {
            // OAuth2 expects form data with 'username' field (can be email or username)
            const formData = new URLSearchParams();
            formData.append('username', email); // backend accepts email in username field
            formData.append('password', password);

            const response = await fetch("http://127.0.0.1:8000/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                console.log("Login successful:", data);
                setMessage("Login successful!");
                // Store auth token if provided (backend returns 'access_token')
                if (data.access_token) {
                    localStorage.setItem('token', data.access_token);
                }
                // Redirect to dashboard
                navigate('/dashboard');
            } else {
                const errorData = await response.json();
                console.log("Error response:", errorData);

                // Handle different error response formats
                let errorMessage = "Email or Password is incorrect";

                if (typeof errorData.detail === 'string') {
                    errorMessage = errorData.detail;
                } else if (Array.isArray(errorData.detail)) {
                    // Handle FastAPI validation errors (array of error objects)
                    errorMessage = errorData.detail.map(err => err.msg).join(', ');
                } else if (errorData.message) {
                    errorMessage = errorData.message;
                }

                setMessage(errorMessage);
            }
        } catch (error) {
            console.error("Error during login:", error);
            setMessage("An error occurred. Please try again later.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleForgotPassword = async (e) => {
        e.preventDefault();
        setForgotPasswordMessage("");

        if (!forgotPasswordEmail) {
            setForgotPasswordMessage("Please enter your email address");
            return;
        }

        try {
            const response = await fetch("http://127.0.0.1:8000/auth/forgot-password", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    email: forgotPasswordEmail,
                }),
            });

            if (response.ok) {
                setIsEmailSent(true);
            } else {
                const errorData = await response.json();
                setForgotPasswordMessage(errorData.detail || "Failed to send reset email");
            }
        } catch (error) {
            console.error("Error sending reset email:", error);
            setForgotPasswordMessage("An error occurred. Please try again later.");
        }
    };

    const closeForgotPasswordModal = () => {
        setShowForgotPassword(false);
        setForgotPasswordEmail("");
        setForgotPasswordMessage("");
        setIsEmailSent(false);
    };

    return (
        <div className="fixed inset-0 flex justify-center items-center bg-[url('../src/assets/dentalbackground.png')] bg-center">

            {/* Email Confirmation Modal - Success */}
            {showEmailConfirmation && emailConfirmationStatus === 'success' && (
                <div className="fixed inset-0 flex justify-center items-center bg-black bg-opacity-50 z-50 bg-[url('../src/assets/dentalbackground.png')] bg-center">
                    <div className="bg-[#555879] rounded-2xl p-16 max-w-2xl w-full mx-4 text-center shadow-2xl">
                        <h1 className="text-5xl font-bold text-green-300 mb-10">Email Confirmed!</h1>
                        <div className="mb-8">
                            <p className="text-[#F4EBD3] text-2xl leading-relaxed">
                                Your email has been successfully confirmed!
                            </p>
                            <p className="text-[#F4EBD3] text-2xl leading-relaxed mt-4">
                                You can now log in with your credentials.
                            </p>
                        </div>
                        <button
                            type="button"
                            onClick={() => window.close()}
                            className="border p-3 rounded-xl bg-[#F4EBD3] text-[#555879] text-lg font-bold hover:bg-[#D4C4A8] transition-all"
                        >
                            Close
                        </button>
                    </div>
                </div>
            )}

            {/* Email Confirmation Modal - Error */}
            {showEmailConfirmation && emailConfirmationStatus === 'error' && (
                <div className="fixed inset-0 flex justify-center items-center bg-black bg-opacity-50 z-50 bg-[url('../src/assets/dentalbackground.png')] bg-center">
                    <div className="bg-[#555879] rounded-2xl p-16 max-w-2xl w-full mx-4 text-center shadow-2xl">
                        <h1 className="text-5xl font-bold text-red-300 mb-10">Confirmation Failed</h1>
                        <div className="mb-8">
                            <p className="text-[#F4EBD3] text-2xl leading-relaxed">
                                The link may be expired or invalid.
                            </p>
                            <p className="text-[#F4EBD3] text-xl leading-relaxed mt-4">
                                Please try signing up again or contact support if the problem persists.
                            </p>
                        </div>
                        <button
                            type="button"
                            onClick={() => window.close()}
                            className="border p-3 rounded-xl bg-[#F4EBD3] text-[#555879] text-lg font-bold hover:bg-[#D4C4A8] transition-all"
                        >
                            Close
                        </button>
                    </div>
                </div>
            )}

            {/* Forgot Password Modal - Email Sent Confirmation */}
            {showForgotPassword && isEmailSent && (
                <div className="fixed inset-0 flex justify-center items-center bg-black bg-opacity-50 z-50">
                    <div className="bg-[#555879] rounded-2xl p-16 max-w-2xl w-full mx-4 text-center shadow-2xl">
                        <h1 className="text-5xl font-bold text-[#F4EBD3] mb-10">Email Sent!</h1>
                        <div className="mb-8">
                            <p className="text-[#F4EBD3] text-2xl leading-relaxed">
                                A password reset link was sent to your inbox.
                            </p>
                            <p className="text-[#F4EBD3] text-2xl leading-relaxed">
                                Please check your email and follow the instructions
                            </p>
                            <p className="text-[#F4EBD3] text-2xl leading-relaxed">
                                to reset your password.
                            </p>
                        </div>
                        <button
                            type="button"
                            onClick={closeForgotPasswordModal}
                            className="border p-3 rounded-xl bg-[#F4EBD3] text-[#555879] text-lg font-bold hover:bg-[#D4C4A8] transition-all"
                        >
                            Back to Login
                        </button>
                    </div>
                </div>
            )}

            {/* Forgot Password Modal - Enter Email */}
            {showForgotPassword && !isEmailSent && (
                <div className="fixed inset-0 flex justify-center items-center bg-black bg-opacity-50 z-50">
                    <form onSubmit={handleForgotPassword}>
                        <div className="bg-[#555879] rounded-2xl p-8 max-w-md w-full mx-4 shadow-2xl">
                            <h2 className="text-3xl font-bold text-[#F4EBD3] mb-4 text-center">Forgot Password</h2>
                            <p className="text-[#F4EBD3] text-center mb-6">
                                Enter your email address and we'll send you a link to reset your password.
                            </p>
                            
                            <input
                                className="w-full border p-2 rounded text-[#F4EBD3] bg-transparent placeholder-[#F4EBD3] placeholder-opacity-60 mb-4"
                                type="email"
                                placeholder="Enter Email"
                                value={forgotPasswordEmail}
                                onChange={(e) => setForgotPasswordEmail(e.target.value)}
                            />

                            {forgotPasswordMessage && (
                                <p className="text-center text-red-300 font-semibold mb-4">
                                    {forgotPasswordMessage}
                                </p>
                            )}

                            <div className="flex gap-4">
                                <button
                                    type="button"
                                    onClick={closeForgotPasswordModal}
                                    className="flex-1 border p-2 rounded-xl bg-transparent border-[#F4EBD3] text-[#F4EBD3] font-bold hover:bg-[#F4EBD3] hover:bg-opacity-20 transition-all"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="flex-1 border p-2 rounded-xl bg-[#F4EBD3] text-[#555879] font-bold hover:bg-[#D4C4A8] transition-all"
                                >
                                    Send Reset Link
                                </button>
                            </div>
                        </div>
                    </form>
                </div>
            )}

            <form onSubmit={handleSubmit}>
                <div className="flex flex-col gap-4 w-100 p-6 bg-[#555879] rounded-xl shadow-lg">
                    <h2 className="text-center text-3xl font-bold text-[#F4EBD3]">Log In</h2>
                    
                    <input
                        className="border p-2 rounded text-[#F4EBD3] bg-transparent placeholder-[#F4EBD3] placeholder-opacity-60"
                        type="text"
                        placeholder="Email or Username"
                        value={email}
                        onChange={(e) => {
                            setEmail(e.target.value);
                            setEmailError(false);
                        }}
                    />
                    {emailError && <span style={{ color: "red" }}>*Email or Username* is mandatory</span>}

                    <input
                        className="border p-2 rounded text-[#F4EBD3] bg-transparent placeholder-[#F4EBD3] placeholder-opacity-60"
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => {
                            setPassword(e.target.value);
                            setPasswordError(false);
                        }}
                    />
                    {passwordError && <span style={{ color: "red" }}>*Password* is mandatory</span>}

                    <button
                        type="button"
                        onClick={() => setShowForgotPassword(true)}
                        className="text-[#F4EBD3] text-sm text-right hover:underline transition-all"
                    >
                        Forgot Password?
                    </button>

                    <button
                        type="submit"
                        className="border p-2 rounded-xl bg-[#F4EBD3] text-[#555879] font-bold hover:bg-[#D4C4A8] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled={isLoading}
                    >
                        {isLoading ? "Logging in..." : "Log In"}
                    </button>

                    {message && (
                        <p className={`text-center font-semibold ${
                            message === "Login successful!" ? "text-green-300" : "text-red-300"
                        }`}>
                            {message}
                        </p>
                    )}

                    <p className="text-center text-[#F4EBD3] text-sm">
                        Don't have an account?{" "}
                        <button
                            type="button"
                            className="underline hover:text-[#D4C4A8] transition-colors"
                            onClick={() => navigate('/signup')}
                        >
                            Sign Up
                        </button>
                    </p>
                </div>
            </form>
        </div>
    );
}

export default Login;