Gunterdown — 터미널 Markdown 편집기

화면 언어: 도구 > 화면 언어 (Alt+U). 선택한 언어는 저장됩니다.
자동 완성 언어: Alt+L 또는 --lang en/ja/zh/ko/fr.
화면 언어와 자동 완성 언어는 각각 설정할 수 있습니다.
시작 시 --ui-lang ko를 사용하세요 (en / ja / zh / fr도 지원).

입력 중 후보 창이 표시됩니다. 영문은 3글자, 일본어와 한국어는 2글자,
중국어는 1글자부터 제안합니다.
↑/↓ 또는 Shift+Tab으로 선택하고 Tab으로 적용하며 Esc로 닫습니다.
Enter는 줄 바꿈입니다. Ctrl+Space로 후보를 직접 표시합니다.
다른 언어의 후보에는 언어 코드가 표시됩니다.
일본어와 중국어는 공백이 없는 문장 안에서도 자동 완성됩니다.
가나, 한자, 한글 입력에는 운영 체제의 입력기를 사용하세요.
로마자, 병음 또는 영문에서 한글로 변환하는 입력기는 포함하지 않습니다.

Ctrl+S: 저장, Ctrl+X: 종료, F2: 메뉴, F9: 파일 트리.
Shift+왼쪽/오른쪽: 선택, Ctrl+U: 실행 취소, Ctrl+Y: 다시 실행.
Alt+B: 문서 전환. 후보가 없으면 Tab으로 트리와 편집기를 전환합니다.
저장하지 않은 문서는 *로 표시되며 닫을 때 확인합니다.
복구 사본은 30초마다 GUNTERDOWN_HOME/recover/에 저장됩니다.
모든 제안은 오프라인으로 처리됩니다. 영어와 프랑스어 교정은 단어 제안이며
문법 검사가 아닙니다. CJK 자동 완성은 입력된 원문 접두어를 사용합니다.

단축키 (Esc로 편집기에 돌아가기):

파일
  Ctrl+N       새로 만들기
  Ctrl+O       열기…
  Ctrl+R       최근 파일
  Ctrl+S       저장
  Alt+E        다른 이름으로 저장…
  —            모두 저장
  Alt+X        닫기
  —            가져오기
  Ctrl+E       내보내기
  Ctrl+P       인쇄
  Ctrl+X       종료
편집
  Ctrl+U       실행 취소
  Ctrl+Y       다시 실행
  Ctrl+K       잘라내기
  Ctrl+C       복사
  Ctrl+V       붙여넣기
  Ctrl+A       모두 선택
  —            들여쓰기
  —            내어쓰기
  Alt+/        주석 전환
  F5           날짜 삽입
  Ctrl+L       링크 삽입
  Alt+I        이미지 삽입
검색
  Ctrl+W       찾기
  Ctrl+D       다음
  Ctrl+B       이전
  Ctrl+\       바꾸기
  Ctrl+G       줄로 이동
  F3           제목으로 이동
  —            파일에서 찾기
문서
  Alt+T        템플릿
  Alt+F        메타데이터
  Alt+S        목차
  Alt+N        제목 번호 갱신
  Alt+2        H2 제목
  Alt+3        H3 제목
  Alt+C        코드
  Alt+Q        인용
  Alt+M        표
  Alt+P        이미지 설명
  Alt+V        Markdown 검사
도구
  F6           HTML 미리보기
  F7           통계
  F8           맞춤법 검사
  Alt+L        자동 완성 언어
  Alt+U        화면 언어
  Alt+D        자동 완성
  Alt+Z        집중 모드
  Alt+W        자동 줄 바꿈
  Alt+#        줄 번호
  F9           파일 트리
  —            폴더 변경
  —            환경 설정
도움말
  F1           사용 설명서
  Alt+H        단축키
  F12          정보
  —            진단

테마: Alt+Y 또는 도구 > 테마. ↑/↓ 미리보기, Enter 저장, Esc 취소.
팔레트: dark, light, solarized, nord, dracula, ocean, contrast.
시작 시 --theme nord. 사용자 테마: GUNTERDOWN_HOME/themes/*.json.
