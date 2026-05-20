import { FormEvent, useEffect, useState } from "react";
import { api, AdminStats, Course, Lesson, Module, Task, TestCase, User } from "../api/client";
import { Layout } from "../components/Layout";

type AdminData = {
  users: User[];
  courses: Course[];
  modules: Module[];
  lessons: Lesson[];
  tasks: Task[];
  cases: TestCase[];
};

export function AdminPage() {
  const [data, setData] = useState<AdminData>({ users: [], courses: [], modules: [], lessons: [], tasks: [], cases: [] });
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [course, setCourse] = useState({ title: "", description: "", difficulty_level: "beginner", publish_status: "draft" });
  const [module, setModule] = useState({ course_id: "", title: "", description: "" });
  const [lesson, setLesson] = useState({ module_id: "", title: "", content: "" });
  const [task, setTask] = useState({ lesson_id: "", title: "", statement: "", difficulty: "easy", starter_code: "" });
  const [testCase, setTestCase] = useState({ task_id: "", input_data: "", expected_output: "", is_hidden: false });

  const load = async () => {
    const [users, courses, modules, lessons, tasks, cases, statsResponse] = await Promise.all([
      api.get<User[]>("/admin/users"),
      api.get<Course[]>("/admin/courses"),
      api.get<Module[]>("/admin/modules"),
      api.get<Lesson[]>("/admin/lessons"),
      api.get<Task[]>("/admin/tasks"),
      api.get<TestCase[]>("/admin/test-cases"),
      api.get<AdminStats>("/admin/stats")
    ]);
    setData({ users: users.data, courses: courses.data, modules: modules.data, lessons: lessons.data, tasks: tasks.data, cases: cases.data });
    setStats(statsResponse.data);
  };

  useEffect(() => {
    load();
  }, []);

  const createCourse = async (event: FormEvent) => {
    event.preventDefault();
    await api.post("/admin/courses", course);
    setCourse({ title: "", description: "", difficulty_level: "beginner", publish_status: "draft" });
    await load();
  };

  const createModule = async (event: FormEvent) => {
    event.preventDefault();
    await api.post("/admin/modules", { ...module, course_id: Number(module.course_id), order_index: nextOrder(data.modules.filter((item) => item.course_id === Number(module.course_id))) });
    setModule({ course_id: "", title: "", description: "" });
    await load();
  };

  const createLesson = async (event: FormEvent) => {
    event.preventDefault();
    await api.post("/admin/lessons", { ...lesson, module_id: Number(lesson.module_id), order_index: nextOrder(data.lessons.filter((item) => item.module_id === Number(lesson.module_id))) });
    setLesson({ module_id: "", title: "", content: "" });
    await load();
  };

  const createTask = async (event: FormEvent) => {
    event.preventDefault();
    await api.post("/admin/tasks", { ...task, lesson_id: Number(task.lesson_id), time_limit_ms: 5000, memory_limit_mb: 128, order_index: nextOrder(data.tasks.filter((item) => item.lesson_id === Number(task.lesson_id))) });
    setTask({ lesson_id: "", title: "", statement: "", difficulty: "easy", starter_code: "" });
    await load();
  };

  const createTestCase = async (event: FormEvent) => {
    event.preventDefault();
    await api.post("/admin/test-cases", { ...testCase, task_id: Number(testCase.task_id), order_index: nextOrder(data.cases.filter((item) => item.task_id === Number(testCase.task_id))) });
    setTestCase({ task_id: "", input_data: "", expected_output: "", is_hidden: false });
    await load();
  };

  const publishCourse = async (id: number, publish_status: string) => {
    await api.patch(`/admin/courses/${id}`, { publish_status });
    await load();
  };

  const deleteCourse = async (id: number) => {
    await api.delete(`/admin/courses/${id}`);
    await load();
  };

  const changeUserStatus = async (id: number, status: string) => {
    await api.patch(`/admin/users/${id}/status?status_value=${status}`);
    await load();
  };

  return (
    <Layout>
      <section className="page-head">
        <h1>Admin dashboard</h1>
        <p>Content management, users, submissions and platform-wide learning analytics.</p>
      </section>

      {stats && (
        <>
          <section className="stats-grid">
            <div className="stat-card"><span>Users</span><strong>{stats.users_count}</strong></div>
            <div className="stat-card"><span>Students</span><strong>{stats.students_count}</strong></div>
            <div className="stat-card"><span>Published courses</span><strong>{stats.published_courses_count}/{stats.courses_count}</strong></div>
            <div className="stat-card"><span>Lessons</span><strong>{stats.lessons_count}</strong></div>
            <div className="stat-card"><span>Tasks</span><strong>{stats.tasks_count}</strong></div>
            <div className="stat-card"><span>Accepted</span><strong>{stats.accepted_submissions_count}/{stats.submissions_count}</strong></div>
            <div className="stat-card"><span>Average score</span><strong>{stats.average_score}%</strong></div>
            <div className="stat-card"><span>Blocked users</span><strong>{stats.blocked_users_count}</strong></div>
          </section>

          <section className="panel">
            <h2>Course analytics</h2>
            <div className="table">
              <div className="table-head"><span>Course</span><span>Content</span><span>Submissions</span><span>Students</span></div>
              {stats.course_stats.map((item) => (
                <div className="table-row" key={item.course_id}>
                  <strong>{item.title}<small>{item.publish_status}</small></strong>
                  <span>{item.modules_count} modules · {item.lessons_count} lessons · {item.tasks_count} tasks</span>
                  <span>{item.accepted_submissions_count}/{item.submissions_count} accepted</span>
                  <span>{item.active_students_count}</span>
                </div>
              ))}
            </div>
          </section>

          <section className="panel">
            <h2>Recent submissions</h2>
            <div className="status-strip">
              {stats.submissions_by_status.map((item) => <span key={item.status}>{item.status}: {item.count}</span>)}
            </div>
            {stats.recent_submissions.map((submission) => (
              <div className="activity-row" key={submission.id}>
                <strong>{submission.username}</strong>
                <span>{submission.task_title}</span>
                <span className={`status ${submission.status}`}>{submission.status}</span>
                <em>{submission.score}%</em>
              </div>
            ))}
          </section>
        </>
      )}

      <div className="admin-grid">
        <form className="panel form" onSubmit={createCourse}>
          <h2>New course</h2>
          <input placeholder="Title" value={course.title} onChange={(e) => setCourse({ ...course, title: e.target.value })} />
          <textarea placeholder="Description" value={course.description} onChange={(e) => setCourse({ ...course, description: e.target.value })} />
          <select value={course.difficulty_level} onChange={(e) => setCourse({ ...course, difficulty_level: e.target.value })}>
            <option>beginner</option><option>basic</option><option>intermediate</option>
          </select>
          <select value={course.publish_status} onChange={(e) => setCourse({ ...course, publish_status: e.target.value })}>
            <option>draft</option><option>published</option><option>archived</option>
          </select>
          <button>Create course</button>
        </form>

        <form className="panel form" onSubmit={createModule}>
          <h2>New module</h2>
          <select value={module.course_id} onChange={(e) => setModule({ ...module, course_id: e.target.value })}>
            <option value="">Course</option>
            {data.courses.map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}
          </select>
          <input placeholder="Title" value={module.title} onChange={(e) => setModule({ ...module, title: e.target.value })} />
          <textarea placeholder="Description" value={module.description} onChange={(e) => setModule({ ...module, description: e.target.value })} />
          <button>Create module</button>
        </form>

        <form className="panel form" onSubmit={createLesson}>
          <h2>New lesson</h2>
          <select value={lesson.module_id} onChange={(e) => setLesson({ ...lesson, module_id: e.target.value })}>
            <option value="">Module</option>
            {data.modules.map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}
          </select>
          <input placeholder="Title" value={lesson.title} onChange={(e) => setLesson({ ...lesson, title: e.target.value })} />
          <textarea placeholder="Content" value={lesson.content} onChange={(e) => setLesson({ ...lesson, content: e.target.value })} />
          <button>Create lesson</button>
        </form>

        <form className="panel form" onSubmit={createTask}>
          <h2>New task</h2>
          <select value={task.lesson_id} onChange={(e) => setTask({ ...task, lesson_id: e.target.value })}>
            <option value="">Lesson</option>
            {data.lessons.map((lesson) => <option key={lesson.id} value={lesson.id}>{lesson.title}</option>)}
          </select>
          <input placeholder="Title" value={task.title} onChange={(e) => setTask({ ...task, title: e.target.value })} />
          <select value={task.difficulty} onChange={(e) => setTask({ ...task, difficulty: e.target.value })}>
            <option>easy</option><option>medium</option><option>hard</option>
          </select>
          <textarea placeholder="Statement" value={task.statement} onChange={(e) => setTask({ ...task, statement: e.target.value })} />
          <textarea placeholder="Starter code" value={task.starter_code} onChange={(e) => setTask({ ...task, starter_code: e.target.value })} />
          <button>Create task</button>
        </form>

        <form className="panel form" onSubmit={createTestCase}>
          <h2>New test case</h2>
          <select value={testCase.task_id} onChange={(e) => setTestCase({ ...testCase, task_id: e.target.value })}>
            <option value="">Task</option>
            {data.tasks.map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}
          </select>
          <textarea placeholder="Input data" value={testCase.input_data} onChange={(e) => setTestCase({ ...testCase, input_data: e.target.value })} />
          <textarea placeholder="Expected output" value={testCase.expected_output} onChange={(e) => setTestCase({ ...testCase, expected_output: e.target.value })} />
          <label className="check"><input type="checkbox" checked={testCase.is_hidden} onChange={(e) => setTestCase({ ...testCase, is_hidden: e.target.checked })} /> Hidden</label>
          <button>Create test case</button>
        </form>

        <section className="panel">
          <h2>Users</h2>
          {data.users.map((user) => (
            <div className="row-link" key={user.id}>
              <span><strong>{user.email}</strong> · {user.role.name}</span>
              <span>
                <button type="button" onClick={() => changeUserStatus(user.id, user.status === "blocked" ? "active" : "blocked")}>{user.status}</button>
              </span>
            </div>
          ))}
        </section>

        <section className="panel">
          <h2>Courses</h2>
          {data.courses.map((item) => (
            <div className="row-link" key={item.id}>
              <span><strong>{item.title}</strong> · {item.difficulty_level}</span>
              <span>
                <button type="button" onClick={() => publishCourse(item.id, item.publish_status === "published" ? "draft" : "published")}>{item.publish_status}</button>
                <button type="button" className="danger" onClick={() => deleteCourse(item.id)}>Delete</button>
              </span>
            </div>
          ))}
          <p>{data.modules.length} modules · {data.lessons.length} lessons · {data.tasks.length} tasks · {data.cases.length} test cases</p>
        </section>
      </div>
    </Layout>
  );
}

function nextOrder(items: Array<{ order_index: number }>) {
  return items.length ? Math.max(...items.map((item) => item.order_index)) + 1 : 1;
}
