# Google Sheets 쓰기 검증 체크리스트

`checklist_id`: `google_sheets_write_validation`

Google Sheets 쓰기 작업은 데이터 변경이므로 기본적으로 승인 게이트를 통과해야 합니다. 자동 실행은 금지되며, 명시적인 사용자 승인 전에는 쓰기, 삭제, 덮어쓰기, 정렬, 구조 변경을 수행하면 안 됩니다.

## 게이트 기준

- `blocked`: 사용자 승인 없이 쓰기, 삭제, 덮어쓰기, 시트 구조 변경을 시도한 경우
- `draft_only`: 쓰기 계획은 있으나 대상 스프레드시트, 대상 탭, 대상 행/열, 원본 값, 제안 값, 변경 미리보기가 불명확한 경우
- `ready_for_approval`: 대상 스프레드시트, 대상 탭, 대상 행/열, 원본 값, 제안 값, 롤백 계획, 사용자 승인 요청이 모두 명확한 경우

## 검사 항목

- [ ] `action.no_write_without_approval`: 사용자 승인 없이 셀 쓰기, 행 추가, 삭제, 정렬, 덮어쓰기를 시도하지 않았는지 확인합니다.
- [ ] `target.spreadsheet_identified`: 대상 스프레드시트가 명확히 식별되었는지 확인합니다.
- [ ] `target.tab_identified`: 대상 탭이 명확히 식별되었는지 확인합니다.
- [ ] `target.row_column_identified`: 대상 행과 열이 명확한지 확인합니다.
- [ ] `preview.source_value_present`: 원본 값이 한국어 설명과 함께 표시되었는지 확인합니다.
- [ ] `preview.proposed_value_present`: 제안 값이 한국어 설명과 함께 표시되었는지 확인합니다.
- [ ] `preview.change_preview_present`: 대상 스프레드시트, 대상 탭, 대상 행/열, 원본 값, 제안 값의 미리보기가 한국어로 제공되었는지 확인합니다.
- [ ] `safety.no_destructive_change`: 삭제, 덮어쓰기, 대량 변경 같은 위험 작업이 별도로 표시되었는지 확인합니다.
- [ ] `rollback.rollback_plan_present`: 되돌리기 방법 또는 변경 전 백업 필요성이 설명되었는지 확인합니다.
- [ ] `approval.explicit_approval_required`: 쓰기 실행 전 사용자 승인이 필요하다는 문구가 있는지 확인합니다.
- [ ] `verification.written_value_verified`: 쓰기 후 기록된 값을 다시 확인하고 검증 결과를 한국어로 보고하는 절차가 있는지 확인합니다.
