import requests
import json
import sys
import argparse

# 윈도우 터미널 인코딩 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://api.ransomware.live/v2"

def call_api(path, label, limit=10):
    url = f"{BASE_URL}/{path}"
    print(f"[*] {label} 호출 중: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # 리스트일 경우 최대 10개(limit)만 슬라이싱
            result = data[:limit] if isinstance(data, list) else data
            
            print("\n" + "="*60)
            print(json.dumps(result, indent=4, ensure_ascii=False))
            print("="*60)
            count = len(result) if isinstance(result, list) else 1
            print(f"조회 성공 (출력 항목: {count}개)\n")
        else:
            print(f"[!] 실패 (코드: {response.status_code})")
    except Exception as e:
        print(f"[!] 에러: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ransomware.live v2 전체 API 마스터 도구")
    
    # 기본 플래그 (인자 없음)
    parser.add_argument("-i", "--info", action="store_true", help="API 메타데이터 (info)")
    parser.add_argument("-v", "--victims", action="store_true", help="최근 피해자 (recentvictims)")
    parser.add_argument("-gs", "--groups", action="store_true", help="전체 그룹 목록 (groups)")
    parser.add_argument("-ac", "--allattacks", action="store_true", help="모든 사이버 공격 (allcyberattacks)")
    parser.add_argument("-rc", "--recentattacks", action="store_true", help="최근 사이버 공격 (recentcyberattacks)")

    # 단일 인자 필요 (-g lockbit 등)
    parser.add_argument("-g", "--group", help="특정 그룹 상세 (group/<name>)")
    parser.add_argument("-gv", "--groupvictims", help="그룹별 피해자 (groupvictims/<name>)")
    parser.add_argument("-q", "--search", help="키워드 검색 (searchvictims/<keyword>)")
    parser.add_argument("-cc", "--countryattacks", help="국가별 공격 (countrycyberattacks/<code>)")
    parser.add_argument("-cv", "--countryvictims", help="국가별 피해자 (countryvictims/<code>)")
    parser.add_argument("-sv", "--sectorvictims", help="섹터별 피해자 (sectorvictims/<sector>)")
    parser.add_argument("-cert", "--certs", help="국가별 CERT 연락처 (certs/<code>)")
    parser.add_argument("-y", "--yara", help="그룹별 YARA 규칙 (yara/<name>)")

    # 복합 인자 필요 (-vm 2024 03 등)
    parser.add_argument("-vm", "--victimsmonth", nargs=2, metavar=('YEAR', 'MONTH'), help="연/월별 피해자 (victims/YYYY/MM)")
    parser.add_argument("-svc", "--sectorcountry", nargs=2, metavar=('SECTOR', 'CC'), help="섹터 및 국가별 피해자 (sectorvictims/S/CC)")

    args = parser.parse_args()
    L = 10 # 최대 한도 10개 고정

    # 분기 처리
    if args.info: call_api("info", "메타데이터")
    elif args.victims: call_api("recentvictims", "최근 피해자", L)
    elif args.groups: call_api("groups", "전체 그룹", L)
    elif args.allattacks: call_api("allcyberattacks", "전체 공격", L)
    elif args.recentattacks: call_api("recentcyberattacks", "최근 공격", L)
    
    elif args.group: call_api(f"group/{args.group}", f"그룹 상세({args.group})")
    elif args.groupvictims: call_api(f"groupvictims/{args.groupvictims}", f"그룹 피해자({args.groupvictims})", L)
    elif args.search: call_api(f"searchvictims/{args.search}", f"검색({args.search})", L)
    elif args.countryattacks: call_api(f"countrycyberattacks/{args.countryattacks}", f"국가 공격({args.countryattacks})", L)
    elif args.countryvictims: call_api(f"countryvictims/{args.countryvictims}", f"국가 피해자({args.countryvictims})", L)
    elif args.sectorvictims: call_api(f"sectorvictims/{args.sectorvictims}", f"섹터 피해자({args.sectorvictims})", L)
    elif args.certs: call_api(f"certs/{args.certs}", f"CERT({args.certs})")
    elif args.yara: call_api(f"yara/{args.yara}", f"YARA({args.yara})")
    
    elif args.victimsmonth: 
        call_api(f"victims/{args.victimsmonth[0]}/{args.victimsmonth[1]}", f"{args.victimsmonth[0]}년 {args.victimsmonth[1]}월 피해자", L)
    elif args.sectorcountry:
        call_api(f"sectorvictims/{args.sectorcountry[0]}/{args.sectorcountry[1]}", f"{args.sectorcountry[1]}국가 {args.sectorcountry[0]}섹터", L)
    
    else:
        parser.print_help()