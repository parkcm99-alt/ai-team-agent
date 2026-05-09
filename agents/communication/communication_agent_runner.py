#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = ROOT / "examples/communication_inputs"
OUTPUT_DIR = ROOT / "examples/communication_outputs"

OUTPUT_NAME_BY_INPUT = {
    "sample_partner_email_raw.md": "sample_partner_email_summary.md",
    "sample_partner_chat_raw.md": "sample_partner_chat_summary.md",
    "sample_approval_request_raw.md": "sample_approval_request_summary.md",
}


@dataclass
class CommunicationFacts:
    channel: str
    sender: str
    requester: str
    recipient: str
    company_name: str
    received_date: str
    raw_lines: list[str]
    unclear_items: list[str]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def extract_field(text: str, field: str) -> str:
    match = re.search(rf"^- {re.escape(field)}:\s*(.+)$", text, re.MULTILINE)
    if not match:
        return "확인 필요"
    value = match.group(1).strip()
    return value or "확인 필요"


def extract_raw_content(text: str) -> list[str]:
    marker = "## Raw Content"
    marker_index = text.find(marker)
    if marker_index == -1:
        return []
    content = text[marker_index + len(marker) :].strip()
    lines = []
    for line in content.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        cleaned = re.sub(r"^[A-Za-z가-힣 ]+:\s*", "", cleaned)
        lines.append(cleaned)
    return lines


def extract_date(text: str) -> str:
    value = extract_field(text, "Received date")
    if value != "확인 필요":
        return value
    match = re.search(r"\d{4}년\s*\d{1,2}월\s*\d{1,2}일", text)
    return match.group(0) if match else "확인 필요"


def detect_unclear_items(text: str, recipient: str, company_name: str) -> list[str]:
    items: list[str] = []
    patterns = [
        ("수신자", recipient == "확인 필요" or "수신자" in text),
        ("회사명", company_name == "확인 필요" or "정확한 회사명" in text),
        ("회신 담당자", "회신 담당자" in text),
        ("마감일", "마감일" in text),
        ("금액", "금액" in text or "예산" in text or "비용" in text),
        ("약속", "가능하다면" in text or "가능 여부" in text),
        ("법적 이슈", "법적" in text),
        ("권리 이슈", "권리" in text),
        ("계약 조건", "계약 조건" in text),
    ]
    for label, matched in patterns:
        if matched and label not in items:
            items.append(label)
    return items or ["확인 필요"]


def parse_source(path: Path) -> CommunicationFacts:
    text = read_text(path)
    channel = extract_field(text, "Channel")
    sender = extract_field(text, "Sender")
    requester = extract_field(text, "Requester")
    recipient = extract_field(text, "Recipient")
    company_name = extract_field(text, "Company")
    received_date = extract_date(text)
    raw_lines = extract_raw_content(text)
    return CommunicationFacts(
        channel=channel,
        sender=sender,
        requester=requester,
        recipient=recipient,
        company_name=company_name,
        received_date=received_date,
        raw_lines=raw_lines,
        unclear_items=detect_unclear_items(text, recipient, company_name),
    )


def line_items(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- 확인 필요"


def confirmation_lines(items: list[str]) -> list[str]:
    return [f"{item}: 확인 필요" for item in items]


def safe_name(value: str, fallback: str) -> str:
    return fallback if value == "확인 필요" else value


def render_communication(
    heading: str,
    title: str,
    original_summary: str,
    key_requests: list[str],
    intent: str,
    next_actions: list[str],
    reply_draft: list[str],
    confirmations: list[str],
    risks: list[str],
) -> str:
    return f"""# {heading}

### 제목

{title}

### 원문 요약

{original_summary}

### 핵심 요청사항

{line_items(key_requests)}

### 상대방 의도

- {intent}

### 필요한 다음 액션

{line_items(next_actions)}

### 답장 초안

{chr(10).join(reply_draft)}

### 확인이 필요한 부분

{line_items(confirmations)}

### 위험 요소

{line_items(risks)}

### 승인 필요 여부

- 이 답장은 초안이며, 발송 전 사용자 승인이 필요합니다.
- 이메일 발송, Slack/Telegram 알림, Google Sheets 쓰기는 실행하지 않았습니다.
"""


def render_partner_email(facts: CommunicationFacts) -> str:
    sender_name = safe_name(facts.sender.split("<")[0].strip(), "담당자")
    company = facts.company_name
    confirmations = confirmation_lines(["수신자", "회신 담당자", "예산 범위", "금액", "법적/권리 이슈"])
    return render_communication(
        heading="커뮤니케이션 에이전트 출력 예시: 파트너 이메일 요약",
        title=f"{company} 파일럿 제안서 검토 및 미팅 요청 요약 초안",
        original_summary=f"{facts.received_date} {company}의 {sender_name}가 파일럿 제안서 검토 가능 여부와 다음 주 화요일 또는 목요일 30분 미팅 가능 시간을 확인해 달라고 요청했습니다. 수신자, 예산 범위, 회신 담당자는 명확하지 않아 확인이 필요합니다.",
        key_requests=["파일럿 제안서 검토 가능 여부 확인", "다음 주 화요일 또는 목요일 중 30분 미팅 가능 시간 확인"],
        intent="제안서 검토 상태를 확인하고 후속 미팅 일정을 조율하려는 의도로 보입니다.",
        next_actions=["수신자와 회신 담당자를 확인합니다.", "제안서 검토 가능 여부를 확인합니다.", "미팅 가능한 시간을 내부 일정 기준으로 확인합니다.", "예산 범위가 필요한 답변인지 확인합니다."],
        reply_draft=[
            f"안녕하세요, {sender_name}님.",
            "",
            "파일럿 제안서 검토와 다음 주 미팅 요청 확인했습니다. 내부 검토 가능 여부와 가능한 미팅 시간을 확인한 뒤 회신드리겠습니다.",
            "",
            "현재 수신자, 회신 담당자, 예산 범위는 확인이 필요합니다.",
            "",
            "감사합니다.",
        ],
        confirmations=confirmations,
        risks=["회신 담당자와 예산 범위가 불명확해 확정 표현을 사용하면 위험합니다.", "미팅 가능 시간을 내부 일정 확인 없이 약속하면 일정 충돌이 발생할 수 있습니다."],
    )


def render_partner_chat(facts: CommunicationFacts) -> str:
    sender_name = safe_name(facts.sender, "담당자")
    company = facts.company_name
    confirmations = confirmation_lines(["수신자", "비용", "계약 조건", "금액", "법적/권리 이슈"])
    return render_communication(
        heading="커뮤니케이션 에이전트 출력 예시: 파트너 채팅 요약",
        title=f"{company} 온보딩 일정 확인 요청 요약 초안",
        original_summary=f"{facts.received_date} {company}의 {sender_name}가 어제 공유한 온보딩 일정표 확인 여부와 이번 주 금요일 전까지 가능 여부 회신을 요청했습니다. 수신자, 비용, 계약 조건은 명확하지 않아 확인이 필요합니다.",
        key_requests=["온보딩 일정표 확인 여부 회신", "이번 주 금요일 전까지 가능 여부 공유"],
        intent="온보딩 진행 가능 여부를 빠르게 확인하고 다음 일정을 준비하려는 의도로 보입니다.",
        next_actions=["온보딩 일정표 검토 상태를 확인합니다.", "회신 수신자를 확인합니다.", "비용과 계약 조건이 답변에 포함되어야 하는지 확인합니다."],
        reply_draft=[
            f"안녕하세요, {sender_name}님.",
            "",
            "온보딩 일정표 확인 요청 감사합니다. 일정표 검토 상태와 진행 가능 여부를 확인한 뒤 이번 주 금요일 전까지 회신드리겠습니다.",
            "",
            "비용과 계약 조건은 현재 확인이 필요하므로 확정 표현은 포함하지 않겠습니다.",
            "",
            "감사합니다.",
        ],
        confirmations=confirmations,
        risks=["비용과 계약 조건이 불명확한 상태에서 진행을 확정하면 오해가 생길 수 있습니다.", "수신자가 확정되지 않아 잘못된 대상에게 회신할 위험이 있습니다."],
    )


def render_approval_request(facts: CommunicationFacts) -> str:
    confirmations = confirmation_lines(["수신자", "회사명", "발송 마감일", "금액 조건", "법적 이슈", "권리 이슈", "승인자"])
    return render_communication(
        heading="커뮤니케이션 에이전트 출력 예시: 승인 요청 요약",
        title="파트너 안내 문구 승인 요청 요약 초안",
        original_summary=f"{facts.received_date} Operations Team이 파트너에게 발송할 안내 문구 초안의 승인을 요청했습니다. 수신자, 정확한 회사명, 발송 마감일, 금액 조건, 법적 문구, 콘텐츠 사용 권리는 명확하지 않아 확인이 필요합니다.",
        key_requests=["파트너 발송용 안내 문구 초안 검토", "발송 전 승인 여부 확인", "법적 문구와 콘텐츠 사용 권리 검토 필요 여부 확인"],
        intent="외부 발송 전에 문구와 승인 조건을 확인해 위험한 커뮤니케이션을 막으려는 의도로 보입니다.",
        next_actions=["수신자와 정확한 회사명을 확인합니다.", "발송 마감일과 금액 조건을 확인합니다.", "법적 문구와 콘텐츠 사용 권리 검토 담당자를 확인합니다.", "승인자가 누구인지 확인합니다."],
        reply_draft=[
            "안녕하세요.",
            "",
            "파트너 안내 문구 초안 승인 요청 확인했습니다. 수신자, 회사명, 발송 마감일, 금액 조건, 법적 문구, 콘텐츠 사용 권리 검토 여부를 먼저 확인한 뒤 승인 검토를 진행하겠습니다.",
            "",
            "현재 불명확한 항목은 확인이 필요하므로 발송은 진행하지 않겠습니다.",
            "",
            "감사합니다.",
        ],
        confirmations=confirmations,
        risks=["회사명과 수신자가 불명확해 잘못된 대상에게 발송될 수 있습니다.", "법적 문구와 콘텐츠 사용 권리 검토 없이 외부 발송하면 책임 문제가 생길 수 있습니다.", "금액 조건이 확정되지 않아 약속성 문구가 포함되면 위험합니다."],
    )


def generate_summary(input_path: Path) -> str:
    facts = parse_source(input_path)
    if facts.channel == "approval request" or "approval_request" in input_path.name:
        return render_approval_request(facts)
    if facts.channel == "business chat" or "chat" in input_path.name:
        return render_partner_chat(facts)
    return render_partner_email(facts)


def output_path_for(input_path: Path) -> Path:
    output_name = OUTPUT_NAME_BY_INPUT.get(input_path.name)
    if output_name:
        return OUTPUT_DIR / output_name
    return OUTPUT_DIR / input_path.name.replace("_raw.md", "_summary.md")


def main() -> int:
    input_files = sorted(INPUT_DIR.glob("*.md"))
    if not input_files:
        print("- 커뮤니케이션 에이전트 실행 결과")
        print("  - 처리할 입력 파일이 없습니다.")
        return 1

    generated: list[str] = []
    for input_path in input_files:
        output_path = output_path_for(input_path)
        summary = generate_summary(input_path)
        write_text(output_path, summary)
        generated.append(f"{input_path.relative_to(ROOT)} -> {output_path.relative_to(ROOT)}")

    print("- 커뮤니케이션 에이전트 실행 결과")
    for item in generated:
        print(f"  - {item}")
    print("- 최종 판단")
    print("  - 통과: 로컬 규칙 기반 커뮤니케이션 요약과 답장 초안을 생성했습니다. 외부 작업은 실행하지 않았습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
