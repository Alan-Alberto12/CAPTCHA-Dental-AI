import React from 'react';
import Header from '../components/Header';
import BottomTabs from '../components/BottomTab';
import { useNavigate } from 'react-router-dom';

export default function Leaderboard() {
  const currentPage = 'leaderboard';
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#98A1BC] pb-20 md:pb-6">
      <Header />
      <BottomTabs
        active="leaderboard"
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
    </div>
    )
}
