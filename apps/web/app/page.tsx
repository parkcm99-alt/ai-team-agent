const agentStatuses = [
  {
    name: "Assistant Report Agent",
    status: "로컬 상태 보고서 생성 가능",
    detail: "reports/daily_status_report.md 기준으로 요약합니다.",
  },
  {
    name: "Document Agent",
    status: "문서 요약 MVP 준비",
    detail: "문서 출력 검증과 워크플로 검증이 준비되어 있습니다.",
  },
  {
    name: "Communication Agent",
    status: "커뮤니케이션 초안 MVP 준비",
    detail: "발송 없이 한국어 요약과 답장 초안만 생성합니다.",
  },
  {
    name: "Sheets Reader Agent",
    status: "로컬 CSV 읽기 전용 MVP 준비",
    detail: "Google Sheets API 연결 없이 샘플 CSV만 분석합니다.",
  },
  {
    name: "Harness Agent",
    status: "통합 점검 실행 가능",
    detail: "정책, 리플레이, 문서, 커뮤니케이션, Sheets Reader, 보고서 검증을 확인합니다.",
  },
];

const risks = [
  "아직 외부 API와 인증 정보가 연결되지 않았습니다.",
  "Vercel 배포 후에도 로컬 하네스와 Next.js 빌드 검증을 계속 유지해야 합니다.",
  "실제 이메일, Slack/Telegram, Google Sheets, Instagram 작업은 승인 게이트가 필요합니다.",
];

const nextTasks = [
  "Vercel 배포 상태를 기록하고, reports/daily_status_report.md 내용을 대시보드에 반영합니다.",
];

const externalActions = [
  ["이메일 발송", "수행하지 않음"],
  ["Slack/Telegram 알림", "수행하지 않음"],
  ["Google Sheets 쓰기", "수행하지 않음"],
  ["Instagram 게시", "수행하지 않음"],
];

export default function Home() {
  return (
    <main className="dashboard-shell">
      <section className="hero-section" aria-labelledby="dashboard-title">
        <div>
          <p className="eyebrow">Vercel 배포 완료 정적 MVP</p>
          <h1 id="dashboard-title">AI 팀 에이전트 상태</h1>
          <p className="hero-copy">
            로컬 하네스와 에이전트 산출물을 기준으로 현재 프로젝트 상태를 한눈에 확인합니다.
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
          <span className="metric-label">전체 점검 상태</span>
          <strong>통과 기준 준비</strong>
          <p>통합 하네스 명령으로 로컬 검증을 수행합니다.</p>
        </article>
        <article className="metric-card">
          <span className="metric-label">최근 보고서 요약</span>
          <strong>한국어 상태 보고서</strong>
          <p>완료 작업, 리스크, 승인 필요 항목을 정리합니다.</p>
        </article>
        <article className="metric-card">
          <span className="metric-label">외부 실행 여부</span>
          <strong>모두 미수행</strong>
          <p>발송, 알림, 쓰기, 게시 작업은 실행하지 않습니다.</p>
        </article>
      </section>

      <section className="content-section" aria-labelledby="agents-title">
        <div className="section-heading">
          <h2 id="agents-title">에이전트별 상태</h2>
          <p>각 에이전트는 로컬 MVP 범위에서만 동작합니다.</p>
        </div>
        <div className="agent-list">
          {agentStatuses.map((agent) => (
            <article className="agent-row" key={agent.name}>
              <div>
                <h3>{agent.name}</h3>
                <p>{agent.detail}</p>
              </div>
              <span>{agent.status}</span>
            </article>
          ))}
        </div>
      </section>

      <section className="two-column">
        <article className="content-section" aria-labelledby="report-title">
          <div className="section-heading">
            <h2 id="report-title">최근 보고서 요약</h2>
            <p>Assistant Report Agent가 생성하는 로컬 상태 보고서 기준입니다.</p>
          </div>
          <ul className="plain-list">
            <li>하네스 점검 결과와 최근 커밋 요약을 표시합니다.</li>
            <li>남은 리스크와 다음 추천 작업을 한국어로 정리합니다.</li>
            <li>외부 실행 미수행 상태를 명확히 표시합니다.</li>
          </ul>
        </article>

        <article className="content-section" aria-labelledby="external-title">
          <div className="section-heading">
            <h2 id="external-title">외부 실행 여부</h2>
            <p>현재 대시보드는 표시 전용이며 외부 작업을 실행하지 않습니다.</p>
          </div>
          <dl className="action-list">
            {externalActions.map(([label, value]) => (
              <div key={label}>
                <dt>{label}</dt>
                <dd>{value}</dd>
              </div>
            ))}
          </dl>
        </article>
      </section>

      <section className="two-column">
        <article className="content-section" aria-labelledby="risks-title">
          <div className="section-heading">
            <h2 id="risks-title">남은 리스크</h2>
            <p>배포와 외부 연동 전에 확인해야 할 항목입니다.</p>
          </div>
          <ul className="plain-list">
            {risks.map((risk) => (
              <li key={risk}>{risk}</li>
            ))}
          </ul>
        </article>

        <article className="content-section" aria-labelledby="next-title">
          <div className="section-heading">
            <h2 id="next-title">다음 추천 작업</h2>
            <p>배포 상태를 기준으로 다음 운영 기록을 정리합니다.</p>
          </div>
          <ol className="number-list">
            {nextTasks.map((task) => (
              <li key={task}>{task}</li>
            ))}
          </ol>
        </article>
      </section>
    </main>
  );
}
