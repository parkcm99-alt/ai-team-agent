#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = ROOT / "examples/email_inputs"
OUTPUT_DIR = ROOT / "examples/email_outputs"
UNCLEAR_MARKER = "확인 필요"


@dataclass
class EmailFacts:
    source_name: str
    sender: str
    recipient: str
    company_name: str
    received_date: str
    subject: str
    deadline: str
    requested_action: str
    price: str
    quantity: str
    legal_or_rights_issue: str
    promise: str
    raw_lines: list[str]
    confirmation_needed: list[str]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def extract_field(text: str, field: str) -> str:
    match = re.search(rf"^- {re.escape(field)}:\s*(.+)$", text, re.MULTILINE)
    if not match:
        return UNCLEAR_MARKER
    value = match.group(1).strip()
    return value or UNCLEAR_MARKER


def extract_raw_content(text: str) -> list[str]:
    marker = "## Raw Email"
    marker_index = text.find(marker)
    if marker_index == -1:
        return []
    content = text[marker_index + len(marker) :].strip()
    lines: list[str] = []
    for line in content.splitlines():
        cleaned = line.strip()
        if cleaned:
            lines.append(cleaned)
    return lines


def detect_value(text: str, label: str, patterns: list[str]) -> str:
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()
    if label in text:
        return UNCLEAR_MARKER
    return UNCLEAR_MARKER


def detect_confirmation_needed(facts: EmailFacts) -> list[str]:
    items: list[str] = []
    fields = [
        ("수신자", facts.recipient),
        ("회사명", facts.company_name),
        ("마감일", facts.deadline),
        ("요청 작업", facts.requested_action),
        ("법적/권리 이슈", facts.legal_or_rights_issue),
        ("가격", facts.price),
        ("수량", facts.quantity),
        ("약속", facts.promise),
    ]
    for label, value in fields:
        if value == UNCLEAR_MARKER:
            items.append(f"{label}: {UNCLEAR_MARKER}")
    return items or [f"추가 확인 항목: {UNCLEAR_MARKER}"]


def parse_email(path: Path) -> EmailFacts:
    text = read_text(path)
    raw_lines = extract_raw_content(text)
    sender = extract_field(text, "Sender")
    recipient = extract_field(text, "Recipient")
    company_name = extract_field(text, "Company")
    received_date = extract_field(text, "Received date")
    subject = extract_field(text, "Subject")
    deadline = extract_field(text, "Deadline")
    requested_action = extract_field(text, "Requested action")
    price = extract_field(text, "Price")
    quantity = extract_field(text, "Quantity")
    legal_or_rights_issue = extract_field(text, "Legal or rights issue")
    promise = extract_field(text, "Promise")

    facts = EmailFacts(
        source_name=path.name,
        sender=sender,
        recipient=recipient,
        company_name=company_name,
        received_date=received_date,
        subject=subject,
        deadline=deadline,
        requested_action=requested_action,
        price=price,
        quantity=quantity,
        legal_or_rights_issue=legal_or_rights_issue,
        promise=promise,
        raw_lines=raw_lines,
        confirmation_needed=[],
    )
    facts.confirmation_needed = detect_confirmation_needed(facts)
    return facts


def bullet_lines(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else f"- {UNCLEAR_MARKER}"


def display_value(value: str) -> str:
    return value if value else UNCLEAR_MARKER


def sender_name(sender: str) -> str:
    if sender == UNCLEAR_MARKER:
        return "담당자"
    return sender.split("<")[0].strip() or "담당자"


def make_summary(facts: EmailFacts) -> str:
    return (
        f"{facts.received_date} 수신된 {facts.company_name} 관련 이메일입니다. "
        f"제목은 `{facts.subject}`이며, 주요 요청은 {facts.requested_action}입니다. "
        "불명확한 항목은 확인 필요로 표시했습니다."
    )


def make_major_requests(facts: EmailFacts) -> list[str]:
    requests = [facts.requested_action]
    if facts.deadline != UNCLEAR_MARKER:
        requests.append(f"회신 또는 조치 희망 시점: {facts.deadline}")
    if facts.price != UNCLEAR_MARKER:
        requests.append(f"가격 조건 확인: {facts.price}")
    if facts.quantity != UNCLEAR_MARKER:
        requests.append(f"수량 조건 확인: {facts.quantity}")
    return [item if item != UNCLEAR_MARKER else f"요청 작업: {UNCLEAR_MARKER}" for item in requests]


def make_decisions_needed(facts: EmailFacts) -> list[str]:
    decisions = [
        "답장 발송 여부를 사용자가 승인해야 합니다.",
        f"수신자 확인: {display_value(facts.recipient)}",
        f"회사명 확인: {display_value(facts.company_name)}",
    ]
    if facts.price == UNCLEAR_MARKER:
        decisions.append(f"가격 조건: {UNCLEAR_MARKER}")
    if facts.promise == UNCLEAR_MARKER:
        decisions.append(f"약속 가능 범위: {UNCLEAR_MARKER}")
    if facts.legal_or_rights_issue == UNCLEAR_MARKER:
        decisions.append(f"법적/권리 이슈: {UNCLEAR_MARKER}")
    return decisions


def make_next_actions(facts: EmailFacts) -> list[str]:
    return [
        "사용자가 이메일 내용과 수신자를 검토합니다.",
        "불명확한 항목을 확인합니다.",
        "답장 초안을 검토한 뒤 발송 여부를 명시적으로 승인합니다.",
    ]


def make_reply_draft(facts: EmailFacts) -> list[str]:
    name = sender_name(facts.sender)
    return [
        f"안녕하세요, {name}님.",
        "",
        f"보내주신 `{facts.subject}` 관련 이메일 확인했습니다.",
        f"요청하신 사항은 현재 내부 확인이 필요하며, {facts.requested_action}에 대해 검토 후 회신드리겠습니다.",
        "",
        "수신자, 회사명, 마감일, 가격, 수량, 약속 범위 또는 법적/권리 이슈 중 불명확한 항목은 확인 후 답변드리겠습니다.",
        "아직 이메일은 발송하지 않았으며, 사용자 승인 후에만 발송을 검토할 수 있습니다.",
        "",
        "감사합니다.",
    ]


def make_risks(facts: EmailFacts) -> list[str]:
    risks = [
        "Gmail API는 연결하지 않았습니다.",
        "실제 이메일 발송과 Gmail 초안 생성은 수행하지 않았습니다.",
        "사용자 승인 없이 발송하면 안 됩니다.",
    ]
    if facts.confirmation_needed:
        risks.append("불명확한 항목이 있어 확정 표현이나 과도한 약속을 피해야 합니다.")
    return risks


def render_email_output(heading: str, title: str, facts: EmailFacts) -> str:
    return f"""# {heading}

### 제목

{title}

### 원문 요약

{make_summary(facts)}

### 주요 요청 사항

{bullet_lines(make_major_requests(facts))}

### 결정 필요 사항

{bullet_lines(make_decisions_needed(facts))}

### 다음 액션

{bullet_lines(make_next_actions(facts))}

### 답장 초안

{chr(10).join(make_reply_draft(facts))}

### 수신자

{display_value(facts.recipient)}

### 회사명

{display_value(facts.company_name)}

### 발송 여부

발송하지 않음

- Gmail API 연결 여부: 연결하지 않음
- Gmail API를 통한 실제 초안 생성 여부: 생성하지 않음

### 승인 필요 여부

필요

### 확인이 필요한 부분

{bullet_lines(facts.confirmation_needed)}

### 위험 요소

{bullet_lines(make_risks(facts))}
"""


def generate_outputs() -> list[tuple[Path, Path]]:
    input_files = sorted(INPUT_DIR.glob("*.md"))
    if not input_files:
        return []

    facts_by_name = {path.name: parse_email(path) for path in input_files}
    partner = facts_by_name.get("sample_partner_email_raw.md") or next(iter(facts_by_name.values()))
    followup = facts_by_name.get("sample_meeting_followup_email_raw.md") or partner

    outputs = [
        (
            INPUT_DIR / partner.source_name,
            OUTPUT_DIR / "sample_partner_email_summary.md",
            render_email_output(
                "Email Draft Agent 출력: 파트너 이메일 요약",
                f"{partner.company_name} 이메일 요약",
                partner,
            ),
        ),
        (
            INPUT_DIR / partner.source_name,
            OUTPUT_DIR / "sample_partner_reply_draft.md",
            render_email_output(
                "Email Draft Agent 출력: 파트너 답장 초안",
                f"{partner.company_name} 답장 초안",
                partner,
            ),
        ),
        (
            INPUT_DIR / followup.source_name,
            OUTPUT_DIR / "sample_email_approval_request.md",
            render_email_output(
                "Email Draft Agent 출력: 이메일 발송 승인 요청서",
                f"{followup.company_name} 이메일 발송 승인 요청",
                followup,
            ),
        ),
    ]

    generated: list[tuple[Path, Path]] = []
    for input_path, output_path, content in outputs:
        write_text(output_path, content)
        generated.append((input_path, output_path))
    return generated


def main() -> int:
    generated = generate_outputs()
    print("- Email Draft 실행 결과")
    if not generated:
        print("  - 처리할 입력 파일이 없습니다.")
        print("- 최종 판단")
        print("  - 실패: 로컬 샘플 이메일 입력이 필요합니다.")
        return 1

    for input_path, output_path in generated:
        print(f"  - {input_path.relative_to(ROOT)} -> {output_path.relative_to(ROOT)}")
    print("- 외부 실행 여부")
    print("  - 실제 이메일 발송 여부: 발송하지 않음")
    print("  - Gmail API 연결 여부: 연결하지 않음")
    print("  - Gmail API 초안 생성 여부: 생성하지 않음")
    print("- 최종 판단")
    print("  - 통과: 로컬 이메일 요약, 답장 초안, 승인 요청서를 생성했습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
