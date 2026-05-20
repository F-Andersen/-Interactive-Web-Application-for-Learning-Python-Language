import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, Course } from "../api/client";
import { Layout } from "../components/Layout";

export function CoursePage() {
  const { courseId } = useParams();
  const [course, setCourse] = useState<Course | null>(null);
  const [progress, setProgress] = useState<number>(0);
  useEffect(() => {
    api.get<Course>(`/courses/${courseId}`).then(({ data }) => setCourse(data));
    api.get(`/progress/course/${courseId}`).then(({ data }) => setProgress(data.completion_percent)).catch(() => setProgress(0));
  }, [courseId]);

  if (!course) return <Layout><div className="panel">Loading...</div></Layout>;
  return (
    <Layout>
      <section className="page-head">
        <h1>{course.title}</h1>
        <p>{course.description}</p>
        <div className="progress"><span style={{ width: `${progress}%` }} /></div>
      </section>
      <div className="list">
        {course.modules.map((module) => (
          <section className="panel" key={module.id}>
            <h2>{module.title}</h2>
            <p>{module.description}</p>
            {module.lessons.map((lesson) => (
              <Link className="row-link" to={`/lessons/${lesson.id}`} key={lesson.id}>{lesson.order_index}. {lesson.title}</Link>
            ))}
          </section>
        ))}
      </div>
    </Layout>
  );
}
