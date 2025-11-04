// frontend/src/components/header.jsx
import React, { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

export default function Header( {
    title = "Dental CAPTCHA AI",
}) {
    const navigate = useNavigate();
    const [user, setUser] = useState({ name: "Loading...", avatarUrl: null });
    const [showDropdown, setShowDropdown] = useState(false);

    // Fetch current user data
    useEffect(() => {
        const fetchUser = async () => {
            const token = localStorage.getItem('token');
            if (!token) {
                navigate('/login');
                return;
            }

            try {
                const response = await fetch('http://127.0.0.1:8000/auth/me', {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });

                if (response.ok) {
                    const userData = await response.json();
                    setUser({
                        name: `${userData.first_name} ${userData.last_name}`,
                        avatarUrl: null,
                    });
                } else {
                    localStorage.removeItem('token');
                    navigate('/login');
                }
            } catch (error) {
                console.error('Error fetching user:', error);
                navigate('/login');
            }
        };

        fetchUser();
    }, [navigate]);

    const initials = (user?.name || "Dentist")
        .split(" ")
        .map((s) => s[0])
        .slice(0, 2)
        .join("")
        .toUpperCase();

    const handleSignOut = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    return (
        <header className="sticky top-0 z-50 border-b bg-[#525470] border-[#98A1B6]">
            <div className="grid h-12 w-full grid-cols-2 md:grid-cols-3 items-center px-3 md:px-4 lg:px-8">

                {/* left: title + logo? */}
                <div className="justify-self-start">
                    <Link
                        to="/dashboard"
                        aria-label="Go to dashboard"
                        className="text-sm font-semibold tracking-tight text-[#F5EEDC]"
                    >
                        {title}
                    </Link>
                </div>

                {/* center: navigation */}
                <nav aria-label="Primary" className="justify-self-center hidden md:block">
                    <ul className="flex items-center gap-1 text-sm">
                        <NavItem label="Dashboard" to="/dashboard" />
                        <NavItem label="Play" to="/play" />
                        <NavItem label="Leaderboard" to="/leaderboard" />
                    </ul>
                </nav>

                {/* right: profile */}
                <div className="justify-self-end relative">
                    <button
                        onClick={() => setShowDropdown(!showDropdown)}
                        className="inline-flex h-8 w-8 items-center justify-center overflow-hidden rounded-full border border-transparent bg-[#F5EEDC] text-xs font-semibold text-[#525470] hover:bg-[#E5DECC] transition-colors cursor-pointer"
                        title={user?.name || "Profile"}
                        aria-label="Profile"
                    >
                        {user?.avatarUrl ? (
                            <img src={user.avatarUrl} className="h-full w-full object-cover" />
                        ) : (
                            <span>{initials}</span>
                        )}
                    </button>

                    {/* Dropdown Menu */}
                    {showDropdown && (
                        <div className="absolute right-0 mt-2 w-48 bg-[#F5EEDC] rounded-lg shadow-lg border border-[#98A1B6] z-50">
                            <button
                                onClick={handleSignOut}
                                className="w-full text-left px-4 py-2 text-[#525470] hover:bg-[#E5DECC] rounded-lg transition-colors font-semibold"
                            >
                                Sign Out
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </header>
    );
}

function NavItem({ label, to }) {
    const location = useLocation();
    const isActive = location.pathname === to;

    return (
        <li>
            <Link
                to={to}
                className={`rounded-full hover:cursor-pointer px-3 py-1.5 text-[#F5EEDC] hover:bg-[#98A1B6]/20 focus:outline-none focus-visible:ring focus-visible:ring-[#98A1B6] ${
                    isActive ? 'bg-[#98A1B6]/30' : ''
                }`}
            >
                {label}
            </Link>
        </li>
    );
}
