#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = ROOT / "examples/workflow_inputs"
OUTPUT_DIR = ROOT / "examples/workflow_outputs"
UNCLEAR_MARKER = "확인 필요"


@dataclass
class CampaignIdea:
    title: str
    item_summary: str
    goal: str
    owner: str
    deadline: str
    target_channel: str
    media_file: str
    caption_direction: str
    music_title: str
    track_id: str
    rights_owner: str
    commercial_use_permission: str
    sample_cover_remix_status: str
    posting_account: str
    raw_notes: list[str]


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


def extract_notes(text: str) -> list[str]:
    marker = "## Raw Notes"
    marker_index = text.find(marker)
    if marker_index == -1:
        return []
    content = text[marker_index + len(marker) :].strip()
    return [line.strip("- ").strip() for line in content.splitlines() if line.strip()]


def parse_idea(path: Path) -> CampaignIdea:
    text = read_text(path)
    return CampaignIdea(
        title=extract_field(text, "Title"),
        item_summary=extract_field(text, "Item summary"),
        goal=extract_field(text, "Goal"),
        owner=extract_field(text, "Owner"),
        deadline=extract_field(text, "Deadline"),
        target_channel=extract_field(text, "Target channel"),
        media_file=extract_field(text, "Media file"),
        caption_direction=extract_field(text, "Caption direction"),
        music_title=extract_field(text, "Music title"),
        track_id=extract_field(text, "track_id"),
        rights_owner=extract_field(text, "Rights owner"),
        commercial_use_permission=extract_field(text, "Commercial-use permission"),
        sample_cover_remix_status=extract_field(text, "Sample cover remix status"),
        posting_account=extract_field(text, "Posting account"),
        raw_notes=extract_notes(text),
    )


def bullet_lines(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else f"- {UNCLEAR_MARKER}"


def confirmation_needed(idea: CampaignIdea) -> list[str]:
    checks = [
        ("track_id", idea.track_id),
        ("권리 보유자", idea.rights_owner),
        ("상업적 사용 가능 여부", idea.commercial_use_permission),
        ("샘플/커버/리믹스 여부", idea.sample_cover_remix_status),
        ("캡션 승인", UNCLEAR_MARKER),
        ("미디어 파일", idea.media_file),
        ("마감일", idea.deadline),
        ("게시 계정", idea.posting_account),
    ]
    return [f"{label}: {UNCLEAR_MARKER}" for label, value in checks if value == UNCLEAR_MARKER]


def workflow_risks(idea: CampaignIdea) -> list[str]:
    risks = [
        "Instagram 게시와 미디어 업로드는 수행하지 않았습니다.",
        "Instagram API와 Meta Graph API는 연결하지 않았습니다.",
        "외부 실행 전 사용자 승인과 권리 확인이 필요합니다.",
    ]
    if confirmation_needed(idea):
        risks.append("필수 확인 항목이 남아 있어 실행 단계로 넘길 수 없습니다.")
    return risks


def render_workflow_plan(idea: CampaignIdea) -> str:
    return f"""# Workflow Plan

### 제목

{idea.title}

### 아이템 요약

{idea.item_summary}

### 목표

{idea.goal}

### 실행 단계

- 아이디어와 목표를 확인합니다.
- 필요한 제작물과 캡션 방향을 정리합니다.
- 음악 권리, 미디어 파일, 게시 계정, 마감일을 확인합니다.
- 하네스 검증을 통과한 뒤 승인 요청 상태로 둡니다.
- 승인 전까지 Instagram 게시와 미디어 업로드는 수행하지 않습니다.

### 테스트 계획

- 워크플로 계획 필수 섹션을 검증합니다.
- Instagram 승인 요청서 필수 섹션을 검증합니다.
- 음악 권리 체크리스트에서 track_id와 상업적 사용 가능 여부를 확인합니다.
- 외부 게시, API 연결, 미디어 업로드가 수행되지 않았는지 확인합니다.

### 결과 측정 기준

- 필수 섹션 누락 0개
- 승인 게이트 누락 0개
- 실제 게시 또는 외부 API 연결 0건
- 확인 필요 항목이 명확히 표시됨

### 담당자

{idea.owner}

### 마감일

{idea.deadline}

### 리스크

{bullet_lines(workflow_risks(idea))}

### 다음 액션

- track_id와 권리 보유자를 확인합니다.
- 상업적 사용 가능 여부와 샘플/커버/리믹스 여부를 확인합니다.
- 캡션, 미디어 파일, 게시 계정, 마감일을 사용자에게 확인받습니다.
- 승인 전에는 게시하지 않습니다.

### 승인 필요 여부

필요

### 외부 실행 여부

수행하지 않음

- Instagram API 연결 여부: 연결하지 않음
- Meta Graph API 연결 여부: 연결하지 않음
- 실제 Instagram 게시 여부: 게시하지 않음
- 미디어 업로드 여부: 업로드하지 않음
"""


def render_instagram_approval(idea: CampaignIdea) -> str:
    confirmations = confirmation_needed(idea)
    return f"""# Instagram Post Approval

### 게시물 제목

{idea.title}

### 게시 목적

{idea.goal}

### 캡션 초안

{idea.caption_direction}

승인 전 초안입니다. 캡션 승인 상태는 {UNCLEAR_MARKER}입니다.

### 해시태그 초안

- #AITeamAgent
- #Workflow
- #MVP

### 사용할 제작물

{idea.media_file}

### 사용할 음악

{idea.music_title}

### 음악 권리 확인 여부

{UNCLEAR_MARKER}

### track_id

{idea.track_id}

### 상업적 사용 가능 여부

{idea.commercial_use_permission}

### 샘플/커버/리믹스 여부

{idea.sample_cover_remix_status}

### 게시 승인 필요 여부

필요

### 실제 게시 여부

게시하지 않음

- 실제 Instagram 게시 여부: 게시하지 않음
- Instagram API 연결 여부: 연결하지 않음
- Meta Graph API 연결 여부: 연결하지 않음
- 미디어 업로드 여부: 업로드하지 않음

### 확인이 필요한 부분

{bullet_lines(confirmations)}

### 위험 요소

- 음악 권리 확인 전 게시하면 저작권 또는 사용권 리스크가 있습니다.
- track_id, 권리 보유자, 상업적 사용 가능 여부 확인 전 게시할 수 없습니다.
- Instagram API와 Meta Graph API는 연결하지 않았습니다.
- 실제 Instagram 게시와 미디어 업로드는 수행하지 않았습니다.
"""


def render_music_rights_checklist(idea: CampaignIdea) -> str:
    return f"""# Music Rights Checklist

### 제목

Instagram 게시 전 음악 권리 체크리스트

### 사용할 음악

{idea.music_title}

### track_id

{idea.track_id}

### 권리 보유자

{idea.rights_owner}

### 상업적 사용 가능 여부

{idea.commercial_use_permission}

### 샘플/커버/리믹스 여부

{idea.sample_cover_remix_status}

### 음악 권리 확인 여부

{UNCLEAR_MARKER}

### 확인이 필요한 부분

{bullet_lines(confirmation_needed(idea))}

### 게시 가능 판단

게시 불가: 음악 권리 확인과 사용자 승인이 필요합니다.

### 외부 실행 여부

수행하지 않음

- 실제 Instagram 게시 여부: 게시하지 않음
- Instagram API 연결 여부: 연결하지 않음
- Meta Graph API 연결 여부: 연결하지 않음
- 미디어 업로드 여부: 업로드하지 않음
"""


def generate_outputs() -> list[Path]:
    input_files = sorted(INPUT_DIR.glob("*.md"))
    if not input_files:
        return []
    idea = parse_idea(input_files[0])
    outputs = {
        OUTPUT_DIR / "sample_workflow_plan.md": render_workflow_plan(idea),
        OUTPUT_DIR / "sample_instagram_post_approval.md": render_instagram_approval(idea),
        OUTPUT_DIR / "sample_music_rights_checklist.md": render_music_rights_checklist(idea),
    }
    for path, content in outputs.items():
        write_text(path, content)
    return list(outputs.keys())


def main() -> int:
    generated = generate_outputs()
    print("- Workflow Instagram 실행 결과")
    if not generated:
        print("  - 처리할 입력 파일이 없습니다.")
        print("- 최종 판단")
        print("  - 실패: 로컬 워크플로 입력이 필요합니다.")
        return 1
    for path in generated:
        print(f"  - 생성됨: {path.relative_to(ROOT)}")
    print("- 외부 실행 여부")
    print("  - 실제 Instagram 게시 여부: 게시하지 않음")
    print("  - Instagram API 연결 여부: 연결하지 않음")
    print("  - Meta Graph API 연결 여부: 연결하지 않음")
    print("  - 미디어 업로드 여부: 업로드하지 않음")
    print("- 최종 판단")
    print("  - 통과: 로컬 워크플로 계획과 Instagram 승인 준비 문서를 생성했습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
