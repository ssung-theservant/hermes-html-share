# Hermes HTML Share

공개 GitHub Pages 저장소로 HTML 파일을 배포하는 프로젝트입니다. 공개해도 되는 HTML만 넣으세요. 개인정보·비밀번호·API 키·원본 옵시디언 볼트를 복사하지 않습니다.

## 계정 연결 후 최초 설정

1. GitHub 계정 생성과 이메일 확인을 마칩니다.
2. Mac에서 `gh auth login --web`으로 로그인합니다.
3. 이 폴더에서 `git init -b main`, 커밋 후 `gh repo create hermes-html-share --public --source . --remote origin --push`로 공개 저장소를 만듭니다.
4. `gh api -X POST repos/OWNER/hermes-html-share/pages -f 'source[branch]=main' -f 'source[path]=/'`로 Pages를 활성화하고 `gh api repos/OWNER/hermes-html-share/pages`로 확인합니다.

이 단계들은 계정 연결 후 실제로 검증해야 합니다. 로컬 파일이 있다고 공개 사이트가 이미 만들어진 것은 아닙니다.

## 문서 배포

`python3 publish.py /절대경로/문서.html --slug 문서-이름`

상대 경로 이미지·CSS·JS는 이 도구가 복사하지 않습니다. 단일 HTML 파일 또는 외부에서 접근 가능한 자산을 사용하는 HTML에 적합합니다. 이미 다른 내용이 있는 슬러그는 덮어쓰지 않습니다. 로컬 확인만 할 때는 `--dry-run`을 붙이세요.
