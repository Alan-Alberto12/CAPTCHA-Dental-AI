import React, { useState } from "react";
import { useForm } from "react-hook-form";

function Login() {
    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm();


    const onSubmit = (data) => {
        const userData = JSON.parse(localStorage.getItem(data.email));
        if (userData) {
            if (userData.password === data.password) {
                console.log(userData.name + " Login Success");
            } else {
                console.log("Email or Password is incorrect");
            }
        } else {
            console.log("Email or Password is incorrect");
        }
    };

    return (
      <div className="fixed inset-0 flex justify-center items-center bg-[url('../src/assets/dentalbackground.png')] bg-center">
          <form className="App" onSubmit={handleSubmit(onSubmit)}>
            <div className="flex flex-col gap-4 w-100 p-6 bg-[#555879] rounded-xl shadow-lg">
            <Navbar bg="dark" data-bs-theme="dark">
            <Container>
            <Navbar.Brand href="#home">Navbar</Navbar.Brand>
            <Nav className="me-auto">
                <Nav.Link href="#home">Home</Nav.Link>
                </Nav>
                </Container>
            </Navbar>
            <h2 className="text-center text-3xl font-bold text-[#F4EBD3]">Log In</h2>
                <input
                    className="border p-2 rounded text-[#F4EBD3]"
                    type="email"
                    {...register("email", { required: true })}
                    placeholder="Email"
                />
                {errors.email && <span style={{ color: "red" }}>*Email* is mandatory</span>}

                <input
                    className="border p-2 rounded text-[#F4EBD3]"
                    type="password"
                    {...register("password", { required: true })}
                    placeholder="Password"
                />
                {errors.password && <span style={{ color: "red" }}>*Password* is mandatory</span>}

                <input type="submit" className="border p-2 rounded-xl bg-[#F4EBD3] text-[#555879]" />
            </div>
            </form>
        </div>
    );
}

export default Login;