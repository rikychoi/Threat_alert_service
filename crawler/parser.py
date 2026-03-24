import re

def clean__text(text):
    if not text:
        return ""
    return re.sub(r"<[^>]+>", "", text).strip()

import hashlib

def make_hash(title, author, content):
    raw = title + author + content 
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

from datetime import datetime

def parse_datetime(dt_str):
    if not dt_str:       
        return None      

    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(dt_str, fmt) 
        except ValueError:
            continue     

    return None  

def parse_victim(data):
    title        = data.get("victim")      or "Unknown Victim"
    author       = data.get("group")       or "Unknown Group"
    content      = clean_text(data.get("description") or "")
    published_at = parse_datetime(data.get("attackdate"))
    victim_info  = data.get("domain")      or ""
    original_url = data.get("claim_url")   or data.get("url") or ""
    content_hash = make_hash(title, author, content)

    return {
        "title":        title,
        "author":       author,
        "content":      content,
        "published_at": published_at,
        "victim_info":  victim_info,
        "original_url": original_url,
        "content_hash": content_hash,
        "raw_data":     data,
    }
