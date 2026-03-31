import React, { useEffect, useState } from 'react';
import './Hero.css';


export default function Hero() {
  const [category, setCategory] = useState('group');
  const [query, setQuery] = useState('');
  const [categories, setCategories] = useState(['group', 'country', 'victim_info']);
  const [hasError, setHasError] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadCategories() {
      try {
        const res = await fetch('http://localhost:8000/api/categories');
        if (!res.ok) throw new Error('cat fetch failed');
        const items = await res.json();
        if (Array.isArray(items) && items.length > 0) {
          setCategories(items);
          if (!items.includes(category)) setCategory(items[0]);
        }
      } catch (_err) {
        // 기본값 유지
      }
    }

    loadCategories();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- 카테고리 목록은 마운트 시 1회만 로드
  }, []);

  const validateCategory = (value) => {
    if (!value || !value.trim()) return '분류를 선택해주세요.';
    return '';
  };

  const validateQuery = (value) => {
    if (!value || !value.trim()) return '조회하실 내용을 입력해주세요.';
    return '';
  };

  const handleCategoryChange = (e) => {
    const next = e.target.value;
    setCategory(next);
    if (hasError) {
      const nextError = validateCategory(next) || validateQuery(query);
      setError(nextError);
      setHasError(Boolean(nextError));
    }
  };

  const handleQueryChange = (e) => {
    const next = e.target.value;
    setQuery(next);
    if (hasError) {
      const nextError = validateCategory(category) || validateQuery(next);
      setError(nextError);
      setHasError(Boolean(nextError));
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();

    const categoryError = validateCategory(category);
    const queryError = validateQuery(query);
    const msg = categoryError || queryError;

    if (msg) {
      setError(msg);
      setHasError(true);
      return;
    }

    setError('');
    setHasError(false);
    setLoading(true);
    setResult(null);

    try {
      const res = await fetch('http://localhost:8000/api/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ category, query }),
      });

      if (!res.ok) {
        throw new Error(`server error: ${res.status}`);
      }

      const json = await res.json();
      setResult(json);
    } catch (_err) {
      setError('서버 연결에 실패했습니다. 백엔드가 실행 중인지 확인해주세요.');
      setHasError(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="hero">
      <div className="hero__title-wrapper">
        <h1 className="hero__title-main">Have I been detected</h1>
        <div className="hero__title-by-row">
          <span className="hero__title-by">by</span>
          <span className="hero__title-sentinel">Sentinel</span>
        </div>
      </div>

      <p className="hero__description">
        내 정보가 유출되었는지 확인하세요
      </p>

      <div className="hero__search-wrapper">
        <form
          onSubmit={handleSearch}
          className={`hero__search-form${hasError ? ' hero__search-form--error' : ''}`}
        >
          <select
            id="category"
            value={category}
            onChange={handleCategoryChange}
            className="hero__search-input"
            style={{ maxWidth: '150px' }}
          >
            {categories.map((item) => (
              <option key={item} value={item}>
                {item === 'group' ? '그룹' : item === 'country' ? '국가' : item === 'victim_info' ? '피해자' : item}
              </option>
            ))}
          </select>
          <input
            type="text"
            value={query}
            onChange={handleQueryChange}
            placeholder="조회하실 내용을 입력하세요"
            className="hero__search-input"
          />
          <button type="submit" className="hero__search-btn">
            조회하기
          </button>
        </form>
        {hasError && (
          <p className="hero__error-msg">
            <span>⚠</span>
            <span>{error}</span>
          </p>
        )}
      </div>

      {loading && (
        <div className="mt-6 w-full max-w-2xl text-left text-white/90">
          조회 중입니다...
        </div>
      )}

      {result && !loading && (
        <div className="mt-6 w-full max-w-2xl text-left">
          {result.is_leaked ? (
            <div>
              <div className="bg-red-500/30 backdrop-blur-sm border border-red-400/40 rounded-2xl px-7 py-5 mb-4">
                <p className="text-red-300 text-xl font-bold mb-1">⚠ 유출이 감지되었습니다</p>
                <p className="text-white/90">
                  선택된 분류 ({category})가 유출 데이터에서 발견되었습니다.
                </p>
                <p className="text-white/90">
                  {result.leak_count ?? 0}건의 유출 데이터에 포함되어 있습니다.
                </p>
              </div>

              {Array.isArray(result.records) && result.records.length > 0 && (
                <ul className="flex flex-col gap-3">
                  {result.records.map((record) => (
                    <li
                      key={record.id || `${record.source_name}-${record.category}`}
                      className="bg-blue-300/20 backdrop-blur-sm border border-blue-400/30 rounded-xl px-6 py-4"
                    >
                      <p className="text-white font-semibold">{record.title || 'unnamed'}</p>
                      <p className="text-white text-sm mt-1">
                        출처: {record.source_name} · 유형: {record.category}
                      </p>
                      {record.published_at && (
                        <p className="text-white text-sm">
                          날짜: {new Date(record.published_at).toLocaleDateString('ko-KR')}
                        </p>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ) : (
            <div className="bg-green-500/20 backdrop-blur-sm border border-green-400/30 rounded-2xl px-7 py-5">
              <p className="text-green-600 text-xl font-bold mb-1">✓ 안전합니다</p>
              <p className="text-white">
                선택된 분류 ({category})는 현재 수집된 유출 데이터에서 발견되지 않았습니다.
              </p>
            </div>
          )}
        </div>
      )}
    </main>
  );
}