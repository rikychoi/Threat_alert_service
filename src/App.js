import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Hero from './components/Hero';
import ServiceIntroPage from './pages/ServiceIntroPage';
import AlertPage from './pages/AlertPage';
import NoticePage from './pages/NoticePage';
import DashboardPage from './pages/DashboardPage';
import './App.css';

export default function App() {
  return (
    <BrowserRouter>
      <div
        className="min-h-screen relative overflow-hidden"
        style={{
          background:
            'linear-gradient(180deg, #1d4ed8 0%, #3b82f6 30%, #93c5fd 65%, #eff6ff 100%)',
        }}
      >
        <Header />
        <Routes>
          <Route path="/" element={<Hero />} />
          <Route path="/service" element={<ServiceIntroPage />} />
          <Route path="/alert" element={<AlertPage />} />
          <Route path="/notice" element={<NoticePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/mypage" element={<Navigate to="/dashboard" replace />} />
          <Route path="/search" element={<Navigate to="/" replace />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
