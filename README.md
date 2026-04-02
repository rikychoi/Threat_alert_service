# Threat_alert_service
ransomware.live의 api를 활용한 침해사고 발생 시 알림 서비스 입니다.

# 프로젝트 정보
## 제작기간
2026.03.18 ~ 2026.04.02

## 팀 구성원 (Team Members)

| 이름 | 역할 |
| :--- | :--- |
| **최윤기** | AWS 인프라,서버 담당 및 수집기 개발 |
| 김소의 | 프론트엔드 개발 |
| 전혜은 | slack 알림 기능 및 데이터 시각화 |
| 차지후 | 수집한 데이터 파서 개발 |
| 문상준 | 웹 서버 백엔드 개발 |
| 안성환 | 수집기 개발 |

## 사용 기술 스택

### 백엔드

> * Python 3.9+
> * FastAPI
> * SQLAlchemy (ORM)
> * MySQL 8.0 / MariaDB
> * PyMySQL

### 프론트엔드
> * React
> * Tailwind CSS
> * Recharts
> * axios 


### 수집기(크롤러)
> * Python
> * APScheduler
> * requests (HTTP)
> * ransomware.live Pro API

## structure & ERD
<details>
<summary>structure</summary>
<br>
<img width="1600" height="1077" alt="image" src="https://github.com/user-attachments/assets/3b8d4d4d-4922-4443-be99-4050647e21a1" />



</details>
<details>
<summary>ERD</summary>
<br>
<img width="695" height="402" alt="image" src="https://github.com/user-attachments/assets/e8723f56-af78-446d-b112-fb13c203400a" />


</details>

## 핵심기능

### 유출 정보 조회
<img width="900" height="600" alt="image" src="https://github.com/user-attachments/assets/3c4bb6f4-6bf1-4808-b012-caa1f7d6db75" />
<img width="850" height="600" alt="image" src="https://github.com/user-attachments/assets/74c2c7a7-99b7-46b1-a919-a1957b0c1c25" />

수집된 데이터에 대한 검색 및 조회 기능

### Slack 알림 페이지
<img width="800" height="622" alt="image" src="https://github.com/user-attachments/assets/a191d93e-11ad-4e07-8e05-f420a26f7d1c" />
<img width="850" height="400" alt="image" src="https://github.com/user-attachments/assets/f6ae85b4-8b46-4832-94b4-c383acc470f3" />

slack을 통해 신규 유출 정보 수집 시 알림 수신 

### 대시보드
<img width="800" height="640" alt="image" src="https://github.com/user-attachments/assets/a7eceffa-0f13-4e4d-99f6-0d0fd29f6557" />
<img width="961" height="330" alt="image" src="https://github.com/user-attachments/assets/d1e55ec1-90ad-478d-8a37-1da94ef2bb6a" />

실시간으로 수집된 데이터에 대한 대시보드 기능을 제공
