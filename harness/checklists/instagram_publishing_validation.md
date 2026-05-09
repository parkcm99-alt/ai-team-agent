# Instagram 게시 검증 체크리스트

`checklist_id`: `instagram_publishing_validation`

Instagram 콘텐츠는 초안 작성, 자산 검토, 승인, 게시 실행 단계를 분리해야 합니다.

## 게이트 기준

- `blocked`: 사용자 승인 없이 게시, 예약 게시, 계정 연결, API 호출을 시도한 경우
- `draft_only`: 캡션이나 해시태그 초안은 있으나 자산, 계정, 게시 시간, 승인 여부가 불명확한 경우
- `ready_for_approval`: 한국어 캡션, 해시태그, 자산 목록, 게시 계정, 일정, 승인 요청이 모두 명확한 경우

## 검사 항목

- [ ] `language.user_facing_korean`: 캡션, 설명, 승인 요청 문구가 한국어인지 확인합니다.
- [ ] `action.no_publish_without_approval`: 사용자 승인 없이 게시하거나 예약 게시하지 않았는지 확인합니다.
- [ ] `asset.assets_identified`: 이미지 또는 영상 자산이 명확히 식별되었는지 확인합니다.
- [ ] `account.account_confirmed`: 게시 대상 계정이 명확한지 확인합니다.
- [ ] `caption.caption_present`: 캡션 초안이 목적과 톤에 맞는지 확인합니다.
- [ ] `hashtag.hashtags_reviewed`: 해시태그가 과도하거나 부적절하지 않은지 확인합니다.
- [ ] `timing.publish_time_clear`: 게시 희망 시간이 명확한지 확인합니다.
- [ ] `approval.explicit_approval_required`: 게시 전 사용자 승인이 필요하다는 문구가 있는지 확인합니다.
