# Slack 및 Telegram 알림 검증 체크리스트

`checklist_id`: `slack_telegram_notification_validation`

Slack과 Telegram 알림은 사용자에게 보이는 메시지이자 외부 전송 작업이므로, 작성과 전송을 분리해야 합니다. MVP 단계에서는 어떤 외부 알림도 자동 전송하지 않으며, Telegram 알림은 알림 정책이 완전히 정의될 때까지 명시적인 사용자 승인 이후에만 사용할 수 있습니다.

## 게이트 기준

- `blocked`: 사용자 승인 없이 메시지 전송, 예약, 채널 게시, 봇 알림을 시도한 경우
- `draft_only`: 알림 초안은 있으나 대상 채널, 수신자, 긴급도, 전송 시간이 불명확한 경우
- `ready_for_approval`: 한국어 알림 초안, 대상, 전송 목적, 긴급도, 승인 요청이 모두 명확한 경우

## 검사 항목

- [ ] `language.user_facing_korean`: 알림 본문과 사용자 설명이 한국어인지 확인합니다.
- [ ] `action.no_notify_without_approval`: 사용자 승인 없이 Slack 또는 Telegram 메시지를 전송하지 않았는지 확인합니다.
- [ ] `telegram.policy_defined_before_send`: Telegram 알림 정책이 완전히 정의되기 전에는 전송하지 않는지 확인합니다.
- [ ] `telegram.allowed_after_approval_only`: Telegram은 사용자 승인 후 초안 알림, 승인 요청, 개인 보고 용도로만 사용하는지 확인합니다.
- [ ] `target.destination_confirmed`: 채널, DM, 그룹, 채팅방 등 전송 대상이 명확한지 확인합니다.
- [ ] `urgency.urgency_labeled`: 긴급도와 전송 이유가 명확히 표시되어 있는지 확인합니다.
- [ ] `timing.send_time_clear`: 즉시 전송인지 예약 전송인지 명확한지 확인합니다.
- [ ] `privacy.no_sensitive_data_leak`: 토큰, 내부 링크, 개인정보, 비공개 대화 내용이 불필요하게 포함되지 않았는지 확인합니다.
- [ ] `approval.explicit_approval_required`: 전송 전 사용자 승인이 필요하다는 문구가 있는지 확인합니다.
