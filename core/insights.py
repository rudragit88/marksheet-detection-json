import os
import json

OUTPUT_FOLDER = "output"

def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_student(flat_data):
    insights = []

    subjects = {}
    total_marks = 0
    max_total = 0
    percentage = None

    # ✅ Step 1: Extract marks for subjects
    for key, value in flat_data.items():
        try:
            marks = float(value)
            key_lower = key.lower()

            # Exclude common non-subject fields
            if any(term in key_lower for term in ["percent", "cgpa", "sgpa", "total", "backlog", "gpa"]):
                continue

            # Assume remaining numeric fields are subjects
            subjects[key] = marks
        except (ValueError, TypeError):
            continue

    # ✅ Step 2: Extract total, max total, percentage
    for key, value in flat_data.items():
        key_lower = key.lower()
        try:
            val = float(value)
            if "percent" in key_lower:
                percentage = val
            elif "total" in key_lower and "max" not in key_lower:
                total_marks = val
            elif "max" in key_lower:
                max_total = val
        except (ValueError, TypeError):
            continue

    # ✅ Step 3: Weakest subject
    if subjects:
        weakest_subject = min(subjects, key=subjects.get)
        weakest_mark = subjects[weakest_subject]
        insights.append(f"📉 Weakest subject: **{weakest_subject}** ({weakest_mark} marks)")

    # ✅ Step 4: Suggestion to reach 90%
    if total_marks and max_total:
        target_total = 0.9 * max_total
        if total_marks < target_total:
            diff = target_total - total_marks
            insights.append(f"🎯 You need **{diff:.1f}** more marks to reach **90%** overall.")
    elif percentage is None:
        insights.append("⚠️ Total or max marks not found to calculate gap to 90%.")

    # ✅ Step 5: Performance band
    if percentage is not None:
        if percentage >= 90:
            insights.append("🌟 Excellent performance! Keep it up.")
        elif percentage >= 75:
            insights.append("👍 Good job, aim even higher!")
        elif percentage >= 60:
            insights.append("🙂 Decent performance. Focus on weaker areas.")
        else:
            insights.append("⚠️ Needs improvement. Seek help in weak subjects.")
    else:
        insights.append("ℹ️ Percentage not found in data.")

    return insights

def generate_suggestions(json_data: dict) -> str:
    """
    Wrapper to get a string summary of suggestions for a single JSON result.
    """
    insights = analyze_student(json_data)
    return "\n".join(insights) if insights else "No insights available."

def generate_insights_for_all():
    """
    CLI-style output for all JSONs in the output folder.
    """
    files = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".json")]

    if not files:
        print("No JSON files found for insights.")
        return

    for file in files:
        path = os.path.join(OUTPUT_FOLDER, file)
        data = load_json_file(path)
        insights = analyze_student(data)

        print(f"\n📝 Insights for {file}:")
        for line in insights:
            print(f" - {line}")

# ✅ CLI usage
if __name__ == "__main__":
    generate_insights_for_all()
