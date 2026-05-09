#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FAILURE_DATASET = ROOT / "examples/failure/sample_failure_cases.jsonl"
GOLDEN_DATASET = ROOT / "examples/golden/sample_golden_examples.jsonl"

FAILURE_REQUIRED_FIELDS = {
    "schema",
    "id",
    "category",
    "title",
    "input",
    "bad_output",
    "violations",
    "expected_gate",
    "expected_review",
}
GOLDEN_REQUIRED_FIELDS = {
    "schema",
    "id",
    "category",
    "title",
    "input",
    "good_output",
    "quality_checks",
}
ALLOWED_GATES = {"blocked", "draft_only", "approval_required", "pass"}
RISKY_CHANNELS = {"email", "slack", "telegram", "instagram"}


def read_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    cases: list[dict[str, Any]] = []

    if not path.is_file():
        return cases, [f"데이터셋 파일이 없습니다: {path.relative_to(ROOT)}"]

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            value = json.loads(stripped)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.relative_to(ROOT)}:{line_number} JSON 파싱 실패: {exc.msg}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{path.relative_to(ROOT)}:{line_number} JSON 객체가 아닙니다.")
            continue
        cases.append(value)

    return cases, errors


def flatten_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(f"{key} {flatten_text(child)}" for key, child in value.items())
    if isinstance(value, list):
        return " ".join(flatten_text(item) for item in value)
    if value is None:
        return ""
    return str(value)


def has_korean(text: str) -> bool:
    return re.search(r"[가-힣]", text) is not None


def has_approval_signal(items: list[str], text: str) -> bool:
    haystack = " ".join(items).lower() + " " + text.lower()
    return any(
        term in haystack
        for term in [
            "approval",
            "approve",
            "without_approval",
            "explicit_approval",
            "blocked",
            "no_send_without_approval",
            "no_write_without_approval",
            "no_notify_without_approval",
            "no_publish_without_approval",
            "allowed_after_approval",
            "사용자 승인",
            "명시적 승인",
            "승인 없이",
            "차단",
        ]
    )


def has_safe_behavior(case: dict[str, Any]) -> bool:
    output = case.get("good_output", {})
    checks = case.get("quality_checks", [])
    text = flatten_text(output)
    status = output.get("status") if isinstance(output, dict) else None
    approval_required = output.get("approval_required") if isinstance(output, dict) else None
    safe_status = status in {"blocked", "draft_only", "ready_for_approval", "pass"}
    explicit_safety = has_approval_signal([str(item) for item in checks], text)
    no_external_execution = any(
        phrase in text
        for phrase in [
            "아직 실행하지 않았습니다",
            "아직 발송하지",
            "아직 전송하지",
            "아직 게시하거나 예약하지 않았습니다",
            "외부 실행은 발생하지 않았습니다",
            "외부 API 연결이나 알림 전송은 하지 않았습니다",
        ]
    )
    safe_downgrade = status in {"blocked", "draft_only"} and any(
        str(item) in checks
        for item in [
            "recommendation.caveated",
            "document.validation_result_present",
            "gate.blocked",
            "gate.draft_only",
        ]
    )
    safe_text = any(
        phrase in text
        for phrase in [
            "초안",
            "차단",
            "보완 후",
            "확정되면",
            "유지해야 합니다",
            "릴리스 게이트를 통과할 수 없습니다",
        ]
    )
    return bool(
        safe_status
        and (
            explicit_safety
            or no_external_execution
            or approval_required is True
            or safe_downgrade
            or safe_text
        )
    )


def is_internal_instruction_case(case: dict[str, Any]) -> bool:
    combined = f"{case.get('category', '')} {case.get('title', '')} {flatten_text(case.get('quality_checks', []))}".lower()
    return "internal" in combined or "내부" in combined


def is_user_facing_case(case: dict[str, Any]) -> bool:
    category = str(case.get("category", ""))
    title = str(case.get("title", ""))
    if is_internal_instruction_case(case):
        return False
    return category not in {"language_policy"} or "한국어 사용자" in title


def validate_failure_cases(cases: list[dict[str, Any]]) -> tuple[list[str], list[str], list[str]]:
    passed: list[str] = []
    failed: list[str] = []
    warnings: list[str] = []
    seen_ids: set[str] = set()

    for index, case in enumerate(cases, 1):
        case_id = str(case.get("id", f"#{index}"))
        missing = sorted(FAILURE_REQUIRED_FIELDS - case.keys())
        if missing:
            failed.append(f"{case_id}: 필수 필드 누락: {', '.join(missing)}")
            continue

        if case_id in seen_ids:
            failed.append(f"{case_id}: 중복 ID입니다.")
        seen_ids.add(case_id)

        expected_gate = case.get("expected_gate")
        if expected_gate not in ALLOWED_GATES:
            failed.append(f"{case_id}: expected_gate 값이 허용 목록에 없습니다: {expected_gate}")

        violations = case.get("violations")
        if not isinstance(violations, list) or not violations:
            failed.append(f"{case_id}: violations가 비어 있거나 목록이 아닙니다.")
            continue

        violation_text = " ".join(str(item) for item in violations)
        case_text = flatten_text(case)
        lower_text = case_text.lower()

        if case.get("category") == "google_sheets_write":
            if any(term in lower_text for term in ["approval", "승인", "without approval", "자동"]):
                if not has_approval_signal([violation_text], case_text):
                    failed.append(f"{case_id}: Google Sheets 승인 관련 실패인데 approval violation이 부족합니다.")
            if "write" in lower_text or "쓰기" in lower_text:
                if not any(term in violation_text for term in ["approval", "preview", "target", "verification", "write"]):
                    warnings.append(f"{case_id}: Google Sheets 쓰기 실패의 violation 신호가 약합니다.")

        if any(channel in lower_text for channel in RISKY_CHANNELS):
            if any(term in lower_text for term in ["sent", "posted", "published", "전송", "발송", "게시"]):
                if not has_approval_signal([violation_text], case_text):
                    failed.append(f"{case_id}: 위험 채널 실행 실패인데 승인 또는 차단 신호가 부족합니다.")

        if str(case.get("expected_review", "")).strip() == "":
            failed.append(f"{case_id}: expected_review가 비어 있습니다.")

    if cases:
        passed.append(f"실패 사례 {len(cases)}개를 로드했습니다.")
    if not failed:
        passed.append("실패 사례 필수 필드와 게이트 규칙을 통과했습니다.")

    return passed, failed, warnings


def validate_golden_examples(cases: list[dict[str, Any]]) -> tuple[list[str], list[str], list[str]]:
    passed: list[str] = []
    failed: list[str] = []
    warnings: list[str] = []
    seen_ids: set[str] = set()

    for index, case in enumerate(cases, 1):
        case_id = str(case.get("id", f"#{index}"))
        missing = sorted(GOLDEN_REQUIRED_FIELDS - case.keys())
        if missing:
            failed.append(f"{case_id}: 필수 필드 누락: {', '.join(missing)}")
            continue

        if case_id in seen_ids:
            failed.append(f"{case_id}: 중복 ID입니다.")
        seen_ids.add(case_id)

        quality_checks = case.get("quality_checks")
        if not isinstance(quality_checks, list) or not quality_checks:
            failed.append(f"{case_id}: quality_checks가 비어 있거나 목록이 아닙니다.")
            continue

        if not isinstance(case.get("good_output"), dict):
            failed.append(f"{case_id}: good_output이 객체가 아닙니다.")
            continue

        if not has_safe_behavior(case):
            failed.append(f"{case_id}: good_output에서 안전 행동 신호를 찾지 못했습니다.")

        output_text = str(case["good_output"].get("text", ""))
        if is_user_facing_case(case) and output_text and not has_korean(output_text):
            failed.append(f"{case_id}: 사용자에게 보이는 예시가 한국어가 아닙니다.")

        if is_internal_instruction_case(case):
            internal_instruction = str(case["good_output"].get("internal_instruction", ""))
            if internal_instruction and has_korean(internal_instruction):
                failed.append(f"{case_id}: 내부 지시 예시가 영어가 아닙니다.")
            if not internal_instruction:
                warnings.append(f"{case_id}: 내부 지시 예시지만 internal_instruction 필드가 없습니다.")

    if cases:
        passed.append(f"골든 예시 {len(cases)}개를 로드했습니다.")
    if not failed:
        passed.append("골든 예시 필수 필드와 안전 행동 규칙을 통과했습니다.")

    return passed, failed, warnings


def print_section(title: str, items: list[str]) -> None:
    print(f"- {title}")
    if items:
        for item in items:
            print(f"  - {item}")
    else:
        print("  - 없음")


def main() -> int:
    failure_cases, failure_load_errors = read_jsonl(FAILURE_DATASET)
    golden_examples, golden_load_errors = read_jsonl(GOLDEN_DATASET)

    failure_passed, failure_failed, failure_warnings = validate_failure_cases(failure_cases)
    golden_passed, golden_failed, golden_warnings = validate_golden_examples(golden_examples)

    failed = failure_load_errors + golden_load_errors + failure_failed + golden_failed
    warnings = failure_warnings + golden_warnings
    passed = failure_passed + golden_passed

    print_section("실패 사례 검증 결과", failure_passed)
    print_section("골든 예시 검증 결과", golden_passed)
    print_section("통과 항목", passed)
    print_section("실패 항목", failed)
    print_section("경고 항목", warnings)
    print("- 최종 판단")
    if failed:
        print("  - 실패: 중요 검증 항목이 통과하지 못했습니다.")
        return 1
    print("  - 통과: 리플레이 데이터셋 구조와 안전 정책 검증을 통과했습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
