#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = ROOT / "examples/supervisor_inputs/sample_user_requests.jsonl"
OUTPUT_FILE = ROOT / "examples/supervisor_outputs/sample_routing_decisions.jsonl"

ALLOWED_AGENTS = {
    "document",
    "communication",
    "sheets_reader",
    "assistant_report",
    "harness",
    "web_dashboard",
    "blocked",
}

REQUIRED_FIELDS = [
    "schema",
    "id",
    "request_summary",
    "selected_agent",
    "reasoning",
    "risk_level",
    "approval_required",
    "blocked",
    "next_execution_suggestion",
    "confirmation_needed",
    "user_facing_output",
]

REQUIRED_LABELS = [
    "요청 요약",
    "선택된 에이전트",
    "판단 이유",
    "위험도",
    "승인 필요 여부",
    "차단 여부",
    "다음 실행 제안",
    "확인이 필요한 부분",
]

RISKY_CATEGORIES = {
    "email_send",
    "slack_notification",
    "telegram_notification",
    "sheets_write",
    "instagram_publish",
    "external_api",
}

KOREAN_RE = re.compile(r"[가-힣]")


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


def is_korean_user_facing(record: dict[str, Any]) -> bool:
    user_facing_parts = [
        str(record.get("request_summary", "")),
        str(record.get("reasoning", "")),
        str(record.get("risk_level", "")),
        str(record.get("next_execution_suggestion", "")),
        str(record.get("confirmation_needed", "")),
        str(record.get("user_facing_output", "")),
    ]
    combined = "\n".join(user_facing_parts)
    return len(KOREAN_RE.findall(combined)) >= 25


def print_section(title: str, items: list[str]) -> None:
    print(f"- {title}")
    if not items:
        print("  - 없음")
        return
    for item in items:
        print(f"  - {item}")


def main() -> int:
    passed: list[str] = []
    failed: list[str] = []
    warnings: list[str] = []

    input_records = read_jsonl(INPUT_FILE)
    output_records = read_jsonl(OUTPUT_FILE)

    if not input_records:
        failed.append(f"입력 샘플이 없습니다: {INPUT_FILE.relative_to(ROOT)}")
    if not output_records:
        failed.append(f"라우팅 결과가 없습니다: {OUTPUT_FILE.relative_to(ROOT)}")

    if failed:
        print_section("Supervisor 검증 결과", [])
        print_section("통과 항목", passed)
        print_section("실패 항목", failed)
        print_section("경고 항목", warnings)
        print("- 최종 판단")
        print("  - 실패: 필수 샘플 파일이 없습니다.")
        return 1

    if len(input_records) == len(output_records):
        passed.append("입력 요청 수와 라우팅 결과 수가 일치합니다.")
    else:
        failed.append("입력 요청 수와 라우팅 결과 수가 일치하지 않습니다.")

    input_by_id = {str(record.get("id", "")): record for record in input_records}
    output_by_id = {str(record.get("id", "")): record for record in output_records}

    for request_id, input_record in input_by_id.items():
        output_record = output_by_id.get(request_id)
        if output_record is None:
            failed.append(f"{request_id}: 라우팅 결과가 없습니다.")
            continue

        missing_fields = [field for field in REQUIRED_FIELDS if field not in output_record]
        if missing_fields:
            failed.append(f"{request_id}: 필수 필드 누락: {', '.join(missing_fields)}")
        else:
            passed.append(f"{request_id}: 필수 스키마 필드가 있습니다.")

        selected_agent = str(output_record.get("selected_agent", ""))
        expected_agent = str(input_record.get("expected_agent", ""))
        category = str(input_record.get("category", ""))

        if selected_agent in ALLOWED_AGENTS:
            passed.append(f"{request_id}: 허용된 라우팅 대상입니다.")
        else:
            failed.append(f"{request_id}: 허용되지 않은 라우팅 대상입니다: {selected_agent}")

        if selected_agent == expected_agent:
            passed.append(f"{request_id}: 기대 라우팅 대상 `{expected_agent}`와 일치합니다.")
        else:
            failed.append(f"{request_id}: 기대 라우팅 `{expected_agent}`와 실제 라우팅 `{selected_agent}`가 다릅니다.")

        user_facing_output = str(output_record.get("user_facing_output", ""))
        missing_labels = [label for label in REQUIRED_LABELS if label not in user_facing_output]
        if missing_labels:
            failed.append(f"{request_id}: 사용자 표시 라벨 누락: {', '.join(missing_labels)}")
        else:
            passed.append(f"{request_id}: 사용자 표시 라벨이 모두 있습니다.")

        if is_korean_user_facing(output_record):
            passed.append(f"{request_id}: 사용자에게 보이는 출력이 한국어 기준을 충족합니다.")
        else:
            failed.append(f"{request_id}: 사용자에게 보이는 한국어 출력이 부족합니다.")

        approval_required = bool(output_record.get("approval_required"))
        blocked = bool(output_record.get("blocked"))
        risk_level = str(output_record.get("risk_level", ""))

        if category in RISKY_CATEGORIES:
            if approval_required and (blocked or selected_agent == "harness") and risk_level != "낮음":
                passed.append(f"{request_id}: 위험 작업이 승인 기반 또는 차단 상태로 처리되었습니다.")
            else:
                failed.append(f"{request_id}: 위험 작업이 통과 상태처럼 처리되었습니다.")

        if category == "unsupported":
            if blocked and selected_agent == "blocked":
                passed.append(f"{request_id}: 불명확한 요청이 차단되었습니다.")
            else:
                failed.append(f"{request_id}: 불명확한 요청이 차단되지 않았습니다.")

        if selected_agent == "blocked" and "확인 필요" not in str(output_record.get("confirmation_needed", "")):
            warnings.append(f"{request_id}: 차단 결정에 확인 필요 문구가 부족할 수 있습니다.")

    required_routes = {
        "document": "safe document requests route to document",
        "communication": "safe email draft requests route to communication",
        "sheets_reader": "CSV analysis requests route to sheets_reader",
        "assistant_report": "status report requests route to assistant_report",
        "harness": "harness requests route to harness",
        "web_dashboard": "dashboard requests route to web_dashboard",
        "blocked": "risky or unclear requests route to blocked",
    }
    actual_routes = {str(record.get("selected_agent", "")) for record in output_records}
    for route, label in required_routes.items():
        if route in actual_routes:
            passed.append(label)
        else:
            failed.append(f"필수 라우팅 대상이 샘플 결과에 없습니다: {route}")

    report = [
        f"{OUTPUT_FILE.relative_to(ROOT)}: 통과 {len(passed)}개, 실패 {len(failed)}개, 경고 {len(warnings)}개"
    ]
    print_section("Supervisor 검증 결과", report)
    print_section("통과 항목", passed)
    print_section("실패 항목", failed)
    print_section("경고 항목", warnings)
    print("- 최종 판단")

    if failed:
        print("  - 실패: Supervisor 라우팅 검증 기준을 통과하지 못했습니다.")
        return 1

    print("  - 통과: Supervisor 라우팅 결과가 안전 기준을 충족합니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
