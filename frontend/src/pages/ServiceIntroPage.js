export default function ServiceIntroPage() {
  return (
    <main className="relative z-10 flex flex-col items-center justify-center min-h-[calc(100vh-112px)] px-4 sm:px-6 text-center">
      <h2
        className="text-white text-[32px] sm:text-[52px] font-bold mb-4 sm:mb-6 drop-shadow-md"
        style={{ fontFamily: "'Goldman', sans-serif" }}
      >
        서비스 소개
      </h2>
      <p
        className="text-white/80 text-sm sm:text-xl max-w-2xl leading-relaxed px-2"
        style={{ fontFamily: "'Noto Sans KR', sans-serif" }}
      >
        Sentinel은 유출된 개인정보 데이터베이스를 분석하여 내 이메일 주소가 포함되어 있는지 실시간으로 확인해드립니다. 개인정보 도용 피해를 사전에 방지하세요.
      </p>
    </main>
  );
}
