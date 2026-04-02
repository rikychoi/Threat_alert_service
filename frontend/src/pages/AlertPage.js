import React, { useState, useEffect } from 'react';

const WORKSPACE_INVITE_URL =
  'https://join.slack.com/t/sentinel-sdj3765/shared_invite/zt-3tbi6p4jk-uMeQrCFb9j5vTPYo3qEo1Q';
const CHANNEL_URL =
  'https://sentinel-sdj3765.slack.com/channels/security-alerts';
const STORAGE_KEY = 'slack_workspace_joined';

export default function AlertPage() {
  const [workspaceJoined, setWorkspaceJoined] = useState(false);

  useEffect(() => {
    setWorkspaceJoined(localStorage.getItem(STORAGE_KEY) === 'true');
  }, []);

  function handleWorkspaceJoin() {
    window.open(WORKSPACE_INVITE_URL, '_blank', 'noopener,noreferrer');
    localStorage.setItem(STORAGE_KEY, 'true');
    setWorkspaceJoined(true);
  }

  function handleChannelJoin() {
    window.open(CHANNEL_URL, '_blank', 'noopener,noreferrer');
  }

  return (
    <main
      className="relative z-10 flex flex-col items-center min-h-[calc(100vh-112px)] px-4 sm:px-6 py-8 sm:py-14"
      style={{ fontFamily: "'Noto Sans KR', sans-serif" }}
    >
      {/* 헤더 */}
      <div className="text-center mb-8 sm:mb-14">
        <h2
          className="text-white text-[36px] sm:text-[52px] font-bold mb-3 sm:mb-4 drop-shadow-md"
          style={{ fontFamily: "'Goldman', sans-serif" }}
        >
          알림 받기
        </h2>
        <p className="text-white/70 text-sm sm:text-lg max-w-xl leading-relaxed px-2">
          새로운 유출 게시글이 등록되면 Slack으로 즉시 알림을 받아보세요.
          <br className="hidden sm:block" />
          {' '}아래 두 단계를 완료하면 실시간 알림이 시작됩니다.
        </p>
      </div>

      {/* 스텝 카드 */}
      <div className="w-full max-w-xl flex flex-col gap-4">
        {/* Step 1 */}
        <div
          className={`
            backdrop-blur-sm border rounded-2xl px-4 py-5 sm:px-8 sm:py-7 transition-all duration-200
            ${workspaceJoined
              ? 'bg-white/5 border-white/40 opacity-60'
              : 'bg-blue-400/15 border-white/60'}
          `}
        >
          <div className="flex items-start gap-4">
            <StepBadge number={1} done={workspaceJoined} />
            <div className="flex-1 min-w-0">
              <p className="text-white/50 text-xs font-semibold uppercase tracking-widest mb-1">
                Step 1
              </p>
              <h3 className="text-white text-base sm:text-lg font-bold mb-1">
                워크스페이스 참여
              </h3>
              <p className="text-white/60 text-sm leading-relaxed mb-4 sm:mb-5">
                Sentinel Slack 워크스페이스에 가입합니다.
              </p>
              <button
                onClick={handleWorkspaceJoin}
                disabled={workspaceJoined}
                className={`
                  w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-150
                  ${workspaceJoined
                    ? 'bg-white/10 text-white/40 cursor-default border border-white/10'
                    : 'bg-blue-500 hover:bg-blue-400 text-white border border-blue-400 cursor-pointer'}
                `}
              >
                <SlackIcon />
                {workspaceJoined ? '참여 완료' : 'Slack 워크스페이스 참여하기'}
              </button>
            </div>
          </div>
        </div>

        {/* 연결 점선 */}
        <div className="flex justify-center">
          <div className="w-px h-5 border-l-2 border-dashed border-white/20" />
        </div>

        {/* Step 2 */}
        <div
          className={`
            backdrop-blur-sm border rounded-2xl px-4 py-5 sm:px-8 sm:py-7 transition-all duration-200
            ${workspaceJoined
              ? 'bg-blue-400/15 border-white/60'
              : 'bg-white/5 border-white/60 opacity-50'}
          `}
        >
          <div className="flex items-start gap-4">
            <StepBadge number={2} done={false} active={workspaceJoined} />
            <div className="flex-1 min-w-0">
              <p className="text-white/50 text-xs font-semibold uppercase tracking-widest mb-1">
                Step 2
              </p>
              <h3 className="text-white text-base sm:text-lg font-bold mb-1">
                알림 채널 참여
              </h3>
              <p className="text-white/60 text-sm leading-relaxed mb-4 sm:mb-5">
                <span className="text-white/80 font-semibold">#security-alerts</span> 채널에 참여하면
                유출 게시글 등록 시 즉시 알림을 받습니다.
              </p>
              <button
                onClick={handleChannelJoin}
                disabled={!workspaceJoined}
                className={`
                  w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-150
                  ${workspaceJoined
                    ? 'bg-blue-500 hover:bg-blue-400 text-white border border-blue-400 cursor-pointer'
                    : 'bg-white/10 text-white/30 cursor-not-allowed border border-white/10'}
                `}
              >
                <SlackIcon />
                #security-alerts 채널 참여하기
              </button>
            </div>
          </div>
        </div>

        {/* 완료 안내 */}
        <p className="text-center text-white/40 text-xs mt-2 px-2">
          이미 워크스페이스에 참여했다면 Step 2만 진행하세요.
        </p>
      </div>
    </main>
  );
}

function StepBadge({ number, done, active }) {
  return (
    <div
      className={`
        shrink-0 w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold border-2 mt-0.5
        ${done
          ? 'bg-green-500/20 border-green-400 text-green-400'
          : active
          ? 'bg-blue-500/30 border-blue-400 text-blue-300'
          : 'bg-white/5 border-white/20 text-white/30'}
      `}
    >
      {done ? '✓' : number}
    </div>
  );
}

function SlackIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 54 54" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M19.712 33.17a5.065 5.065 0 01-5.063 5.063 5.065 5.065 0 01-5.063-5.063 5.065 5.065 0 015.063-5.062h5.063v5.062z" fill="currentColor" opacity=".9"/>
      <path d="M22.27 33.17a5.065 5.065 0 015.063-5.062 5.065 5.065 0 015.062 5.062v12.668a5.065 5.065 0 01-5.062 5.062 5.065 5.065 0 01-5.063-5.062V33.17z" fill="currentColor" opacity=".9"/>
      <path d="M27.333 19.712a5.065 5.065 0 01-5.063-5.063 5.065 5.065 0 015.063-5.063 5.065 5.065 0 015.062 5.063v5.063h-5.062z" fill="currentColor" opacity=".9"/>
      <path d="M27.333 22.27a5.065 5.065 0 015.062 5.063 5.065 5.065 0 01-5.062 5.062H14.666a5.065 5.065 0 01-5.063-5.062 5.065 5.065 0 015.063-5.063h12.667z" fill="currentColor" opacity=".9"/>
      <path d="M40.79 27.333a5.065 5.065 0 015.063 5.063 5.065 5.065 0 01-5.063 5.062 5.065 5.065 0 01-5.062-5.062v-5.063h5.062z" fill="currentColor" opacity=".7"/>
      <path d="M38.23 27.333a5.065 5.065 0 01-5.062-5.063 5.065 5.065 0 015.062-5.062h12.668a5.065 5.065 0 015.062 5.062 5.065 5.065 0 01-5.062 5.063H38.23z" fill="currentColor" opacity=".7"/>
      <path d="M33.17 13.875a5.065 5.065 0 01-5.062-5.063A5.065 5.065 0 0133.17 3.75a5.065 5.065 0 015.062 5.062v5.063H33.17z" fill="currentColor" opacity=".7"/>
      <path d="M33.17 16.438a5.065 5.065 0 015.062 5.062 5.065 5.065 0 01-5.062 5.063V14.066c0 .79-.001 1.58 0 2.372z" fill="currentColor" opacity=".7"/>
    </svg>
  );
}
