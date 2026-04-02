# 슬랙이랑 디스코드로 알림 쏘는 함수들
import httpx
from app.config import SLACK_WEBHOOK_URL, DISCORD_WEBHOOK_URL


def send_slack_alert(title: str, author: str, category: str, url: str) -> bool:
    if not SLACK_WEBHOOK_URL:
        return False
    try:
        message = {"text": f"*[신규 유출 탐지]*\n제목: {title}\n작성자: {author}\n유형: {category}\n상세: {url}"}
        response = httpx.post(SLACK_WEBHOOK_URL, json=message, timeout=10)
        return response.status_code == 200
    except Exception:
        return False


def send_discord_alert(title: str, author: str, category: str, url: str) -> bool:
    if not DISCORD_WEBHOOK_URL:
        return False
    try:
        message = {"content": f"**[신규 유출 탐지]**\n제목: {title}\n작성자: {author}\n유형: {category}\n상세: {url}"}
        response = httpx.post(DISCORD_WEBHOOK_URL, json=message, timeout=10)
        return response.status_code == 204
    except Exception:
        return False
