import React, { useState } from "react";

function SignUp() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

     const handleSubmit = (e) => {
        e.preventDefault();
        console.log("Email: ", email);
        console.log("Email: ", email);
        //handle API logic here
    };

    return (
      <div className="fixed inset-0 flex justify-center items-center bg-[url('../src/assets/dentalbackground.png')] bg-center">
        <div className="flex flex-col gap-4 w-100 p-6 bg-[#555879] rounded-xl shadow-lg">
          <h2 className="text-center text-3xl font-bold text-[#F4EBD3]">Sign Up to Play!</h2>
          <input className="border p-2 rounded text-[#F4EBD3]" placeholder="Enter Username" />
          <input className="border p-2 rounded text-[#F4EBD3]" placeholder="Enter Email" />
          <input className="border p-2 rounded text-[#F4EBD3]" placeholder="Password" type="password" />
          <input className="border p-2 rounded text-[#F4EBD3]" placeholder="Confirm Password" type="password" />

          <div className="border p-4 rounded text-[#555879] resize-none bg-[#F4EBD3]">
            Password must contain the following:
            <ul className="list-disc ml-5">
              <li>At least 8 characters</li>
              <li>One uppercase letter</li>
              <li>One number</li>
              <li>One special character</li>
            </ul>
          </div>

          <button className="border p-2 rounded-xl bg-[#F4EBD3] text-[#555879]">Register</button>
        </div>
      </div>

    );
}

export default SignUp;
