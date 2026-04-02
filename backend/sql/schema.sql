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

-- 4. 크롤러 테이블 (크롤러가 수집한 데이터)
CREATE TABLE IF NOT EXISTS domains (
    id              INT             AUTO_INCREMENT PRIMARY KEY,
    uuid            VARCHAR(32)     UNIQUE,
    scheme          VARCHAR(5)      NOT NULL,
    netloc          VARCHAR(255)    UNIQUE NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS emails (
    id              INT             AUTO_INCREMENT PRIMARY KEY,
    email           VARCHAR(255)    UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS addresses (
    id              INT             AUTO_INCREMENT PRIMARY KEY,
    address         VARCHAR(34)     UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS email_identifier (
    domain_id       INT,
    email_id        INT,
    FOREIGN KEY (domain_id) REFERENCES domains(id),
    FOREIGN KEY (email_id) REFERENCES emails(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS address_identifier (
    domain_id       INT,
    email_id        INT,
    FOREIGN KEY (domain_id) REFERENCES domains(id),
    FOREIGN KEY (email_id) REFERENCES addresses(id)
) ENGINE=InnoDB;

-- 초기 데이터

-- 크롤러 테스트 데이터
INSERT IGNORE INTO domains (id, uuid, scheme, netloc) VALUES
(1, 'a1b2c3d4e5f6', 'http', 'breachforum1234.onion'),
(2, 'f6e5d4c3b2a1', 'http', 'darkmarket5678.onion');

INSERT IGNORE INTO emails (id, email) VALUES
(1, 'leaked@company.kr'),
(2, 'admin@targetcorp.com'),
(3, 'test@example.com'),
(4, 'victim@naver.com');

INSERT IGNORE INTO email_identifier (domain_id, email_id) VALUES
(1, 1), (1, 2), (1, 3),
(2, 3), (2, 4);

INSERT IGNORE INTO sources (id, name, url, site_type, description) VALUES
(1, 'BreachForums', 'http://example.onion', 'forum', '해커 포럼'),
(2, 'LockBit Blog', 'http://example2.onion', 'ransomware', 'LockBit 랜섬웨어 조직'),
(3, 'RansomwareLive', 'https://www.ransomware.live', 'other', '랜섬웨어 피해 통합 모니터링');

-- 실제 파서 출력 형식에 맞춘 테스트 데이터
INSERT IGNORE INTO posts (source_id, title, author, content, published_at, content_hash, category, tags, victim_info, original_url, raw_data) VALUES
(3, 'SATS Sports Club Sweden',
 'thegentlemen',
 'sats.se zoominfo.com/c/sats-sports-club-sweden-ab/431547514 SATS is the largest fitness chain in the Nordics, founded in Sweden in 1995 with a mission to make people healthier and happier.',
 '2026-03-22 10:37:09',
 SHA2('sats_sports_club_sweden', 256),
 'ransomware',
 '["thegentlemen"]',
 '{"domain": "sats.se"}',
 'http://tezwsse5cz11ksjb7cwp65rvnk4oobmzti2znn42i43bjdfd2prqqkad.onion/',
 '{"activity": "Not Found", "attackdate": "2026-03-22 10:37:09.000000", "claim_url": "http://tezwsse5cz11ksjb7cwp65rvnk4oobmzti2znn42i43bjdfd2prqqkad.onion/", "country": "SE", "domain": "sats.se", "group": "thegentlemen", "screenshot": "https://images.ransomware.live/victims/8c47959c80ef37fb0095eb6ecb94c7a8.png", "infostealer": {"employees": 0, "users": 0}}'
),
(3, 'Hyundai Motor Europe',
 'blackbasta',
 'hyundai.com Hyundai Motor Europe GmbH based in Germany. Major automotive manufacturer with operations across Europe.',
 '2026-03-20 08:15:00',
 SHA2('hyundai_motor_europe', 256),
 'ransomware',
 '["blackbasta"]',
 '{"domain": "hyundai.com"}',
 'http://stniiomyjliimcgkvdszvgen3eaaoz55hreqqx6o77yvmpwt7gklffqd.onion/',
 '{"activity": "Not Found", "attackdate": "2026-03-20 08:15:00.000000", "claim_url": "http://stniiomyjliimcgkvdszvgen3eaaoz55hreqqx6o77yvmpwt7gklffqd.onion/", "country": "DE", "domain": "hyundai.com", "group": "blackbasta", "screenshot": "https://images.ransomware.live/victims/hyundai_motor_europe.png", "infostealer": {"employees": 0, "users": 0}}'
),
(3, 'Korean National University Hospital',
 'lockbit',
 'knuh.kr Korean National University Hospital leaked. Contains patient records and employee emails: admin@knuh.kr, test@example.com',
 '2026-03-21 14:00:00',
 SHA2('knuh_hospital', 256),
 'ransomware',
 '["lockbit"]',
 '{"domain": "knuh.kr"}',
 'http://lockbit3olp7oetlc70ftef8neffk2ros7ujawd2h4zgbli2regms3yd.onion/',
 '{"activity": "Published", "attackdate": "2026-03-21 14:00:00.000000", "claim_url": "http://lockbit3olp7oetlc70ftef8neffk2ros7ujawd2h4zgbli2regms3yd.onion/", "country": "KR", "domain": "knuh.kr", "group": "lockbit", "screenshot": "https://images.ransomware.live/victims/knuh_hospital.png", "infostealer": {"employees": 500, "users": 12000}}'
),
(1, 'Company ABC Customer DB - 500K Records',
 'dark_hacker_01',
 'Leaked emails include: test@example.com, user123@gmail.com, admin@company.kr\nFull database with passwords.',
 '2026-03-18 15:30:00',
 SHA2('abc_customer_db_500k', 256),
 'leak_data',
 '["database", "email", "usa"]',
 '{"org": "Company ABC", "country": "US", "industry": "retail", "records": 500000}',
 NULL,
 '{"country": "US", "domain": "companyabc.com", "group": "dark_hacker_01"}'
),
(1, 'Korean Portal Site Combo List 2M',
 'stealer_king',
 'Fresh combo list from Korean portal. Emails: victim@naver.com, test@example.com, hello@daum.net',
 '2026-03-20 09:00:00',
 SHA2('korean_portal_combo_2m', 256),
 'combo_list',
 '["combo", "korea", "portal"]',
 '{"org": "Korean Portal", "country": "KR", "records": 2000000}',
 NULL,
 '{"country": "KR", "domain": "portal.kr", "group": "stealer_king"}'
);
