import { useState } from "react";
import { GraduationCap, ChevronDown } from "lucide-react";
import type { Course, GradeItem } from "../services/api";
import { calculateGrade, requiredGrade } from "../utils/gradeCalculator";

interface Props {
  courses: Course[];
}

export default function Grades({ courses }: Props) {
  const [selected, setSelected] = useState<number | null>(null);
  const [target, setTarget] = useState(50);

  const available = courses.filter((course) => course.grade_items.length > 0);

  const course = available.find((c) => c.id === selected) ?? available[0];

  function renderGrade(item: GradeItem) {
    const percentage =
      item.earned_points !== null && Number(item.max_points) > 0
        ? (Number(item.earned_points) / Number(item.max_points)) * 100
        : null;

    const color =
      percentage === null
        ? "#71717a"
        : percentage >= 80
          ? "#4ade80"
          : percentage >= 50
            ? "#facc15"
            : "#f87171";

    return (
      <tr key={item.id}>
        <td>{item.name}</td>

        <td>
          {item.earned_points === null
            ? "—"
            : Number(item.earned_points).toFixed(2)}
          {" / "}
          {Number(item.max_points)}
        </td>

        <td>{Number(item.weight)}%</td>

        <td style={{ color }}>
          {percentage === null ? "Ungraded" : `${percentage.toFixed(1)}%`}
        </td>

        <td>{item.displayed_grade || "—"}</td>
      </tr>
    );
  }

  if (!course) {
    return (
      <section className="panel">
        <h2>Grade tracker</h2>
        <p className="empty">No grade data has been imported.</p>
      </section>
    );
  }

  const graded = course.grade_items.filter(
    (item) => item.earned_points !== null,
  );

  const result = calculateGrade(course);
  const required = requiredGrade(result, target);

  return (
    <div className="grades-page">
      <div className="course-selector">
        <GraduationCap size={20} />

        <select
          value={course.id}
          onChange={(e) => setSelected(Number(e.target.value))}
        >
          {available.map((c) => (
            <option key={c.id} value={c.id}>
              {c.code} — {c.name}
            </option>
          ))}
        </select>

        <ChevronDown size={16} />
      </div>

      <div className="stats">
        <div className="stat">
          <span>Grade items</span>
          <strong>{course.grade_items.length}</strong>
        </div>

        <div className="stat">
          <span>Graded assessments</span>
          <strong>{graded.length}</strong>
        </div>

        <div className="stat">
          <span>Ungraded assessments</span>
          <strong>{course.grade_items.length - graded.length}</strong>
        </div>

        <div className="stat">
          <span>Estimated current average</span>

          <strong>
            {result.currentAverage === null
              ? "—"
              : `${result.currentAverage.toFixed(1)}%`}
          </strong>

          <small>
            {result.supported
              ? `${result.completedWeight.toFixed(1)}% of course graded`
              : "Calculation unavailable"}
          </small>
        </div>
      </div>

      {result.notes.length > 0 && (
        <section className="panel">
          <h2>Grading information</h2>

          {result.notes.map((note) => (
            <p className="empty" key={note}>
              {note}
            </p>
          ))}
        </section>
      )}

      {result.warnings.length > 0 && (
        <section className="panel">
          <h2>Calculation limitations</h2>

          {result.warnings.map((warning) => (
            <p className="empty" key={warning}>
              {warning}
            </p>
          ))}
        </section>
      )}

      {result.supported && (
        <section className="panel predictor">
          <h2>Grade predictor</h2>

          <p className="empty">
            Calculate the average you need on all remaining assessments to reach
            your desired final grade.
          </p>

          <div className="predictor-control">
            <span>Target final grade</span>
            <strong>{target}%</strong>
          </div>

          <input
            type="range"
            min="0"
            max="100"
            value={target}
            onChange={(e) => setTarget(Number(e.target.value))}
          />

          <div className="predictor-results">
            <div>
              <span>Course weight graded</span>
              <strong>{result.completedWeight.toFixed(1)}%</strong>
            </div>

            <div>
              <span>Remaining course weight</span>
              <strong>{result.remainingWeight.toFixed(1)}%</strong>
            </div>

            <div>
              <span>Required remaining average</span>

              <strong
                style={{
                  color:
                    required === null
                      ? "#71717a"
                      : required > 100
                        ? "#f87171"
                        : "#4ade80",
                }}
              >
                {required === null ? "—" : `${required.toFixed(1)}%`}
              </strong>
            </div>
          </div>

          {required !== null && required > 100 && (
            <p className="empty">
              This target is not achievable under the current grading
              assumptions.
            </p>
          )}

          {required === 0 && (
            <p className="empty">
              You have already earned enough weighted marks to reach this target
              under the current assumptions.
            </p>
          )}
        </section>
      )}

      {course.grade_categories.map((category) => {
        const items = course.grade_items.filter(
          (item) => item.category === category.id,
        );

        return (
          <section className="panel" key={category.id}>
            <div className="category-header">
              <h2>{category.name}</h2>

              <span className="category-weight">
                {Number(category.weight)}% of course
              </span>
            </div>

            <div className="table-wrapper">
              <table className="grade-table">
                <thead>
                  <tr>
                    <th>Assessment</th>
                    <th>Points</th>
                    <th>Category weight</th>
                    <th>Percentage</th>
                    <th>Grade</th>
                  </tr>
                </thead>

                <tbody>{items.map(renderGrade)}</tbody>
              </table>
            </div>
          </section>
        );
      })}

      {course.grade_items.some((item) => item.category === null) && (
        <section className="panel">
          <h2>Independent assessments</h2>

          <div className="table-wrapper">
            <table className="grade-table">
              <thead>
                <tr>
                  <th>Assessment</th>
                  <th>Points</th>
                  <th>Weight</th>
                  <th>Percentage</th>
                  <th>Grade</th>
                </tr>
              </thead>

              <tbody>
                {course.grade_items
                  .filter((item) => item.category === null)
                  .map(renderGrade)}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
