#!/usr/bin/env python3
from __future__ import annotations

import sys
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def collect_markdown_and_prompts() -> tuple[list[Path], str]:
    markdown_files = sorted(
        path
        for path in ROOT.rglob("*.md")
        if ".git" not in path.parts
    )
    prompt_files = sorted(ROOT.glob("agents/*/system_prompt.md"))
    files = sorted(set(markdown_files + prompt_files))
    text = "\n".join(read_text(path) for path in files)
    return files, text


def collect_system_prompt_text() -> str:
    prompt_files = sorted(ROOT.glob("agents/*/system_prompt.md"))
    return "\n".join(read_text(path) for path in prompt_files)


def has_all(text: str, terms: list[str]) -> bool:
    return all(term in text for term in terms)


def has_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def add_result(
    condition: bool,
    label: str,
    passed: list[str],
    failed: list[str],
    critical: bool = True,
    warnings: list[str] | None = None,
) -> None:
    if condition:
        passed.append(label)
    elif critical:
        failed.append(label)
    elif warnings is not None:
        warnings.append(label)


def names_are_ascii(paths: list[Path]) -> bool:
    for path in paths:
        relative = path.relative_to(ROOT)
        for part in relative.parts:
            if not part.isascii():
                return False
    return True


def schema_keys_are_english() -> bool:
    def walk_keys(value: object) -> list[str]:
        if isinstance(value, dict):
            keys: list[str] = []
            for key, child in value.items():
                keys.append(str(key))
                keys.extend(walk_keys(child))
            return keys
        if isinstance(value, list):
            keys = []
            for item in value:
                keys.extend(walk_keys(item))
            return keys
        return []

    jsonl_files = sorted((ROOT / "harness").rglob("*.jsonl"))
    for path in jsonl_files:
        for line in read_text(path).splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            data = json.loads(stripped)
            keys = walk_keys(data)
            if any(not key.replace("_", "").replace("-", "").isascii() for key in keys):
                return False
    return True


def main() -> int:
    files, scanned_text = collect_markdown_and_prompts()
    system_prompt_text = collect_system_prompt_text()

    passed: list[str] = []
    failed: list[str] = []
    warnings: list[str] = []

    add_result(
        (ROOT / "tests/harness/replay").is_dir(),
        "`tests/harness/replay` 폴더가 있습니다.",
        passed,
        failed,
    )
    add_result(
        (ROOT / "tests/harness/checklists").is_dir(),
        "`tests/harness/checklists` 폴더가 있습니다.",
        passed,
        failed,
    )
    add_result(
        (ROOT / "tests/harness/replay/README.md").is_file(),
        "`tests/harness/replay/README.md` 파일이 있습니다.",
        passed,
        failed,
    )
    add_result(
        (ROOT / "tests/harness/checklists/README.md").is_file(),
        "`tests/harness/checklists/README.md` 파일이 있습니다.",
        passed,
        failed,
    )
    add_result(
        (ROOT / "examples/failure").is_dir(),
        "`examples/failure` 폴더가 있습니다.",
        passed,
        failed,
    )
    add_result(
        (ROOT / "examples/golden").is_dir(),
        "`examples/golden` 폴더가 있습니다.",
        passed,
        failed,
    )

    google_approval = (
        "Google Sheets" in scanned_text
        and has_any(scanned_text, ["쓰기 작업은 자동 실행하면 안 됩니다", "자동 실행은 금지", "must never run automatically"])
        and has_any(scanned_text, ["명시적인 사용자 승인", "explicit user approval"])
    )
    add_result(
        google_approval,
        "Google Sheets 쓰기 작업이 자동 실행 금지 및 명시적 승인 대상으로 문서화되어 있습니다.",
        passed,
        failed,
    )

    google_preview = has_all(
        scanned_text,
        ["대상 스프레드시트", "대상 탭", "대상 행/열", "원본 값", "제안 값"],
    )
    add_result(
        google_preview,
        "Google Sheets 쓰기 전 대상 스프레드시트, 대상 탭, 대상 행/열, 원본 값, 제안 값 표시가 요구됩니다.",
        passed,
        failed,
    )

    google_verification = has_any(
        scanned_text,
        ["쓰기 후에는 기록된 값을 다시 확인", "쓰기 후 기록된 값을 다시 확인", "verify the written value"],
    ) and has_any(scanned_text, ["검증 결과", "report the result in Korean"])
    add_result(
        google_verification,
        "Google Sheets 쓰기 후 값 검증 및 한국어 결과 보고가 요구됩니다.",
        passed,
        failed,
    )

    telegram_approval = (
        "Telegram" in scanned_text
        and has_any(scanned_text, ["명시적인 사용자 승인", "explicit user approval"])
        and has_any(scanned_text, ["알림 정책이 완전히 정의", "notification policy is fully defined"])
    )
    add_result(
        telegram_approval,
        "Telegram 알림이 정책 확정 전 명시적 승인 대상으로 문서화되어 있습니다.",
        passed,
        failed,
    )

    mvp_notifications_blocked = has_any(
        scanned_text,
        ["MVP 단계에서는 어떤 외부 알림도 자동 전송하지 않습니다", "No external notification should be sent automatically in the MVP stage"],
    )
    add_result(
        mvp_notifications_blocked,
        "MVP 단계에서 외부 알림 자동 전송 금지가 문서화되어 있습니다.",
        passed,
        failed,
    )

    slack_gated = (
        "Slack" in scanned_text
        and has_any(scanned_text, ["사용자 승인 없이 Slack", "Slack 또는 Telegram 메시지를 전송하지 않았는지", "Require explicit user approval before posting"])
    )
    add_result(
        slack_gated,
        "Slack 알림이 차단 또는 승인 기반으로 문서화되어 있습니다.",
        passed,
        failed,
    )

    instagram_gated = (
        "Instagram" in scanned_text
        and has_any(scanned_text, ["사용자 승인 없이 게시", "Do not auto-publish", "게시 전 사용자 승인", "approval workflow"])
    )
    add_result(
        instagram_gated,
        "Instagram 게시가 차단 또는 승인 기반으로 문서화되어 있습니다.",
        passed,
        failed,
    )

    user_korean_required = has_any(
        scanned_text,
        ["사용자에게 보이는 출력, 보고서, 요약, 알림, 설명은 한국어", "User-facing outputs, reports, summaries, notifications, and explanations must be written in Korean"],
    )
    add_result(
        user_korean_required,
        "사용자에게 보이는 출력은 한국어여야 한다는 정책이 문서화되어 있습니다.",
        passed,
        failed,
    )

    internal_english_required = has_any(
        scanned_text,
        ["내부 명령어, 파일 이름, 시스템 프롬프트는 영어", "Internal commands, file names, and system prompts must be written in English"],
    ) and has_any(
        scanned_text,
        ["schema", "schemas", "스키마"],
    )
    add_result(
        internal_english_required,
        "내부 파일명, 폴더명, 스키마 키, 시스템 프롬프트는 영어 기준으로 유지한다는 정책이 문서화되어 있습니다.",
        passed,
        failed,
    )

    all_paths = [path for path in ROOT.rglob("*") if ".git" not in path.parts]
    add_result(
        names_are_ascii(all_paths),
        "현재 파일명과 폴더명이 ASCII 기반 영어 이름으로 유지되어 있습니다.",
        passed,
        failed,
    )

    add_result(
        schema_keys_are_english(),
        "JSONL 스키마 키가 영어 기반으로 유지되어 있습니다.",
        passed,
        failed,
    )

    add_result(
        re.search(r"[가-힣]", system_prompt_text) is None,
        "agent system prompt 파일이 영어로 유지되어 있습니다.",
        passed,
        failed,
    )

    add_result(
        bool(files),
        "Markdown 파일과 agent system prompt를 스캔했습니다.",
        passed,
        failed,
        critical=False,
        warnings=warnings,
    )

    if not (ROOT / "harness/failure_cases/sample_failure_cases.jsonl").is_file():
        warnings.append("하네스 실패 사례 JSONL 파일을 찾지 못했습니다.")
    if not (ROOT / "harness/golden_examples/sample_golden_examples.jsonl").is_file():
        warnings.append("하네스 골든 예시 JSONL 파일을 찾지 못했습니다.")

    print("- 통과 항목")
    if passed:
        for item in passed:
            print(f"  - {item}")
    else:
        print("  - 없음")

    print("- 실패 항목")
    if failed:
        for item in failed:
            print(f"  - {item}")
    else:
        print("  - 없음")

    print("- 경고 항목")
    if warnings:
        for item in warnings:
            print(f"  - {item}")
    else:
        print("  - 없음")

    print("- 최종 판단")
    if failed:
        print("  - 실패: 필수 정책 또는 구조가 누락되어 릴리스 게이트를 통과할 수 없습니다.")
        return 1

    print("  - 통과: 필수 하네스 정책과 승인 게이트가 문서 기준을 충족합니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
