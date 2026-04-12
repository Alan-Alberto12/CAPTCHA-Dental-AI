import React from "react";
import { useLocation, useNavigate } from "react-router-dom";

export default function BottomTabs({ active, onChange }) {
    const navigate = useNavigate();
    const { pathname } = useLocation();

    const inferredActive = active || (
        pathname.startsWith("/play") ? "play" :
        pathname.startsWith("/leaderboard") ? "leaderboard" :
        "dashboard"
    );

    const handleChange = onChange || ((key) => {
        const paths = { dashboard: "/dashboard", play: "/play", leaderboard: "/leaderboard" };
        if (paths[key]) navigate(paths[key]);
    });

    return (
        <nav
            aria-label="Bottom navigation"
            className="md:hidden fixed inset-x-0 bottom-0 z-50 bg-[#525470]/95 backdrop-blur-md border-t border-white/10"
            style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
        >
            <div className="flex items-center justify-center h-16">
                <ul className="flex items-center gap-0.5 bg-black/20 rounded-full px-1 h-9">
                    <BottomNavItem
                        label="Dashboard"
                        isActive={inferredActive === "dashboard"}
                        onClick={() => handleChange("dashboard")}
                    />
                    <BottomPlayButton
                        isActive={inferredActive === "play"}
                        onClick={() => handleChange("play")}
                    />
                    <BottomNavItem
                        label="Leaderboard"
                        isActive={inferredActive === "leaderboard"}
                        onClick={() => handleChange("leaderboard")}
                    />
                </ul>
            </div>
        </nav>
    );
}

function BottomNavItem({ label, isActive, onClick }) {
    return (
        <li>
            <button
                type="button"
                onClick={onClick}
                className={`block rounded-full px-4 py-1 text-sm font-medium transition-all outline-none cursor-pointer ${
                    isActive
                        ? "bg-[#F5EEDC] text-[#525470]"
                        : "text-[#F5EEDC]/70 hover:text-[#F5EEDC] hover:bg-white/10"
                }`}
            >
                {label}
            </button>
        </li>
    );
}

function BottomPlayButton({ isActive, onClick }) {
    return (
        <li>
            <button
                type="button"
                onClick={onClick}
                aria-label="Play"
                className={`inline-flex h-14 w-14 items-center justify-center rounded-full transition-all outline-none cursor-pointer ${
                    isActive
                        ? "bg-[#F5EEDC] text-[#525470]"
                        : "bg-[#474961] text-[#F5EEDC]/80 hover:text-[#F5EEDC] hover:bg-[#4f516a]"
                }`}
            >
                <svg viewBox="0 0 24 24" className="h-6 w-6 translate-x-px" fill="currentColor">
                    <polygon points="5,3 19,12 5,21" />
                </svg>
            </button>
        </li>
    );
}
