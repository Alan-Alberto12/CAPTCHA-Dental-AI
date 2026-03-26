import React, { useState, useEffect, useCallback } from 'react';
import { API_URL } from '../config';

function authHeaders() {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// ─── Config ───────────────────────────────────────────────────────────────────

const CATEGORIES = [
  {
    key: 'lifetime_points',
    label: 'Lifetime Points',
    icon: '⭐',
    description: 'All-time points leaders',
    valueKey: 'total_points',
    valueSuffix: 'pts',
    color: '#f59e0b',
  },
  {
    key: 'weekly_mvp',
    label: "This Week's MVP",
    icon: '🏆',
    description: 'Most points earned this week',
    valueKey: 'weekly_points',
    valueSuffix: 'pts',
    color: '#8b5cf6',
  },
  {
    key: 'daily_contributors',
    label: 'Daily Contributors',
    icon: '🔥',
    description: 'Most sessions completed today',
    valueKey: 'sessions_today',
    valueSuffix: 'sessions',
    color: '#ef4444',
  },
  {
    key: 'longest_streak',
    label: 'Longest Streak',
    icon: '⚡',
    description: 'Consecutive days active',
    valueKey: 'streak_days',
    valueSuffix: 'days',
    color: '#3b82f6',
  },
  {
    key: 'most_consistent',
    label: 'Most Consistent',
    icon: '📈',
    description: 'Highest avg sessions per active day',
    valueKey: 'avg_sessions_per_day',
    valueSuffix: 'avg/day',
    color: '#10b981',
  },
];

const POINTS_INFO = [
  { label: 'Session Complete',    value: '+100', icon: '✅', desc: 'Per completed session' },
  { label: 'First Session Today', value: '+50',  icon: '🌅', desc: 'Daily first-session bonus' },
  { label: 'Thoughtful Review',   value: '+25',  icon: '🧠', desc: 'Avg 30s+ per image' },
  { label: 'No Skips',            value: '+50',  icon: '💯', desc: 'All images reviewed' },
  { label: '3 Sessions / Day',    value: '+75',  icon: '📦', desc: 'Volume bonus' },
  { label: '5 Sessions / Day',    value: '+150', icon: '📦', desc: 'Volume bonus' },
  { label: '10 Sessions / Day',   value: '+300', icon: '📦', desc: 'Volume bonus' },
  { label: '2-Day Streak',        value: '+20',  icon: '🔥', desc: 'Streak bonus' },
  { label: '3-Day Streak',        value: '+30',  icon: '🔥', desc: 'Streak bonus' },
  { label: '7-Day Streak',        value: '+100', icon: '🔥', desc: 'Milestone streak' },
  { label: '30-Day Streak',       value: '+500', icon: '🔥', desc: 'Achievement streak' },
];

// ─── Sub-components ───────────────────────────────────────────────────────────

function RankBadge({ rank }) {
  if (rank === 1) return <span className="text-2xl leading-none">🥇</span>;
  if (rank === 2) return <span className="text-2xl leading-none">🥈</span>;
  if (rank === 3) return <span className="text-2xl leading-none">🥉</span>;
  return (
    <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-[#3a3c56] text-[#F4EBD3] text-sm font-bold">
      {rank}
    </span>
  );
}

function formatValue(val) {
  if (typeof val !== 'number') return val;
  return Number.isInteger(val) ? val.toLocaleString() : val.toFixed(2);
}

function Podium({ entries, category }) {
  if (!entries || entries.length < 3) return null;

  const PodiumSlot = ({ entry, medal, bgClass, textClass, subClass, extraPaddingTop }) => (
    <div className={`flex flex-col items-center ${extraPaddingTop || ''}`}>
      <span className="text-3xl mb-2 leading-none">{medal}</span>
      <div className={`${bgClass} rounded-2xl w-full px-3 py-4 text-center shadow-lg`}>
        <p className={`font-bold text-sm truncate ${textClass}`}>{entry.username}</p>
        <p className={`font-bold text-xl mt-1 ${textClass}`}>
          {formatValue(entry[category.valueKey])}
        </p>
        <p className={`text-xs mt-0.5 ${subClass}`}>{category.valueSuffix}</p>
      </div>
    </div>
  );

  return (
    <div className="grid grid-cols-3 gap-3 mb-6 items-end">
      <PodiumSlot entry={entries[1]} medal="🥈" bgClass="bg-gray-400"
        textClass="text-gray-800" subClass="text-gray-600" extraPaddingTop="pt-6" />
      <PodiumSlot entry={entries[0]} medal="🥇" bgClass="bg-yellow-400"
        textClass="text-yellow-900" subClass="text-yellow-700" />
      <PodiumSlot entry={entries[2]} medal="🥉" bgClass="bg-amber-600"
        textClass="text-amber-100" subClass="text-amber-300" extraPaddingTop="pt-10" />
    </div>
  );
}

function LeaderboardTable({ entries, category, currentUserId }) {
  if (!entries || entries.length === 0) {
    return (
      <div className="text-center py-10 text-[#c9bfa8] text-sm italic">
        No data yet — be the first on the board!
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {entries.map((entry) => {
        const isMe = entry.user_id === currentUserId;
        return (
          <div
            key={entry.user_id}
            className={`flex items-center gap-3 rounded-xl px-4 py-3 transition-all
              ${isMe
                ? 'bg-[#F4EBD3] shadow-md scale-[1.01]'
                : entry.rank <= 3
                  ? 'bg-[#3a3c56] shadow-sm'
                  : 'bg-[#3a3c56]/60 hover:bg-[#3a3c56]'
              }`}
          >
            <div className="w-9 flex items-center justify-center shrink-0">
              <RankBadge rank={entry.rank} />
            </div>

            <div className="flex-1 min-w-0">
              <p className={`font-semibold truncate ${isMe ? 'text-[#525470]' : 'text-[#F4EBD3]'}`}>
                {entry.username}
                {isMe && (
                  <span className="ml-2 text-xs font-bold bg-[#525470] text-[#F4EBD3] px-2 py-0.5 rounded-full">
                    You
                  </span>
                )}
              </p>
            </div>

            <div className="text-right shrink-0">
              <span
                className="text-lg font-bold"
                style={{ color: isMe ? '#525470' : category.color }}
              >
                {formatValue(entry[category.valueKey])}
              </span>
              <span className={`ml-1 text-xs ${isMe ? 'text-[#525470]/70' : 'text-[#c9bfa8]'}`}>
                {category.valueSuffix}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function CategoryCard({ category, entries, isActive, onClick }) {
  const topUser = entries?.[0];
  return (
    <button
      onClick={onClick}
      className={`w-full text-left rounded-2xl p-4 transition-all border-2
        ${isActive
          ? 'bg-[#F4EBD3] border-[#F4EBD3] shadow-md'
          : 'bg-[#3a3c56] border-transparent hover:border-[#c9bfa8]/40 hover:bg-[#444660]'
        }`}
    >
      <div className="flex items-center gap-3">
        <span className="text-2xl leading-none">{category.icon}</span>
        <div className="min-w-0">
          <p className={`font-bold text-sm ${isActive ? 'text-[#525470]' : 'text-[#F4EBD3]'}`}>
            {category.label}
          </p>
          <p className={`text-xs truncate ${isActive ? 'text-[#525470]/70' : 'text-[#c9bfa8]'}`}>
            {category.description}
          </p>
        </div>
      </div>
      {topUser && (
        <p className={`mt-2 text-xs truncate ${isActive ? 'text-[#525470]/80' : 'text-[#c9bfa8]'}`}>
          🥇 {topUser.username}
        </p>
      )}
    </button>
  );
}

function SkeletonRow() {
  return (
    <div className="flex items-center gap-3 rounded-xl px-4 py-3 bg-[#3a3c56]/60 animate-pulse">
      <div className="w-8 h-8 rounded-full bg-[#525470]" />
      <div className="flex-1 h-4 rounded bg-[#525470]" />
      <div className="w-16 h-4 rounded bg-[#525470]" />
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────

export default function Leaderboard() {
  const [activeCategory, setActiveCategory] = useState('lifetime_points');
  const [showPointsInfo, setShowPointsInfo] = useState(false);

  const [leaderboardData, setLeaderboardData] = useState(null);
  const [myStats, setMyStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Public leaderboard — no auth required
      const lbRes = await fetch(`${API_URL}/leaderboard`);
      if (!lbRes.ok) throw new Error(`Failed to load leaderboard (${lbRes.status})`);
      const lbData = await lbRes.json();
      setLeaderboardData(lbData);

      // My stats — only if logged in
      const token = localStorage.getItem('token');
      if (token) {
        const meRes = await fetch(`${API_URL}/leaderboard/me`, { headers: authHeaders() });
        if (meRes.ok) {
          const meData = await meRes.json();
          setMyStats(meData);
        }
        // If 401/403, leave myStats null — user still sees leaderboard
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const activeCategoryObj = CATEGORIES.find(c => c.key === activeCategory);
  const activeEntries = leaderboardData?.[activeCategory] ?? [];

  return (
    <div className="min-h-screen bg-[#98A1BC] pb-20 md:pb-8">
      <div className="max-w-6xl mx-auto px-4 pt-8">

        {/* Page Header */}
        <div className="flex items-center gap-4 justify-between mb-6">
          <div />
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowPointsInfo(v => !v)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl font-semibold text-sm transition-colors shadow-sm
                ${showPointsInfo
                  ? 'bg-[#F4EBD3] text-[#525470]'
                  : 'bg-[#525470] text-[#F4EBD3] hover:bg-[#3a3c56]'
                }`}
            >
              <span>💡</span> How Points Work
            </button>
          </div>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="mb-6 bg-red-100 text-red-800 rounded-2xl px-5 py-4 text-sm font-semibold shadow">
            Failed to load leaderboard: {error}
          </div>
        )}

        {/* Points Info Panel */}
        {showPointsInfo && (
          <div className="mb-6 bg-[#525470] rounded-3xl p-6 shadow-lg">
            <h2 className="text-xl font-bold text-[#F4EBD3] mb-4">Points Breakdown</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {POINTS_INFO.map((item, i) => (
                <div key={i} className="bg-[#3a3c56] rounded-2xl px-4 py-3">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-lg leading-none">{item.icon}</span>
                    <span className="text-green-400 font-bold text-sm">{item.value}</span>
                  </div>
                  <p className="text-[#F4EBD3] font-semibold text-xs">{item.label}</p>
                  <p className="text-[#c9bfa8] text-xs mt-0.5">{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* My Stats Banner */}
        {myStats && (
          <div className="mb-6 bg-[#525470] rounded-3xl p-5 shadow-lg">
            <p className="text-[#F4EBD3] text-lg font-bold uppercase tracking-wide mb-3">Your Stats</p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-[#3a3c56] rounded-2xl p-4 text-center">
                <p className="text-[#c9bfa8] text-xs mb-1">Total Points</p>
                <p className="text-3xl font-bold text-yellow-400">{myStats.total_points.toLocaleString()}</p>
              </div>
              <div className="bg-[#3a3c56] rounded-2xl p-4 text-center">
                <p className="text-[#c9bfa8] text-xs mb-1">Daily Streak</p>
                <p className="text-3xl font-bold text-orange-400">
                  {myStats.daily_streak}
                  <span className="text-base ml-1">🔥</span>
                </p>
              </div>
              <div className="bg-[#3a3c56] rounded-2xl p-4 text-center col-span-2">
                <p className="text-[#c9bfa8] text-xs mb-1">Username</p>
                <p className="text-2xl font-bold text-[#F4EBD3] truncate">{myStats.username}</p>
              </div>
            </div>
          </div>
        )}

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* Category Selector */}
          <div className="lg:col-span-1 space-y-3">
            <p className="text-[#F4EBD3]/70 text-xs font-semibold uppercase tracking-wide mb-2 px-1">
              Categories
            </p>
            {CATEGORIES.map(cat => (
              <CategoryCard
                key={cat.key}
                category={cat}
                entries={leaderboardData?.[cat.key] ?? []}
                isActive={activeCategory === cat.key}
                onClick={() => setActiveCategory(cat.key)}
              />
            ))}
          </div>

          {/* Active Leaderboard */}
          <div className="lg:col-span-2">
            <div className="bg-[#525470] rounded-3xl p-6 shadow-lg">

              {/* Category Header */}
              <div className="flex items-center gap-3 mb-6">
                <span className="text-4xl leading-none">{activeCategoryObj?.icon}</span>
                <div>
                  <h2 className="text-2xl font-bold text-[#F4EBD3]">{activeCategoryObj?.label}</h2>
                  <p className="text-[#c9bfa8] text-sm">{activeCategoryObj?.description}</p>
                </div>
              </div>

              {loading ? (
                <div className="space-y-2">
                  {Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} />)}
                </div>
              ) : (
                <>
                  {/* Podium */}
                  <Podium entries={activeEntries} category={activeCategoryObj} />

                  {/* Full Rankings */}
                  <div>
                    <p className="text-[#c9bfa8] text-xs font-semibold uppercase tracking-wide mb-3">
                      Full Rankings
                    </p>
                    <LeaderboardTable
                      entries={activeEntries}
                      category={activeCategoryObj}
                      currentUserId={myStats?.user_id}
                    />
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
