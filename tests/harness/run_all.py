#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

COMMANDS = [
    ["python3", "tests/harness/policy_checker.py"],
    ["python3", "tests/harness/replay_runner.py"],
    ["python3", "tests/harness/document_validation_runner.py"],
    ["python3", "tests/harness/document_workflow_runner.py"],
    ["python3", "tests/harness/communication_validation_runner.py"],
    ["python3", "tests/harness/communication_workflow_runner.py"],
    ["python3", "tests/harness/sheets_reader_validation_runner.py"],
    ["python3", "tests/harness/assistant_report_validation_runner.py"],
    ["python3", "tests/harness/supervisor_validation_runner.py"],
    ["python3", "tests/harness/notification_validation_runner.py"],
    ["python3", "-m", "py_compile", "tests/harness/policy_checker.py"],
    ["python3", "-m", "py_compile", "tests/harness/replay_runner.py"],
    ["python3", "-m", "py_compile", "tests/harness/document_validation_runner.py"],
    ["python3", "-m", "py_compile", "tests/harness/document_workflow_runner.py"],
    ["python3", "-m", "py_compile", "tests/harness/communication_validation_runner.py"],
    ["python3", "-m", "py_compile", "tests/harness/communication_workflow_runner.py"],
    ["python3", "-m", "py_compile", "tests/harness/sheets_reader_validation_runner.py"],
    ["python3", "-m", "py_compile", "tests/harness/assistant_report_validation_runner.py"],
    ["python3", "-m", "py_compile", "tests/harness/supervisor_validation_runner.py"],
    ["python3", "-m", "py_compile", "tests/harness/notification_validation_runner.py"],
    ["python3", "-m", "py_compile", "agents/assistant/assistant_report_runner.py"],
    ["python3", "-m", "py_compile", "agents/sheets/sheets_reader_runner.py"],
    ["python3", "-m", "py_compile", "agents/supervisor/supervisor_router.py"],
    ["python3", "-m", "py_compile", "agents/notification/notification_draft_runner.py"],
]


@dataclass
class CheckResult:
    command: str
    returncode: int
    output: str


def run_command(command: list[str]) -> CheckResult:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return CheckResult(
        command=" ".join(command),
        returncode=completed.returncode,
        output=completed.stdout.strip(),
    )


def print_section(title: str, items: list[str]) -> None:
    print(f"- {title}")
    if not items:
        print("  - 없음")
        return
    for item in items:
        print(f"  - {item}")


def print_command_output(result: CheckResult) -> None:
    if not result.output:
        return
    print(f"  - 출력: {result.command}")
    for line in result.output.splitlines():
        print(f"    {line}")


def main() -> int:
    passed: list[str] = []
    failed: list[str] = []
    warnings: list[str] = []
    results: list[CheckResult] = []

    for command in COMMANDS:
        result = run_command(command)
        results.append(result)
        if result.returncode == 0:
            passed.append(result.command)
        else:
            failed.append(f"{result.command} 종료 코드 {result.returncode}")
            break

    print("- 전체 점검 결과")
    for result in results:
        status = "통과" if result.returncode == 0 else "실패"
        print(f"  - {status}: {result.command}")
        if result.returncode != 0:
            print_command_output(result)

    print_section("통과 항목", passed)
    print_section("실패 항목", failed)
    print_section("경고 항목", warnings)
    print("- 최종 판단")

    if failed:
        print("  - 실패: 하나 이상의 하위 점검 명령이 실패했습니다.")
        print("- 다음 권장 작업")
        print("  - 실패한 명령의 출력 내용을 먼저 확인하고 해당 러너나 데이터셋을 수정하세요.")
        return 1

    print("  - 통과: 모든 하네스 점검과 Python 문법 검사가 통과했습니다.")
    print("- 다음 권장 작업")
    print("  - 릴리스 전에도 `python3 tests/harness/run_all.py`를 다시 실행하세요.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
