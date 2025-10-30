// frontend/src/components/header.jsx
import React from "react";

export default function Header({
    title = "Dental CAPTCHA AI",
    user = { name: "Peter Griffin", avatarUrl: null },
}) {
    const initials = (user?.name || "Dentist")
        .split(" ")
        .map((s) => s[0])
        .slice(0, 2)
        .join("")
        .toUpperCase();

    return (
        <header className="sticky top-0 z-50 border-b bg-[#525470] border-[#98A1B6]">
            <div className="grid h-12 w-full grid-cols-2 md:grid-cols-3 items-center px-3 md:px-4 lg:px-8">

                {/* left: title + logo? */}
                <div className="justify-self-start">
                    <a
                        href="#"
                        aria-label="Go to dashboard"
                        className="text-sm font-semibold tracking-tight text-[#F5EEDC]"
                    >
                        {title}
                    </a>
                </div>

                {/* center: navigation */}
                <nav aria-label="Primary" className="justify-self-center hidden md:block">
                    <ul className="flex items-center gap-1 text-sm">
                        <NavItem label="Dashboard" />
                        <NavItem label="Play" />
                        <NavItem label="Leaderboard" />
                    </ul>
                </nav>

                {/* right: profile */}
                <div className="justify-self-end">
                    <div
                        className="inline-flex h-8 w-8 items-center justify-center overflow-hidden rounded-full border border-transparent bg-[#F5EEDC] text-xs font-semibold text-[#525470]"
                        title={user?.name || "Profile"}
                        aria-label="Profile"
                    >
                        {user?.avatarUrl ? (
                            <img src={user.avatarUrl} className="h-full w-full object-cover" />
                        ) : (
                            <span>{initials}</span>
                        )}
                    </div>
                </div>
            </div>
        </header>
    );
}

function NavItem({ label }) {
    return (
        <li>
            <button
                type="button"
                aria-disabled="true"
                className="rounded-full hover:cursor-pointer px-3 py-1.5 text-[#F5EEDC] hover:bg-[#98A1B6]/20 focus:outline-none focus-visible:ring focus-visible:ring-[#98A1B6]"
            >
                {label}
            </button>
        </li>
    );
}
