import axios from "axios";

const api = axios.create({
  baseURL: "/api/",
  withCredentials: true,
  timeout: 15000,
});

export interface CalendarEvent {
  id: number;
  external_id: string;
  title: string;
  description: string;
  starts_at: string;
  ends_at: string | null;
  all_day: boolean;
  user: number;
  course: number | null;
}

export interface GradeCategory {
  id: number;
  name: string;
  weight: string;
  excluded: boolean;
  highest_to_drop: number;
  lowest_to_drop: number;
}

export interface GradeItem {
  id: number;
  category: number | null;
  name: string;
  max_points: string;
  earned_points: string | null;
  percentage: number | null;
  weight: string;
  displayed_grade: string;
  is_bonus: boolean;
  excluded: boolean;
  feedback: string;
}

export interface Assignment {
  id: number;
  title: string;
  due_date: string | null;
  status: string;
  grade_item: number | null;
  submission_count: number;
}

export interface Course {
  id: number;
  semester: number;
  brightspace_id: number | null;
  code: string;
  name: string;
  instructor: string;
  color: string;
  is_active: boolean;
  can_access: boolean;
  home_url: string;
  grade_categories: GradeCategory[];
  grade_items: GradeItem[];
  assignments: Assignment[];
}
export async function getCalendarEvents(): Promise<CalendarEvent[]> {
  const response = await api.get("calendar/");
  return response.data;
}

export async function getCourses(): Promise<Course[]> {
  const response = await api.get("courses/");
  return response.data;
}

export default api;
