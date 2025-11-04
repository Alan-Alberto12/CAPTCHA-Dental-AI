import React from "react";

export default function BottomTabs({ active = "dashboard", onChange = () => { } }) {
    const items = [
        { key: "dashboard", label: "Home", icon: HomeIcon },
        { key: "play", label: "Play", icon: PlayIcon },
        { key: "leaderboard", label: "Leaderboard", icon: TrophyIcon },
    ];

    return (
        <nav
            aria-label="Bottom navigation"
            className="md:hidden fixed inset-x-0 bottom-0 z-50 bg-[#525470] text-[#F5EEDC]"
            style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
        >
            <ul className="mx-auto flex h-14 max-w-3xl items-stretch justify-around px-2">
                {items.map(({ key, label, icon: Icon }) => {
                    const isActive = key === active;
                    return (
                        <li key={key} className="flex-1">
                            <button
                                type="button"
                                onClick={() => onChange(key)}
                                className="group flex h-full w-full flex-col items-center justify-center gap-0.5 outline-none hover:cursor-pointer"
                            >
                                <span
                                    className={[
                                        "inline-flex items-center justify-center rounded-full px-3 py-1 text-md font-medium transition",
                                        isActive ? "bg-[#D9CEC1] text-[#525470]" : "text-[#F5EEDC]/90 group-hover:text-[#F5EEDC]",
                                    ].join(" ")}
                                >
                                    <Icon className="mr-1 h-4 w-4" /> {label}
                                </span>
                            </button>
                        </li>
                    );
                })}
            </ul>
        </nav>
    );
}

function HomeIcon({ className = "h-4 w-4" }) {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className={className} aria-hidden="true">
            <path d="M11.47 3.84a.75.75 0 0 1 1.06 0l7 7a.75.75 0 1 1-1.06 1.06l-.47-.47V19.5a1.5 1.5 0 0 1-1.5 1.5h-3a.75.75 0 0 1-.75-.75V16.5a1.5 1.5 0 0 0-1.5-1.5h-2a1.5 1.5 0 0 0-1.5 1.5v3.75a.75.75 0 0 1-.75.75h-3A1.5 1.5 0 0 1 6 19.5v-8.07l-.47.47a.75.75 0 0 1-1.06-1.06l7-7Z" />
        </svg>
    );
}

function PlayIcon({ className = "h-4 w-4" }) {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className={className} aria-hidden="true">
            <path d="M5.25 5.653c0-1.44 1.552-2.332 2.811-1.62l10.04 5.847c1.31.763 1.31 2.68 0 3.442L8.06 19.169c-1.259.713-2.81-.18-2.81-1.62V5.653z" />
        </svg>
    );
}

function TrophyIcon({ className = "h-4 w-4" }) {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className={className} aria-hidden="true">
            <path d="M4.5 4.5h15v1.5a4.5 4.5 0 0 1-3.75 4.44A6.75 6.75 0 0 1 12.75 15v1.5h3a.75.75 0 0 1 0 1.5h-7.5a.75.75 0 0 1 0-1.5h3V15a6.75 6.75 0 0 1-2.97-4.56A4.5 4.5 0 0 1 4.5 6V4.5Zm1.5 1.5V6a3 3 0 0 0 2.7 2.985 9.07 9.07 0 0 1 6.6 0A3 3 0 0 0 18 6v0-0.0V6H6Z" />
        </svg>
    );
}
