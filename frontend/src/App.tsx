import { Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./hooks/useAuth";
import { ProtectedRoute } from "./routes/ProtectedRoute";
import { AdminPage } from "./pages/AdminPage";
import { CoursePage } from "./pages/CoursePage";
import { CoursesPage } from "./pages/CoursesPage";
import { LessonPage } from "./pages/LessonPage";
import { LoginPage } from "./pages/LoginPage";
import { ProfilePage } from "./pages/ProfilePage";
import { RegisterPage } from "./pages/RegisterPage";
import { TaskPage } from "./pages/TaskPage";

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/courses" element={<ProtectedRoute><CoursesPage /></ProtectedRoute>} />
        <Route path="/courses/:courseId" element={<ProtectedRoute><CoursePage /></ProtectedRoute>} />
        <Route path="/lessons/:lessonId" element={<ProtectedRoute><LessonPage /></ProtectedRoute>} />
        <Route path="/tasks/:taskId" element={<ProtectedRoute><TaskPage /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
        <Route path="/admin" element={<ProtectedRoute adminOnly><AdminPage /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/courses" replace />} />
      </Routes>
    </AuthProvider>
  );
}
