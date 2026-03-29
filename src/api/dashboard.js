import { getApiBase } from './config';

/**
 * @typedef {Object} DashboardModel
 * @property {Object} summary
 * @property {number} summary.totalPosts
 * @property {number} summary.activeSources
 * @property {number} summary.newPostsToday
 * @property {number} summary.newPostsThisWeek
 * @property {number} summary.alertSuccessRate
 * @property {{ monthKey: string, label: string, count: number }[]} postsByMonth
 * @property {{ name: string, count: number }[]} postsByCategory
 * @property {{ name: string, count: number }[]} topSources
 * @property {{ siteType: string, count: number }[]} postsBySiteType
 * @property {{ channel: string, count: number }[]} alertsByChannel
 * @property {{ success: number, failure: number }} alertOutcomes
 * @property {Object[]} recentPosts
 * @property {Object[]} recentAlerts
 */

function startOfLocalDay(d) {
  const x = new Date(d);
  x.setHours(0, 0, 0, 0);
  return x;
}

function startOfLocalWeekMonday(d) {
  const x = startOfLocalDay(d);
  const day = x.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  x.setDate(x.getDate() + diff);
  return x;
}

function parseDate(value) {
  if (value == null || value === '') return null;
  const t = new Date(value);
  return Number.isNaN(t.getTime()) ? null : t;
}

function monthKeyFromDate(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  return `${y}-${m}`;
}

function monthLabelKo(d) {
  return `${d.getFullYear()}년 ${d.getMonth() + 1}월`;
}

async function fetchJsonSafe(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

function unwrapList(payload) {
  if (payload == null) return [];
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload.items)) return payload.items;
  if (Array.isArray(payload.data)) return payload.data;
  if (Array.isArray(payload.results)) return payload.results;
  return [];
}

/**
 * Raw posts / sources / alerts → aggregated dashboard model.
 * @param {Object[]} posts
 * @param {Object[]} sources
 * @param {Object[]} alerts
 * @returns {DashboardModel}
 */
export function buildDashboardModel(posts, sources, alerts) {
  const postList = Array.isArray(posts) ? posts : [];
  const sourceList = Array.isArray(sources) ? sources : [];
  const alertList = Array.isArray(alerts) ? alerts : [];

  const now = new Date();
  const dayStart = startOfLocalDay(now);
  const weekStart = startOfLocalWeekMonday(now);

  const totalPosts = postList.length;

  const activeSources = sourceList.filter(
    (s) => s.is_active === 1 || s.is_active === true
  ).length;

  const newPostsToday = postList.filter((p) => {
    const c = parseDate(p.created_at);
    return c && c >= dayStart;
  }).length;

  const newPostsThisWeek = postList.filter((p) => {
    const c = parseDate(p.created_at);
    return c && c >= weekStart;
  }).length;

  const successAlerts = alertList.filter(
    (a) => a.is_success === 1 || a.is_success === true
  );
  const alertSuccessRate =
    alertList.length > 0
      ? Math.round((1000 * successAlerts.length) / alertList.length) / 10
      : 0;

  const sourceById = new Map();
  sourceList.forEach((s) => {
    const id = s.id ?? s.source_id;
    if (id != null) sourceById.set(Number(id), s);
  });

  /** 최근 12개월(당월 포함)만 집계 */
  const monthKeysOrdered = [];
  for (let i = 11; i >= 0; i -= 1) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    monthKeysOrdered.push(monthKeyFromDate(d));
  }
  const monthCounts = new Map(monthKeysOrdered.map((k) => [k, 0]));

  postList.forEach((p) => {
    const pd = parseDate(p.published_at) || parseDate(p.created_at);
    if (!pd) return;
    const key = monthKeyFromDate(pd);
    if (monthCounts.has(key)) {
      monthCounts.set(key, monthCounts.get(key) + 1);
    }
  });

  const postsByMonth = monthKeysOrdered.map((monthKey) => {
    const count = monthCounts.get(monthKey) || 0;
    const [y, m] = monthKey.split('-').map(Number);
    const d = new Date(y, m - 1, 1);
    return { monthKey, label: monthLabelKo(d), count };
  });

  const catCounts = new Map();
  postList.forEach((p) => {
    const c = p.category != null && String(p.category).trim() !== ''
      ? String(p.category)
      : '미분류';
    catCounts.set(c, (catCounts.get(c) || 0) + 1);
  });
  const postsByCategory = Array.from(catCounts.entries())
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count);

  const sourcePostCounts = new Map();
  postList.forEach((p) => {
    const sid = p.source_id;
    if (sid == null) return;
    const n = Number(sid);
    sourcePostCounts.set(n, (sourcePostCounts.get(n) || 0) + 1);
  });
  const topSources = Array.from(sourcePostCounts.entries())
    .map(([id, count]) => {
      const s = sourceById.get(id);
      const name = s?.name || `소스 #${id}`;
      return { name, count };
    })
    .sort((a, b) => b.count - a.count)
    .slice(0, 10);

  const siteTypeCounts = new Map();
  postList.forEach((p) => {
    const sid = p.source_id;
    if (sid == null) return;
    const s = sourceById.get(Number(sid));
    const st =
      s?.site_type != null && String(s.site_type).trim() !== ''
        ? String(s.site_type)
        : '미지정';
    siteTypeCounts.set(st, (siteTypeCounts.get(st) || 0) + 1);
  });
  const postsBySiteType = Array.from(siteTypeCounts.entries())
    .map(([siteType, count]) => ({ siteType, count }))
    .sort((a, b) => b.count - a.count);

  const channelCounts = new Map();
  alertList.forEach((a) => {
    const ch =
      a.channel != null && String(a.channel).trim() !== ''
        ? String(a.channel)
        : '기타';
    channelCounts.set(ch, (channelCounts.get(ch) || 0) + 1);
  });
  const alertsByChannel = Array.from(channelCounts.entries())
    .map(([channel, count]) => ({ channel, count }))
    .sort((a, b) => b.count - a.count);

  const failureCount = alertList.length - successAlerts.length;
  const alertOutcomes = {
    success: successAlerts.length,
    failure: Math.max(0, failureCount),
  };

  const recentPosts = [...postList]
    .sort((a, b) => {
      const ta = parseDate(a.created_at)?.getTime() ?? 0;
      const tb = parseDate(b.created_at)?.getTime() ?? 0;
      return tb - ta;
    })
    .slice(0, 20);

  const recentAlerts = [...alertList]
    .sort((a, b) => {
      const ta = parseDate(a.sent_at)?.getTime() ?? 0;
      const tb = parseDate(b.sent_at)?.getTime() ?? 0;
      return tb - ta;
    })
    .slice(0, 20);

  return {
    summary: {
      totalPosts,
      activeSources,
      newPostsToday,
      newPostsThisWeek,
      alertSuccessRate,
    },
    postsByMonth,
    postsByCategory,
    topSources,
    postsBySiteType,
    alertsByChannel,
    alertOutcomes,
    recentPosts,
    recentAlerts,
  };
}

/**
 * Normalize `/api/dashboard` JSON (snake_case or camelCase).
 * @param {Object} raw
 * @returns {DashboardModel}
 */
export function normalizeDashboardResponse(raw) {
  const empty = buildDashboardModel([], [], []);
  if (!raw || typeof raw !== 'object') return empty;

  const s = raw.summary || {};
  const num = (v, d = 0) =>
    typeof v === 'number' && !Number.isNaN(v) ? v : d;

  const pickSeries = (arr, mapRow) => {
    if (!Array.isArray(arr)) return [];
    return arr.map(mapRow).filter(Boolean);
  };

  const postsByMonth = pickSeries(raw.posts_by_month || raw.postsByMonth, (row) => ({
    monthKey: row.month_key || row.monthKey || '',
    label: row.label || row.month_key || '',
    count: num(row.count, 0),
  })).filter((r) => r.monthKey || r.label);

  const postsByCategory = pickSeries(
    raw.posts_by_category || raw.postsByCategory,
    (row) => ({
      name: row.category != null ? String(row.category) : row.name != null ? String(row.name) : '미분류',
      count: num(row.count, 0),
    })
  );

  const topSources = pickSeries(raw.top_sources || raw.topSources, (row) => ({
    name: row.name != null ? String(row.name) : '—',
    count: num(row.count, 0),
  }));

  const postsBySiteType = pickSeries(
    raw.posts_by_site_type || raw.postsBySiteType,
    (row) => ({
      siteType:
        row.site_type != null
          ? String(row.site_type)
          : row.siteType != null
            ? String(row.siteType)
            : '미지정',
      count: num(row.count, 0),
    })
  );

  const alertsByChannel = pickSeries(
    raw.alerts_by_channel || raw.alertsByChannel,
    (row) => ({
      channel: row.channel != null ? String(row.channel) : '기타',
      count: num(row.count, 0),
    })
  );

  const ao = raw.alert_outcomes || raw.alertOutcomes || {};
  const alertOutcomes = {
    success: num(ao.success, 0),
    failure: num(ao.failure, 0),
  };

  return {
    summary: {
      totalPosts: num(
        s.total_posts ?? s.totalPosts,
        empty.summary.totalPosts
      ),
      activeSources: num(
        s.active_sources ?? s.activeSources,
        empty.summary.activeSources
      ),
      newPostsToday: num(
        s.new_posts_today ?? s.newPostsToday,
        empty.summary.newPostsToday
      ),
      newPostsThisWeek: num(
        s.new_posts_this_week ?? s.newPostsThisWeek,
        empty.summary.newPostsThisWeek
      ),
      alertSuccessRate: num(
        s.alert_success_rate ?? s.alertSuccessRate,
        empty.summary.alertSuccessRate
      ),
    },
    postsByMonth: postsByMonth.length ? postsByMonth : empty.postsByMonth,
    postsByCategory: postsByCategory.length
      ? postsByCategory
      : empty.postsByCategory,
    topSources: topSources.length ? topSources : empty.topSources,
    postsBySiteType: postsBySiteType.length
      ? postsBySiteType
      : empty.postsBySiteType,
    alertsByChannel: alertsByChannel.length
      ? alertsByChannel
      : empty.alertsByChannel,
    alertOutcomes:
      alertOutcomes.success + alertOutcomes.failure > 0
        ? alertOutcomes
        : empty.alertOutcomes,
    recentPosts: Array.isArray(raw.recent_posts)
      ? raw.recent_posts
      : Array.isArray(raw.recentPosts)
        ? raw.recentPosts
        : [],
    recentAlerts: Array.isArray(raw.recent_alerts)
      ? raw.recent_alerts
      : Array.isArray(raw.recentAlerts)
        ? raw.recentAlerts
        : [],
  };
}

/** @returns {Promise<{ data: DashboardModel }>} */
export async function loadDashboardData() {
  const base = getApiBase();

  const dashUrl = `${base}/api/dashboard`;
  const dashRaw = await fetchJsonSafe(dashUrl);
  if (
    dashRaw &&
    typeof dashRaw === 'object' &&
    !Array.isArray(dashRaw)
  ) {
    return { data: normalizeDashboardResponse(dashRaw) };
  }

  const [postsJ, sourcesJ, alertsJ] = await Promise.all([
    fetchJsonSafe(`${base}/api/posts`),
    fetchJsonSafe(`${base}/api/sources`),
    fetchJsonSafe(`${base}/api/alerts`),
  ]);

  const posts = unwrapList(postsJ);
  const sources = unwrapList(sourcesJ);
  const alerts = unwrapList(alertsJ);

  return { data: buildDashboardModel(posts, sources, alerts) };
}
