import React, { useEffect, useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  Legend,
} from 'recharts';
import { loadDashboardData } from '../api/dashboard';

const CHART_COLORS = [
  '#1d4ed8',
  '#3b82f6',
  '#60a5fa',
  '#93c5fd',
  '#2563eb',
  '#818cf8',
  '#a5b4fc',
  '#c4b5fd',
];

const cardClass =
  'bg-white/15 backdrop-blur-sm border border-white/20 rounded-2xl px-3 sm:px-5 py-3 sm:py-4 text-left shadow-lg';

const chartWrapClass = `${cardClass} flex flex-col min-h-[240px] sm:min-h-[320px]`;

/** 테이블 영역: 짙은 남색 대신 살짝만 어두운 회색 톤 */
const tablePanelClass =
  'rounded-xl border border-white/50 bg-slate-400/25 backdrop-blur-sm shadow-inner overflow-hidden';

function StatCard({ title, value, sub }) {
  return (
    <div className={cardClass}>
      <p
        className="text-white/70 text-sm mb-1"
        style={{ fontFamily: "'Noto Sans KR', sans-serif" }}
      >
        {title}
      </p>
      <p
        className="text-white text-2xl sm:text-3xl font-bold tabular-nums"
        style={{ fontFamily: "'Goldman', sans-serif" }}
      >
        {value}
      </p>
      {sub != null && sub !== '' && (
        <p
          className="text-white/55 text-xs mt-2"
          style={{ fontFamily: "'Noto Sans KR', sans-serif" }}
        >
          {sub}
        </p>
      )}
    </div>
  );
}

function ChartTitle({ icon, children }) {
  return (
    <h3
      className="text-white font-semibold text-base mb-3 flex items-center gap-2"
      style={{ fontFamily: "'Noto Sans KR', sans-serif" }}
    >
      <span aria-hidden>{icon}</span>
      {children}
    </h3>
  );
}

const tooltipStyle = {
  backgroundColor: 'rgba(255,255,255,0.95)',
  border: '1px solid rgba(59,130,246,0.35)',
  borderRadius: '8px',
  fontSize: '12px',
};

export default function DashboardPage() {
  const [model, setModel] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError('');
      try {
        const { data } = await loadDashboardData();
        if (!cancelled) setModel(data);
      } catch (e) {
        if (!cancelled) setError('대시보드 데이터를 불러오지 못했습니다.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const s = model?.summary;
  const categoryPieData =
    model?.postsByCategory?.map((x) => ({ name: x.name, value: x.count })) ||
    [];
  const alertPieData = model
    ? [
        { name: '성공', value: model.alertOutcomes.success },
        { name: '실패', value: model.alertOutcomes.failure },
      ].filter((x) => x.value > 0)
    : [];

  const formatPostRow = (p) => {
    const title = p.title || p.name || '—';
    const cat = p.category ?? '—';
    const created = p.created_at
      ? new Date(p.created_at).toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })
      : '—';
    return { key: p.id ?? `${title}-${created}`, title, cat, created };
  };

  const formatAlertRow = (a) => {
    const channel = a.channel ?? '—';
    const ok =
      a.is_success === 1 || a.is_success === true ? '성공' : '실패';
    const sent = a.sent_at
      ? new Date(a.sent_at).toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })
      : '—';
    return { key: a.id ?? `${channel}-${sent}`, channel, ok, sent };
  };

  return (
    <main
      className="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 pb-20 pt-10"
      style={{ fontFamily: "'Noto Sans KR', sans-serif" }}
    >
      <div className="text-center mb-10">
        <h2
          className="text-white text-[40px] sm:text-[52px] font-bold mb-2 drop-shadow-md"
          style={{ fontFamily: "'Goldman', sans-serif" }}
        >
          대시보드
        </h2>
        <p className="text-white/80 text-base max-w-2xl mx-auto">
          수집·알림 지표를 한눈에 확인하세요.
        </p>
      </div>

      {loading && (
        <p className="text-white/90 text-center py-12">불러오는 중…</p>
      )}

      {error && !loading && (
        <p className="text-amber-200 text-center py-4">{error}</p>
      )}

      {!loading && model && (
        <>
          <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
            <StatCard
              title="전체 게시물 수"
              value={s.totalPosts.toLocaleString('ko-KR')}
            />
            <StatCard
              title="활성 소스 수"
              value={s.activeSources.toLocaleString('ko-KR')}
            />
            <StatCard
              title="신규 게시물 (오늘 / 이번 주)"
              value={`${s.newPostsToday} / ${s.newPostsThisWeek}`}
            />
            <StatCard
              title="알림 발송 성공률"
              value={`${s.alertSuccessRate}%`}
            />
          </section>

          <section className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-6">
            <div className={chartWrapClass}>
              <ChartTitle icon="📅">월별 게시물 추이</ChartTitle>
              <div className="flex-1 w-full min-h-[260px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={model.postsByMonth}
                    margin={{ top: 8, right: 8, left: 0, bottom: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.15)" />
                    <XAxis
                      dataKey="label"
                      tick={{ fill: 'rgba(255,255,255,0.75)', fontSize: 11 }}
                      interval="preserveStartEnd"
                    />
                    <YAxis
                      tick={{ fill: 'rgba(255,255,255,0.75)', fontSize: 11 }}
                      allowDecimals={false}
                    />
                    <Tooltip contentStyle={tooltipStyle} />
                    <Line
                      type="monotone"
                      dataKey="count"
                      name="게시물"
                      stroke="#93c5fd"
                      strokeWidth={2}
                      dot={{ fill: '#1d4ed8', r: 3 }}
                      activeDot={{ r: 5 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className={chartWrapClass}>
              <ChartTitle icon="🏷️">카테고리별 비율</ChartTitle>
              <div className="flex-1 w-full min-h-[260px] flex items-center justify-center">
                {categoryPieData.length === 0 ? (
                  <p className="text-white/60 text-sm">데이터 없음</p>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={categoryPieData}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        innerRadius={56}
                        outerRadius={88}
                        paddingAngle={2}
                      >
                        {categoryPieData.map((_, i) => (
                          <Cell
                            key={String(i)}
                            fill={CHART_COLORS[i % CHART_COLORS.length]}
                          />
                        ))}
                      </Pie>
                      <Tooltip contentStyle={tooltipStyle} />
                      <Legend
                        wrapperStyle={{ fontSize: '12px' }}
                        formatter={(value) => (
                          <span className="text-slate-800">{value}</span>
                        )}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>
          </section>

          <section className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-6">
            <div className={chartWrapClass}>
              <ChartTitle icon="🌐">소스별 게시물 Top 10</ChartTitle>
              <div className="flex-1 w-full min-h-[280px]">
                {model.topSources.length === 0 ? (
                  <p className="text-white/60 text-sm text-center py-16">데이터 없음</p>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={model.topSources}
                      layout="vertical"
                      margin={{ top: 4, right: 16, left: 8, bottom: 4 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.12)" />
                      <XAxis type="number" tick={{ fill: 'rgba(255,255,255,0.75)', fontSize: 11 }} allowDecimals={false} />
                      <YAxis
                        type="category"
                        dataKey="name"
                        width={80}
                        tick={{ fill: 'rgba(255,255,255,0.8)', fontSize: 10 }}
                      />
                      <Tooltip contentStyle={tooltipStyle} />
                      <Bar dataKey="count" name="게시물 수" fill="#60a5fa" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>

            <div className={chartWrapClass}>
              <ChartTitle icon="📡">사이트 유형별 현황</ChartTitle>
              <div className="flex-1 w-full min-h-[280px]">
                {model.postsBySiteType.length === 0 ? (
                  <p className="text-white/60 text-sm text-center py-16">데이터 없음</p>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={model.postsBySiteType}
                      margin={{ top: 8, right: 8, left: 0, bottom: 32 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.12)" />
                      <XAxis
                        dataKey="siteType"
                        tick={{ fill: 'rgba(255,255,255,0.75)', fontSize: 11 }}
                        angle={-20}
                        textAnchor="end"
                        height={56}
                      />
                      <YAxis tick={{ fill: 'rgba(255,255,255,0.75)', fontSize: 11 }} allowDecimals={false} />
                      <Tooltip contentStyle={tooltipStyle} />
                      <Bar dataKey="count" name="게시물" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>
          </section>

          <section className="grid grid-cols-1 gap-8">
            <div className={`${cardClass} overflow-x-auto`}>
              <h3
                className="text-white font-semibold text-lg mb-4"
                style={{ fontFamily: "'Noto Sans KR', sans-serif" }}
              >
                최근 수집된 게시물
              </h3>
              <div className={tablePanelClass}>
                <table className="w-full text-sm text-left min-w-[640px]">
                  <thead>
                    <tr className="border-b ">
                      <th className="py-3 px-3 font-semibold text-white">제목</th>
                      <th className="py-3 px-3 font-semibold text-white">카테고리</th>
                      <th className="py-3 px-3 font-semibold whitespace-nowrap text-white">수집 시간</th>
                    </tr>
                  </thead>
                  <tbody>
                    {model.recentPosts.length === 0 ? (
                      <tr>
                        <td colSpan={3} className="py-10 px-3 text-slate-600 text-center text-white">
                          게시물이 없습니다.
                        </td>
                      </tr>
                    ) : (
                      model.recentPosts.map((p) => {
                        const row = formatPostRow(p);
                        return (
                          <tr
                            key={row.key}
                            className="border-b border-slate-500/20 last:border-0 odd:bg-white/20"
                          >
                            <td className="py-3 px-3 max-w-md truncate text-slate-900 font-medium text-white">
                              {row.title}
                            </td>
                            <td className="py-3 px-3 text-slate-700 text-white">{row.cat}</td>
                            <td className="py-3 px-3 text-slate-600 whitespace-nowrap tabular-nums text-white">
                              {row.created}
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            <div className={`${cardClass} overflow-x-auto`}>
              <h3
                className="text-white font-semibold text-lg mb-4"
                style={{ fontFamily: "'Noto Sans KR', sans-serif" }}
              >
                최근 알림 발송 내역
              </h3>
              <div className={tablePanelClass}>
                <table className="w-full text-sm text-left min-w-[520px]">
                  <thead>
                    <tr className="border-b">
                      <th className="py-3 px-3 font-semibold text-white">채널</th>
                      <th className="py-3 px-3 font-semibold text-white">결과</th>
                      <th className="py-3 px-3 font-semibold whitespace-nowrap text-white">발송 시간</th>
                    </tr>
                  </thead>
                  <tbody>
                    {model.recentAlerts.length === 0 ? (
                      <tr>
                        <td colSpan={3} className="py-10 px-3 text-slate-600 text-center text-white">
                          알림 내역이 없습니다.
                        </td>
                      </tr>
                    ) : (
                      model.recentAlerts.map((a) => {
                        const row = formatAlertRow(a);
                        return (
                          <tr
                            key={row.key}
                            className="border-b border-slate-500/20 last:border-0 odd:bg-white/20"
                          >
                            <td className="py-3 px-3 text-slate-900 font-medium">{row.channel}</td>
                            <td className="py-3 px-3">
                              <span
                                className={
                                  row.ok === '성공'
                                    ? 'text-emerald-700 font-semibold'
                                    : 'text-red-600 font-semibold'
                                }
                              >
                                {row.ok}
                              </span>
                            </td>
                            <td className="py-3 px-3 text-slate-600 whitespace-nowrap tabular-nums">
                              {row.sent}
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </section>
        </>
      )}
    </main>
  );
}
