import Editor from "@monaco-editor/react";
import { Send } from "lucide-react";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api, SubmissionResult, Task } from "../api/client";
import { Layout } from "../components/Layout";

export function TaskPage() {
  const { taskId } = useParams();
  const [task, setTask] = useState<Task | null>(null);
  const [code, setCode] = useState("");
  const [result, setResult] = useState<SubmissionResult | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api.get<Task>(`/tasks/${taskId}`).then(({ data }) => {
      setTask(data);
      setCode(data.starter_code ?? "");
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
  return (
    <Layout>
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
            <button onClick={submit} disabled={submitting}><Send size={16} /> {submitting ? "Checking..." : "Submit"}</button>
          </div>
        </section>
      </div>
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
        </section>
      )}
    </Layout>
  );
}
