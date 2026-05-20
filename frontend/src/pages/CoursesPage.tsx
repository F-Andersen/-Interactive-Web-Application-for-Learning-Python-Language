import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, Course } from "../api/client";
import { Layout } from "../components/Layout";

export function CoursesPage() {
  const [courses, setCourses] = useState<Course[]>([]);
  useEffect(() => {
    api.get<Course[]>("/courses").then(({ data }) => setCourses(data));
  }, []);

  return (
    <Layout>
      <section className="page-head">
        <h1>Courses</h1>
        <p>Published Python learning paths with lessons and browser-based practice.</p>
      </section>
      <div className="grid">
        {courses.map((course) => (
          <Link className="course-card" key={course.id} to={`/courses/${course.id}`}>
            <span className="pill">{course.difficulty_level}</span>
            <h2>{course.title}</h2>
            <p>{course.description}</p>
            <strong>{course.modules.length} modules</strong>
          </Link>
        ))}
      </div>
    </Layout>
  );
}
