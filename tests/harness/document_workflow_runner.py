#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from document_validation_runner import (
    ROOT,
    ValidationResult,
    has_missing_action_items,
    has_missing_decisions,
    has_overconfident_recommendation,
    has_unsupported_assumptions,
    has_wrong_company_name_risk,
    has_wrong_date_risk,
    is_korean_user_facing,
    missing_confirmation_needed,
    print_section,
    read_text,
    required_sections_present,
)


OUTPUT_DIR = ROOT / "examples/document_outputs"


def validate_output(path: Path) -> ValidationResult:
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
        ("액션아이템 누락 없음", not has_missing_action_items(document), "액션아이템이 누락되었거나 `없음`으로 표시되었습니다."),
        ("결정 사항 누락 없음", not has_missing_decisions(document), "결정 사항이 누락되었거나 불명확합니다."),
        ("회사명 오류 위험 없음", not has_wrong_company_name_risk(document, document), "회사명이 원문과 다르거나 오류 위험이 있습니다."),
        ("날짜 오류 위험 없음", not has_wrong_date_risk(document, document), "날짜가 원문과 다르거나 누락되었습니다."),
        ("근거 없는 가정 없음", not has_unsupported_assumptions(document), "근거 없는 확정 표현이 있습니다."),
        ("사용자 출력 한국어", is_korean_user_facing(document), "사용자에게 보이는 출력이 한국어 기준을 충족하지 않습니다."),
        ("과신 추천 없음", not has_overconfident_recommendation(document), "다음 제안에 과신 표현이 있습니다."),
        ("불명확 정보 확인 필요 표시", not missing_confirmation_needed(document, document), "불명확한 담당자, 마감일, 회사명 또는 숫자에 `확인 필요` 표시가 부족합니다."),
    ]

    for label, ok, message in checks:
        if ok:
            passed.append(label)
        else:
            failed.append(message)

    if any(term in document for term in ["발송했습니다", "전송했습니다", "게시했습니다", "시트에 썼습니다"]):
        failed.append("외부 작업을 실행한 것으로 보이는 문구가 있습니다.")

    if "확인 필요" not in document:
        warnings.append("불명확 정보가 없는 출력인지 확인이 필요합니다.")

    return ValidationResult(path.relative_to(ROOT).as_posix(), passed, failed, warnings)


def main() -> int:
    markdown_files = sorted(OUTPUT_DIR.glob("*.md"))
    passed: list[str] = []
    failed: list[str] = []
    warnings: list[str] = []
    report: list[str] = []

    if not markdown_files:
        print_section("문서 워크플로 검증 결과", [])
        print_section("통과 항목", [])
        print_section("실패 항목", ["검증할 문서 출력 파일이 없습니다."])
        print_section("경고 항목", [])
        print("- 최종 판단")
        print("  - 실패: 문서 출력 예시가 없어 검증할 수 없습니다.")
        return 1

    for path in markdown_files:
        result = validate_output(path)
        report.append(f"{result.name}: 통과 {len(result.passed)}개, 실패 {len(result.failed)}개, 경고 {len(result.warnings)}개")
        passed.extend(f"{result.name}: {item}" for item in result.passed)
        failed.extend(f"{result.name}: {item}" for item in result.failed)
        warnings.extend(f"{result.name}: {item}" for item in result.warnings)

    print_section("문서 워크플로 검증 결과", report)
    print_section("통과 항목", passed)
    print_section("실패 항목", failed)
    print_section("경고 항목", warnings)
    print("- 최종 판단")

    if failed:
        print("  - 실패: 하나 이상의 문서 출력 예시가 검증을 통과하지 못했습니다.")
        return 1

    print("  - 통과: 모든 문서 출력 예시가 필수 형식과 안전 기준을 통과했습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
