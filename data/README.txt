MUNSHI — INDIAN SCHOOL MARKS DATASET (SYNTHETIC)

Purpose
- Demo/testing data for Munshi's Marks Pre-flight Checker.
- School classes 6–12 only.
- Indian-style names, class/section/roll numbers and subject combinations.
- This is synthetic/fictitious data, NOT real student data and NOT an official CBSE/State Board dataset.

Files
1. munshi_indian_school_marks_clean.csv
   Clean baseline dataset. Use this to test normal import and validation.

2. munshi_indian_school_marks_error_test.csv
   Separate test copy containing deliberately injected data-quality issues.
   Use this to test detection. Do not treat injected values as correct.

3. munshi_error_ground_truth.csv
   Expected error labels and affected record IDs. Keep this as the evaluator/reference file;
   do not expose it to the checker during blind testing.

Schema notes
- One row represents one student's marks in one subject.
- Classes 6–10: English, Hindi, Mathematics, Science, Social Science.
- Classes 11–12: stream-specific subject sets (Science, Commerce, Humanities).
- Theory is out of 80; internal assessment is out of 20; total is out of 100.
- The 80+20 split is a demo convention for this synthetic dataset, not a claim about every Indian school's assessment policy.
- Academic year: 2026–27; exam: Half-Yearly.

Suggested validation checks
- Marks must be numeric and within their maximum.
- Missing marks should be flagged.
- total_marks should equal theory_marks + internal_marks.
- Duplicate student/class/exam/subject records should be flagged.
- Do not auto-correct, overwrite or send anything without teacher confirmation.
