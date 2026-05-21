import Editor from "@monaco-editor/react";
import { ChevronLeft, ChevronRight, ListChecks, Send } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api, Lesson, SubmissionResult, Task } from "../api/client";
import { Layout } from "../components/Layout";

export function TaskPage() {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const [task, setTask] = useState<Task | null>(null);
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [code, setCode] = useState("");
  const [result, setResult] = useState<SubmissionResult | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api.get<Task>(`/tasks/${taskId}`).then(({ data }) => {
      setTask(data);
      setCode(data.starter_code ?? "");
      setResult(null);
      api.get<Lesson>(`/lessons/${data.lesson_id}`).then(({ data: lessonData }) => setLesson(lessonData));
    });
  }, [taskId]);

  const submit = async () => {
    setSubmitting(true);
    try {
      const { data } = await api.post<SubmissionResult>(`/tasks/${taskId}/submit`, { code });
      setResult(data);
    } finally {
      setSubmitting(false);
    }
  };

  if (!task) return <Layout><div className="panel">Loading...</div></Layout>;
  const sortedTasks = [...(lesson?.tasks ?? [])].sort((first, second) => first.order_index - second.order_index);
  const currentIndex = sortedTasks.findIndex((item) => item.id === task.id);
  const previousTask = currentIndex > 0 ? sortedTasks[currentIndex - 1] : null;
  const nextTask = currentIndex >= 0 && currentIndex < sortedTasks.length - 1 ? sortedTasks[currentIndex + 1] : null;

  const goToTask = (nextId?: number) => {
    if (nextId) {
      navigate(`/tasks/${nextId}`);
    }
  };

  return (
    <Layout>
      <div className="task-nav">
        <button className="secondary-btn" onClick={() => goToTask(previousTask?.id)} disabled={!previousTask} title="Previous question">
          <ChevronLeft size={16} /> Previous
        </button>
        <Link className="secondary-link" to={`/lessons/${task.lesson_id}`}><ListChecks size={16} /> All questions</Link>
        <span>{currentIndex + 1 > 0 ? currentIndex + 1 : 1} / {sortedTasks.length || 1}</span>
        <button className="secondary-btn" onClick={() => goToTask(nextTask?.id)} disabled={!nextTask} title="Next question">
          Next <ChevronRight size={16} />
        </button>
      </div>
      <div className="task-layout">
        <section className="panel task-brief">
          <span className="pill">{task.difficulty}</span>
          <h1>{task.title}</h1>
          <p>{task.statement}</p>
          <dl>
            <dt>Time</dt><dd>{task.time_limit_ms} ms</dd>
            <dt>Memory</dt><dd>{task.memory_limit_mb} MB</dd>
          </dl>
        </section>
        <section className="editor-panel">
          <Editor height="430px" language="python" theme="vs-dark" value={code} onChange={(value) => setCode(value ?? "")} options={{ minimap: { enabled: false }, fontSize: 14 }} />
          <div className="toolbar">
            <button className="secondary-btn dark" onClick={() => goToTask(previousTask?.id)} disabled={!previousTask}><ChevronLeft size={16} /> Previous</button>
            <button onClick={submit} disabled={submitting}><Send size={16} /> {submitting ? "Checking..." : "Submit"}</button>
            <button className="secondary-btn dark" onClick={() => goToTask(nextTask?.id)} disabled={!nextTask}>Next <ChevronRight size={16} /></button>
          </div>
        </section>
      </div>
      {lesson && sortedTasks.length > 1 && (
        <section className="panel question-strip">
          <h2>Lesson questions</h2>
          <div>
            {sortedTasks.map((item, index) => (
              <Link className={item.id === task.id ? "question-pill active" : "question-pill"} to={`/tasks/${item.id}`} key={item.id}>
                {index + 1}. {item.title}
              </Link>
            ))}
          </div>
        </section>
      )}
      {result && (
        <section className={`panel result ${result.status}`}>
          <h2>{result.status}</h2>
          <p>{result.passed_tests} / {result.total_tests} tests, score {result.score}%, {result.execution_time_ms} ms</p>
          {result.error_message && <pre>{result.error_message}</pre>}
          {result.tests.map((test) => (
            <div className="test-row" key={test.order_index}>
              <strong>#{test.order_index} {test.status}</strong>
              {test.is_hidden ? <span>Hidden case</span> : <code>{test.input_data || "no input"} =&gt; {test.expected_output}</code>}
            </div>
          ))}
          {nextTask && result.status === "accepted" && (
            <button className="next-accepted" onClick={() => goToTask(nextTask.id)}>
              Next question <ChevronRight size={16} />
            </button>
          )}
        </section>
      )}
    </Layout>
  );
}
