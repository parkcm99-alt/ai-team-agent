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
};

// TODO: Automate syncing from reports/daily_status_report.md.
const assistantReport: ReportData = {
  title: "AI 팀 에이전트 일일 상태 보고서",
  overallStatus: [
    "현재 저장소 상태: 로컬 변경 사항이 있어 커밋 전 확인이 필요합니다.",
    "하네스 상태: 전체 하네스 점검이 통과했습니다.",
    "보고서 생성 단계: final",
  ],
  completedWork: [
    "Document Agent MVP와 검증 러너가 준비되어 있습니다.",
    "Communication Agent MVP, 워크플로 테스트, 로컬 러너가 준비되어 있습니다.",
    "Sheets Reader MVP가 로컬 CSV 읽기 전용으로 준비되어 있습니다.",
    "Assistant Report Agent MVP가 로컬 상태 보고서를 생성합니다.",
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
      name: "Sheets Reader Agent",
      status: "로컬 CSV 읽기 전용 리포트 생성 및 검증 통과",
    },
    {
      name: "Harness Agent",
      status: "정책, 리플레이, 문서, 커뮤니케이션, Sheets Reader 검증 실행",
    },
    {
      name: "Supervisor/Workflow/Instagram Agent",
      status: "구조와 정책 중심의 초기 상태",
    },
  ],
  harnessResults: [
    "`python3 tests/harness/run_all.py`: 통과",
    "전체 하네스 점검이 통과했습니다.",
  ],
  recentCommits: [
    "2ebe609 docs: record vercel dashboard deployment",
    "d884853 fix: set Vercel framework preset to Next.js",
    "fe89f4d chore: document Vercel preview settings",
    "e195504 fix: resolve web dashboard postcss audit issue",
    "ec60780 feat: add web dashboard scaffold",
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
    "Slack 또는 Telegram 알림이 필요한 경우 명시적 사용자 승인이 필요합니다.",
    "Google Sheets 쓰기가 필요한 경우 대상 시트, 탭, 행/열, 원본 값, 제안 값을 제시한 뒤 명시적 사용자 승인이 필요합니다.",
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
          <p>저장소 상태, 하네스 상태, 보고서 생성 단계를 요약합니다.</p>
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
            <p>Assistant Report Agent가 생성한 상태 요약입니다.</p>
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
