// frontend/src/components/header.jsx
import React, { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { API_URL } from '../config';


export default function Header( {
    title = "DenTag",
}) {
    const navigate = useNavigate();
    const [user, setUser] = useState({ name: "Loading...", avatarUrl: null, isAdmin: false });
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
                const response = await fetch(`${API_URL}/auth/me`, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });

                if (response.ok) {
                    const userData = await response.json();
                    setUser({
                        name: `${userData.first_name} ${userData.last_name}`,
                        avatarUrl: null,
                        isAdmin: userData.is_admin || false,
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

    const handleEditUser = () => {
        navigate('/edit-user');
    }

    const handleAdminPanel = () => {
        navigate('/admin');
    }

    return (
        <header className="sticky top-0 z-50 bg-[#525470]/95 backdrop-blur-md border-b border-white/10 shadow-sm">
            <div className="grid h-14 w-full grid-cols-2 md:grid-cols-3 items-center px-4 md:px-6 lg:px-10">

                {/* left: title */}
                <div className="justify-self-start">
                    <Link
                        to="/dashboard"
                        aria-label="Go to dashboard"
                        className="text-base font-bold tracking-wide text-[#F5EEDC] hover:text-white transition-colors"
                    >
                        {title}
                    </Link>
                </div>

                {/* center: navigation */}
                <nav aria-label="Primary" className="justify-self-center hidden md:block">
                    <ul className="flex items-center gap-0.5 text-sm bg-black/20 rounded-full px-1 h-7">
                        <NavItem label="Dashboard" to="/dashboard" />
                        <PlayButton to="/play" />
                        <NavItem label="Leaderboard" to="/leaderboard" />
                    </ul>
                </nav>

                {/* right: profile */}
                <div className="justify-self-end relative">
                    <button
                        onClick={() => setShowDropdown(!showDropdown)}
                        className="inline-flex h-8 w-8 items-center justify-center overflow-hidden rounded-full bg-[#DED3C4] text-xs font-bold text-[#525470] ring-2 ring-transparent hover:ring-[#F5EEDC]/50 hover:bg-[#F4EBD3] transition-all cursor-pointer"
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
                        <div className="absolute right-0 mt-2 w-44 bg-[#3f4157] rounded-xl shadow-xl border border-white/10 z-50 overflow-hidden">
                            {user.isAdmin && (
                                <button
                                    onClick={handleAdminPanel}
                                    className="w-full text-left px-4 py-2.5 text-[#F5EEDC] text-sm hover:bg-white/10 transition-colors"
                                >
                                    Admin Portal
                                </button>
                            )}
                            
                            <button
                                onClick={handleEditUser}
                                className="w-full text-left px-4 py-2.5 text-[#F5EEDC] text-sm hover:bg-white/10 transition-colors"
                            >
                                Edit Account
                            </button>

                            <div className="border-t border-white/10" />
                            <button
                                onClick={handleSignOut}
                                className="w-full text-left px-4 py-2.5 text-red-400 text-sm hover:bg-white/10 transition-colors"
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
                className={`block rounded-full px-3.5 py-0.5 text-sm font-medium transition-all focus:outline-none focus-visible:ring focus-visible:ring-[#F5EEDC]/50 ${
                    isActive
                        ? 'bg-[#F5EEDC] text-[#525470] shadow-sm'
                        : 'text-[#F5EEDC]/70 hover:text-[#F5EEDC] hover:bg-white/10'
                }`}
            >
                {label}
            </Link>
        </li>
    );
}

function PlayButton({ to }) {
    const location = useLocation();
    const isActive = location.pathname === to;

    return (
        <li>
            <Link
                to={to}
                aria-label="Play"
                className={`inline-flex h-12 w-12 items-center justify-center rounded-full transition-all focus:outline-none focus-visible:ring focus-visible:ring-[#F5EEDC]/50 ${
                    isActive
                        ? 'bg-[#F5EEDC] text-[#525470]'
                        : 'bg-[#474961] text-[#F5EEDC]/80 hover:text-[#F5EEDC] hover:bg-[#4f516a]'
                }`}
            >
                <svg viewBox="0 0 24 24" className="h-5 w-5 translate-x-px" fill="currentColor">
                    <polygon points="5,3 19,12 5,21" />
                </svg>
            </Link>
        </li>
    );
}
