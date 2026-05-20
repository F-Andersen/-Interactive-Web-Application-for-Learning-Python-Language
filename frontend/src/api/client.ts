import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "/api"
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export type Role = { id: number; name: string; description?: string };
export type User = { id: number; username: string; email: string; status: string; role: Role };
export type TestCase = { id: number; task_id: number; input_data?: string | null; expected_output?: string | null; is_hidden: boolean; order_index: number };
export type Task = {
  id: number;
  lesson_id: number;
  title: string;
  statement: string;
  difficulty?: string;
  starter_code?: string;
  time_limit_ms: number;
  memory_limit_mb: number;
  order_index: number;
  test_cases: TestCase[];
};
export type Lesson = { id: number; module_id: number; title: string; content: string; order_index: number; tasks: Task[] };
export type Module = { id: number; course_id: number; title: string; description?: string; order_index: number; lessons: Lesson[] };
export type Course = {
  id: number;
  title: string;
  description?: string;
  difficulty_level?: string;
  publish_status: string;
  modules: Module[];
};
export type SubmissionResult = {
  id: number;
  task_id: number;
  status: string;
  score: number;
  passed_tests: number;
  total_tests: number;
  execution_time_ms: number;
  error_message?: string | null;
  submitted_at: string;
  tests: Array<{ order_index: number; status: string; output?: string | null; error?: string | null; input_data?: string | null; expected_output?: string | null; is_hidden: boolean }>;
};
export type ProgressItem = {
  id: number;
  lesson_id: number;
  completion_percent: number;
  last_activity_at: string;
  completed_at?: string | null;
  lesson_title?: string | null;
  course_title?: string | null;
};

export type StatusCount = { status: string; count: number };
export type SubmissionActivity = {
  id: number;
  user_email: string;
  username: string;
  task_title: string;
  course_title?: string | null;
  status: string;
  score: number;
  submitted_at: string;
};
export type StudentStats = {
  lessons_started: number;
  lessons_completed: number;
  average_completion_percent: number;
  submissions_count: number;
  accepted_submissions_count: number;
  solved_tasks_count: number;
  average_score: number;
  submissions_by_status: StatusCount[];
  recent_submissions: SubmissionActivity[];
};
export type CourseStats = {
  course_id: number;
  title: string;
  publish_status: string;
  modules_count: number;
  lessons_count: number;
  tasks_count: number;
  submissions_count: number;
  accepted_submissions_count: number;
  active_students_count: number;
};
export type AdminStats = {
  users_count: number;
  students_count: number;
  admins_count: number;
  blocked_users_count: number;
  courses_count: number;
  published_courses_count: number;
  lessons_count: number;
  tasks_count: number;
  test_cases_count: number;
  submissions_count: number;
  accepted_submissions_count: number;
  average_score: number;
  submissions_by_status: StatusCount[];
  course_stats: CourseStats[];
  recent_submissions: SubmissionActivity[];
};
