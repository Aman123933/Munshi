import random
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.models import (
    ClassSection,
    Holiday,
    School,
    Student,
    Subject,
    SyllabusTopic,
    Teacher,
    TeacherAssignment,
    TimetableSlot,
)

SUBJECT_CHAPTERS: Dict[str, List[str]] = {
    "Mathematics": [
        "Number Systems & Real Numbers",
        "Polynomials & Algebraic Expressions",
        "Linear Equations in Two Variables",
        "Quadratic Equations",
        "Arithmetic Progressions",
        "Coordinate Geometry",
        "Triangles & Congruence",
        "Introduction to Trigonometry",
        "Circles & Tangents",
        "Constructions & Mensuration",
        "Surface Areas and Volumes",
        "Statistics & Probability",
    ],
    "Science": [
        "Chemical Reactions and Equations",
        "Acids, Bases and Salts",
        "Metals and Non-metals",
        "Carbon and its Compounds",
        "Periodic Classification of Elements",
        "Life Processes & Cellular Respiration",
        "Control and Coordination",
        "How do Organisms Reproduce?",
        "Heredity and Evolution",
        "Light: Reflection and Refraction",
        "Electricity and Magnetic Effects",
        "Our Environment and Natural Resources",
    ],
    "Physics": [
        "Physical World and Measurement",
        "Kinematics: Motion in a Straight Line",
        "Laws of Motion and Friction",
        "Work, Energy, and Power",
        "Rotational Motion and System of Particles",
        "Gravitation and Planetary Motion",
        "Mechanical Properties of Solids and Fluids",
        "Thermal Properties of Matter",
        "Thermodynamics and Heat Engines",
        "Kinetic Theory of Gases",
        "Oscillations and Simple Harmonic Motion",
        "Waves and Sound Propagation",
    ],
    "Chemistry": [
        "Some Basic Concepts of Chemistry",
        "Structure of Atom",
        "Classification of Elements and Periodicity",
        "Chemical Bonding and Molecular Structure",
        "States of Matter: Gases and Liquids",
        "Chemical Thermodynamics",
        "Equilibrium and Acid-Base Theories",
        "Redox Reactions",
        "Hydrogen and Its Compounds",
        "s-Block and p-Block Elements",
        "Organic Chemistry: Basic Principles",
        "Hydrocarbons and Environmental Chemistry",
    ],
    "Biology": [
        "The Living World and Biological Classification",
        "Plant Kingdom and Morphology",
        "Animal Kingdom and Anatomy",
        "Cell: The Unit of Life",
        "Biomolecules and Enzymes",
        "Cell Cycle and Cell Division",
        "Transport in Plants and Mineral Nutrition",
        "Photosynthesis in Higher Plants",
        "Respiration in Plants",
        "Plant Growth and Development",
        "Human Digestion, Breathing, and Circulation",
        "Neural Control and Chemical Coordination",
    ],
    "English": [
        "Reading Comprehension and Critical Analysis",
        "Narrative Prose and Short Fiction",
        "Classical and Modern Poetry",
        "Dramatic Texts and Play Scripts",
        "Grammar: Tenses, Modals and Voice",
        "Grammar: Clauses and Reported Speech",
        "Formal Letter and Official Email Writing",
        "Article, Essay, and Speech Composition",
        "Notice, Circular and Report Writing",
        "Idiomatic Expressions and Vocabulary in Context",
        "Literary Devices, Tone and Perspective",
        "Debate, Public Discourse and Discussion",
    ],
    "Hindi": [
        "वर्ण विचार, वर्तनी एवं उच्चारण",
        "शब्द रचना: संधि, उपसर्ग एवं प्रत्यय",
        "गद्य खंड: यथार्थवादी कहानियाँ (प्रेमचंद)",
        "पद्य खंड: कबीर, तुलसी एवं सूरदास के पद",
        "समास एवं पद-परिचय",
        "वाक्य शुद्धि, मुहावरे एवं लोकोक्तियाँ",
        "पत्र लेखन एवं औपचारिक संवाद",
        "निबंध एवं समसामयिक विचार विमर्श",
        "छायावादी कविता: प्रकृति एवं मानवीय चेतना",
        "अपठित गद्यांश एवं सारांश लेखन",
        "रस, छंद और प्रमुख अलंकार",
        "संवाद लेखन, विज्ञापन एवं संक्षेपण",
    ],
    "Social Science": [
        "The Rise of Nationalism in Europe and India",
        "The Making of a Global World",
        "Resources and Sustainable Development",
        "Forest, Wildlife and Water Resources",
        "Agriculture and Cropping Patterns",
        "Minerals, Energy Resources and Manufacturing",
        "Lifelines of National Economy",
        "Power Sharing and Federalism",
        "Democracy, Diversity, and Political Parties",
        "Outcomes of Democracy and Popular Struggles",
        "Development and Sectors of Indian Economy",
        "Money, Credit, and Globalisation",
    ],
    "History": [
        "Early Societies and Mesopotamian Civilization",
        "Empires Across Three Continents",
        "Nomadic Empires: The Mongols",
        "The Three Orders: Feudal Society",
        "Changing Cultural Traditions and Renaissance",
        "Confrontation of Cultures in the Americas",
        "Paths to Modernization: East Asia",
        "The Industrial Revolution",
        "Displacing Indigenous Peoples",
        "Colonialism and the Countryside",
        "Rebels and the Raj: The 1857 Revolt",
        "Framing the Indian Constitution",
    ],
    "Geography": [
        "Geography as an Integrating Discipline",
        "The Origin and Evolution of the Earth",
        "Interior of the Earth and Plate Tectonics",
        "Geomorphic Processes and Landforms",
        "Atmospheric Composition and Solar Radiation",
        "Atmospheric Circulation and Weather Systems",
        "Water in the Atmosphere and Precipitation",
        "Oceans: Relief, Temperature, and Salinity",
        "Movements of Ocean Water: Waves and Tides",
        "Life on the Earth: Biomes and Ecology",
        "India: Location, Physiography, and Drainage",
        "Climate, Natural Vegetation, and Soil of India",
    ],
    "Political Science": [
        "Constitution: Why and How? Philosophy of Constitution",
        "Rights and Fundamental Duties in the Indian Constitution",
        "Election and Representation Systems",
        "Executive, Legislature, and Judiciary in India",
        "Federalism and Local Governments",
        "Political Theory: An Introduction to Freedom",
        "Equality and Social Justice",
        "Rights, Citizenship, and Nationalism",
        "Secularism and Religious Pluralism",
        "Peace, Non-Violence, and Development",
        "Challenges to Democratic Consolidation",
        "Global Politics and Contemporary World Order",
    ],
    "Economics": [
        "Introduction to Microeconomics and Central Problems",
        "Consumer Behaviour and Utility Analysis",
        "Theory of Demand and Elasticity",
        "Production, Costs, and Revenue Functions",
        "Market Forms and Price Determination",
        "National Income Accounting and Aggregates",
        "Money and Banking Systems",
        "Determination of Income and Employment",
        "Government Budget and the Fiscal Economy",
        "Balance of Payments and Foreign Exchange",
        "Indian Economic Development on Eve of Independence",
        "Economic Reforms, Poverty, and Sustainable Development",
    ],
    "Accountancy": [
        "Introduction to Accounting and Basic Concepts",
        "Theory Base of Accounting and Standards",
        "Recording of Transactions: Journal and Ledger",
        "Bank Reconciliation Statement",
        "Trial Balance and Rectification of Errors",
        "Depreciation, Provisions, and Reserves",
        "Bills of Exchange and Promissory Notes",
        "Financial Statements of Sole Proprietorship",
        "Accounts from Incomplete Records",
        "Accounting for Partnership Firms: Fundamentals",
        "Reconstitution: Admission and Retirement of Partner",
        "Company Accounts: Issue of Shares and Debentures",
    ],
    "Business Studies": [
        "Nature and Purpose of Business",
        "Forms of Business Organisation",
        "Public, Private and Global Enterprises",
        "Business Services: Banking, Insurance, Transport",
        "Emerging Modes of Business and E-Commerce",
        "Social Responsibilities of Business and Ethics",
        "Sources of Business Finance",
        "Small Business and Entrepreneurship",
        "Internal Trade and Wholesale-Retail Logistics",
        "International Trade: Export-Import Procedures",
        "Principles and Functions of Management",
        "Financial Markets, Marketing, and Consumer Protection",
    ],
}


def get_clean_dataset_path() -> Path:
    current = Path(__file__).resolve()
    for parent in [current.parent.parent.parent, current.parent.parent]:
        candidate = parent / "data" / "munshi_indian_school_marks_clean.csv"
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Could not find data/munshi_indian_school_marks_clean.csv")


def seed_database(db: Session = None, force: bool = False) -> Dict:
    """
    Seed database idempotently.
    Returns summary statistics and collision reports.
    """
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True

    try:
        # Create all tables if they don't exist
        Base.metadata.create_all(bind=engine)

        existing_students = db.query(Student).count()
        if existing_students > 0 and not force:
            # Already seeded; return report of existing data
            return generate_seed_report(db, printed=False)

        if force:
            # Clear seed tables in reverse dependency order
            for model in [
                TimetableSlot,
                SyllabusTopic,
                Holiday,
                TeacherAssignment,
                Student,
                Teacher,
                ClassSection,
                Subject,
                School,
            ]:
                db.query(model).delete()
            db.commit()

        # Fixed random seed for synthetic data generation
        rnd = random.Random(42)

        # 1. School (S1)
        school = db.query(School).filter_by(school_id="S1").first()
        if not school:
            school = School(
                school_id="S1",
                name="Delhi Public School, R.K. Puram",
                created_at=datetime.now(timezone.utc),
            )
            db.add(school)
            db.flush()

        # 2. Read Clean Dataset
        csv_path = get_clean_dataset_path()
        df = pd.read_csv(csv_path)

        # Unique Subjects from Clean Dataset
        unique_subjects = sorted(df["subject"].dropna().unique().tolist())
        subject_map = {}
        for subj_name in unique_subjects:
            subj = db.query(Subject).filter_by(name=subj_name).first()
            if not subj:
                subj = Subject(
                    school_id="S1",
                    name=subj_name,
                    code=subj_name[:4].upper(),
                    is_synthetic=False,
                )
                db.add(subj)
                db.flush()
            subject_map[subj_name] = subj

        # Class Sections (14 sections: 6A..12B)
        class_sec_df = (
            df[["class", "section", "stream"]].drop_duplicates().sort_values(["class", "section"])
        )
        section_map = {}
        for _, row in class_sec_df.iterrows():
            c_num = int(row["class"])
            s_name = str(row["section"]).strip()
            label = f"{c_num}{s_name}"
            stream_val = str(row["stream"]).strip() if pd.notna(row["stream"]) else "General"
            cs = db.query(ClassSection).filter_by(label=label).first()
            if not cs:
                cs = ClassSection(
                    school_id="S1",
                    class_num=c_num,
                    section=s_name,
                    label=label,
                    stream=stream_val,
                    is_synthetic=False,
                )
                db.add(cs)
                db.flush()
            section_map[label] = cs

        # Students (140 unique students)
        students_df = df[
            ["student_id", "roll_no", "student_name", "class", "section", "stream"]
        ].drop_duplicates()
        for _, row in students_df.iterrows():
            sid = str(row["student_id"]).strip()
            sname = str(row["student_name"]).strip()
            first_name = sname.split()[0]
            label = f"{int(row['class'])}{str(row['section']).strip()}"
            cs = section_map[label]
            stream_val = str(row["stream"]).strip() if pd.notna(row["stream"]) else None

            existing_s = db.query(Student).filter_by(student_id=sid).first()
            if not existing_s:
                st = Student(
                    school_id="S1",
                    student_id=sid,
                    roll_no=int(row["roll_no"]),
                    name=sname,
                    first_name=first_name,
                    class_section_id=cs.id,
                    class_label=label,
                    stream=stream_val,
                    is_synthetic=False,
                    created_at=datetime.now(timezone.utc),
                )
                db.add(st)
        db.flush()

        # 3. Synthetic Teachers (8 teachers with 1 subject each, assigned to 2-3 class sections each)
        teachers_data = [
            ("T01", "Rajesh Sharma", "Mathematics", ["8A", "8B", "9A"]),
            ("T02", "Sunita Verma", "English", ["8A", "9B", "10A"]),
            ("T03", "Vikram Malhotra", "Science", ["7A", "8A", "10B"]),
            ("T04", "Meenakshi Sundaram", "Social Science", ["7B", "8A", "9A"]),
            ("T05", "Anita Gupta", "Hindi", ["6A", "6B", "8A"]),
            ("T06", "Pradeep Joshi", "Physics", ["11A", "12A"]),
            ("T07", "Neha Kapoor", "Chemistry", ["11B", "12B"]),
            ("T08", "Ramesh Iyer", "Economics", ["11A", "12B"]),
        ]

        for tid, tname, tsubj, assigned_classes in teachers_data:
            teacher = db.query(Teacher).filter_by(teacher_id=tid).first()
            if not teacher:
                teacher = Teacher(
                    school_id="S1",
                    teacher_id=tid,
                    name=tname,
                    subject=tsubj,
                    role="teacher",
                    pin="1234",
                    is_synthetic=True,
                    created_at=datetime.now(timezone.utc),
                )
                db.add(teacher)
                db.flush()

                for cl in assigned_classes:
                    assign = TeacherAssignment(
                        school_id="S1",
                        teacher_id=tid,
                        class_label=cl,
                        is_synthetic=True,
                    )
                    db.add(assign)

        # One Principal user (role: principal)
        principal = db.query(Teacher).filter_by(teacher_id="P01").first()
        if not principal:
            principal = Teacher(
                school_id="S1",
                teacher_id="P01",
                name="Dr. Anand Swaminathan",
                subject=None,
                role="principal",
                pin="1234",
                is_synthetic=True,
                created_at=datetime.now(timezone.utc),
            )
            db.add(principal)
        db.flush()

        # 4. Timetable Slots (6 periods, Monday to Saturday for each class-section)
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        all_class_labels = sorted(section_map.keys())

        # Precompute teacher assignment lookup
        class_teachers = {}
        for cl in all_class_labels:
            assigned = (
                db.query(Teacher)
                .join(TeacherAssignment)
                .filter(TeacherAssignment.class_label == cl)
                .all()
            )
            class_teachers[cl] = assigned if assigned else db.query(Teacher).filter_by(role="teacher").all()

        for cl in all_class_labels:
            avail_teachers = class_teachers[cl]
            for day in days:
                for period in range(1, 7):
                    # Deterministic slot assignment per day/period
                    t_idx = (days.index(day) * 6 + period + all_class_labels.index(cl)) % len(avail_teachers)
                    t_assigned = avail_teachers[t_idx]
                    slot = TimetableSlot(
                        school_id="S1",
                        class_label=cl,
                        day_of_week=day,
                        period=period,
                        subject=t_assigned.subject or "General Studies",
                        teacher_id=t_assigned.teacher_id,
                        is_synthetic=True,
                    )
                    db.add(slot)
        db.flush()

        # 5. Syllabus Topics (Chapters 1 to 12 for all subjects across classes 6 to 12)
        classes = list(range(6, 13))
        for c_num in classes:
            for subj_name, chapters in SUBJECT_CHAPTERS.items():
                for ch_no, ch_title in enumerate(chapters, start=1):
                    topic = SyllabusTopic(
                        school_id="S1",
                        class_num=c_num,
                        subject=subj_name,
                        chapter_no=ch_no,
                        title=ch_title,
                        is_synthetic=True,
                    )
                    db.add(topic)
        db.flush()

        # 6. Holidays (Every Sunday up to 31 Dec 2026 + 3 invented dates)
        start_date = date(2026, 1, 1)
        end_date = date(2026, 12, 31)
        curr = start_date
        while curr <= end_date:
            if curr.weekday() == 6:  # Sunday
                h_iso = curr.isoformat()
                if not db.query(Holiday).filter_by(date=h_iso).first():
                    db.add(
                        Holiday(
                            school_id="S1",
                            date=h_iso,
                            name="Sunday Holiday",
                            is_synthetic=True,
                        )
                    )
            curr += timedelta(days=1)

        # 3 Invented non-Sunday dates
        invented_holidays = [
            ("2026-04-14", "Spring Festival & Founder's Holiday"),  # Tuesday
            ("2026-08-15", "Independence Day Celebration Holiday"), # Saturday
            ("2026-10-02", "Gandhi Jayanti Peace Holiday"),          # Friday
        ]
        for h_date, h_name in invented_holidays:
            if not db.query(Holiday).filter_by(date=h_date).first():
                db.add(
                    Holiday(
                        school_id="S1",
                        date=h_date,
                        name=h_name,
                        is_synthetic=True,
                    )
                )

        db.commit()

        # Generate and print the seed report
        report = generate_seed_report(db, printed=True)
        return report

    finally:
        if should_close:
            db.close()


def generate_seed_report(db: Session, printed: bool = True) -> Dict:
    """Computes and optionally prints the database seed report with name collision details."""
    student_count = db.query(Student).count()
    class_count = db.query(ClassSection).count()
    teacher_count = db.query(Teacher).filter(Teacher.role == "teacher").count()
    principal_count = db.query(Teacher).filter(Teacher.role == "principal").count()
    subject_count = db.query(Subject).count()
    slot_count = db.query(TimetableSlot).count()
    topic_count = db.query(SyllabusTopic).count()
    holiday_count = db.query(Holiday).count()

    # Query students to calculate collisions
    students = db.query(Student).all()
    records = [
        {
            "student_id": s.student_id,
            "first_name": s.first_name,
            "name": s.name,
            "section_label": s.class_label,
        }
        for s in students
    ]
    df_st = pd.DataFrame(records)

    collision_list: List[Tuple[str, str, int]] = []
    if not df_st.empty:
        grouped = (
            df_st.groupby(["section_label", "first_name"])
            .size()
            .reset_index(name="count")
        )
        coll_df = grouped[grouped["count"] > 1].sort_values(
            ["count", "section_label", "first_name"], ascending=[False, True, True]
        )
        for _, row in coll_df.iterrows():
            collision_list.append((str(row["first_name"]), str(row["section_label"]), int(row["count"])))

    report = {
        "student_count": student_count,
        "class_section_count": class_count,
        "teacher_count": teacher_count,
        "principal_count": principal_count,
        "subject_count": subject_count,
        "timetable_slot_count": slot_count,
        "syllabus_topic_count": topic_count,
        "holiday_count": holiday_count,
        "collision_count": len(collision_list),
        "collisions": collision_list,
    }

    if printed:
        print("\n" + "=" * 50)
        print("           MUNSHI DATABASE SEED REPORT")
        print("=" * 50)
        print(f"School ID:            S1 (Delhi Public School, R.K. Puram)")
        print(f"Class-Sections:       {class_count}")
        print(f"Students:             {student_count}")
        print(f"Teachers:             {teacher_count} (+ {principal_count} Principal)")
        print(f"Subjects:             {subject_count}")
        print(f"Timetable Slots:      {slot_count} (6 periods x Mon-Sat)")
        print(f"Syllabus Topics:      {topic_count} (12 chapters per subject)")
        print(f"Holidays:             {holiday_count} (Sundays + 3 synthetic)")
        print("-" * 50)
        print("FIRST-NAME COLLISIONS PER SECTION (DEMO HIGHLIGHTS):")
        for idx, (first_name, sec, count) in enumerate(collision_list, start=1):
            star = " ⭐ [DEMO]" if sec == "8A" and first_name == "Kabir" else ""
            print(f"  {idx:2d}. {first_name:10s} in {sec:4s}: {count} students{star}")
        print(f"Total collision groups detected: {len(collision_list)}")
        print("=" * 50 + "\n")

    return report


if __name__ == "__main__":
    seed_database(force=True)
