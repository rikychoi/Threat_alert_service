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
  return (
    <header className="header">
      <NavLink to="/" className="header__logo">
        Sentinel
      </NavLink>
      <nav className="header__nav">
        {NAV_ITEMS.map(({ label, to }) => (
          <NavLink
            key={to + label}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              isActive
                ? 'header__nav-link header__nav-link--active'
                : 'header__nav-link'
            }
          >
            {label}
          </NavLink>
        ))}
      </nav>
    </header>
  );
}
