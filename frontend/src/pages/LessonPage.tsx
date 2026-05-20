import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, Lesson } from "../api/client";
import { Layout } from "../components/Layout";

export function LessonPage() {
  const { lessonId } = useParams();
  const [lesson, setLesson] = useState<Lesson | null>(null);
  useEffect(() => {
    api.get<Lesson>(`/lessons/${lessonId}`).then(({ data }) => setLesson(data));
  }, [lessonId]);

  if (!lesson) return <Layout><div className="panel">Loading...</div></Layout>;
  return (
    <Layout>
      <article className="lesson">
        <h1>{lesson.title}</h1>
        <p>{lesson.content}</p>
      </article>
      <section className="panel">
        <h2>Practice</h2>
        {lesson.tasks.map((task) => (
          <Link className="row-link" to={`/tasks/${task.id}`} key={task.id}>{task.title}<span>{task.difficulty}</span></Link>
        ))}
      </section>
    </Layout>
  );
}
