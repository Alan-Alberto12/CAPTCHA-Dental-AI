import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { API_URL } from '../config';


function SignUp() {
    const navigate = useNavigate();
    const [username, setUsername] = useState("");
    const [fullname, setFullName] = useState("");
    const [lastname, setLastName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [message, setMessage] = useState("");
    const [isSubmitted, setIsSubmitted] = useState(false);
    const [resendMessage, setResendMessage] = useState("");
    const [isResending, setIsResending] = useState(false);
    const submittedEmailRef = useRef("");

    const validatePassword = (password) => {
      const minLength = password.length >= 8;
      const hasUppercase = /[A-Z]/.test(password);
      const hasNumber = /[0-9]/.test(password);
      const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);
      
      return { minLength, hasUppercase, hasNumber, hasSpecial };
    };

    const handleResend = async () => {
      setIsResending(true);
      setResendMessage("");
      try {
        const response = await fetch(`${API_URL}/auth/resend-confirmation`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: submittedEmailRef.current }),
        });
        const data = await response.json();
        if (response.ok) {
          setResendMessage("Confirmation email resent! Please check your inbox.");
        } else {
          setResendMessage(data.detail || "Failed to resend email.");
        }
      } catch {
        setResendMessage("An error occurred. Please try again.");
      } finally {
        setIsResending(false);
      }
    };

    const handleSubmit = async (e) => {
      e.preventDefault();

      const passwordValidation = validatePassword(password);
      if (!passwordValidation.minLength || !passwordValidation.hasUppercase || !passwordValidation.hasNumber || !passwordValidation.hasSpecial) {
        setMessage("Password does not meet requirements.");
        return;
      }

      if (password !== confirmPassword) {
        setMessage("Passwords do not match, please try again.");
        return;
      }

      try {
        const response = await fetch(`${API_URL}/auth/signup`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email,
            username,
            first_name: fullname,
            last_name: lastname,
            password,
          }),
        });

        if(response.ok) {
          const data = await response.json();
          setMessage(`User ${data.username} registered successfully!`);
          submittedEmailRef.current = email;
          setEmail("");
          setUsername("");
          setFullName("");
          setLastName("");
          setPassword("");
          setConfirmPassword("");
          setIsSubmitted(true);
        } 
        else {
          const errorData = await response.json();
          let errorMessage = "Signup failed.";
          if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          } else if (Array.isArray(errorData.detail)) {
            errorMessage = errorData.detail.map(err => err.msg).join(', ');
          }
          setMessage(errorMessage);
        }
      } catch (error) {
        console.error("Error during signup:", error);
        setMessage("An error occurred. Please try again later.");
      }
    };

    return (
      <div className="fixed inset-0 flex justify-center items-center bg-[url('../src/assets/dentalbackground.png')] bg-center bg-cover">
          {/* Modal */}
          {isSubmitted && (
            <div className="fixed inset-0 flex justify-center items-center bg-black bg-opacity-50 z-50 bg-[url('../src/assets/dentalbackground.png')] bg-center bg-cover">
              <div className="bg-[#555879] rounded-2xl p-16 max-w-2xl w-full mx-4 text-center shadow-2xl">
                <h1 className="text-5xl font-bold text-[#F4EBD3] mb-10">Email Sent!</h1>
                <div className="mb-8">
                  <p className="text-[#F4EBD3] text-2xl leading-relaxed">
                    A confirmation email was sent to your inbox.
                  </p>
                  <p className="text-[#F4EBD3] text-2xl leading-relaxed">
                    Please click the confirmation link to proceed
                  </p>
                  <p className="text-[#F4EBD3] text-2xl leading-relaxed">
                    to login.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => navigate('/login')}
                  className="border p-3 rounded-xl bg-[#F4EBD3] text-[#555879] text-lg font-bold hover:bg-[#D4C4A8] transition-all"
                >
                  Back to Login
                </button>

                <div className="mt-6">
                  <p className="text-[#F4EBD3] text-sm mb-3">
                    Resend Confirmation
                  </p>
                  <button
                    type="button"
                    onClick={handleResend}
                    disabled={isResending}
                    className="border p-2 rounded-xl bg-transparent border-[#F4EBD3] text-[#F4EBD3] text-sm font-semibold hover:bg-[#F4EBD3] hover:bg-opacity-20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isResending ? "Resending..." : "Resend Confirmation Email"}
                  </button>
                  {resendMessage && (
                    <p className="text-[#F4EBD3] text-sm mt-3 font-semibold">{resendMessage}</p>
                  )}
                </div>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="flex flex-col gap-4 w-100 p-6 bg-[#555879] rounded-xl shadow-lg">
              <h2 className="text-center text-3xl font-bold text-[#F4EBD3]">Sign Up to Play!</h2>
              <input 
                className="border p-2 rounded text-[#F4EBD3]" 
                placeholder="Enter First Name" 
                value={fullname}
                onChange={(e) => setFullName(e.target.value)}
              />
              <input 
                className="border p-2 rounded text-[#F4EBD3]" 
                placeholder="Enter Last Name" 
                value={lastname}
                onChange={(e) => setLastName(e.target.value)}
              />
              <input 
                className="border p-2 rounded text-[#F4EBD3]" 
                placeholder="Enter Username" 
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
              <input 
                className="border p-2 rounded text-[#F4EBD3]" 
                placeholder="Enter Email" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <input 
              className="border p-2 rounded text-[#F4EBD3]" 
              placeholder="Enter Password" 
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              />
              <input 
              className="border p-2 rounded text-[#F4EBD3]" 
              placeholder="Confirm Password" 
              type="password" 
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              />

              <div className="border p-4 rounded text-[#555879] resize-none bg-[#F4EBD3]">
                Password must contain the following:
                <ul className="list-disc ml-5">
                  <li>At least 8 characters</li>
                  <li>One uppercase letter</li>
                  <li>One number</li>
                  <li>One special character</li>
                </ul>
              </div>

              {/*Register Button */}
              <button
                type="submit"
                className="border p-2 rounded-xl bg-[#F4EBD3] text-[#555879] font-bold hover:bg-[#D4C4A8] transition-all"
              >
                Register
              </button>

              <button
                type="button"
                onClick={() => navigate('/login')}
                className="text-center text-[#F4EBD3] text-sm hover:underline"
              >
                Back to Login
              </button>

              {message && !isSubmitted && (
              <p className="text-center text-[#F4EBD3] font-semibold">{message}</p>
              )}
            </div>
        </form>
      </div>
    );
}

export default SignUp;