# Munshi — 4-Minute Video Demonstration Script

This script provides second-by-second walkthrough cues, exact inputs, narrator dialogue, UI actions, and contingency fallback procedures for demonstrating Munshi.

---

## Demonstration Metadata

- **Total Duration**: 4 Minutes (0:00 – 4:00)
- **Target Role**: Teacher Rajesh Sharma (`T01`, Mathematics) & Principal Dr. Anand Swaminathan (`P01`)
- **Key Principle**: *AI proposes. Rules verify. The teacher confirms. The model never writes to the database.*
- **Contingency Plan**: If internet connection or Gemini API slows down, toggle API mode to `mock` or set LLM mode to `Cached demo` via the TopBar switcher; the demonstration continues with 100% fidelity using pre-cached extractions.

---

## Timeline & Narration

### [0:00 – 0:30] The Problem & The Munshi Principle
- **Screen**: Munshi homepage (`http://localhost:8000` or live URL). Amber accent bar, brand logo, and the 3-step explainer (1. Send, 2. Review, 3. Confirm).
- **Narration**:
  > *"Every afternoon in Indian schools, teachers spend 30 to 45 minutes manually copying attendance into register books, drafting homework updates for parents on WhatsApp, and filling out class diaries. Many schools try using raw LLMs or voice bots, but they make critical mistakes: they hallucinate student names, guess who was absent, or silently write corrupted records to databases.*
  > *Munshi solves this with one core safety principle: **AI proposes. Rules verify. The teacher confirms. The AI model never writes to the database.** Let's see how it works."*

---

### [0:30 – 1:15] Demo 1: Clean English Attendance
- **Action**: In the composer, click the chip button: `8A: Clean English Attendance`.
- **Exact Input**:
  ```text
  8A: 2 absent - Sneha Reddy, Aditya Das. Covered Chapter 3 Linear Equations. Homework Ex 3.2.
  ```
- **Action**: Click **Send Message**.
- **Screen**: Transitions to Review screen.
- **Visuals to Highlight**:
  1. Top banner shows: **Ready to Confirm** (0 items left), badge `Gemini` (or `fallback`).
  2. Left column: Teacher message with color-coded interactive span highlights. Hovering over `"Sneha Reddy"` pulses the row on the right.
  3. Right column: Table of 6 verified entities: Class (8A), Stated Count (2), Absent Students (Sneha Reddy, Aditya Das), Topic, and Homework.
  4. Span verifier (Rule R1): Highlights show exact offsets `[start, end)`. Quotes match verbatim.
- **Narration**:
  > *"We click the clean English message and send it. Gemini extracts the structured entities. Our deterministic Span Verifier verifies that every field has a verbatim quote in the original message. Because Rajesh Sharma teaches Class 8A, both students exist on the roster, and the stated count matches, all rules pass: 0 items left, status Ready to Confirm."*

---

### [1:15 – 1:50] Demo 2: Hindi Voice & Transliteration
- **Action**: Click **Edit message in composer** (returns with kept text).
- **Action**: Click the chip button: `8A: Hindi Devanagari Script` (or click Dictate Voice in Chrome/Edge).
- **Exact Input**:
  ```text
  8A में आज 2 अनुपस्थित - स्नेहा, आदित्य। पाठ 3 पढ़ाया। गृहकार्य अभ्यास 3.2।
  ```
- **Action**: Click **Send Message**.
- **Visuals to Highlight**:
  1. Devanagari message displayed with highlighted source words.
  2. In the Entities table, `स्नेहा` is resolved via phonetic romanization to `Sneha Reddy` (MUN0052) and `आदित्य` to `Aditya Das` (MUN0002).
  3. Hindi syllabus match: `पाठ 3` matches Mathematics Chapter 3 (Linear Equations).
- **Narration**:
  > *"Now let's test a message written in Hindi Devanagari script. Teachers can also speak this directly using the voice dictation button. Notice what happens: the model extracts the Devanagari names, and our RapidFuzz resolver matches the phonetic transliteration against the Class 8A roster. Even though the teacher only typed 'स्नेहा', it accurately maps to Sneha Reddy with roll number 812."*

---

### [1:50 – 2:30] Demo 3: Three-Kabirs Ambiguity & Sunday Holiday Block
- **Action**: Click **Edit message in composer**.
- **Action**: Click the chip button: `8A: Three-Kabirs Name Collision`.
- **Exact Input**:
  ```text
  8A: 1 absent - Kabir. Covered chapter 3 Linear Equations. Homework Ex 3.2.
  ```
- **Action**: Click **Send Message**.
- **Visuals to Highlight**:
  1. Top banner switches to: **Needs Teacher Review (1 items left)**.
  2. Confirm button is **disabled**.
  3. Hovering the disabled Confirm button shows the tooltip: *"Ambiguity: Select one candidate for 'Kabir' (3 options)"*.
  4. In the table, Kabir displays three radio options:
     - `Kabir Bansal` (Roll 801)
     - `Kabir Sharma` (Roll 806)
     - `Kabir Mehta` (Roll 811)
  5. Click `Kabir Bansal`. Notice the banner transitions in real-time to **Ready to Confirm (0 items left)**, and the Confirm button unlocks.
- **Narration**:
  > *"Here is our core safety test: In Class 8A, there are three boys named Kabir: roll 801, 806, and 811. The teacher simply wrote 'Kabir'. An ordinary LLM would silently hallucinate one. Munshi's Rule R3 strictly refuses to guess. The Confirm button is locked, and the teacher is presented with the three options. Only when the teacher selects Kabir Bansal does the system transition to Ready to Confirm."*
- **Action (Sunday Block)**: Click Edit message in composer, select `8A: Sunday Date Verification`:
  ```text
  8A: 1 absent - Sneha Reddy on 2026-11-15. Covered chapter 3 Linear Equations.
  ```
- **Narration**:
  > *"Similarly, when a teacher accidentally enters attendance for a Sunday holiday (2026-11-15), Rule R6 fires a Block discrepancy. The button locks with 'Submission Blocked'—no transaction can occur on non-school days."*

---

### [2:30 – 2:50] Confirmation & Parent Notification Drafts
- **Action**: Return to the resolved Three-Kabirs review screen (or Clean English screen) and click **Confirm and create records**.
- **Screen**: Success Panel appears with an animated green checkmark.
- **Visuals to Highlight**:
  1. **Audit ID**: UUID transaction logged.
  2. **Created Records**: Attendance Records (140), Class Diary Entry (1), Homework Task (1).
  3. **Notification Drafts**: Bilingual tabs (English and हिन्दी).
  4. Click the **हिन्दी** toggle to show the generated parent alert in Hindi:
     > *"प्रिय अभिभावक, आपका बच्चा Kabir Bansal (रोल नं 801) दिनांक 2026-11-24 को कक्षा 8A में अनुपस्थित दर्ज किया गया है..."*
  5. Click **Records** tab &rarr; select Class 8A to show the saved attendance ledger.
- **Narration**:
  > *"When the teacher confirms, all records commit in one atomic database transaction. Munshi instantly generates bilingual notification drafts for parents in English and Hindi, along with a daily summary for the principal. In the Records tab, the attendance is permanently recorded."*

---

### [2:50 – 3:30] Module A: Marks Pre-Flight Checker
- **Action**: Click the **Marks** tab in the navigation bar.
- **Visuals to Highlight**:
  1. Header: *Marks Pre-Flight Checker (Module A)*.
  2. Summary strip: **703 Rows Checked**, **28 Total Flags** (20 Blocks, 8 Reviews).
  3. Filter buttons: *All (28)*, *Blocks (20)*, *Reviews (8)*.
  4. Scroll down to show an evidence card:
     - **Student**: `REC0553`, Class 12A, Physics.
     - **Rule**: `theory_above_max`.
     - **Observed**: `71.0` (Expected: Max 70).
     - **Evidence**: *"Theory marks 71.0 exceeds maximum allowed 70 for Class 12A Physics."*
  5. Test the local toggle: Click **Mark as checked** on the card &rarr; changes to green **Checked by teacher**.
- **Narration**:
  > *"Now let's switch to Module A: the Marks Pre-Flight Checker. Teachers upload their term exam spreadsheets before submission. Here we ran our 703-row error benchmark. Munshi detected all 13 injected data errors with 100% recall. Each card provides full transparency: observed score, expected limit, rule name, and actionable hint. Teachers can verify each flag locally with a single click."*

---

### [3:30 – 3:50] Results, Governance & Principal Audit
- **Action**: Switch Teacher dropdown to `Dr. Anand Swaminathan (Principal)`.
- **Action**: Click the **Audit** tab (visible only to principals).
- **Visuals to Highlight**:
  - Immutable ledger row showing teacher `Rajesh Sharma`, action `confirm`, class `8A`, timestamp, and before/after state diffs.
- **Narration**:
  > *"Finally, we log in as Principal Dr. Anand Swaminathan. The Audit ledger shows every confirmed update with full timestamped before-and-after provenance. In our benchmark evaluation across 60 messages in English, Hindi, and Hinglish, Munshi achieved 99.8% macro F1, 100% grounding, and 0 silent name guesses."*

---

### [3:50 – 4:00] Closing
- **Screen**: Munshi homepage / GitHub repository.
- **Narration**:
  > *"Munshi bridges the gap between AI speed and school record accuracy: AI proposes, rules verify, and teachers confirm. Thank you."*

---

## Contingency & Fallback Plan

| Potential Issue | Immediate Action | Demo Continuity |
|---|---|---|
| **Gemini API Network Timeout / Error** | None needed; `CompositeExtractionClient` automatically cascades to `RegexFallback`. | Point out the top badge: *"Notice Munshi automatically switched to Fallback parser without failing the teacher's workflow."* |
| **Offline / No Internet at Venue** | Click the **Live** badge in the TopBar to switch to **Mock** mode. | Uses pre-cached extractions and mock responses instantly with zero network dependencies. |
| **Microphone blocked by browser** | Use the 6 clickable demo message chips on the composer screen. | The demo chips contain the exact benchmark test sentences. |
