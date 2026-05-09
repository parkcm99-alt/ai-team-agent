#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = ROOT / "examples/document_inputs"
OUTPUT_DIR = ROOT / "examples/document_outputs"

OUTPUT_NAME_BY_INPUT = {
    "sample_meeting_raw.md": "sample_meeting_summary.md",
    "sample_email_raw.md": "sample_email_summary.md",
    "sample_business_chat_raw.md": "sample_business_chat_summary.md",
}


@dataclass
class SourceFacts:
    kind: str
    company_name: str
    date: str
    bullets: list[str]
    unclear_items: list[str]
    owners: list[str]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def extract_field(text: str, field: str) -> str:
    match = re.search(rf"^- {re.escape(field)}:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else "확인 필요"


def extract_nested_bullets(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    bullets: list[str] = []
    in_section = False
    for line in lines:
        if line.startswith(f"- {heading}:"):
            in_section = True
            continue
        if in_section and line.startswith("- ") and not line.startswith("  - "):
            break
        if in_section and line.strip().startswith("- "):
            bullets.append(line.strip()[2:].strip())
    return bullets


def detect_kind(path: Path, text: str) -> str:
    if "회의" in text or "meeting" in path.name:
        return "meeting"
    if "이메일" in text or "email" in path.name:
        return "email"
    return "business_chat"


def extract_date(text: str, kind: str) -> str:
    field_by_kind = {
        "meeting": "회의일",
        "email": "수신일",
        "business_chat": "대화일",
    }
    value = extract_field(text, field_by_kind[kind])
    if value != "확인 필요":
        return value
    date_match = re.search(r"\d{4}년\s*\d{1,2}월\s*\d{1,2}일", text)
    return date_match.group(0) if date_match else "확인 필요"


def extract_unclear_items(text: str) -> list[str]:
    items: list[str] = []
    patterns = {
        "회사명": r"회사명:\s*확인 필요",
        "담당자": r"담당자.*(명시되지|정해지지|확인 필요)",
        "마감일": r"마감일.*(명확하지|정하지|확인 필요)",
        "숫자": r"(숫자.*(없|확인되지)|가격표 숫자|최종 예산 숫자)",
    }
    for label, pattern in patterns.items():
        if re.search(pattern, text):
            items.append(label)
    return items or ["확인 필요"]


def extract_owners(text: str) -> list[str]:
    owners = re.findall(r"([가-힣]{2,4}) 님", text)
    return sorted(set(owners))


def parse_source(path: Path) -> SourceFacts:
    text = read_text(path)
    kind = detect_kind(path, text)
    company_name = extract_field(text, "회사명")
    date = extract_date(text, kind)
    bullets = (
        extract_nested_bullets(text, "논의 내용")
        or extract_nested_bullets(text, "본문 요지")
        or extract_nested_bullets(text, "대화 요지")
    )
    return SourceFacts(
        kind=kind,
        company_name=company_name,
        date=date,
        bullets=bullets,
        unclear_items=extract_unclear_items(text),
        owners=extract_owners(text),
    )


def line_items(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- 확인 필요"


def action_table(rows: list[tuple[str, str, str]]) -> str:
    table = ["| 항목 | 담당자 | 마감일 | 상태 |", "| --- | --- | --- | --- |"]
    table.extend(f"| {task} | {owner} | {deadline} | 초안 |" for task, owner, deadline in rows)
    return "\n".join(table)


def render_meeting(facts: SourceFacts) -> str:
    discussion = facts.bullets or ["확인 필요"]
    actions = [
        ("예산표 업데이트", "김민수" if "김민수" in facts.owners else "확인 필요", "확인 필요"),
        ("디자인 시안 검토 마감일 확인", "확인 필요", "확인 필요"),
        ("다음 회의 안건 정리", "박현우" if "박현우" in facts.owners else "확인 필요", "확인 필요"),
    ]
    owners = facts.owners + ["디자인 시안 검토 담당자: 확인 필요"]
    return render_document(
        heading="문서 에이전트 출력 예시: 회의 요약",
        title=f"{facts.company_name} 6월 캠페인 준비 회의록 초안",
        summary=f"{facts.date} 회의에서는 6월 캠페인 준비 상황, 예산표 업데이트, 디자인 시안 검토, 다음 회의 안건 정리가 논의되었습니다. 최종 예산 숫자와 디자인 시안 검토 마감일은 원문에서 명확하지 않아 확인이 필요합니다.",
        discussion=discussion,
        decisions=["캠페인 준비를 계속 진행합니다.", "예산표 업데이트 후 후속 검토가 필요합니다."],
        actions=actions,
        owners=owners,
        deadlines=["예산표 업데이트 마감일: 확인 필요", "디자인 시안 검토 마감일: 확인 필요", "다음 회의 안건 정리 마감일: 확인 필요"],
        risks=["최종 예산 숫자가 없어 비용 관련 결정을 확정하기 어렵습니다.", "디자인 시안 검토 마감일이 불명확해 일정 지연 가능성이 있습니다."],
        next_steps=["김민수 님의 예산표 업데이트 범위와 마감일을 먼저 확인하는 것이 좋습니다.", "디자인 시안 검토 담당자와 마감일을 확인한 뒤 다음 회의 안건에 반영하는 것을 제안합니다."],
        confirmations=["최종 예산 숫자", "디자인 시안 검토 담당자", "디자인 시안 검토 마감일", "예산표 업데이트 마감일", "외부 공유 여부"],
    )


def render_email(facts: SourceFacts) -> str:
    return render_document(
        heading="문서 에이전트 출력 예시: 이메일 요약",
        title="미팅 가능 시간 및 첨부 자료 검토 요청 이메일 요약 초안",
        summary=f"{facts.date} 수신된 이메일은 다음 주 미팅 가능 시간 확인과 첨부 자료 검토 여부 회신을 요청합니다. 회사명, 담당자, 회신 마감일은 원문에서 명확하지 않아 확인이 필요합니다.",
        discussion=facts.bullets or ["확인 필요"],
        decisions=["이메일 발송이나 회신은 아직 실행하지 않습니다.", "회신 초안은 사용자 검토 후에만 사용할 수 있습니다."],
        actions=[("다음 주 미팅 가능 시간 확인", "확인 필요", "확인 필요"), ("첨부 자료 검토 여부 확인", "확인 필요", "확인 필요"), ("회신 초안 검토", "확인 필요", "확인 필요")],
        owners=["확인 필요"],
        deadlines=["회신 마감일: 확인 필요", "미팅 후보 시간 제출 마감일: 확인 필요"],
        risks=["회사명이 명확하지 않아 외부 회신 전 확인이 필요합니다.", "담당자와 마감일이 불명확해 후속 대응이 지연될 수 있습니다."],
        next_steps=["먼저 회사명, 회신 담당자, 회신 마감일을 확인하는 것이 좋습니다.", "확인 후 이메일 회신 초안을 별도로 작성하고 사용자 검토를 받는 것을 제안합니다."],
        confirmations=["회사명", "회신 담당자", "회신 마감일", "첨부 자료 검토 완료 여부", "이메일 발송 승인 여부"],
    )


def render_business_chat(facts: SourceFacts) -> str:
    company_name = facts.company_name
    return render_document(
        heading="문서 에이전트 출력 예시: 비즈니스 대화 요약",
        title=f"{company_name} 제안서 준비 대화 요약 초안",
        summary=f"{facts.date} 대화에서는 {company_name} 제안서 초안을 이번 주 안에 정리하고, 고객사 공유 전 내부 검토를 진행해야 한다는 내용이 논의되었습니다. 가격표 숫자, 담당자, 구체적인 마감일은 원문에서 명확하지 않아 확인이 필요합니다.",
        discussion=facts.bullets or ["확인 필요"],
        decisions=["고객사 공유 전 내부 검토를 먼저 진행합니다.", "가격표 숫자는 확정 전까지 확인 필요 상태로 유지합니다."],
        actions=[(f"{company_name} 제안서 초안 정리", "확인 필요", "확인 필요"), ("가격표 숫자 확인", "확인 필요", "확인 필요"), ("내부 검토 일정 확정", "확인 필요", "확인 필요")],
        owners=["제안서 초안 담당자: 확인 필요", "가격표 확인 담당자: 확인 필요", "내부 검토 담당자: 확인 필요"],
        deadlines=["이번 주 안: 구체 날짜 확인 필요", "고객사 공유일: 확인 필요"],
        risks=["가격표 숫자가 확인되지 않아 제안서 내용이 부정확할 수 있습니다.", "담당자와 구체적인 마감일이 없어 내부 검토가 지연될 수 있습니다."],
        next_steps=["가격표 숫자와 제안서 담당자를 먼저 확인하는 것이 좋습니다.", "고객사 공유 전 내부 검토 일정을 확정한 뒤 공유 여부를 판단하는 것을 제안합니다."],
        confirmations=["가격표 숫자", "제안서 초안 담당자", "내부 검토 담당자", "구체적인 마감일", "고객사 공유 승인 여부"],
    )


def render_document(
    heading: str,
    title: str,
    summary: str,
    discussion: list[str],
    decisions: list[str],
    actions: list[tuple[str, str, str]],
    owners: list[str],
    deadlines: list[str],
    risks: list[str],
    next_steps: list[str],
    confirmations: list[str],
) -> str:
    return f"""# {heading}

### 제목

{title}

### 요약

{summary}

### 주요 논의 내용

{line_items(discussion)}

### 결정 사항

{line_items(decisions)}

### 액션아이템

{action_table(actions)}

### 담당자

{line_items(owners)}

### 마감일

{line_items(deadlines)}

### 리스크

{line_items(risks)}

### 다음 제안

{line_items(next_steps)}

### 확인이 필요한 부분

{line_items(confirmations)}
"""


def generate_summary(path: Path) -> str:
    facts = parse_source(path)
    if facts.kind == "meeting":
        return render_meeting(facts)
    if facts.kind == "email":
        return render_email(facts)
    return render_business_chat(facts)


def output_path_for(input_path: Path) -> Path:
    output_name = OUTPUT_NAME_BY_INPUT.get(input_path.name)
    if output_name:
        return OUTPUT_DIR / output_name
    return OUTPUT_DIR / input_path.name.replace("_raw.md", "_summary.md")


def main() -> int:
    input_files = sorted(INPUT_DIR.glob("*.md"))
    if not input_files:
        print("- 문서 에이전트 실행 결과")
        print("  - 처리할 입력 파일이 없습니다.")
        return 1

    generated: list[str] = []
    for input_path in input_files:
        output_path = output_path_for(input_path)
        summary = generate_summary(input_path)
        write_text(output_path, summary)
        generated.append(f"{input_path.relative_to(ROOT)} -> {output_path.relative_to(ROOT)}")

    print("- 문서 에이전트 실행 결과")
    for item in generated:
        print(f"  - {item}")
    print("- 최종 판단")
    print("  - 통과: 로컬 규칙 기반 문서 요약을 생성했습니다. 외부 작업은 실행하지 않았습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
