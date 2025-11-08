import React, { useEffect } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import BottomTabs from '../components/BottomTab';

export default function ProtectedLayout() {
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login', { replace: true });
    }
  }, [navigate]);

  return (
    <>
      <Header />
      <div className="pb-20 md:pb-0">
        <Outlet />
      </div>
      <BottomTabs />
    </>
  );
}

