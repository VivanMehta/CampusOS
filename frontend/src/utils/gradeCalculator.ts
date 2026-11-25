import type { Course, GradeItem } from "../services/api";

export interface GradeResult {
  currentAverage: number | null;
  completedWeight: number;
  earnedWeight: number;
  remainingWeight: number;
  supported: boolean;
  warnings: string[];
  notes: string[];
}

function isGraded(item: GradeItem): boolean {
  return item.earned_points !== null && Number(item.max_points) > 0;
}

function getScore(item: GradeItem): number {
  return Number(item.earned_points) / Number(item.max_points);
}

export function calculateGrade(course: Course): GradeResult {
  let earnedWeight = 0;
  let completedWeight = 0;
  let totalWeight = 0;

  const warnings: string[] = [];
  const notes: string[] = [];

  for (const category of course.grade_categories) {
    if (category.excluded) continue;

    const categoryWeight = Number(category.weight);

    if (categoryWeight <= 0) continue;

    const items = course.grade_items.filter(
      (item) =>
        item.category === category.id && !item.excluded && !item.is_bonus,
    );

    if (category.highest_to_drop > 0 || category.lowest_to_drop > 0) {
      warnings.push(`${category.name} uses grade dropping rules.`);
    }

    const itemWeightTotal = items.reduce(
      (sum, item) => sum + Number(item.weight),
      0,
    );

    if (itemWeightTotal <= 0) {
      warnings.push(`${category.name} has no valid assessment weights.`);
      continue;
    }

    if (Math.abs(itemWeightTotal - 100) > 0.1) {
      notes.push(
        `${category.name}: weights normalized from ` +
          `${itemWeightTotal.toFixed(2)}% to 100%.`,
      );
    }

    totalWeight += categoryWeight;

    for (const item of items) {
      const effectiveWeight =
        (categoryWeight * Number(item.weight)) / itemWeightTotal;

      if (isGraded(item)) {
        completedWeight += effectiveWeight;
        earnedWeight += getScore(item) * effectiveWeight;
      }
    }
  }

  const independentItems = course.grade_items.filter(
    (item) => item.category === null && !item.excluded && !item.is_bonus,
  );

  for (const item of independentItems) {
    const weight = Number(item.weight);

    totalWeight += weight;

    if (isGraded(item)) {
      completedWeight += weight;
      earnedWeight += getScore(item) * weight;
    }
  }

  if (course.grade_items.some((item) => item.is_bonus && !item.excluded)) {
    warnings.push("Bonus assessments are not yet supported.");
  }

  if (Math.abs(totalWeight - 100) > 0.1) {
    warnings.push("Course weights do not total 100%.");
  }

  const supported = warnings.length === 0;

  return {
    currentAverage:
      supported && completedWeight > 0
        ? (earnedWeight / completedWeight) * 100
        : null,

    completedWeight,
    earnedWeight,
    remainingWeight: Math.max(0, 100 - completedWeight),
    supported,
    warnings,
    notes,
  };
}

export function requiredGrade(
  result: GradeResult,
  target: number,
): number | null {
  if (!result.supported || result.remainingWeight <= 0) {
    return null;
  }

  return Math.max(
    0,
    ((target - result.earnedWeight) / result.remainingWeight) * 100,
  );
}
