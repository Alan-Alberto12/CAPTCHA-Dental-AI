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
                <div className="flex items-center">
                    <BottomNavPill
                        label="Dashboard"
                        isActive={inferredActive === "dashboard"}
                        side="left"
                        onClick={() => handleChange("dashboard")}
                    />
                    <BottomPlayButton
                        isActive={inferredActive === "play"}
                        onClick={() => handleChange("play")}
                    />
                    <BottomNavPill
                        label="Leaderboard"
                        isActive={inferredActive === "leaderboard"}
                        side="right"
                        onClick={() => handleChange("leaderboard")}
                    />
                </div>
            </div>
        </nav>
    );
}

function BottomNavPill({ label, isActive, side, onClick }) {
    const isLeft = side === "left";

    return (
        <button
            type="button"
            onClick={onClick}
            className={`relative flex h-9 w-36 items-center rounded-full bg-black/20 p-1 transition-all outline-none cursor-pointer ${
                isLeft ? "-mr-6 z-0" : "-ml-6 z-0"
            }`}
        >
            <span className={`flex h-full w-full items-center text-sm font-medium transition-all ${
                isLeft
                    ? "rounded-l-full rounded-r-none justify-center pl-2 pr-7"
                    : "rounded-r-full rounded-l-none justify-center pr-2 pl-7"
            } ${
                isActive
                    ? "bg-[#F5EEDC] text-[#525470]"
                    : "text-[#F5EEDC]/70"
            }`}>
                {label}
            </span>
        </button>
    );
}

function BottomPlayButton({ isActive, onClick }) {
    return (
        <button
            type="button"
            onClick={onClick}
            aria-label="Play"
            className="relative z-10 inline-flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-[#474961] p-1 transition-all outline-none cursor-pointer hover:bg-[#4f516a]"
        >
            <span className={`flex h-full w-full items-center justify-center rounded-full transition-all ${
                isActive ? "bg-[#F5EEDC] text-[#525470]" : "text-[#F5EEDC]/80"
            }`}>
                <svg viewBox="0 0 24 24" className="h-6 w-6 translate-x-px" fill="currentColor">
                    <polygon points="5,3 19,12 5,21" />
                </svg>
            </span>
        </button>
    );
}
