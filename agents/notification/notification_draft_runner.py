#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = ROOT / "examples/notification_inputs/sample_status_report_raw.md"
SLACK_OUTPUT = ROOT / "examples/notification_outputs/sample_slack_status_draft.md"
TELEGRAM_OUTPUT = ROOT / "examples/notification_outputs/sample_telegram_alert_draft.md"


@dataclass
class DraftSpec:
    title: str
    channel_type: str
    message_purpose: str
    body_lines: list[str]
    confirmation_lines: list[str]
    risk_lines: list[str]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def extract_bullets(source: str, heading: str) -> list[str]:
    pattern = re.compile(rf"^## {re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(source)
    if not match:
        return []
    body_start = match.end()
    next_match = re.search(r"^## .+$", source[body_start:], re.MULTILINE)
    body = source[body_start:] if not next_match else source[body_start : body_start + next_match.start()]
    bullets = [line.strip("- ").strip() for line in body.splitlines() if line.strip().startswith("-")]
    return bullets


def first_or_confirmation_needed(items: list[str]) -> str:
    return items[0] if items else "확인 필요"


def render_draft(spec: DraftSpec) -> str:
    body = "\n".join(f"- {line}" for line in spec.body_lines) if spec.body_lines else "- 확인 필요"
    confirmations = "\n".join(f"- {line}" for line in spec.confirmation_lines) if spec.confirmation_lines else "- 확인 필요"
    risks = "\n".join(f"- {line}" for line in spec.risk_lines) if spec.risk_lines else "- 확인 필요"
    return f"""# Notification Draft

### 제목

{spec.title}

### 채널 유형

{spec.channel_type}

### 메시지 목적

{spec.message_purpose}

### 초안 본문

{body}

### 승인 필요 여부

필요

### 발송 여부

발송하지 않음

### 확인이 필요한 부분

{confirmations}

### 위험 요소

{risks}
"""


def build_drafts(source: str) -> tuple[str, str]:
    status_items = extract_bullets(source, "상태 요약")
    completed_items = extract_bullets(source, "완료된 작업")
    risk_items = extract_bullets(source, "리스크")
    next_items = extract_bullets(source, "다음 작업")
    approval_items = extract_bullets(source, "승인 필요")

    slack_spec = DraftSpec(
        title="Slack 상태 요약 초안",
        channel_type="Slack",
        message_purpose="일일 상태 보고 초안과 팀 공유용 상태 요약",
        body_lines=[
            f"전체 상태: {first_or_confirmation_needed(status_items)}",
            f"완료된 작업: {first_or_confirmation_needed(completed_items)}",
            f"남은 리스크: {first_or_confirmation_needed(risk_items)}",
            f"다음 추천 작업: {first_or_confirmation_needed(next_items)}",
            "이 메시지는 초안이며 실제 Slack 알림은 발송하지 않았습니다.",
        ],
        confirmation_lines=[
            "수신 채널: 확인 필요",
            "승인 담당자: 확인 필요",
            "공유 마감일: 확인 필요",
            "외부 실행 여부: 확인 필요",
        ],
        risk_lines=[
            "승인 전 Slack 전송 금지",
            "외부 API 연결 없음",
            "수신 채널이 불명확하면 발송하면 안 됩니다.",
        ],
    )

    telegram_spec = DraftSpec(
        title="Telegram 긴급 알림 승인 요청 초안",
        channel_type="Telegram",
        message_purpose="긴급 알림 초안과 승인 요청 초안",
        body_lines=[
            f"긴급도: {first_or_confirmation_needed(risk_items)}",
            f"요청 내용: {first_or_confirmation_needed(approval_items)}",
            f"다음 조치: {first_or_confirmation_needed(next_items)}",
            "이 메시지는 승인 요청 초안이며 실제 Telegram 알림은 발송하지 않았습니다.",
        ],
        confirmation_lines=[
            "수신자: 확인 필요",
            "긴급도: 확인 필요",
            "승인 담당자: 확인 필요",
            "마감일: 확인 필요",
            "외부 실행 여부: 확인 필요",
        ],
        risk_lines=[
            "승인 전 Telegram 전송 금지",
            "외부 API 연결 없음",
            "긴급도가 불명확하면 알림을 보내면 안 됩니다.",
        ],
    )

    return render_draft(slack_spec), render_draft(telegram_spec)


def print_section(title: str, items: list[str]) -> None:
    print(f"- {title}")
    if not items:
        print("  - 없음")
        return
    for item in items:
        print(f"  - {item}")


def main() -> int:
    source = read_text(INPUT_FILE)
    if not source:
        print_section("Notification Draft 실행 결과", [])
        print_section("실패 항목", [f"입력 파일이 없습니다: {INPUT_FILE.relative_to(ROOT)}"])
        return 1

    slack_draft, telegram_draft = build_drafts(source)
    write_text(SLACK_OUTPUT, slack_draft)
    write_text(TELEGRAM_OUTPUT, telegram_draft)

    print_section(
        "Notification Draft 실행 결과",
        [
            f"입력 파일: {INPUT_FILE.relative_to(ROOT)}",
            f"Slack 초안: {SLACK_OUTPUT.relative_to(ROOT)}",
            f"Telegram 초안: {TELEGRAM_OUTPUT.relative_to(ROOT)}",
            "Slack/Telegram 발송: 수행하지 않음",
            "외부 API 연결: 수행하지 않음",
        ],
    )
    print("- 최종 판단")
    print("  - 통과: 한국어 알림 초안만 생성했습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
