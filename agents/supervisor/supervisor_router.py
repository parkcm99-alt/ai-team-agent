#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, dataclass
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

DECISION_LABELS = [
    "요청 요약",
    "선택된 에이전트",
    "판단 이유",
    "위험도",
    "승인 필요 여부",
    "차단 여부",
    "다음 실행 제안",
    "확인이 필요한 부분",
]


@dataclass
class RoutingDecision:
    schema: str
    id: str
    request_summary: str
    selected_agent: str
    reasoning: str
    risk_level: str
    approval_required: bool
    blocked: bool
    next_execution_suggestion: str
    confirmation_needed: str
    user_facing_output: str


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


def write_jsonl(path: Path, records: list[RoutingDecision]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(asdict(record), ensure_ascii=False, sort_keys=True) for record in records]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def contains_any(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms)


def asks_not_to_execute(text: str) -> bool:
    return contains_any(
        text,
        [
            "do not",
            "don't",
            "without sending",
            "without writing",
            "하지 마",
            "하지말",
            "수행하지",
            "실행하지",
            "발송은 하지",
            "발송하지",
            "보내지",
            "전송하지",
            "쓰기는 하지",
            "쓰지",
            "게시하지",
        ],
    )


def has_explicit_approval(text: str) -> bool:
    negative_terms = [
        "without approval",
        "no approval",
        "not approved",
        "승인 없이",
        "승인 없음",
        "미승인",
        "승인 전",
    ]
    if contains_any(text, negative_terms):
        return False
    positive_terms = [
        "explicit approval granted",
        "approved by user",
        "user approved",
        "사용자 승인 완료",
        "명시적 승인 완료",
        "승인했습니다",
        "승인 받았습니다",
        "승인됨",
    ]
    return contains_any(text, positive_terms)


def has_rights_confirmation(text: str) -> bool:
    negative_terms = [
        "without rights",
        "rights not confirmed",
        "권리 확인 없이",
        "권리 미확인",
        "저작권 확인 전",
    ]
    if contains_any(text, negative_terms):
        return False
    positive_terms = [
        "rights confirmed",
        "rights checklist completed",
        "권리 확인 완료",
        "권리 체크리스트 완료",
        "게시 권한 확인 완료",
    ]
    return contains_any(text, positive_terms)


def is_email_send_request(text: str) -> bool:
    if asks_not_to_execute(text):
        return False
    return contains_any(text, ["email", "gmail", "메일", "이메일"]) and contains_any(
        text,
        ["send", "sent", "발송", "보내", "전송", "회신 완료"],
    ) and not contains_any(text, ["draft", "초안", "summary", "요약"])


def is_slack_or_telegram_notification(text: str) -> bool:
    if asks_not_to_execute(text):
        return False
    return contains_any(text, ["slack", "telegram", "텔레그램"]) and contains_any(
        text,
        ["send", "notify", "notification", "post", "message", "알림", "전송", "보내", "공지"],
    ) and not contains_any(text, ["draft", "초안", "summary", "요약"])


def is_sheets_write_request(text: str) -> bool:
    if asks_not_to_execute(text):
        return False
    return contains_any(text, ["google sheets", "spreadsheet", "sheet", "시트", "스프레드시트"]) and contains_any(
        text,
        ["write", "update", "delete", "append", "edit", "쓰기", "수정", "삭제", "추가", "업데이트", "기록"],
    )


def is_instagram_publish_request(text: str) -> bool:
    if asks_not_to_execute(text):
        return False
    return contains_any(text, ["instagram", "인스타그램"]) and contains_any(
        text,
        ["publish", "post", "upload", "게시", "업로드", "발행"],
    )


def is_external_api_request(text: str) -> bool:
    return contains_any(
        text,
        [
            "external api",
            "call api",
            "connect api",
            "api 연결",
            "외부 api",
            "credentials",
            "credential",
            "api key",
            "token",
            "토큰",
            "인증 정보",
        ],
    )


def is_unclear_or_unsupported(text: str) -> bool:
    normalized = re.sub(r"\s+", " ", text.strip())
    if len(normalized) < 8:
        return True
    return contains_any(
        normalized,
        [
            "do that thing",
            "whatever",
            "unsupported",
            "그거 해줘",
            "알아서 처리",
            "뭔지 모르지만",
        ],
    )


def summarize_request(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text.strip())
    if len(normalized) <= 80:
        return normalized
    return f"{normalized[:77]}..."


def format_user_facing(decision: RoutingDecision) -> str:
    approval = "필요" if decision.approval_required else "필요 없음"
    blocked = "차단" if decision.blocked else "차단하지 않음"
    return "\n".join(
        [
            f"요청 요약: {decision.request_summary}",
            f"선택된 에이전트: {decision.selected_agent}",
            f"판단 이유: {decision.reasoning}",
            f"위험도: {decision.risk_level}",
            f"승인 필요 여부: {approval}",
            f"차단 여부: {blocked}",
            f"다음 실행 제안: {decision.next_execution_suggestion}",
            f"확인이 필요한 부분: {decision.confirmation_needed}",
        ]
    )


def make_decision(
    request_id: str,
    text: str,
    selected_agent: str,
    reasoning: str,
    risk_level: str,
    approval_required: bool,
    blocked: bool,
    next_execution_suggestion: str,
    confirmation_needed: str,
) -> RoutingDecision:
    decision = RoutingDecision(
        schema="supervisor_routing_decision_v1",
        id=request_id,
        request_summary=summarize_request(text),
        selected_agent=selected_agent,
        reasoning=reasoning,
        risk_level=risk_level,
        approval_required=approval_required,
        blocked=blocked,
        next_execution_suggestion=next_execution_suggestion,
        confirmation_needed=confirmation_needed,
        user_facing_output="",
    )
    decision.user_facing_output = format_user_facing(decision)
    return decision


def block_decision(request_id: str, text: str, reason: str, confirmation_needed: str) -> RoutingDecision:
    return make_decision(
        request_id=request_id,
        text=text,
        selected_agent="blocked",
        reasoning=reason,
        risk_level="높음",
        approval_required=True,
        blocked=True,
        next_execution_suggestion="요청을 실행하지 말고, 필요한 승인과 세부 정보를 먼저 확인합니다.",
        confirmation_needed=confirmation_needed,
    )


def route_request(record: dict[str, Any]) -> RoutingDecision:
    request_id = str(record.get("id", "unknown_request"))
    text = str(record.get("text", "")).strip()

    if is_unclear_or_unsupported(text):
        return make_decision(
            request_id=request_id,
            text=text or "확인 필요",
            selected_agent="blocked",
            reasoning="요청 의도나 실행 범위가 불명확하여 안전하게 라우팅할 수 없습니다.",
            risk_level="중간",
            approval_required=False,
            blocked=True,
            next_execution_suggestion="사용자에게 목적, 입력 자료, 기대 산출물을 한국어로 다시 확인합니다.",
            confirmation_needed="요청 목적, 대상 자료, 기대 출력, 외부 실행 필요 여부 확인 필요",
        )

    if is_email_send_request(text):
        if not has_explicit_approval(text):
            return block_decision(
                request_id,
                text,
                "이메일 발송 요청이지만 명시적 사용자 승인이 없습니다.",
                "수신자, 발송 내용, 명시적 사용자 승인 확인 필요",
            )
        return make_decision(
            request_id,
            text,
            "harness",
            "승인이 언급된 이메일 발송 요청이므로 실제 실행 전 하네스 승인 게이트 확인이 필요합니다.",
            "높음",
            True,
            False,
            "발송하지 말고 하네스에서 승인 증거와 초안 내용을 검증합니다.",
            "수신자, 발송 본문, 승인 기록 확인 필요",
        )

    if is_slack_or_telegram_notification(text):
        if not has_explicit_approval(text):
            return block_decision(
                request_id,
                text,
                "Slack 또는 Telegram 알림 요청이지만 MVP 단계의 명시적 승인이 없습니다.",
                "대상 채널 또는 수신자, 메시지 내용, 명시적 사용자 승인 확인 필요",
            )
        return make_decision(
            request_id,
            text,
            "harness",
            "승인이 언급된 알림 요청이므로 전송 전 하네스 검증이 필요합니다.",
            "높음",
            True,
            False,
            "알림을 보내지 말고 하네스에서 승인과 메시지 안전성을 검증합니다.",
            "대상, 메시지, 승인 기록 확인 필요",
        )

    if is_sheets_write_request(text):
        if not has_explicit_approval(text):
            return block_decision(
                request_id,
                text,
                "Google Sheets 쓰기/수정 계열 요청이지만 명시적 사용자 승인이 없습니다.",
                "대상 시트, 탭, 행/열, 원본 값, 제안 값, 사후 검증 계획, 명시적 승인 확인 필요",
            )
        return make_decision(
            request_id,
            text,
            "harness",
            "승인이 언급된 Google Sheets 쓰기 요청이므로 실행 전 승인 게이트와 사후 검증 계획 점검이 필요합니다.",
            "높음",
            True,
            False,
            "쓰기 작업을 수행하지 말고 하네스에서 대상 범위와 검증 계획을 확인합니다.",
            "대상 시트, 탭, 행/열, 원본 값, 제안 값, 사후 검증 계획 확인 필요",
        )

    if is_instagram_publish_request(text):
        if not has_explicit_approval(text) or not has_rights_confirmation(text):
            return block_decision(
                request_id,
                text,
                "Instagram 게시 요청이지만 권리 확인 또는 명시적 사용자 승인이 부족합니다.",
                "이미지/영상 권리, 캡션, 게시 계정, 명시적 사용자 승인 확인 필요",
            )
        return make_decision(
            request_id,
            text,
            "harness",
            "승인과 권리 확인이 언급된 Instagram 게시 요청이므로 게시 전 하네스 검증이 필요합니다.",
            "높음",
            True,
            False,
            "게시하지 말고 하네스에서 권리 체크리스트와 승인 기록을 검증합니다.",
            "권리 체크리스트, 게시 계정, 승인 기록 확인 필요",
        )

    if is_external_api_request(text):
        if not has_explicit_approval(text):
            return block_decision(
                request_id,
                text,
                "외부 API 또는 인증 정보 관련 요청이지만 명시적 승인이 없습니다.",
                "API 범위, 인증 정보 처리 방식, 명시적 사용자 승인 확인 필요",
            )
        return make_decision(
            request_id,
            text,
            "harness",
            "승인이 언급된 외부 API 요청이므로 연결 전 하네스와 보안 검토가 필요합니다.",
            "높음",
            True,
            False,
            "외부 API를 연결하지 말고 승인 범위와 보안 정책을 검토합니다.",
            "API 범위, 비밀값 관리, 승인 기록 확인 필요",
        )

    if contains_any(text, ["dashboard", "web", "vercel", "page", "대시보드", "웹", "화면"]):
        return make_decision(
            request_id,
            text,
            "web_dashboard",
            "정적 웹 대시보드 표시 또는 문구 수정 요청으로 판단했습니다.",
            "낮음",
            False,
            False,
            "Web Dashboard 작업으로 라우팅하되 Vercel 설정 변경이나 배포는 별도 승인 없이 수행하지 않습니다.",
            "표시할 문구, 반영할 보고서 항목, 배포 필요 여부 확인 필요",
        )

    if contains_any(text, ["status report", "daily report", "보고서", "상태 보고", "리포트"]):
        return make_decision(
            request_id,
            text,
            "assistant_report",
            "로컬 상태 보고서 생성 요청으로 판단했습니다.",
            "낮음",
            False,
            False,
            "Assistant Report Agent가 로컬 git과 하네스 결과 기반 한국어 보고서를 생성합니다.",
            "보고서 기준 시점과 포함할 에이전트 범위 확인 필요",
        )

    if contains_any(text, ["harness", "test", "validation", "release gate", "하네스", "검증", "점검"]):
        return make_decision(
            request_id,
            text,
            "harness",
            "하네스 점검 또는 릴리스 게이트 검증 요청으로 판단했습니다.",
            "낮음",
            False,
            False,
            "Harness Agent가 로컬 검증 명령을 실행하고 한국어 결과를 보고합니다.",
            "점검 범위와 실패 시 처리 방식 확인 필요",
        )

    if contains_any(text, ["csv", "spreadsheet", "sheet", "스프레드시트", "시트", "데이터", "컬럼", "행"]):
        return make_decision(
            request_id,
            text,
            "sheets_reader",
            "로컬 CSV 또는 표 데이터 읽기 전용 분석 요청으로 판단했습니다.",
            "낮음",
            False,
            False,
            "Sheets Reader Agent가 로컬 샘플 파일만 분석하고 쓰기 작업은 수행하지 않습니다.",
            "컬럼 의미, 누락값, 숫자 형식, 중복 의심값 확인 필요",
        )

    if contains_any(text, ["meeting", "document", "notes", "summary", "회의", "회의록", "문서", "요약", "액션아이템"]):
        return make_decision(
            request_id,
            text,
            "document",
            "문서 요약, 회의록, 액션아이템 정리 요청으로 판단했습니다.",
            "낮음",
            False,
            False,
            "Document Agent가 한국어 구조화 문서 초안을 작성합니다.",
            "담당자, 마감일, 회사명, 숫자가 불명확하면 확인 필요로 표시",
        )

    if contains_any(text, ["email", "gmail", "메일", "이메일", "reply draft", "답장 초안", "partner", "파트너"]):
        return make_decision(
            request_id,
            text,
            "communication",
            "커뮤니케이션 요약 또는 답장 초안 요청으로 판단했습니다.",
            "낮음",
            False,
            False,
            "Communication Agent가 한국어 초안과 확인 필요 항목을 작성합니다.",
            "수신자, 회사명, 마감일, 금액, 약속 내용이 불명확하면 확인 필요로 표시",
        )

    return make_decision(
        request_id=request_id,
        text=text,
        selected_agent="blocked",
        reasoning="현재 MVP 라우팅 규칙으로 지원 범위를 확정할 수 없습니다.",
        risk_level="중간",
        approval_required=False,
        blocked=True,
        next_execution_suggestion="요청을 재정의한 뒤 적절한 에이전트로 다시 라우팅합니다.",
        confirmation_needed="요청 목적, 입력 자료, 기대 출력 확인 필요",
    )


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
        print_section("Supervisor Router 실행 결과", [])
        print_section("실패 항목", [f"입력 파일을 찾을 수 없거나 비어 있습니다: {INPUT_FILE.relative_to(ROOT)}"])
        return 1

    decisions = [route_request(record) for record in records]
    invalid_agents = [decision.selected_agent for decision in decisions if decision.selected_agent not in ALLOWED_AGENTS]
    if invalid_agents:
        print_section("Supervisor Router 실행 결과", [])
        print_section("실패 항목", [f"허용되지 않은 라우팅 대상: {', '.join(invalid_agents)}"])
        return 1

    write_jsonl(OUTPUT_FILE, decisions)

    route_summary = [f"{decision.id}: {decision.selected_agent}" for decision in decisions]
    blocked_count = sum(1 for decision in decisions if decision.blocked)
    approval_count = sum(1 for decision in decisions if decision.approval_required)

    print_section(
        "Supervisor Router 실행 결과",
        [
            f"처리한 요청: {len(decisions)}개",
            f"차단된 요청: {blocked_count}개",
            f"승인 필요 요청: {approval_count}개",
            f"생성된 파일: {OUTPUT_FILE.relative_to(ROOT)}",
        ],
    )
    print_section("라우팅 요약", route_summary)
    print("- 최종 판단")
    print("  - 통과: 외부 실행 없이 로컬 라우팅 결정을 생성했습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
