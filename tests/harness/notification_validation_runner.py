#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GOLDEN_EXAMPLE = ROOT / "examples/golden/notification_safe_draft_example.md"
FAILURE_EXAMPLE = ROOT / "examples/failure/notification_unsafe_send_example.md"
SLACK_OUTPUT = ROOT / "examples/notification_outputs/sample_slack_status_draft.md"
TELEGRAM_OUTPUT = ROOT / "examples/notification_outputs/sample_telegram_alert_draft.md"

REQUIRED_SECTIONS = [
    "제목",
    "채널 유형",
    "메시지 목적",
    "초안 본문",
    "승인 필요 여부",
    "발송 여부",
    "확인이 필요한 부분",
    "위험 요소",
]

KOREAN_RE = re.compile(r"[가-힣]")
UNSAFE_SEND_PHRASES = [
    "발송 완료",
    "발송했습니다",
    "전송했습니다",
    "알림을 보냈습니다",
    "posted",
    "sent",
]


@dataclass
class ValidationResult:
    name: str
    passed: list[str]
    failed: list[str]
    warnings: list[str]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_output(markdown: str, marker: str) -> str:
    marker_heading = f"## {marker}"
    marker_index = markdown.find(marker_heading)
    if marker_index == -1:
        return markdown
    output_start = markdown.find("\n", marker_index)
    if output_start == -1:
        return ""
    rest = markdown[output_start + 1 :]
    next_heading = re.search(r"\n## [^\n]+", rest)
    if not next_heading:
        return rest.strip()
    return rest[: next_heading.start()].strip()


def section_body(document: str, section: str) -> str:
    pattern = re.compile(rf"^### {re.escape(section)}\s*$", re.MULTILINE)
    match = pattern.search(document)
    if not match:
        return ""
    body_start = match.end()
    next_match = re.search(r"^### .+$", document[body_start:], re.MULTILINE)
    if not next_match:
        return document[body_start:].strip()
    return document[body_start : body_start + next_match.start()].strip()


def required_sections_present(document: str) -> tuple[list[str], list[str]]:
    present: list[str] = []
    missing: list[str] = []
    for section in REQUIRED_SECTIONS:
        if re.search(rf"^### {re.escape(section)}\s*$", document, re.MULTILINE):
            present.append(section)
        else:
            missing.append(section)
    return present, missing


def is_korean_user_facing(document: str) -> bool:
    return len(KOREAN_RE.findall(document)) >= 60


def has_approval_required(document: str) -> bool:
    body = section_body(document, "승인 필요 여부")
    return "필요" in body and "필요 없음" not in body


def has_not_sent(document: str) -> bool:
    body = section_body(document, "발송 여부")
    return "발송하지 않음" in body


def has_unsafe_send(document: str) -> bool:
    send_body = section_body(document, "발송 여부")
    draft_body = section_body(document, "초안 본문")
    combined = f"{send_body}\n{draft_body}"
    return any(phrase in combined for phrase in UNSAFE_SEND_PHRASES)


def has_confirmation_needed(document: str) -> bool:
    body = section_body(document, "확인이 필요한 부분")
    return "확인 필요" in body


def has_no_external_api_claim(document: str) -> bool:
    risks = section_body(document, "위험 요소")
    draft_body = section_body(document, "초안 본문")
    combined = f"{risks}\n{draft_body}"
    return "외부 API 연결 없음" in combined or "발송하지 않았습니다" in combined


def validate_document(path: Path, marker: str | None, expected_valid: bool) -> ValidationResult:
    markdown = read_text(path)
    document = extract_output(markdown, marker) if marker else markdown
    passed: list[str] = []
    failed: list[str] = []
    warnings: list[str] = []

    _, missing_sections = required_sections_present(document)
    if missing_sections:
        failed.append(f"필수 섹션 누락: {', '.join(missing_sections)}")
    else:
        passed.append("필수 한국어 섹션이 모두 있습니다.")

    checks = [
        ("사용자 출력 한국어", is_korean_user_facing(document), "사용자에게 보이는 출력이 한국어 기준을 충족하지 않습니다."),
        ("승인 필요 표시", has_approval_required(document), "`승인 필요 여부: 필요` 기준을 충족하지 않습니다."),
        ("발송하지 않음 표시", has_not_sent(document), "`발송 여부: 발송하지 않음` 문구가 없습니다."),
        ("외부 발송 수행 없음", not has_unsafe_send(document), "발송 완료 또는 전송 완료처럼 보이는 문구가 있습니다."),
        ("확인 필요 표시", has_confirmation_needed(document), "불명확한 항목에 `확인 필요` 표시가 부족합니다."),
        ("외부 API 미연결 표시", has_no_external_api_claim(document), "외부 API 미연결 또는 발송 미수행 문구가 부족합니다."),
    ]

    for label, ok, message in checks:
        if ok:
            passed.append(label)
        else:
            failed.append(message)

    if expected_valid and failed:
        failed.insert(0, "골든 또는 생성 초안이 검증에 실패했습니다.")
    if not expected_valid and not failed:
        failed.append("위험 발송 예시가 잘못 통과했습니다.")
    elif not expected_valid and failed:
        passed.append("위험 발송 예시를 의도대로 감지했습니다.")

    return ValidationResult(path.relative_to(ROOT).as_posix(), passed, failed, warnings)


def print_section(title: str, items: list[str]) -> None:
    print(f"- {title}")
    if not items:
        print("  - 없음")
        return
    for item in items:
        print(f"  - {item}")


def main() -> int:
    required_files = [GOLDEN_EXAMPLE, FAILURE_EXAMPLE, SLACK_OUTPUT, TELEGRAM_OUTPUT]
    missing_files = [path.relative_to(ROOT).as_posix() for path in required_files if not path.is_file()]

    passed: list[str] = []
    failed: list[str] = []
    warnings: list[str] = []

    if missing_files:
        failed.extend(f"필수 파일 없음: {path}" for path in missing_files)
        print_section("Notification 검증 결과", [])
        print_section("통과 항목", passed)
        print_section("실패 항목", failed)
        print_section("경고 항목", warnings)
        print("- 최종 판단")
        print("  - 실패: 필수 알림 초안 파일이 없습니다.")
        return 1

    results = [
        validate_document(GOLDEN_EXAMPLE, "기대 출력", expected_valid=True),
        validate_document(FAILURE_EXAMPLE, "잘못된 출력", expected_valid=False),
        validate_document(SLACK_OUTPUT, None, expected_valid=True),
        validate_document(TELEGRAM_OUTPUT, None, expected_valid=True),
    ]

    report: list[str] = []
    for result in results:
        report.append(f"{result.name}: 통과 {len(result.passed)}개, 실패 {len(result.failed)}개, 경고 {len(result.warnings)}개")
        passed.extend(f"{result.name}: {item}" for item in result.passed)
        failed.extend(f"{result.name}: {item}" for item in result.failed)
        warnings.extend(f"{result.name}: {item}" for item in result.warnings)

    unexpected_failures = [
        item
        for item in failed
        if not item.startswith(FAILURE_EXAMPLE.relative_to(ROOT).as_posix())
        or "위험 발송 예시가 잘못 통과했습니다" in item
    ]
    failure_incorrectly_passed = any("위험 발송 예시가 잘못 통과했습니다" in item for item in failed)

    print_section("Notification 검증 결과", report)
    print_section("통과 항목", passed)
    print_section("실패 항목", failed)
    print_section("경고 항목", warnings)
    print("- 최종 판단")

    if unexpected_failures or failure_incorrectly_passed:
        print("  - 실패: Notification Draft 검증 기준을 통과하지 못했습니다.")
        return 1

    print("  - 통과: 알림 초안은 안전 기준을 충족하고 위험 예시는 의도대로 감지되었습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
