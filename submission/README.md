# PULSE AI — FinTechathon 2026 submission package

All deliverables are in English. Start with the presentation PDF, then the technical documentation and security assessment.

## Contents

- `PULSE_Presentation.pptx`: editable 10-slide pitch, with speaker notes.
- `PULSE_Presentation.pdf`: matching presentation for immediate viewing.
- `PULSE_Technical_Documentation.pdf`: architecture, financial methods, simulation, agents, automation and validation.
- `PULSE_Security_Self_Assessment.pdf`: implemented controls, limitations and remediation priorities.
- `PULSE_Demo.mp4`: genuine browser recording of the synthetic demonstration, without narration.
- `screenshots/`: 12 actual product and n8n screenshots.
- `execution_evidence/`: test output, production frontend build, actual API results, financial assertions and database schema.
- `PULSE_Source_Code.zip`: source snapshot; excludes credentials, databases and installed dependencies.

## Database and deployment

The team's shared deployment architecture uses **Supabase PostgreSQL** through SQLAlchemy. The included reproducible evidence was generated against an isolated synthetic SQLite database; it is not a live Supabase connectivity certification. No production customer data was used.

For accounts created on different computers to appear in the same administrator console, every frontend must use the same deployed API (`VITE_API_BASE_URL`) and that API must use the same Supabase database (`DATABASE_URL`). Separate localhost servers and SQLite files do not share registrations. Never put database credentials in frontend variables.

## Verified demonstration

The backend run passed **86 tests**. The frontend production build completed. An independent Decimal replay matched cash of EUR 7,020. The 90-day baseline minimum was EUR -2,308 with seven days below zero. A 15-day supplier delay scenario produced a minimum of EUR 2,064 with zero days below zero. A EUR 8,000 purchase reduced the minimum to EUR -10,308. These are synthetic scenario results, not financial guarantees.

The recorded action is explicitly queued because external delivery was disabled for this isolated evidence run. No real payment or invoice record was changed. No LLM key was needed.

Repository: https://github.com/EyaAzzabi/Pulse

This ZIP is a delivery bundle. Uploading it to a competition portal remains a separate step.
