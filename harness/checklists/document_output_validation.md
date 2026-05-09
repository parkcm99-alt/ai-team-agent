# 문서 출력 검증 체크리스트

`checklist_id`: `document_output_validation`

문서 출력물이 사용자에게 전달되기 전에 한국어 품질, 근거, 형식, 안전성을 확인합니다.

## 게이트 기준

- `blocked`: 사용자에게 보이는 본문이 한국어가 아니거나, 근거 없는 확정 표현이 있거나, 민감정보가 노출된 경우
- `draft_only`: 구조는 맞지만 근거, 범위, 출처, 검토 표시가 부족한 경우
- `ready_for_approval`: 한국어 출력, 범위 명확성, 근거 표시, 민감정보 검토가 모두 충족된 경우

## 검사 항목

- [ ] `language.user_facing_korean`: 사용자에게 보이는 제목, 요약, 설명, 결론이 한국어인지 확인합니다.
- [ ] `structure.required_sections_present`: 요청한 문서 섹션이 모두 포함되어 있는지 확인합니다.
- [ ] `scope.no_unrequested_claims`: 요청하지 않은 확정 주장이나 추측이 포함되지 않았는지 확인합니다.
- [ ] `evidence.source_limits_respected`: 출처가 필요한 내용은 근거가 표시되어 있고, 과도한 인용이 없는지 확인합니다.
- [ ] `privacy.no_sensitive_data_leak`: 개인정보, 토큰, 계정 정보, 내부 식별자가 노출되지 않았는지 확인합니다.
- [ ] `tone.user_appropriate`: 문체가 사용자 상황에 맞고 과장되거나 단정적이지 않은지 확인합니다.
- [ ] `action.next_steps_clear`: 다음 확인 사항이나 승인 요청이 명확히 표시되어 있는지 확인합니다.
