export default function NoticePage() {
  const NOTICES = [
    {
      id: 1,
      date: '2026.03.20',
      title: '서비스 오픈 안내',
      desc: 'Sentinel 서비스가 정식 오픈되었습니다.',
    },
    {
      id: 2,
      date: '2026.03.15',
      title: '데이터베이스 업데이트 안내',
      desc: '최신 유출 데이터베이스가 반영되었습니다.',
    },
    {
      id: 3,
      date: '2026.03.10',
      title: '개인정보 처리방침 안내',
      desc: '개인정보 처리방침이 갱신되었습니다.',
    },
  ];

  return (
    <main className="relative z-10 flex flex-col items-center min-h-[calc(100vh-112px)] px-4 sm:px-6 pt-8 sm:pt-16 pb-12">
      <h2
        className="text-white text-[32px] sm:text-[52px] font-bold mb-6 sm:mb-10 drop-shadow-md"
        style={{ fontFamily: "'Goldman', sans-serif" }}
      >
        공지사항
      </h2>
      <ul className="w-full max-w-2xl flex flex-col gap-3 sm:gap-4">
        {NOTICES.map((notice) => (
          <li
            key={notice.id}
            className="bg-white/15 backdrop-blur-sm border border-white/20 rounded-2xl px-4 sm:px-7 py-4 sm:py-5 text-left hover:bg-white/25 transition-colors cursor-pointer"
          >
            <span
              className="text-white/55 text-xs sm:text-sm mb-1 block"
              style={{ fontFamily: "'Noto Sans KR', sans-serif" }}
            >
              {notice.date}
            </span>
            <p
              className="text-white text-base sm:text-lg font-semibold mb-1"
              style={{ fontFamily: "'Noto Sans KR', sans-serif" }}
            >
              {notice.title}
            </p>
            <p
              className="text-white/70 text-xs sm:text-sm"
              style={{ fontFamily: "'Noto Sans KR', sans-serif" }}
            >
              {notice.desc}
            </p>
          </li>
        ))}
      </ul>
    </main>
  );
}
