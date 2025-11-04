// src/frontend/pages/DashboardPage/index.jsx
import React from "react";
import Header from "../../components/Header";
import BottomTabs from "../../components/BottomTab";


export default function Dashboard() {
    return (
        <>
            <Header />
            <main className="pb-16 md:pb-0">
                <BottomTabs
                    active="dashboard"
                    onChange={(tab) => {
                        console.log("Tab changed:", tab);
                    }}
                />
            </main>
        </>
    );
}
