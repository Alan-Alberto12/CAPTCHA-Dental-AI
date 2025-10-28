import React, { useState } from "react";

function SignUp() {
    const [username, setUsername] = useState("");
    const [fullname, setFullName] = useState("");
    const [lastname, setLastName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [message, setMessage] = useState("");
    const [isSubmitted, setIsSubmitted] = useState(false);


    const handleSubmit = async (e) => {
      e.preventDefault();
      console.log("Email: ", email);

      if (password !== confirmPassword) {
        setMessage("Passwords do not match, please try again.");
        return;
      }

      try {
        const response = await fetch("http://127.0.0.1:8000/auth/signup", {
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
          console.log("Response data:", data);
          console.log("Status:", response.status);
          setMessage(`User ${data.username} registered successfully!`);
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
          setMessage(errorData.detail || "Signup failed.");
        }
      } catch (error) {
        console.error("Error during signup:", error);
        setMessage("An error occurred. Please try again later.");
      }
    };

    return (
      <div className="fixed inset-0 flex justify-center items-center bg-[url('../src/assets/dentalbackground.png')] bg-center">
          {/* Modal */}
          {isSubmitted && (
            <div className="fixed inset-0 flex justify-center items-center bg-black bg-opacity-50 z-50 bg-[url('../src/assets/dentalbackground.png')] bg-center">
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
                  type="submit"
                  className="border p-3 rounded-xl bg-[#F4EBD3] text-[#555879] text-lg font-bold hover:bg-[#D4C4A8] transition-all"
                >
                  Back to Login
                </button>
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
            placeholder="Password" 
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

            {message && !isSubmitted && (
            <p className="text-center text-[#F4EBD3] font-semibold">{message}</p>
            )}
            </div>
        </form>
      </div>
    );
}

export default SignUp;
