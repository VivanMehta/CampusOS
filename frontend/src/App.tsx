import { useEffect, useState } from "react";
import Grades from "./pages/Grades";
import {
  LayoutDashboard,
  BookOpen,
  CalendarDays,
  GraduationCap,
  ClipboardList,
  Settings,
  RefreshCw,
  ExternalLink,
  Clock,
  AlertCircle,
} from "lucide-react";

import { getCalendarEvents, getCourses } from "./services/api";

import type { CalendarEvent, Course } from "./services/api";

import "./App.css";

function App() {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [page, setPage] = useState("Overview");

  async function loadData() {
    setLoading(true);
    setError("");

    try {
      const [calendarData, courseData] = await Promise.all([
        getCalendarEvents(),
        getCourses(),
      ]);

      setEvents(calendarData);
      setCourses(courseData);
    } catch {
      setError("Unable to load academic data. Check your CampusOS login.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  const upcoming = events
    .filter((event) => new Date(event.starts_at).getTime() >= Date.now())
    .sort(
      (a, b) =>
        new Date(a.starts_at).getTime() - new Date(b.starts_at).getTime(),
    );

  const deadlines = upcoming.filter((event) =>
    / - Due$| - Availability Ends$/.test(event.title),
  );

  const nextWeek = deadlines.filter(
    (event) =>
      new Date(event.starts_at).getTime() <=
      Date.now() + 7 * 24 * 60 * 60 * 1000,
  );

  const navigation = [
    { name: "Overview", icon: LayoutDashboard },
    { name: "Courses", icon: BookOpen },
    { name: "Assignments", icon: ClipboardList },
    { name: "Grades", icon: GraduationCap },
    { name: "Calendar", icon: CalendarDays },
    { name: "Settings", icon: Settings },
  ];

  function formatDate(value: string) {
    return new Date(value).toLocaleString("en-CA", {
      timeZone: "America/Edmonton",
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  }
  function EventList({ items }: { items: CalendarEvent[] }) {
    if (!items.length) {
      return <p className="empty">No events to display.</p>;
    }

    return (
      <div className="event-list">
        {items.map((event) => (
          <div className="event" key={event.id}>
            <div className="event-icon">
              <Clock size={18} />
            </div>

            <div className="event-info">
              <strong>{event.title}</strong>
              <span>{formatDate(event.starts_at)}</span>
            </div>

            <span className="event-tag">
              {event.title.endsWith(" - Available")
                ? "Opens"
                : event.title.endsWith(" - Availability Ends")
                  ? "Closes"
                  : event.title.endsWith(" - Due")
                    ? "Due"
                    : "Event"}
            </span>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <GraduationCap size={28} />
          <span>CampusOS</span>
        </div>

        <div className="nav-label">WORKSPACE</div>

        <nav>
          {navigation.map((item) => (
            <button
              key={item.name}
              className={`nav-item ${page === item.name ? "active" : ""}`}
              onClick={() => setPage(item.name)}
            >
              <item.icon size={19} />
              {item.name}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <a
            href="https://learn.sait.ca/d2l/home"
            target="_blank"
            rel="noreferrer"
          >
            Open Brightspace
            <ExternalLink size={15} />
          </a>

          <small>CampusOS · Development build</small>
        </div>
      </aside>

      <main className="main">
        <header className="header">
          <div>
            <h1>{page}</h1>
            <p>Your academic workspace.</p>
          </div>

          <button className="refresh" onClick={loadData}>
            <RefreshCw size={16} />
            Refresh data
          </button>
        </header>

        {error && (
          <div className="error">
            <AlertCircle size={18} />
            {error}
            <a href="http://127.0.0.1:8000/api-auth/login/">Log in</a>
          </div>
        )}

        {loading ? (
          <p className="empty">Loading academic data...</p>
        ) : (
          <>
            {page === "Overview" && (
              <>
                <div className="stats">
                  <div className="stat">
                    <BookOpen size={20} />
                    <span>Imported courses</span>
                    <strong>{courses.length}</strong>
                  </div>

                  <div className="stat">
                    <CalendarDays size={20} />
                    <span>Upcoming events</span>
                    <strong>{upcoming.length}</strong>
                  </div>

                  <div className="stat">
                    <ClipboardList size={20} />
                    <span>Upcoming deadlines</span>
                    <strong>{deadlines.length}</strong>
                  </div>

                  <div className="stat">
                    <Clock size={20} />
                    <span>Due or closing in 7 days</span>
                    <strong>{nextWeek.length}</strong>
                  </div>
                </div>

                <section className="panel">
                  <h2>Upcoming deadlines</h2>
                  <EventList items={deadlines.slice(0, 8)} />
                </section>

                <section className="panel">
                  <h2>Upcoming calendar events</h2>
                  <EventList items={upcoming.slice(0, 8)} />
                </section>
              </>
            )}

            {page === "Calendar" && (
              <section className="panel">
                <h2>Upcoming events</h2>
                <EventList items={upcoming} />
              </section>
            )}

            {page === "Assignments" && (
              <section className="panel">
                <h2>Upcoming deadlines</h2>
                <p className="empty">
                  Submission status has not been imported yet.
                </p>
                <EventList items={deadlines} />
              </section>
            )}

            {page === "Courses" && (
              <section className="panel">
                <h2>Your courses</h2>

                {courses.length === 0 && (
                  <p className="empty">
                    Course synchronization is not configured yet.
                  </p>
                )}

                {courses.map((course) => (
                  <div className="event" key={course.id}>
                    <BookOpen size={20} />

                    <div className="event-info">
                      <strong>{course.code}</strong>
                      <span>{course.name}</span>
                    </div>
                  </div>
                ))}
              </section>
            )}

            {page === "Grades" && <Grades courses={courses} />}

            {page === "Settings" && (
              <section className="panel">
                <h2>Integrations</h2>
                <div className="event">
                  <div className="event-info">
                    <strong>Brightspace calendar</strong>
                    <span>{events.length} imported events</span>
                  </div>
                </div>

                <div className="event">
                  <div className="event-info">
                    <strong>Academic account synchronization</strong>
                    <span>Not configured</span>
                  </div>
                </div>
              </section>
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;
