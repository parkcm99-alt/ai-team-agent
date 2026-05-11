#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = ROOT / "examples/sheets_write_inputs/sample_write_requests.jsonl"
OUTPUT_FILE = ROOT / "examples/sheets_write_outputs/sample_write_approval_report.md"
UNCLEAR_MARKER = "확인 필요"

REQUIRED_FIELDS = [
    "target_spreadsheet",
    "target_tab",
    "target_row",
    "target_column",
    "original_value",
    "proposed_value",
    "change_reason",
    "post_write_verification_plan",
]


@dataclass
class WriteRequest:
    request_id: str
    request_summary: str
    target_spreadsheet: str
    target_tab: str
    target_row: str
    target_column: str
    original_value: str
    proposed_value: str
    change_reason: str
    post_write_verification_plan: str
    execute_requested: bool
    explicit_approval: bool


@dataclass
class ApprovalDecision:
    request: WriteRequest
    gate_status: str
    risk_factors: list[str]
    confirmation_needed: list[str]


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


def normalize_value(value: object) -> str:
    text = str(value or "").strip()
    return text if text else UNCLEAR_MARKER


def parse_request(record: dict[str, Any]) -> WriteRequest:
    return WriteRequest(
        request_id=normalize_value(record.get("id")),
        request_summary=normalize_value(record.get("request_summary")),
        target_spreadsheet=normalize_value(record.get("target_spreadsheet")),
        target_tab=normalize_value(record.get("target_tab")),
        target_row=normalize_value(record.get("target_row")),
        target_column=normalize_value(record.get("target_column")),
        original_value=normalize_value(record.get("original_value")),
        proposed_value=normalize_value(record.get("proposed_value")),
        change_reason=normalize_value(record.get("change_reason")),
        post_write_verification_plan=normalize_value(record.get("post_write_verification_plan")),
        execute_requested=bool(record.get("execute_requested", False)),
        explicit_approval=bool(record.get("explicit_approval", False)),
    )


def classify_request(request: WriteRequest) -> ApprovalDecision:
    risk_factors = [
        "실제 Google Sheets 쓰기는 MVP에서 비활성화되어 있습니다.",
        "명시적 승인 전에는 어떤 쓰기 작업도 실행할 수 없습니다.",
    ]
    confirmation_needed: list[str] = []

    field_values = {
        "대상 스프레드시트": request.target_spreadsheet,
        "대상 탭": request.target_tab,
        "대상 행": request.target_row,
        "대상 열": request.target_column,
        "원본 값": request.original_value,
        "제안 값": request.proposed_value,
        "변경 사유": request.change_reason,
        "사후 검증 계획": request.post_write_verification_plan,
    }
    for label, value in field_values.items():
        if value == UNCLEAR_MARKER:
            confirmation_needed.append(f"{label}: {UNCLEAR_MARKER}")

    if request.execute_requested:
        risk_factors.append("즉시 쓰기 요청이 감지되어 차단 상태로 낮췄습니다.")
    if not request.explicit_approval:
        risk_factors.append("명시적 사용자 승인이 아직 없습니다.")

    gate_status = "blocked" if request.execute_requested or confirmation_needed else "approval_required"
    if gate_status == "approval_required":
        confirmation_needed.append("사용자 명시적 승인: 확인 필요")

    return ApprovalDecision(
        request=request,
        gate_status=gate_status,
        risk_factors=risk_factors,
        confirmation_needed=confirmation_needed or ["사용자 명시적 승인: 확인 필요"],
    )


def bullet_lines(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else f"- {UNCLEAR_MARKER}"


def decision_label(decision: ApprovalDecision) -> str:
    if decision.gate_status == "blocked":
        return "차단"
    return "승인 필요"


def render_report(decisions: list[ApprovalDecision]) -> str:
    first = decisions[0] if decisions else None
    request = first.request if first else None
    all_risks = []
    all_confirmations = []
    final_statuses = []
    for decision in decisions:
        all_risks.append(f"{decision.request.request_id}: {', '.join(decision.risk_factors)}")
        all_confirmations.append(f"{decision.request.request_id}: {', '.join(decision.confirmation_needed)}")
        final_statuses.append(f"{decision.request.request_id}: {decision_label(decision)}")

    return f"""# Sheets Write Approval Report

### 제목

Google Sheets 쓰기 승인 요청서

### 요청 요약

{request.request_summary if request else UNCLEAR_MARKER}

### 승인 필요 여부

필요

### 실제 쓰기 수행 여부

수행하지 않음

- Google Sheets API 연결 여부: 연결하지 않음
- Google 인증 정보 사용 여부: 사용하지 않음
- 실제 스프레드시트 쓰기, 수정, 삭제, 추가, 업데이트를 수행하지 않았습니다.

### 대상 스프레드시트

{request.target_spreadsheet if request else UNCLEAR_MARKER}

### 대상 탭

{request.target_tab if request else UNCLEAR_MARKER}

### 대상 행

{request.target_row if request else UNCLEAR_MARKER}

### 대상 열

{request.target_column if request else UNCLEAR_MARKER}

### 원본 값

{request.original_value if request else UNCLEAR_MARKER}

### 제안 값

{request.proposed_value if request else UNCLEAR_MARKER}

### 변경 사유

{request.change_reason if request else UNCLEAR_MARKER}

### 위험 요소

{bullet_lines(all_risks)}

### 확인이 필요한 부분

{bullet_lines(all_confirmations)}

### 사후 검증 계획

{request.post_write_verification_plan if request else UNCLEAR_MARKER}

### 최종 상태

{bullet_lines(final_statuses)}
"""


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def print_section(title: str, items: list[str]) -> None:
    print(f"- {title}")
    if not items:
        print("  - 없음")
        return
    for item in items:
        print(f"  - {item}")


def main() -> int:
    records = read_jsonl(INPUT_FILE)
    if not records:
        print_section("Sheets Write Approval 실행 결과", [])
        print_section("실패 항목", [f"입력 파일이 없거나 비어 있습니다: {INPUT_FILE.relative_to(ROOT)}"])
        return 1

    decisions = [classify_request(parse_request(record)) for record in records]
    report = render_report(decisions)
    write_text(OUTPUT_FILE, report)

    print_section(
        "Sheets Write Approval 실행 결과",
        [
            f"처리한 요청: {len(decisions)}개",
            f"생성된 승인 요청서: {OUTPUT_FILE.relative_to(ROOT)}",
            "실제 쓰기 수행 여부: 수행하지 않음",
            "Google Sheets API 연결 여부: 연결하지 않음",
        ],
    )
    print("- 최종 판단")
    print("  - 통과: 로컬 승인 요청서만 생성했습니다. 실제 Google Sheets 쓰기는 수행하지 않았습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
