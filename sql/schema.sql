CREATE DATABASE IF NOT EXISTS darkweb_monitor
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE darkweb_monitor;

-- 1. sources: 크롤링 대상 사이트
CREATE TABLE IF NOT EXISTS sources (
    id              BIGINT          AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100)    NOT NULL,
    url             VARCHAR(500)    NOT NULL,
    site_type       VARCHAR(20)     NOT NULL DEFAULT 'forum',
    description     VARCHAR(500)    NULL,
    last_crawled_at DATETIME        NULL,
    is_active       TINYINT(1)      NOT NULL DEFAULT 1,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. posts: 수집된 게시물 (핵심 테이블)
CREATE TABLE IF NOT EXISTS posts (
    id              BIGINT          AUTO_INCREMENT PRIMARY KEY,
    source_id       BIGINT          NOT NULL,
    title           VARCHAR(500)    NOT NULL,
    author          VARCHAR(200)    NULL,
    content         TEXT            NULL,
    published_at    DATETIME        NULL,
    content_hash    VARCHAR(64)     NOT NULL,
    category        VARCHAR(20)     NOT NULL DEFAULT 'other',
    tags            JSON            NULL,
    victim_info     JSON            NULL,
    original_url    VARCHAR(500)    NULL,
    raw_data        JSON            NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_posts_source FOREIGN KEY (source_id) REFERENCES sources(id),
    UNIQUE KEY uk_content_hash (content_hash),
    INDEX idx_published_at (published_at),
    INDEX idx_category (category),
    INDEX idx_author (author),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB;

-- 3. alerts: 발송된 알림 기록
CREATE TABLE IF NOT EXISTS alerts (
    id              BIGINT          AUTO_INCREMENT PRIMARY KEY,
    post_id         BIGINT          NOT NULL,
    channel         VARCHAR(20)     NOT NULL,
    message         TEXT            NULL,
    sent_at         DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_success      TINYINT(1)      NOT NULL DEFAULT 1,
    error_message   VARCHAR(500)    NULL,

    CONSTRAINT fk_alerts_post FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    INDEX idx_post_id (post_id),
    INDEX idx_sent_at (sent_at)
) ENGINE=InnoDB;

-- 초기 데이터
INSERT IGNORE INTO sources (id, name, url, site_type, description) VALUES
(1, 'BreachForums', 'http://example.onion', 'forum', '해커 포럼'),
(2, 'LockBit Blog', 'http://example2.onion', 'ransomware', 'LockBit 랜섬웨어 조직'),
(3, 'RansomwareLive', 'https://www.ransomware.live', 'other', '랜섬웨어 피해 통합 모니터링');

-- 이메일 유출 조회 테스트용 더미 데이터
INSERT IGNORE INTO posts (source_id, title, author, content, published_at, content_hash, category, tags, victim_info) VALUES
(1, 'Company ABC Customer DB - 500K Records',
 'dark_hacker_01',
 'Leaked emails include: test@example.com, user123@gmail.com, admin@company.kr\nFull database with passwords.',
 '2026-03-18 15:30:00',
 SHA2('abc_customer_db_500k', 256),
 'leak_data',
 '["database", "email", "usa"]',
 '{"org": "Company ABC", "country": "US", "industry": "retail", "records": 500000}'
),
(1, 'Korean Portal Site Combo List 2M',
 'stealer_king',
 'Fresh combo list from Korean portal. Emails: victim@naver.com, test@example.com, hello@daum.net',
 '2026-03-20 09:00:00',
 SHA2('korean_portal_combo_2m', 256),
 'combo_list',
 '["combo", "korea", "portal"]',
 '{"org": "Korean Portal", "country": "KR", "records": 2000000}'
),
(2, 'XYZ Corp Ransomware - Data Published',
 'LockBit',
 'XYZ Corp refused to pay. Publishing internal docs and employee emails: staff@xyzcorp.com',
 '2026-03-22 12:00:00',
 SHA2('lockbit_xyz_corp', 256),
 'ransomware',
 '["lockbit", "korea", "manufacturing"]',
 '{"org": "XYZ Corp", "country": "KR", "industry": "manufacturing"}'
);
