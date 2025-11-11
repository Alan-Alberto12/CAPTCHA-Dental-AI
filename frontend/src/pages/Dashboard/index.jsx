// src/frontend/pages/DashboardPage/index.jsx
import React from "react";
import Header from "../../components/Header";
import BottomTabs from "../../components/BottomTab";
import { useNavigate } from "react-router-dom";


export default function Dashboard() {
    const navigate = useNavigate();

    return (
        <>
            <Header />
            <main className="pb-16 md:pb-0">
                <BottomTabs
                    active="dashboard"
                    onChange={(tab) => {
                        navigate(
                            tab === 'dashboard'
                                ? '/dashboard'
                                : tab === 'play'
                                ? '/play'
                                : '/leaderboard'
                        );
                    }}
                />
            </main>
        </>
    );
}
