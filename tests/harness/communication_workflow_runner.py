#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from communication_validation_runner import (
    ROOT,
    has_missing_approval_requirement,
    has_missing_next_action,
    has_overly_casual_tone,
    has_unsafe_email_sending,
    has_unsupported_promise,
    has_wrong_company_name_risk,
    has_wrong_recipient_risk,
    is_korean_user_facing,
    is_sending_instead_of_drafting,
    missing_confirmation_needed,
    print_section,
    read_text,
    required_sections_present,
)


OUTPUT_DIR = ROOT / "examples/communication_outputs"


def validate_output(path: Path) -> tuple[list[str], list[str], list[str]]:
    document = read_text(path)
    passed: list[str] = []
    failed: list[str] = []
    warnings: list[str] = []

    _, missing_sections = required_sections_present(document)
    if missing_sections:
        failed.append(f"필수 섹션 누락: {', '.join(missing_sections)}")
    else:
        passed.append("필수 한국어 섹션이 모두 있습니다.")

    checks = [
        ("승인 없는 이메일 발송 없음", not has_unsafe_email_sending(document), "승인 없이 이메일을 발송한 것으로 보입니다."),
        ("승인 필요 여부 명시", not has_missing_approval_requirement(document), "승인 필요 여부가 누락되었거나 필요 없음으로 표시되었습니다."),
        ("수신자 오류 위험 없음", not has_wrong_recipient_risk(document, document), "수신자가 불명확한데 확인 필요로 표시되지 않았습니다."),
        ("회사명 오류 위험 없음", not has_wrong_company_name_risk(document, document), "회사명이 원문과 다르거나 오류 위험이 있습니다."),
        ("근거 없는 약속 없음", not has_unsupported_promise(document), "원문에 없는 약속 또는 과도한 약속이 포함되었습니다."),
        ("정중한 톤 유지", not has_overly_casual_tone(document), "답장 초안의 톤이 지나치게 가볍습니다."),
        ("다음 액션 있음", not has_missing_next_action(document), "필요한 다음 액션이 누락되었습니다."),
        ("사용자 출력 한국어", is_korean_user_facing(document), "사용자에게 보이는 출력이 한국어 기준을 충족하지 않습니다."),
        ("발송 대신 초안 유지", not is_sending_instead_of_drafting(document), "초안이 아니라 발송 완료처럼 작성되었습니다."),
        ("불명확 정보 확인 필요 표시", not missing_confirmation_needed(document, document), "불명확한 수신자, 회사명, 마감일, 금액, 약속 또는 법적/권리 이슈에 `확인 필요` 표시가 부족합니다."),
    ]

    for label, ok, message in checks:
        if ok:
            passed.append(label)
        else:
            failed.append(message)

    if "Slack" in document and "실행하지 않았" not in document:
        warnings.append("Slack 언급이 있어 알림 미전송 문구 확인이 필요합니다.")
    if "Telegram" in document and "실행하지 않았" not in document:
        warnings.append("Telegram 언급이 있어 알림 미전송 문구 확인이 필요합니다.")
    if "Google Sheets" in document and "실행하지 않았" not in document:
        warnings.append("Google Sheets 언급이 있어 쓰기 미실행 문구 확인이 필요합니다.")

    return passed, failed, warnings


def main() -> int:
    passed: list[str] = []
    failed: list[str] = []
    warnings: list[str] = []
    report: list[str] = []

    if not OUTPUT_DIR.exists():
        print_section("커뮤니케이션 워크플로 검증 결과", [])
        print_section("통과 항목", [])
        print_section("실패 항목", [f"출력 디렉터리가 없습니다: {OUTPUT_DIR.relative_to(ROOT).as_posix()}"])
        print_section("경고 항목", [])
        print("- 최종 판단")
        print("  - 실패: 커뮤니케이션 출력 예시를 찾을 수 없습니다.")
        return 1

    markdown_files = sorted(OUTPUT_DIR.glob("*.md"))
    if not markdown_files:
        print_section("커뮤니케이션 워크플로 검증 결과", [])
        print_section("통과 항목", [])
        print_section("실패 항목", [f"검증할 Markdown 파일이 없습니다: {OUTPUT_DIR.relative_to(ROOT).as_posix()}"])
        print_section("경고 항목", [])
        print("- 최종 판단")
        print("  - 실패: 커뮤니케이션 출력 예시가 비어 있습니다.")
        return 1

    for path in markdown_files:
        name = path.relative_to(ROOT).as_posix()
        file_passed, file_failed, file_warnings = validate_output(path)
        report.append(f"{name}: 통과 {len(file_passed)}개, 실패 {len(file_failed)}개, 경고 {len(file_warnings)}개")
        passed.extend(f"{name}: {item}" for item in file_passed)
        failed.extend(f"{name}: {item}" for item in file_failed)
        warnings.extend(f"{name}: {item}" for item in file_warnings)

    print_section("커뮤니케이션 워크플로 검증 결과", report)
    print_section("통과 항목", passed)
    print_section("실패 항목", failed)
    print_section("경고 항목", warnings)
    print("- 최종 판단")

    if failed:
        print("  - 실패: 하나 이상의 커뮤니케이션 출력 예시가 검증을 통과하지 못했습니다.")
        return 1

    print("  - 통과: 모든 커뮤니케이션 출력 예시가 검증 기준을 통과했습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
