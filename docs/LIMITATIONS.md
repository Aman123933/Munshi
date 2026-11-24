# Munshi — System Limitations & Constraints

This document outlines the known boundaries, trade-offs, and deliberate non-goals of the Munshi prototype.

---

## 1. Fixed Message Scope & Schema
- **Supported Updates**: Munshi is strictly designed for **daily classroom updates**: class label, absent students, topic covered, and assigned homework.
- **Unsupported Topics**: The pipeline intentionally does not process ad-hoc administrative requests (e.g., fee collection inquiries, permission slips, bus schedule changes, or discipline incident reports). Messages containing non-academic requests are flagged as ambiguous or rejected by syllabus and schema rules.

## 2. No Direct School ERP Link
- **Standalone Prototype**: Munshi does not have direct live bidirectional API integrations with commercial School Management Information Systems (e.g., Fedena, Vidyalaya, PowerSchool).
- **Export Workaround**: Attendance and marks can be exported to standardized CSV/XLSX spreadsheets for manual import into existing school databases.

## 3. Synthetic Data Statement
- **No Real Student Data**: To protect child privacy and adhere to data protection standards, all student names (`MUN0001`–`MUN0140`), marks, roll numbers, and teacher profiles in this repository are entirely synthetic.
- **Roster Characteristics**: The 140 synthetic student profiles and repeating name patterns (e.g., three Kabirs in 8A) were generated specifically to benchmark ambiguity resolution under controlled conditions.

## 4. Benchmark Test-Set Scale
- **Harness Size**: The message evaluation harness consists of 60 curated messages (20 English, 20 Hindi, 20 Hinglish) and 703 marks rows.
- **Coverage**: While this test set rigorously probes edge cases (name collisions, count mismatches, calendar holidays, unassigned teachers), it does not cover every Indian regional dialect, phonetic transliteration variant, or handwritten marksheet defect.

## 5. Free-Tier Hosting Sleep & Cold Starts
- **Render Inactivity Spindown**: When hosted on Render's free tier, the container spins down after 15 minutes of inactivity.
- **Cold-Start Delay**: The first inbound request after sleep incurs a 30–50 second container wakeup delay. Although the frontend notifies the user (*"Waking the server, this can take up to a minute"*), real-world school operations require persistent compute tiers.
- **Ephemeral Storage**: Free-tier restarts wipe local SQLite files; the database is re-seeded on startup. Production deployments require managed PostgreSQL.

## 6. Alerts Are Drafts Only (No Outbound Gateway)
- **Drafts, Not Dispatches**: Munshi produces bilingual notification drafts (English and Hindi) for parents and the principal upon confirmation.
- **No SMS/WhatsApp Gateway**: Munshi does not automatically dispatch live SMS or WhatsApp messages. Outbound alerts remain in `draft` status for review and manual copy, preventing accidental mass-messaging during testing.

## 7. Hindi & Hinglish Transcription Variability
- **Speech Recognition Variance**: The Web Speech API's accuracy on Indian accented Hindi or mixed Hinglish fluctuates significantly depending on microphone quality, ambient classroom background noise, and dialect.
- **Spelling Nuances**: While the span verifier and RapidFuzz roster resolver tolerate slight spelling variations, heavily distorted phonetic spellings or non-standard romanizations may fail quote verification, intentionally routing the message to teacher review rather than guessing silently.
