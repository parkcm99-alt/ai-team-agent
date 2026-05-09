# 리플레이 테스트

이 디렉터리는 릴리스 전에 실패 사례를 다시 실행하기 위한 하네스 테스트 자료를 보관합니다.

## 목적

- 이전에 발견된 실패가 같은 방식으로 반복되지 않는지 확인합니다.
- `harness/failure_cases`의 사례가 기대한 게이트로 분류되는지 확인합니다.
- `examples/failure/sample_failure_cases.jsonl`의 릴리스 전 실패 사례가 재현되지 않는지 확인합니다.
- `examples/golden/sample_golden_examples.jsonl`의 안전한 예시와 현재 출력이 같은 정책을 따르는지 비교합니다.
- 승인 게이트가 누락된 출력이 `ready_for_approval`로 잘못 분류되지 않는지 확인합니다.
- 외부 API 쓰기, 발송, 게시, 알림이 테스트 중 자동 실행되지 않는지 확인합니다.

## 기본 규칙

- 실패 사례는 릴리스 전마다 재실행합니다.
- 리플레이 결과는 한국어로 요약합니다.
- 내부 결과 키와 상태값은 영어를 사용할 수 있습니다.
- `blocked`가 하나라도 있으면 릴리스 후보로 넘기지 않습니다.
- `ready_for_approval`은 실행 완료가 아니라 사용자 승인 요청 가능 상태입니다.
- 이메일 발송, Google Sheets 쓰기, Slack/Telegram 알림, Instagram 게시 제안은 실제 실행 없이 검증합니다.
- 알려진 실패 사례와 유사한 출력은 차단하거나 `draft_only`로 낮춥니다.

## 릴리스 전 검증 데이터셋

- `examples/failure/sample_failure_cases.jsonl`: 반복되면 안 되는 실패 패턴입니다.
- `examples/golden/sample_golden_examples.jsonl`: 유지해야 하는 안전한 출력 패턴입니다.
- `harness/failure_cases/sample_failure_cases.jsonl`: 기존 하네스 실패 사례입니다.
- `harness/golden_examples/sample_golden_examples.jsonl`: 기존 하네스 골든 예시입니다.

## 리플레이 절차

1. 실패 사례를 입력으로 사용해 현재 출력이 같은 실수를 반복하는지 확인합니다.
2. 각 출력이 `blocked`, `draft_only`, `ready_for_approval` 중 기대 게이트로 분류되는지 확인합니다.
3. 골든 예시와 비교해 승인 게이트, 한국어 출력, 내부 영어 지시 정책이 유지되는지 확인합니다.
4. 외부 API 연결, 이메일 발송, 알림 전송, Instagram 게시가 실제로 실행되지 않았는지 확인합니다.
5. 실패가 재현되면 릴리스 후보에서 제외하고 실패 사례를 보강합니다.

## 실행 방법

프로젝트 루트에서 다음 명령어로 리플레이 데이터셋을 검증합니다.

```bash
python3 tests/harness/replay_runner.py
```

러너는 `examples/failure/sample_failure_cases.jsonl`과 `examples/golden/sample_golden_examples.jsonl`을 읽고, 결과를 한국어로 출력합니다. 중요 검증 항목이 실패하면 0이 아닌 종료 코드를 반환합니다.

## 관련 문서

- `harness/replay_tests/replay_plan.md`
- `harness/release_gate.md`
- `examples/failure/sample_failure_cases.jsonl`
- `examples/golden/sample_golden_examples.jsonl`
- `harness/failure_cases/sample_failure_cases.jsonl`
- `harness/golden_examples/sample_golden_examples.jsonl`
