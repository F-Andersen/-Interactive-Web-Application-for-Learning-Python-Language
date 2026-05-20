import { useEffect, useState } from "react";
import { api, ProgressItem, StudentStats } from "../api/client";
import { Layout } from "../components/Layout";
import { useAuth } from "../hooks/useAuth";

export function ProfilePage() {
  const { user } = useAuth();
  const [items, setItems] = useState<ProgressItem[]>([]);
  const [stats, setStats] = useState<StudentStats | null>(null);

  useEffect(() => {
    api.get<ProgressItem[]>("/progress/me").then(({ data }) => setItems(data));
    api.get<StudentStats>("/progress/me/stats").then(({ data }) => setStats(data));
  }, []);

  return (
    <Layout>
      <section className="page-head">
        <h1>{user?.username}</h1>
        <p>{user?.email} · {user?.role.name}</p>
      </section>
      {stats && (
        <section className="stats-grid">
          <div className="stat-card"><span>Started lessons</span><strong>{stats.lessons_started}</strong></div>
          <div className="stat-card"><span>Completed lessons</span><strong>{stats.lessons_completed}</strong></div>
          <div className="stat-card"><span>Solved tasks</span><strong>{stats.solved_tasks_count}</strong></div>
          <div className="stat-card"><span>Accepted</span><strong>{stats.accepted_submissions_count}/{stats.submissions_count}</strong></div>
          <div className="stat-card"><span>Average score</span><strong>{stats.average_score}%</strong></div>
          <div className="stat-card"><span>Average progress</span><strong>{stats.average_completion_percent}%</strong></div>
        </section>
      )}
      <section className="panel">
        <h2>Progress</h2>
        {items.length === 0 && <p>No accepted submissions yet.</p>}
        {items.map((item) => (
          <div className="progress-row" key={item.id}>
            <strong>{item.lesson_title}</strong>
            <span>{item.course_title}</span>
            <div className="progress"><span style={{ width: `${item.completion_percent}%` }} /></div>
            <em>{item.completion_percent}%</em>
          </div>
        ))}
      </section>
      {stats && (
        <section className="panel">
          <h2>Recent submissions</h2>
          {stats.submissions_by_status.length > 0 && (
            <div className="status-strip">
              {stats.submissions_by_status.map((item) => <span key={item.status}>{item.status}: {item.count}</span>)}
            </div>
          )}
          {stats.recent_submissions.length === 0 && <p>No submissions yet.</p>}
          {stats.recent_submissions.map((submission) => (
            <div className="activity-row" key={submission.id}>
              <strong>{submission.task_title}</strong>
              <span>{submission.course_title}</span>
              <span className={`status ${submission.status}`}>{submission.status}</span>
              <em>{submission.score}%</em>
            </div>
          ))}
        </section>
      )}
    </Layout>
  );
}
