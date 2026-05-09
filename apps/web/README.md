# AI Team Agent Web Dashboard

이 디렉터리는 Vercel 배포를 준비하기 위한 Next.js 정적 대시보드 스캐폴드입니다.

## 현재 범위

- `apps/web` 아래에 App Router 기반 Next.js 구조를 준비했습니다.
- 대시보드는 로컬 MVP용 정적 페이지입니다.
- 외부 API, 인증 정보, 비밀값, 실서비스 데이터 연결은 없습니다.
- Vercel 배포는 아직 수행하지 않습니다.

## npm audit 리스크

- 현재 `npm audit`는 Next.js 의존 경로의 `postcss` 관련 moderate 취약점 2건을 보고합니다.
- `npm audit fix --force`는 breaking change를 만들거나 Next.js를 다운그레이드할 수 있어 사용하지 않았습니다.
- Vercel 배포는 이 리스크를 다시 검토하고 안전한 업그레이드 경로가 확인된 뒤에만 진행해야 합니다.

## 로컬 실행 준비

패키지 설치가 필요한 단계는 아직 실행하지 않았습니다. 향후 로컬에서 확인할 때는 이 디렉터리에서 의존성을 설치한 뒤 다음 명령어를 사용할 수 있습니다.

```bash
npm run dev
```

빌드 검증은 배포 전에 로컬 점검이 통과한 뒤 실행해야 합니다.

```bash
npm run build
```

## 배포 전 조건

- `python3 tests/harness/run_all.py`가 통과해야 합니다.
- 외부 실행 정책과 승인 게이트가 문서화되어야 합니다.
- 이메일, Slack/Telegram, Google Sheets, Instagram 연동은 별도 승인 전까지 연결하지 않습니다.
- Vercel 배포는 로컬 점검과 사용자 승인 이후에만 진행합니다.
- npm audit의 남은 moderate 취약점 2건을 배포 전 다시 검토합니다.
