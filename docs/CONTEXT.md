# Munshi context
Product: a teacher sends one short message (text or voice; English, Hindi or Hinglish). Munshi turns it into attendance, class diary, homework and parent-alert drafts. Principle: AI proposes. Rules verify. The teacher confirms. The model never writes to the database.

## Pipeline
1 POST message. 2 Normalise and store raw text. 3 Gemini returns typed fields as JSON; every field carries an exact quote copied from the message, and names also carry a romanised spelling. 4 Span verifier: code finds the quote with str.find and computes [start,end) offsets; if the quote is missing or does not support the value, the field is Review. 5 Roster resolver (RapidFuzz). 6 Rule engine R1 to R9. 7 Review object returned. 8 Teacher resolves and edits. 9 POST confirm writes records plus audit_log in ONE transaction. 10 Notification drafts are generated from templates. Steps 1 to 7 never write to record tables. Never ask the model for numeric offsets.

## Field types
class (e.g. 8A), date (ISO; if absent use today and mark as assumed), stated_count (int), absent_student (one per name), topic (text), homework (text). Model field shape: {type, value, quote, roman}. roman is only for names.

## Rules (status OK, Review or Block; each result has rule_id, status, plain-English reason)
R1 quote exists and supports the value: Review
R2 class exists and the teacher is assigned to it: Block
R3 each name matches exactly one student in that class: Review, list candidates
R4 stated_count equals the number of names: Review
R5 no duplicate student in the list and none already marked for that date: Review
R6 date not in the future and a school day (not Sunday or a seeded holiday): Block
R7 topic matches the syllabus for subject and class (chapter number in range or fuzzy title match): Review
R8 marks numeric, from 0 to the maximum: Block (marks checker)
R9 no existing submission for same class, date and type: Review

## API contract
POST /api/login {teacher_id, pin} -> {token, role, teacher:{id,name,subject}}. Demo pin 1234. Roles: teacher, principal. JWT.
POST /api/messages {text, lang_hint?} -> Review object
GET /api/messages/{id}/review -> Review object
POST /api/messages/{id}/confirm {resolutions:{field_id: student_id}, edits:{field_id: value}} -> {records:{attendance:n, diary:1, homework:1}, drafts:[{id,audience,language,text}], audit_id}. Return 409 while any field is Block or any needed choice is unresolved.
GET /api/attendance?class=8A&date=YYYY-MM-DD -> [{student_id,name,roll_no,present}]
GET /api/attendance/export?class=&date=&format=csv|xlsx
POST /api/marks/upload (multipart CSV) -> {upload_id, rows, flags:[Flag]}
GET /api/marks/flags?upload_id= -> [Flag]
GET /api/audit (principal only) -> [{id,time,teacher,message_id,action,summary}]
GET /api/demo/messages -> 6 ready-made demo messages
Review object: {message_id, text, status:"ready|needs_review|blocked", llm_mode:"gemini|fallback|cached", fields:[{id,type,label,value,quote,start,end,status,reason,rule_id,candidates:[{student_id,name,roll_no}],resolved_student_id}], rule_results:[]}
Flag: {record_id,student_name,class,subject,column,observed,expected,rule,severity:"review|block",evidence,hint}

## Data
Seed from data/munshi_indian_school_marks_clean.csv: students (student_id, roll_no, name, class, section, stream). 140 students, 14 class-sections, classes 6 to 12, labels like 8A. First names repeat inside sections (for example three Kabirs in 8A): this is the name-collision demo. Generate synthetically with a fixed random seed and label as synthetic: 8 teachers with one subject each and assigned class-sections, timetable slots, syllabus chapters 1 to 12 per subject and class, a holiday list. data/munshi_error_ground_truth.csv is for evaluation scripts only; the app must never read it. Every table has school_id (single school S1).

## Tables (minimum)
school, teacher, class_section, student, subject, timetable_slot, syllabus_topic, holiday, message, extraction_field, attendance_record, diary_entry, homework, mark_entry, flag, notification_draft, audit_log.

## UI tokens
ink #0B1220, blue #1F4FD8, amber #FFB020, tint #EAF0FF, grey #475467, line #D0D5DD. Archivo 800 uppercase for headings, Inter for body. Status colours: OK green #067647, Review amber #B54708, Block red #B42318.

## Engineering rules
- LLM sits behind one interface: LLMClient.extract(text, today). Implementations: GeminiClient, RegexFallback, CachedClient. The mode is returned as llm_mode and shown in the UI.
- Temperature 0. A PROMPT_VERSION constant. JSON schema output.
- Only the message text, class label and today's date go to the model. The roster is never sent.
- Records tables are written only inside the confirm transaction.
- Type hints. pytest for the span verifier and every rule. No secrets in git.
