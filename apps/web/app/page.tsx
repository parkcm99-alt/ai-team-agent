type ReportData = {
  title: string;
  overallStatus: string[];
  completedWork: string[];
  agentStatus: Array<{
    name: string;
    status: string;
  }>;
  harnessResults: string[];
  recentCommits: string[];
  remainingRisks: string[];
  nextRecommendations: string[];
  approvalRequired: string[];
  externalActions: Array<{
    label: string;
    value: string;
  }>;
  supervisorRouting: {
    totalRequests: string;
    blockedRequests: string;
    approvalRequiredRequests: string;
    routeTargets: string;
    riskBlockSummary: string[];
    externalExecution: string;
  };
  notificationDraft: {
    slackDraft: string;
    telegramDraft: string;
    approvalRequired: string;
    sendStatus: string;
    externalApi: string;
    confirmations: string[];
    risks: string[];
  };
  emailDraft: {
    summaryGenerated: string;
    replyDraftGenerated: string;
    approvalRequestGenerated: string;
    sendStatus: string;
    approvalRequired: string;
    gmailApiStatus: string;
    recipient: string;
    companyName: string;
    majorRequests: string[];
    nextActions: string[];
    confirmations: string[];
    risks: string[];
  };
  sheetsWriteApproval: {
    approvalRequired: string;
    actualWriteStatus: string;
    apiConnectionStatus: string;
    targetSpreadsheet: string;
    targetTab: string;
    targetRow: string;
    targetColumn: string;
    originalValue: string;
    proposedValue: string;
    changeReason: string;
    risks: string[];
    confirmations: string[];
    verificationPlan: string;
    finalStatus: string[];
  };
};

// TODO: Automate syncing from reports/daily_status_report.md.
// TODO: Automate syncing Supervisor and Notification results from local reports.
// TODO: Automate syncing Sheets Write Approval status from local approval reports.
// TODO: Automate syncing Email Draft status from local email outputs.
const assistantReport: ReportData = {
  title: "AI 팀 에이전트 일일 상태 보고서",
  overallStatus: [
    "보고서 생성 시점 기준 저장소 상태: 로컬 변경 사항이 감지되었습니다.",
    "최신 Git 상태는 Vercel/GitHub 배포 기준으로 확인 필요",
    "하네스 상태: 전체 하네스 점검이 통과했습니다.",
    "보고서 생성 단계: final",
  ],
  completedWork: [
    "Document Agent MVP와 검증 러너가 준비되어 있습니다.",
    "Communication Agent MVP, 워크플로 테스트, 로컬 러너가 준비되어 있습니다.",
    "Email Draft Workflow MVP가 로컬 이메일 요약, 답장 초안, 승인 요청서를 생성합니다.",
    "Sheets Reader MVP가 로컬 CSV 읽기 전용으로 준비되어 있습니다.",
    "Sheets Write Approval Flow MVP가 실제 쓰기 없이 승인 요청서를 생성합니다.",
    "Assistant Report Agent MVP가 로컬 상태 보고서를 생성합니다.",
    "Supervisor Agent MVP 라우팅 결과가 보고서와 대시보드에 반영됩니다.",
    "Notification Draft Agent MVP가 Slack/Telegram 초안 상태를 표시합니다.",
  ],
  agentStatus: [
    {
      name: "Assistant Agent",
      status: "로컬 상태 보고서 생성 MVP 준비",
    },
    {
      name: "Document Agent",
      status: "로컬 문서 요약 및 문서 검증 통과",
    },
    {
      name: "Communication Agent",
      status: "로컬 커뮤니케이션 요약, 워크플로, 검증 통과",
    },
    {
      name: "Email Draft Agent",
      status: "로컬 이메일 요약, 답장 초안, 승인 요청서 생성 및 검증 통과",
    },
    {
      name: "Sheets Reader Agent",
      status: "로컬 CSV 읽기 전용 리포트 생성 및 검증 통과",
    },
    {
      name: "Sheets Write Approval Agent",
      status: "로컬 승인 요청서 생성, 실제 쓰기 미수행, API 미연결",
    },
    {
      name: "Harness Agent",
      status:
        "정책, 리플레이, 문서, 커뮤니케이션, Email Draft, Sheets Reader, Sheets Write Approval 검증 실행",
    },
    {
      name: "Supervisor Agent",
      status: "로컬 규칙 기반 라우팅과 위험 작업 차단 검증 통과",
    },
    {
      name: "Notification Draft Agent",
      status: "Slack/Telegram 초안 생성, 발송 미수행, 승인 필요 상태",
    },
    {
      name: "Workflow/Instagram Agent",
      status: "구조와 정책 중심의 초기 상태",
    },
  ],
  harnessResults: [
    "`python3 tests/harness/run_all.py`: 통과",
    "전체 하네스 점검이 통과했습니다.",
  ],
  recentCommits: [
    "424825f feat: add email draft workflow MVP",
    "47b373e feat: show sheets write approval status on dashboard",
    "aee9504 feat: add sheets write approval flow MVP",
    "b2a548a feat: show supervisor and notification status on dashboard",
    "3809520 feat: add notification draft agent MVP",
  ],
  remainingRisks: [
    "현재 보고서는 로컬 명령 결과 기반이며 외부 서비스 상태는 확인하지 않습니다.",
    "실제 Google Sheets, 이메일, Slack, Telegram, Instagram 연동은 아직 연결하지 않았습니다.",
    "외부 실행이 필요한 작업은 별도 승인 게이트와 사후 검증 정책이 필요합니다.",
  ],
  nextRecommendations: [
    "Assistant Report Agent 보고서를 정기 실행하기 전에 승인 정책과 배포 전 검증 흐름을 확정합니다.",
    "다음 MVP는 Supervisor Agent가 각 에이전트의 로컬 결과를 통합하는 방식으로 확장하는 것을 제안합니다.",
  ],
  approvalRequired: [
    "이메일 발송이 필요한 경우 명시적 사용자 승인이 필요합니다.",
    "Email Draft 결과에서 수신자, 회사명, 마감일, 가격, 수량, 약속, 법적/권리 이슈가 불명확하면 확인 필요로 표시해야 합니다.",
    "Slack 또는 Telegram 알림이 필요한 경우 명시적 사용자 승인이 필요합니다.",
    "Google Sheets 쓰기가 필요한 경우 대상 시트, 탭, 행/열, 원본 값, 제안 값을 제시한 뒤 명시적 사용자 승인이 필요합니다.",
    "Google Sheets 쓰기 실행 전 사후 검증 계획을 제시해야 합니다.",
    "Instagram 게시가 필요한 경우 권리 체크리스트와 명시적 사용자 승인이 필요합니다.",
  ],
  externalActions: [
    {
      label: "이메일 발송",
      value: "수행하지 않음",
    },
    {
      label: "Slack/Telegram 알림",
      value: "수행하지 않음",
    },
    {
      label: "Google Sheets 쓰기 작업",
      value: "수행하지 않음",
    },
    {
      label: "Instagram 게시",
      value: "수행하지 않음",
    },
    {
      label: "외부 API 호출",
      value: "수행하지 않음",
    },
  ],
  supervisorRouting: {
    totalRequests: "13",
    blockedRequests: "7",
    approvalRequiredRequests: "6",
    routeTargets:
      "assistant_report 1건, blocked 7건, communication 1건, document 1건, harness 1건, sheets_reader 1건, web_dashboard 1건",
    riskBlockSummary: [
      "승인 없는 이메일 발송 요청을 차단했습니다.",
      "승인 없는 Slack/Telegram 알림 요청을 차단했습니다.",
      "승인 없는 Google Sheets 쓰기와 Instagram 게시 요청을 차단했습니다.",
      "명시적 승인 없는 외부 API 연결 요청을 차단했습니다.",
    ],
    externalExecution: "수행하지 않음",
  },
  notificationDraft: {
    slackDraft: "Slack 상태 보고 초안 생성 완료",
    telegramDraft: "Telegram 긴급 알림 승인 요청 초안 생성 완료",
    approvalRequired: "필요",
    sendStatus: "발송하지 않음",
    externalApi: "연결하지 않음",
    confirmations: [
      "수신 채널 또는 수신자: 확인 필요",
      "승인 담당자: 확인 필요",
      "긴급도와 마감일: 확인 필요",
    ],
    risks: [
      "승인 전 Slack/Telegram 전송 금지",
      "외부 API 연결 없음",
      "실제 알림 발송은 승인 게이트 이후 별도 검증 필요",
    ],
  },
  emailDraft: {
    summaryGenerated: "생성됨",
    replyDraftGenerated: "생성됨",
    approvalRequestGenerated: "생성됨",
    sendStatus: "발송하지 않음",
    approvalRequired: "필요",
    gmailApiStatus: "연결하지 않음",
    recipient: "확인 필요",
    companyName: "Acme Korea",
    majorRequests: [
      "파일럿 계약 조건과 견적 검토 가능 여부 회신",
      "회신 또는 조치 희망 시점: 이번 주 금요일",
    ],
    nextActions: [
      "사용자가 이메일 내용과 수신자를 검토합니다.",
      "불명확한 항목을 확인합니다.",
      "답장 초안을 검토한 뒤 발송 여부를 명시적으로 승인합니다.",
    ],
    confirmations: [
      "수신자: 확인 필요",
      "법적/권리 이슈: 확인 필요",
      "가격: 확인 필요",
      "수량: 확인 필요",
      "약속: 확인 필요",
    ],
    risks: [
      "Gmail API는 연결하지 않았습니다.",
      "실제 이메일 발송과 Gmail 초안 생성은 수행하지 않았습니다.",
      "사용자 승인 없이 발송하면 안 됩니다.",
      "불명확한 항목이 있어 확정 표현이나 과도한 약속을 피해야 합니다.",
    ],
  },
  sheetsWriteApproval: {
    approvalRequired: "필요",
    actualWriteStatus: "수행하지 않음",
    apiConnectionStatus: "연결하지 않음",
    targetSpreadsheet: "AI Team Agent Ops Tracker",
    targetTab: "Tasks",
    targetRow: "12",
    targetColumn: "status",
    originalValue: "대기",
    proposedValue: "완료",
    changeReason:
      "Supervisor Agent MVP 검증이 통과되어 상태 업데이트가 제안되었습니다.",
    risks: [
      "실제 Google Sheets 쓰기는 MVP에서 비활성화되어 있습니다.",
      "명시적 승인 전에는 어떤 쓰기 작업도 실행할 수 없습니다.",
      "명시적 사용자 승인이 아직 없습니다.",
      "필수 필드가 누락된 쓰기 요청은 차단 상태로 낮춰야 합니다.",
    ],
    confirmations: [
      "사용자 명시적 승인: 확인 필요",
      "누락 필드가 있는 요청의 대상 스프레드시트, 대상 행, 원본 값, 변경 사유, 사후 검증 계획: 확인 필요",
    ],
    verificationPlan:
      "쓰기 후 같은 스프레드시트, Tasks 탭, 12행 status 열을 다시 읽어 값이 완료인지 확인하고 결과를 한국어로 보고합니다.",
    finalStatus: [
      "write_status_complete: 승인 필요",
      "write_missing_fields_unsafe: 차단",
    ],
  },
};

function BulletList({ items }: { items: string[] }) {
  return (
    <ul className="plain-list">
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
}

export default function Home() {
  return (
    <main className="dashboard-shell">
      <section className="hero-section" aria-labelledby="dashboard-title">
        <div>
          <p className="eyebrow">Vercel 배포 완료 정적 MVP</p>
          <h1 id="dashboard-title">AI 팀 에이전트 상태</h1>
          <p className="hero-copy">
            Assistant Report Agent의 로컬 보고서 내용을 정적 대시보드에 반영합니다.
          </p>
        </div>
        <div className="status-panel" aria-label="현재 배포 상태">
          <span className="status-dot" />
          <strong>배포 완료</strong>
          <span>외부 API 연결 없음</span>
        </div>
      </section>

      <section className="summary-grid" aria-label="핵심 상태 요약">
        <article className="metric-card">
          <span className="metric-label">보고서 제목</span>
          <strong>{assistantReport.title}</strong>
          <p>대시보드는 현재 보고서 내용을 빌드 시점의 정적 데이터로 표시합니다.</p>
        </article>
        <article className="metric-card">
          <span className="metric-label">오늘의 전체 상태</span>
          <strong>하네스 통과</strong>
          <p>보고서 생성 시점의 저장소 상태와 최신 배포 확인 필요 여부를 요약합니다.</p>
        </article>
        <article className="metric-card">
          <span className="metric-label">외부 실행 여부</span>
          <strong>모두 미수행</strong>
          <p>발송, 알림, 쓰기, 게시, 외부 API 호출은 실행하지 않습니다.</p>
        </article>
      </section>

      <section className="two-column">
        <article className="content-section" aria-labelledby="overall-title">
          <div className="section-heading">
            <h2 id="overall-title">오늘의 전체 상태</h2>
            <p>Assistant Report Agent가 생성한 시점 기준 상태 요약입니다.</p>
          </div>
          <BulletList items={assistantReport.overallStatus} />
        </article>

        <article className="content-section" aria-labelledby="completed-title">
          <div className="section-heading">
            <h2 id="completed-title">완료된 작업</h2>
            <p>현재 준비된 로컬 MVP와 검증 레이어입니다.</p>
          </div>
          <BulletList items={assistantReport.completedWork} />
        </article>
      </section>

      <section className="content-section" aria-labelledby="agents-title">
        <div className="section-heading">
          <h2 id="agents-title">에이전트별 상태</h2>
          <p>보고서에 기록된 에이전트별 준비 상태입니다.</p>
        </div>
        <div className="agent-list">
          {assistantReport.agentStatus.map((agent) => (
            <article className="agent-row" key={agent.name}>
              <div>
                <h3>{agent.name}</h3>
                <p>{agent.status}</p>
              </div>
              <span>보고서 반영</span>
            </article>
          ))}
        </div>
      </section>

      <section className="two-column">
        <article className="content-section" aria-labelledby="harness-title">
          <div className="section-heading">
            <h2 id="harness-title">하네스 점검 결과</h2>
            <p>릴리스 전 로컬 검증 결과입니다.</p>
          </div>
          <BulletList items={assistantReport.harnessResults} />
        </article>

        <article className="content-section" aria-labelledby="commits-title">
          <div className="section-heading">
            <h2 id="commits-title">최근 커밋 요약</h2>
            <p>보고서 생성 시점 기준 최근 커밋입니다.</p>
          </div>
          <ol className="number-list">
            {assistantReport.recentCommits.map((commit) => (
              <li key={commit}>{commit}</li>
            ))}
          </ol>
        </article>
      </section>

      <section className="two-column">
        <article className="content-section" aria-labelledby="supervisor-title">
          <div className="section-heading">
            <h2 id="supervisor-title">Supervisor 라우팅 상태</h2>
            <p>로컬 라우팅 결과와 위험 작업 차단 상태입니다.</p>
          </div>
          <dl className="action-list">
            <div>
              <dt>총 요청 수</dt>
              <dd>{assistantReport.supervisorRouting.totalRequests}</dd>
            </div>
            <div>
              <dt>차단된 요청 수</dt>
              <dd>{assistantReport.supervisorRouting.blockedRequests}</dd>
            </div>
            <div>
              <dt>승인 필요 요청 수</dt>
              <dd>{assistantReport.supervisorRouting.approvalRequiredRequests}</dd>
            </div>
            <div>
              <dt>외부 실행 여부</dt>
              <dd>{assistantReport.supervisorRouting.externalExecution}</dd>
            </div>
          </dl>
          <div className="detail-block">
            <h3>라우팅 대상 에이전트 목록</h3>
            <p>{assistantReport.supervisorRouting.routeTargets}</p>
          </div>
          <div className="detail-block">
            <h3>위험 작업 차단 요약</h3>
            <BulletList items={assistantReport.supervisorRouting.riskBlockSummary} />
          </div>
        </article>

        <article className="content-section" aria-labelledby="notification-title">
          <div className="section-heading">
            <h2 id="notification-title">Notification 초안 상태</h2>
            <p>Slack/Telegram 발송 없이 검토용 초안만 표시합니다.</p>
          </div>
          <dl className="action-list">
            <div>
              <dt>Slack 상태 보고 초안</dt>
              <dd>{assistantReport.notificationDraft.slackDraft}</dd>
            </div>
            <div>
              <dt>Telegram 긴급 알림 초안</dt>
              <dd>{assistantReport.notificationDraft.telegramDraft}</dd>
            </div>
            <div>
              <dt>승인 필요 여부</dt>
              <dd>{assistantReport.notificationDraft.approvalRequired}</dd>
            </div>
            <div>
              <dt>발송 여부</dt>
              <dd>{assistantReport.notificationDraft.sendStatus}</dd>
            </div>
            <div>
              <dt>외부 API 연결 여부</dt>
              <dd>{assistantReport.notificationDraft.externalApi}</dd>
            </div>
          </dl>
          <div className="detail-block">
            <h3>확인이 필요한 부분</h3>
            <BulletList items={assistantReport.notificationDraft.confirmations} />
          </div>
          <div className="detail-block">
            <h3>위험 요소</h3>
            <BulletList items={assistantReport.notificationDraft.risks} />
          </div>
        </article>
      </section>

      <section className="content-section" aria-labelledby="sheets-write-title">
        <div className="section-heading">
          <h2 id="sheets-write-title">Sheets 쓰기 승인 상태</h2>
          <p>Google Sheets 실제 쓰기 없이 로컬 승인 요청서 상태만 표시합니다.</p>
        </div>
        <dl className="action-list">
          <div>
            <dt>승인 필요 여부</dt>
            <dd>{assistantReport.sheetsWriteApproval.approvalRequired}</dd>
          </div>
          <div>
            <dt>실제 쓰기 수행 여부</dt>
            <dd>{assistantReport.sheetsWriteApproval.actualWriteStatus}</dd>
          </div>
          <div>
            <dt>Google Sheets API 연결 여부</dt>
            <dd>{assistantReport.sheetsWriteApproval.apiConnectionStatus}</dd>
          </div>
          <div>
            <dt>대상 스프레드시트</dt>
            <dd>{assistantReport.sheetsWriteApproval.targetSpreadsheet}</dd>
          </div>
          <div>
            <dt>대상 탭</dt>
            <dd>{assistantReport.sheetsWriteApproval.targetTab}</dd>
          </div>
          <div>
            <dt>대상 행</dt>
            <dd>{assistantReport.sheetsWriteApproval.targetRow}</dd>
          </div>
          <div>
            <dt>대상 열</dt>
            <dd>{assistantReport.sheetsWriteApproval.targetColumn}</dd>
          </div>
          <div>
            <dt>원본 값</dt>
            <dd>{assistantReport.sheetsWriteApproval.originalValue}</dd>
          </div>
          <div>
            <dt>제안 값</dt>
            <dd>{assistantReport.sheetsWriteApproval.proposedValue}</dd>
          </div>
        </dl>
        <div className="detail-block">
          <h3>변경 사유</h3>
          <p>{assistantReport.sheetsWriteApproval.changeReason}</p>
        </div>
        <div className="detail-block">
          <h3>위험 요소</h3>
          <BulletList items={assistantReport.sheetsWriteApproval.risks} />
        </div>
        <div className="detail-block">
          <h3>확인이 필요한 부분</h3>
          <BulletList items={assistantReport.sheetsWriteApproval.confirmations} />
        </div>
        <div className="detail-block">
          <h3>사후 검증 계획</h3>
          <p>{assistantReport.sheetsWriteApproval.verificationPlan}</p>
        </div>
        <div className="detail-block">
          <h3>최종 상태</h3>
          <BulletList items={assistantReport.sheetsWriteApproval.finalStatus} />
        </div>
      </section>

      <section className="content-section" aria-labelledby="email-draft-title">
        <div className="section-heading">
          <h2 id="email-draft-title">Email Draft 상태</h2>
          <p>Gmail API 연결 없이 로컬 이메일 요약과 검토용 답장 초안만 표시합니다.</p>
        </div>
        <dl className="action-list">
          <div>
            <dt>이메일 요약 생성 여부</dt>
            <dd>{assistantReport.emailDraft.summaryGenerated}</dd>
          </div>
          <div>
            <dt>답장 초안 생성 여부</dt>
            <dd>{assistantReport.emailDraft.replyDraftGenerated}</dd>
          </div>
          <div>
            <dt>승인 요청서 생성 여부</dt>
            <dd>{assistantReport.emailDraft.approvalRequestGenerated}</dd>
          </div>
          <div>
            <dt>발송 여부</dt>
            <dd>{assistantReport.emailDraft.sendStatus}</dd>
          </div>
          <div>
            <dt>승인 필요 여부</dt>
            <dd>{assistantReport.emailDraft.approvalRequired}</dd>
          </div>
          <div>
            <dt>Gmail API 연결 여부</dt>
            <dd>{assistantReport.emailDraft.gmailApiStatus}</dd>
          </div>
          <div>
            <dt>수신자</dt>
            <dd>{assistantReport.emailDraft.recipient}</dd>
          </div>
          <div>
            <dt>회사명</dt>
            <dd>{assistantReport.emailDraft.companyName}</dd>
          </div>
        </dl>
        <div className="detail-block">
          <h3>주요 요청 사항</h3>
          <BulletList items={assistantReport.emailDraft.majorRequests} />
        </div>
        <div className="detail-block">
          <h3>다음 액션</h3>
          <BulletList items={assistantReport.emailDraft.nextActions} />
        </div>
        <div className="detail-block">
          <h3>확인이 필요한 부분</h3>
          <BulletList items={assistantReport.emailDraft.confirmations} />
        </div>
        <div className="detail-block">
          <h3>위험 요소</h3>
          <BulletList items={assistantReport.emailDraft.risks} />
        </div>
      </section>

      <section className="two-column">
        <article className="content-section" aria-labelledby="risks-title">
          <div className="section-heading">
            <h2 id="risks-title">남은 리스크</h2>
            <p>외부 연동 전 계속 확인해야 할 항목입니다.</p>
          </div>
          <BulletList items={assistantReport.remainingRisks} />
        </article>

        <article className="content-section" aria-labelledby="next-title">
          <div className="section-heading">
            <h2 id="next-title">다음 추천 작업</h2>
            <p>보고서 기반 다음 실행 후보입니다.</p>
          </div>
          <ol className="number-list">
            {assistantReport.nextRecommendations.map((task) => (
              <li key={task}>{task}</li>
            ))}
          </ol>
        </article>
      </section>

      <section className="two-column">
        <article className="content-section" aria-labelledby="approval-title">
          <div className="section-heading">
            <h2 id="approval-title">승인 필요 항목</h2>
            <p>외부 실행 전에 사용자 승인이 필요한 작업입니다.</p>
          </div>
          <BulletList items={assistantReport.approvalRequired} />
        </article>

        <article className="content-section" aria-labelledby="external-title">
          <div className="section-heading">
            <h2 id="external-title">외부 실행 여부</h2>
            <p>현재 대시보드는 표시 전용이며 외부 작업을 실행하지 않습니다.</p>
          </div>
          <dl className="action-list">
            {assistantReport.externalActions.map((action) => (
              <div key={action.label}>
                <dt>{action.label}</dt>
                <dd>{action.value}</dd>
              </div>
            ))}
          </dl>
        </article>
      </section>
    </main>
  );
}
