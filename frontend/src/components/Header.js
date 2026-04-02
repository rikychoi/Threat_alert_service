import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import './Header.css';

const NAV_ITEMS = [
  { label: '서비스 소개', to: '/service' },
  { label: '유출정보 조회하기', to: '/' },
  { label: '알림 받기', to: '/alert' },
  { label: '공지사항', to: '/notice' },
  { label: '대시보드', to: '/dashboard' },
];

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false);

  const navLinkClass = ({ isActive }) =>
    isActive ? 'header__nav-link header__nav-link--active' : 'header__nav-link';

  return (
    <header className="header">
      <NavLink to="/" className="header__logo" onClick={() => setMenuOpen(false)}>
        Sentinel
      </NavLink>

      {/* 데스크탑 nav */}
      <nav className="header__nav">
        {NAV_ITEMS.map(({ label, to }) => (
          <NavLink key={to + label} to={to} end={to === '/'} className={navLinkClass}>
            {label}
          </NavLink>
        ))}
      </nav>

      {/* 모바일 햄버거 버튼 */}
      <button
        className="header__hamburger"
        onClick={() => setMenuOpen((prev) => !prev)}
        aria-label="메뉴 열기"
      >
        {menuOpen ? (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        ) : (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        )}
      </button>

      {/* 모바일 드롭다운 메뉴 */}
      {menuOpen && (
        <nav className="header__mobile-menu">
          {NAV_ITEMS.map(({ label, to }) => (
            <NavLink
              key={to + label}
              to={to}
              end={to === '/'}
              className={navLinkClass}
              onClick={() => setMenuOpen(false)}
            >
              {label}
            </NavLink>
          ))}
        </nav>
      )}
    </header>
  );
}
