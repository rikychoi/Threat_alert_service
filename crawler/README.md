# Ransomware.live api를 사용한 위협 정보 수집기
OSINT 플랫폼 ransomware.live의 api를 활용해 실시간으로 위협 정보를 가져오는 도구입니다.

## Main Features
* 실행 시 1시간 간격으로 ransomeware.live의 recentvictims api를 활용해 최근 발생한 침해사고 정보를 가져와 파싱합니다.
* 이후 백엔드 api를 호출하여 해당 정보 중 db에 저장되지 않은 정보가 있을 시 slack으로 알림을 전송합니다.
  
