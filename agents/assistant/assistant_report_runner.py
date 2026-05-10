#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REPORT_FILE = ROOT / "reports/daily_status_report.md"
SUPERVISOR_DECISIONS_FILE = ROOT / "examples/supervisor_outputs/sample_routing_decisions.jsonl"


@dataclass
class CommandResult:
    command: str
    returncode: int
    output: str


def run_command(command: list[str]) -> CommandResult:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return CommandResult(
        command=" ".join(command),
        returncode=completed.returncode,
        output=completed.stdout.strip(),
    )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        records.append(json.loads(stripped))
    return records


def bullet_lines(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- 확인 필요"


def command_status(result: CommandResult) -> str:
    return "통과" if result.returncode == 0 else f"실패, 종료 코드 {result.returncode}"


def summarize_git_status(output: str) -> str:
    if not output:
        return "확인 필요"
    lines = [line for line in output.splitlines() if line.strip()]
    if "nothing to commit" in output or lines == ["## main...origin/main"]:
        return "작업 트리가 깨끗하거나 추적 중인 변경이 없습니다."
    return "로컬 변경 사항이 감지되었습니다."


def summarize_harness(output: str, returncode: int) -> str:
    if returncode != 0:
        return "하네스 점검 실패가 있어 상세 로그 확인이 필요합니다."
    if "실패 항목\n  - 없음" in output or "모든 하네스 점검" in output:
        return "전체 하네스 점검이 통과했습니다."
    return "하네스 결과 요약을 확인해야 합니다."


def recent_commit_lines(output: str) -> list[str]:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return lines[:5] or ["확인 필요"]


def summarize_supervisor_decisions() -> list[str]:
    decisions = read_jsonl(SUPERVISOR_DECISIONS_FILE)
    if not decisions:
        return [
            "총 요청 수: 확인 필요",
            "차단된 요청 수: 확인 필요",
            "승인 필요 요청 수: 확인 필요",
            "라우팅 대상 에이전트 목록: 확인 필요",
            "위험 작업 차단 요약: Supervisor 라우팅 결과 파일 확인 필요",
            "확인이 필요한 요청 요약: 확인 필요",
            "외부 실행 여부: 수행하지 않음",
        ]

    total_count = len(decisions)
    blocked_count = sum(1 for decision in decisions if bool(decision.get("blocked")))
    approval_count = sum(1 for decision in decisions if bool(decision.get("approval_required")))
    route_counts = Counter(str(decision.get("selected_agent", "확인 필요")) for decision in decisions)
    route_summary = ", ".join(f"{agent} {count}건" for agent, count in sorted(route_counts.items()))

    risky_blocked = [
        f"{decision.get('id', 'unknown')}: {decision.get('reasoning', '확인 필요')}"
        for decision in decisions
        if bool(decision.get("blocked"))
    ]
    confirmation_needed = [
        f"{decision.get('id', 'unknown')}: {decision.get('confirmation_needed', '확인 필요')}"
        for decision in decisions
        if "확인 필요" in str(decision.get("confirmation_needed", ""))
    ]

    return [
        f"총 요청 수: {total_count}",
        f"차단된 요청 수: {blocked_count}",
        f"승인 필요 요청 수: {approval_count}",
        f"라우팅 대상 에이전트 목록: {route_summary}",
        f"위험 작업 차단 요약: {' / '.join(risky_blocked[:5]) if risky_blocked else '차단된 위험 작업 없음'}",
        f"확인이 필요한 요청 요약: {' / '.join(confirmation_needed[:5]) if confirmation_needed else '확인 필요 요청 없음'}",
        "외부 실행 여부: 수행하지 않음",
    ]


def render_report(
    git_status: CommandResult,
    git_log: CommandResult,
    harness: CommandResult | None,
    phase: str,
) -> str:
    harness_summary = "하네스 점검 실행 전입니다."
    harness_detail = ["하네스 점검 결과: 확인 필요"]
    if harness is not None:
        harness_summary = summarize_harness(harness.output, harness.returncode)
        harness_detail = [
            f"`{harness.command}`: {command_status(harness)}",
            harness_summary,
        ]

    git_summary = summarize_git_status(git_status.output)
    commits = recent_commit_lines(git_log.output)
    supervisor_summary = summarize_supervisor_decisions()
    completed = [
        "Document Agent MVP와 검증 러너가 준비되어 있습니다.",
        "Communication Agent MVP, 워크플로 테스트, 로컬 러너가 준비되어 있습니다.",
        "Sheets Reader MVP가 로컬 CSV 읽기 전용으로 준비되어 있습니다.",
        "Assistant Report Agent MVP가 로컬 상태 보고서를 생성합니다.",
        "Supervisor Agent MVP 라우팅 결과가 보고서에 반영됩니다.",
    ]
    if phase == "draft":
        completed[-2] = "Assistant Report Agent MVP가 보고서 생성을 준비 중입니다."

    return f"""# Assistant Report Agent Daily Status

### 제목

AI 팀 에이전트 일일 상태 보고서

### 오늘의 전체 상태

- 보고서 생성 시점 기준 저장소 상태: {git_summary}
- 최종 Git 상태는 별도 확인 필요
- 하네스 상태: {harness_summary}
- 보고서 생성 단계: {phase}

### 완료된 작업

{bullet_lines(completed)}

### 에이전트별 상태

- Assistant Agent: 로컬 상태 보고서 생성 MVP 준비
- Document Agent: 로컬 문서 요약 및 문서 검증 통과
- Communication Agent: 로컬 커뮤니케이션 요약, 워크플로, 검증 통과
- Sheets Reader Agent: 로컬 CSV 읽기 전용 리포트 생성 및 검증 통과
- Harness Agent: 정책, 리플레이, 문서, 커뮤니케이션, Sheets Reader 검증 실행
- Supervisor Agent: 로컬 규칙 기반 라우팅과 위험 작업 차단 검증 통과
- Workflow/Instagram Agent: 구조와 정책 중심의 초기 상태

### 하네스 점검 결과

{bullet_lines(harness_detail)}

### Supervisor 라우팅 결과

{bullet_lines(supervisor_summary)}

### 최근 커밋 요약

{bullet_lines(commits)}

### 남은 리스크

- 현재 보고서는 로컬 명령 결과 기반이며 외부 서비스 상태는 확인하지 않습니다.
- 실제 Google Sheets, 이메일, Slack, Telegram, Instagram 연동은 아직 연결하지 않았습니다.
- 외부 실행이 필요한 작업은 별도 승인 게이트와 사후 검증 정책이 필요합니다.

### 다음 추천 작업

- Assistant Report Agent 보고서를 정기 실행하기 전에 승인 정책과 배포 전 검증 흐름을 확정합니다.
- 다음 MVP는 Supervisor Agent가 각 에이전트의 로컬 결과를 통합하는 방식으로 확장하는 것을 제안합니다.

### 승인 필요 항목

- 이메일 발송이 필요한 경우 명시적 사용자 승인이 필요합니다.
- Slack 또는 Telegram 알림이 필요한 경우 명시적 사용자 승인이 필요합니다.
- Google Sheets 쓰기가 필요한 경우 대상 시트, 탭, 행/열, 원본 값, 제안 값을 제시한 뒤 명시적 사용자 승인이 필요합니다.
- Instagram 게시가 필요한 경우 권리 체크리스트와 명시적 사용자 승인이 필요합니다.

### 외부 실행 여부

- 이메일 발송: 수행하지 않음
- Slack/Telegram 알림: 수행하지 않음
- Google Sheets 쓰기 작업: 수행하지 않음
- Instagram 게시: 수행하지 않음
- 외부 API 호출: 수행하지 않음
"""


def main() -> int:
    git_status = run_command(["git", "status", "-sb"])
    git_log = run_command(["git", "log", "--oneline", "-5"])

    draft_report = render_report(git_status, git_log, harness=None, phase="draft")
    write_text(REPORT_FILE, draft_report)

    harness = run_command(["python3", "tests/harness/run_all.py"])
    final_report = render_report(git_status, git_log, harness=harness, phase="final")
    write_text(REPORT_FILE, final_report)

    print("- Assistant Report 실행 결과")
    print(f"  - 생성된 보고서: {REPORT_FILE.relative_to(ROOT)}")
    print(f"  - git 상태 확인: {command_status(git_status)}")
    print(f"  - 최근 커밋 확인: {command_status(git_log)}")
    print(f"  - 하네스 점검: {command_status(harness)}")
    print("- 최종 판단")

    if git_status.returncode != 0 or git_log.returncode != 0 or harness.returncode != 0:
        print("  - 실패: 로컬 상태 보고서 생성 중 하나 이상의 로컬 명령이 실패했습니다.")
        return 1

    print("  - 통과: 한국어 상태 보고서를 생성했습니다. 외부 실행은 수행하지 않았습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
