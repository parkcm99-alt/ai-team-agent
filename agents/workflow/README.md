# Workflow Agent

Workflow Agent는 아이디어를 실행 계획, 테스트, 결과 검토, 승인 준비 단계로 정리하는 로컬 MVP입니다. Instagram 게시 준비는 승인 요청서와 음악 권리 체크리스트까지만 생성하며 실제 게시하지 않습니다.

## 현재 상태

- 로컬 샘플 입력을 읽어 워크플로 계획을 생성합니다.
- Instagram 게시 승인 요청서를 생성합니다.
- 음악 권리 체크리스트를 생성합니다.
- Instagram API와 Meta Graph API는 연결하지 않습니다.
- 실제 Instagram 게시와 미디어 업로드는 수행하지 않습니다.
- 워크플로 엔진이나 스케줄러는 아직 없습니다.

## 실행 방법

프로젝트 루트에서 다음 명령어를 실행합니다.

```bash
python3 agents/workflow/workflow_runner.py
```

검증은 다음 명령어로 실행합니다.

```bash
python3 tests/harness/workflow_instagram_validation_runner.py
```

## 다음 작업

- 공통 상태값을 정의합니다.
- 작업 전이 규칙과 승인 지점을 설계합니다.
- 보고서와 하네스 검증 흐름을 연결합니다.
- 향후 실제 Instagram 게시가 필요해지면 track_id 기준 음악 권리, 상업적 사용 가능 여부, 샘플/커버/리믹스 여부, 게시 계정, 미디어 파일, 캡션 승인을 먼저 확인해야 합니다.
