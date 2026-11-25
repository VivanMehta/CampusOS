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

export interface Course {
  id: number;
  brightspace_id: number | null;
  code: string;
  name: string;
  instructor: string;
  color: string;
  is_active: boolean;
  can_access: boolean;
  home_url: string;
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
