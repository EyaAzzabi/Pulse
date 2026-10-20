# MASTER ENGINEERING PROMPT — PULSE AI
## Build a Competition-Ready, Full-Stack, Agentic FinTech Platform

You are an elite autonomous software engineering team consisting of a Principal AI Architect, Senior Full-Stack Engineer, FinTech Domain Expert, UX/UI Designer, AI Agent Engineer, Security Engineer, MLOps Engineer, and QA Lead.

Your mission is to **design, implement, integrate, test, and document a complete, visually exceptional, functional FinTech application named PULSE AI**.

This is a real competition project, not a tutorial, mockup, or collection of disconnected screens.

### Competition context

- Competition: Shenzhen International FinTech Competition 2026 — FinTechathon.
- Track: International Track.
- Theme: AI as a Financial Participant.
- Selected Topic: E — SME Finance Copilot.
- Team size: 3 engineering students.
- Application language: English.
- Deadline: October 20, 2026.
- Primary audience: international judges, financial professionals, investors, and technical evaluators.

The application must show how AI can become a useful, responsible financial participant, capable of understanding a business's financial situation, anticipating problems, planning interventions, and preparing safe actions.

**Our goal is not to build another AI chatbot. We are building an intelligent financial operating system for small businesses.**

## 1. PRODUCT IDENTITY

Name: PULSE AI

Tagline: "Your business deserves a financial brain."

Core concept:

PULSE AI is an intelligent financial copilot that transforms financial data from SMEs into predictive insights, risk alerts, simulated strategies, actionable recommendations, and human-approved financial workflows.

Its central innovation is the **Financial Digital Twin**: a living computational representation of a business's financial situation.

Users can ask questions such as:

- "Will I have enough cash to pay my employees next month?"
- "What happens if my largest customer pays 15 days late?"
- "Can I afford to purchase €8,000 of inventory?"
- "Which customers should I follow up with first?"
- "How can I avoid a cash shortage in the next 30 days?"
- "Which financing option would be appropriate for my situation?"
- "Prepare a reminder email for my three overdue invoices."
- "Explain my biggest financial risk in simple language."

PULSE should not simply return a text response.

It should:

1. Understand the user's intent and business context.
2. Retrieve relevant structured and unstructured evidence.
3. Calculate financial indicators using trustworthy deterministic code.
4. Forecast possible future scenarios.
5. Explain underlying causes and uncertainties.
6. Propose prioritized solutions.
7. Simulate their financial impacts.
8. Request approval for consequential actions.
9. Execute permitted integrations when configured.
10. Preserve a traceable history of decisions and actions.

## 2. ABSOLUTE ENGINEERING REQUIREMENTS

Build actual working software.

Do not generate a static demonstration pretending to be a functional product.

Do not leave buttons disconnected.

Do not display invented live financial metrics.

Do not rely on hardcoded fake LLM responses presented as genuine AI.

Do not claim an integration is working unless it is actually configured and verified.

When an external service is unavailable, implement an explicitly labeled demo or offline fallback with functioning local behavior.

Use synthetic financial data only. Clearly identify it as demo data.

Keep all secrets in environment variables.

Never place API keys inside frontend code.

Never commit credentials.

Use structured logging and useful error messages.

Financial calculations must be performed in deterministic Python services, not delegated to an LLM.

Use decimal-safe monetary calculations.

Implement strong tenant isolation and authorization.

The project must be independently reproducible from its README.

Keep the code modular, understandable, typed where practical, and testable.

Prioritize a fully working vertical slice before secondary features.

**Very important:** Do not stop after producing a plan. Create the actual files, implement the modules, run available checks, fix errors, and continue until the agreed implementation scope is functional. Work in verifiable checkpoints rather than attempting everything in one uncontrolled pass.

## 3. TECHNOLOGY STACK

Use a modern stack optimized for implementation speed, visual quality, and AI extensibility.

### Frontend
- React with TypeScript.
- Vite.
- Tailwind CSS.
- shadcn/ui components.
- Lucide React icons.
- Framer Motion or Motion for React.
- Recharts for financial data visualization.
- TanStack Query for server-state management.
- React Router.
- React Hook Form and Zod validation.

### Backend
- Python 3.11+.
- FastAPI.
- Pydantic.
- SQLAlchemy.
- Alembic for database migrations.
- JWT/session-based authentication with secure password hashing.
- PostgreSQL for production.
- SQLite fallback for fast local execution.
- Async-capable service design where appropriate.

### AI
- Configurable LLM provider abstraction.
- Groq or compatible OpenAI-style APIs where available.
- Support structured JSON outputs, schema validation, and retries.
- Agent orchestration using modular Python services.
- Embeddings and local FAISS-based RAG.
- Configurable LLM model IDs through environment variables.

### Automation
- n8n for workflow orchestration.
- Webhook integrations.
- SMTP or configured email provider.
- Local action queue and audit records when n8n is unavailable.

### Infrastructure
- Docker Compose where available.
- Local development without Docker must also work.
- Pytest backend tests.
- Vitest frontend tests where practical.
- GitHub Actions CI.
- .env.example.
- Reproducible seed commands.

Do not introduce heavy infrastructure such as Kubernetes, Kafka, or complex distributed microservices for this prototype.

Use a modular monolith with explicit domain boundaries.

## 4. USER EXPERIENCE — WORLD-CLASS FINTECH DESIGN

The UX/UI is a major competitive differentiator.

Design PULSE as if it were a polished, investor-backed, premium FinTech SaaS application.

Visual inspiration:
- Linear-level polish.
- Stripe-style clarity.
- Modern banking dashboards.
- High-quality AI command centers.
- Editorial typography.
- Subtle motion.
- Meaningful data visualization.

Do not copy any existing product.

### Visual identity

Primary background: deep navy / midnight blue.

Suggested palette:
- Midnight: #070D1B.
- Deep Navy: #101A2E.
- Electric Cyan: #22D3EE.
- Teal: #14B8A6.
- White: #F8FAFC.
- Muted Slate: #94A3B8.
- Amber: #F59E0B.
- Risk Red: #F87171.

Use bright accent colors sparingly.

The product must feel:
- Premium.
- Intelligent.
- Calm.
- Credible.
- Futuristic but practical.
- Professional enough for financial decision-making.

Avoid overly flashy animations, excessive gradients, generic robot images, and crowded dashboards.

### UX requirements

- Fully responsive desktop, tablet, and mobile layouts.
- Desktop sidebar with collapsed state.
- Mobile bottom navigation or responsive drawer.
- Accessible keyboard navigation.
- Strong contrast.
- Visible loading states.
- Empty states.
- Helpful validation errors.
- Error recovery.
- Skeleton loaders.
- Tooltips explaining financial terms.
- Search functionality.
- Toast notifications.
- Confirmation dialogs.
- Progressive disclosure of complex information.
- Consistent spacing and typography.
- Dark theme first, optional light theme.
- Financial values with appropriate currency formatting.
- Clear differentiation between actual data, forecasts, and hypothetical scenarios.

Never rely solely on color to convey financial risk.

Build reusable design-system components, not independently styled pages.

## 5. LANDING PAGE

Build a complete public landing page.

### Navigation

Logo: PULSE AI.

Links:
- Platform.
- How It Works.
- Features.
- Security.
- Sign In.
- Get Started.

### Hero

Headline:

"Your business has a heartbeat. We help you understand its future."

Supporting text:

"Meet the AI financial copilot that predicts cash shortages, simulates smarter decisions, and turns financial uncertainty into confident action."

Primary CTA:
"Start Your Financial Journey"

Secondary CTA:
"Explore Interactive Demo"

Design a highly visual hero with a realistic mini financial command center showing:

- Current cash.
- Forecasted cash.
- Upcoming risk.
- Recommended intervention.
- An interactive preview of a scenario.

### Further landing sections

1. The problem facing SMEs.
2. How PULSE works.
3. The Financial Digital Twin.
4. AI agents.
5. Cash-flow forecasting.
6. Human-controlled financial actions.
7. Security and transparency.
8. Final CTA.

Do not use invented customer testimonials or fabricated performance statistics.

## 6. AUTHENTICATION AND USER MANAGEMENT

Implement real authentication and persistence.

Pages:
- Sign up.
- Login.
- Forgot password.
- Password reset when email delivery is configured.
- User profile.
- Organization settings.
- Team management.
- Security settings.

### Roles

Implement organization-scoped RBAC.

OWNER:
- Full organization access.
- Manage team and financial settings.
- Approve high-impact actions.
- Manage integrations.

FINANCE_MANAGER:
- Import financial data.
- View forecasts.
- Run simulations.
- Propose and approve authorized actions within assigned permissions.

ACCOUNTANT:
- Import and review records.
- View reports.
- Access invoice information.
- Cannot manage the organization or execute unauthorized financial actions.

VIEWER:
- Read-only access to allowed dashboards and reports.
- No financial mutations.

Each account may belong to multiple organizations.

Each organization's data must remain isolated.

Team invitations should use expiring tokens and appropriate permission checks.

Avoid IDOR and cross-tenant access vulnerabilities.

All sensitive endpoints require server-side authorization.

### User settings

Include:
- Full name.
- Avatar or initials.
- Preferred language.
- Default currency.
- Timezone.
- Notification preferences.
- Accessibility and motion preferences.
- Connected integrations.
- Logout.

## 7. PREMIUM STEP-BY-STEP ONBOARDING

Design an onboarding journey that feels like the application is building a personalized financial intelligence system for the user.

The onboarding must be interactive, validated, resumable, and persisted.

Use a progress indicator.

### Step 1 — Welcome

Headline:

"Let's understand the business behind the numbers."

Offer:
- Set up my business.
- Explore with a demo business.

### Step 2 — Business identity

Collect:
- Business name.
- Industry.
- Country.
- Preferred currency.
- Company size.
- Year founded (optional).
- Operating timezone.

Industry choices:
- Retail.
- E-commerce.
- Hospitality.
- Services.
- Manufacturing.
- Other.

### Step 3 — Business financial profile

Collect:
- Approximate monthly revenue.
- Approximate monthly fixed expenses.
- Current cash balance.
- Typical customer payment delay.
- Typical supplier payment delay.
- Number of employees.
- Payroll frequency.
- Existing loans (optional).

Do not require unnecessary sensitive banking information.

Clearly explain why each field matters.

### Step 4 — Connect financial data

Offer:
- Upload CSV.
- Upload PDF invoices.
- Use synthetic demo dataset.
- Manual entry.

Support CSV preview, column matching, date parsing, currency validation, error reporting, and confirmation before import.

### Step 5 — Define financial goals

Multi-select:
- Prevent cash shortages.
- Improve payment collection.
- Control operating costs.
- Plan business growth.
- Explore financing.
- Reduce financial uncertainty.

### Step 6 — AI personalization

Collect:
- Desired alert sensitivity.
- Forecast horizon.
- Email notification preference.
- Preferred response tone: concise or detailed.
- Whether voice assistance is enabled.
- Preferred financial risk tolerance (conservative, balanced, growth-focused).

### Step 7 — Team setup

Allow the owner to invite colleagues or skip.

### Step 8 — Financial initialization

Show a polished processing experience, but do not fake a long AI computation.

Perform actual:
- Data validation.
- Initial cash-flow calculations.
- Liquidity analysis.
- Risk detection.
- Initial forecast.
- Recommendation generation if AI is available.

### Step 9 — Personalized welcome

Show:
- Business name.
- Data status.
- Cash position.
- Most important identified financial risk.
- Suggested next step.

CTA:
"Enter My Financial Command Center"

Persist onboarding completion and allow later editing.

## 8. MAIN APPLICATION LAYOUT

The authenticated application must provide the following routes.

- /dashboard
- /copilot
- /forecast
- /simulator
- /transactions
- /invoices
- /financing
- /documents
- /automations
- /notifications
- /decisions
- /team
- /settings

Navigation must remain coherent.

Provide a global command/search entry point.

Make the currently selected business visible.

Include an accessible organization switcher.

Show consistent notification indicators.

### DASHBOARD — THE FINANCIAL COMMAND CENTER

Create a beautiful executive financial overview.

Top greeting:

"Good morning. Here's your business pulse."

Use the user's preferred timezone.

Main KPI cards:
- Current cash balance.
- Estimated monthly net cash flow.
- Projected 30-day cash position.
- Cash runway.
- Overdue receivables.
- Upcoming payment obligations.

Hero chart:
Historical actual cash flow and projected future cash flow, visually differentiated.

Include uncertainty ranges only if a meaningful uncertainty method is actually implemented.

Financial Health section:
- Liquidity status.
- Revenue trend.
- Expense pressure.
- Collection risk.
- Upcoming obligations.

Prioritize 1–3 actionable alerts.

Include a prominent AI insight card:

"PULSE detected a potential cash shortfall in 18 days."

Only show this statement if supported by calculated data.

Include an action CTA:
"Explore Rescue Strategies"

Create a "Recommended Next Actions" section with:
- Action description.
- Financial rationale.
- Expected impact.
- Risk level.
- Approval requirement.
- View details.

Include a "What Changed?" section summarizing material movements in the business finances.

Make all data server-driven.

## 9. FINANCIAL DATA MODEL

Design normalized database models.

Core tables/entities:
- users
- organizations
- memberships
- invitations
- business_profiles
- onboarding_progress
- financial_accounts
- transactions
- invoices
- invoice_payments
- recurring_obligations
- financing_options
- cashflow_snapshots
- forecast_runs
- forecast_points
- simulation_scenarios
- recommendations
- action_proposals
- action_executions
- approval_records
- uploaded_documents
- document_chunks
- conversations
- chat_messages
- notifications
- automation_rules
- integration_connections
- audit_logs

Define proper relationships, indexes, timestamps, uniqueness constraints, and organization ownership.

Financial records need:
- Unique IDs.
- Organization ID.
- Currency.
- Amount.
- Date.
- Category.
- Direction.
- Source.
- Status.
- Import reference.
- Created/updated timestamps.

Preserve original transaction values for traceability.

Validate amounts, dates, duplicates, and accounting direction.

Use idempotent import processing.

Never mix financial data across organizations.

## 10. SYNTHETIC DEMONSTRATION DATA

Create a realistic seeded company:

Company name: Northstar Studio.

Industry: E-commerce and retail.

Currency: EUR.

Generate:
- 6 months of historical transactions.
- Customer invoices.
- Supplier invoices.
- Payroll obligations.
- Rent.
- Software subscriptions.
- Operational expenses.
- Pending receivables.
- Several overdue invoices.
- Upcoming large payments.
- A possible future liquidity shortage.

Make the dataset coherent.

All dashboard numbers must be derived from this dataset.

Create at least three reproducible demonstration scenarios:

SCENARIO A:
A future liquidity shortfall caused by delayed customer payments.

SCENARIO B:
A large inventory purchase that may become unaffordable.

SCENARIO C:
A recovery strategy involving earlier receivable collection and payment rescheduling.

Ensure the backend computes the actual financial outcomes.

Never fake results inside frontend components.

Create a one-command demo seed process.

## 11. DETERMINISTIC FINANCIAL ENGINE

Implement a financial analysis engine in Python.

Minimum functions:
- Current liquidity.
- Net cash flow.
- Cash inflows and outflows.
- Monthly burn rate.
- Cash runway.
- Outstanding receivables.
- Outstanding payables.
- Overdue invoices.
- Upcoming obligations.
- Concentration risk.
- Expense trends.
- Cash-flow forecast.
- Risk classification.
- Scenario comparison.

Use Decimal for money.

Forecasting:

Implement a defensible, deterministic baseline first:
- Historical patterns.
- Known payment schedules.
- Recurring obligations.
- Invoice due dates.
- Explicit assumptions for uncertain inflows.

Future forecasts must distinguish known scheduled commitments from uncertain estimates.

When historical data is insufficient, label confidence appropriately rather than inventing precision.

Optional enhancement:
Add an evaluated statistical or ML forecasting model only if sufficient data and time are available.

Avoid data leakage.

Provide error metrics when backtesting is possible.

Implement tests proving financial conservation and consistent scenario calculations.

## 12. FINANCIAL DIGITAL TWIN

This is the signature feature.

The Digital Twin must allow users to explore future business outcomes without changing real records.

Create:
- A baseline financial state.
- Immutable or isolated scenario assumptions.
- Simulation engine.
- Comparison engine.
- Scenario history.
- Ability to reset and rerun.
- Explanation of assumptions.

### Interactive scenario controls

Users can change:
- Customer payment delay.
- Supplier payment delay.
- Revenue change percentage.
- Expense change percentage.
- Inventory purchase amount.
- Financing amount.
- Interest cost.
- One-time cash injection.

Display:
- Baseline forecast.
- Simulated forecast.
- Lowest projected cash point.
- Estimated runway.
- Days below zero cash.
- Impact versus baseline.
- Risk trade-offs.

Show visually distinct forecast lines.

Display the source of every major number.

### Rescue Plan Generator

Given a detected risk, generate up to three candidate strategies.

Example:
- Accelerate customer collections.
- Negotiate supplier payment extensions.
- Reduce discretionary expenses.

Rank strategies based on:
- Estimated liquidity benefit.
- Implementation feasibility.
- Cost.
- Residual risk.
- Timing.

Provide explicit assumptions.

A strategy should never be presented as guaranteed.

## 13. MULTI-AGENT AI ARCHITECTURE

Build a modular multi-agent system, not a single enormous prompt.

### Agent 1 — Financial Analyst

Responsibilities:
- Understand financial questions.
- Select required data.
- Call financial calculation tools.
- Explain verified metrics.
- Detect inconsistencies.

### Agent 2 — Forecast Analyst

Responsibilities:
- Interpret forecasting results.
- Explain critical dates.
- Identify risk drivers.
- Communicate uncertainty.

### Agent 3 — Strategic Planner

Responsibilities:
- Produce candidate interventions.
- Request simulations.
- Compare simulated outcomes.
- Rank recommendations.

### Agent 4 — Risk Guardian

Responsibilities:
- Verify authorization requirements.
- Detect unsupported claims.
- Identify unacceptable financial assumptions.
- Enforce tool permissions.
- Flag potentially harmful actions.

### Agent 5 — Workflow Coordinator

Responsibilities:
- Convert approved recommendations into actionable drafts.
- Prepare email notifications.
- Create approval proposals.
- Trigger authorized workflow integrations.

### Agent 6 — Orchestrator

Responsibilities:
- Classify user intent.
- Determine whether tools are necessary.
- Select appropriate specialist agents.
- Maintain conversation context.
- Build the final grounded response.

Important:

Use tool/function calling or explicitly validated structured outputs.

Agents must invoke real Python services.

LLMs must not invent balances, dates, customer names, or financial outcomes.

Protect against prompt injection in uploaded documents.

Keep retrieved document text lower-trust than system policy and user authorization.

Implement bounded retries and timeouts.

Provide graceful fallback if the LLM API is unavailable.

### Explainability

Every important AI recommendation should expose:

- WHAT was detected.
- WHY it matters.
- EVIDENCE used.
- CALCULATION or simulation performed.
- RECOMMENDED action.
- UNCERTAINTY.
- APPROVAL status.

Add a "Why this recommendation?" expandable panel.

## 14. AI COPILOT EXPERIENCE

Build an exceptional AI workspace.

Features:
- Conversational chat.
- Streaming responses where supported.
- Conversation history.
- Suggested contextual prompts.
- Markdown rendering.
- Financial charts embedded in responses.
- Evidence references.
- Interactive action cards.
- Suggested follow-up questions.
- Copy response.
- New conversation.
- Error recovery.
- Clear AI availability status.

Context-aware prompts should change based on the active business.

Examples:
- "Explain my cash runway."
- "What is my biggest financial risk?"
- "Simulate a 15-day payment delay."
- "Can I afford this purchase?"
- "Prepare reminders for overdue invoices."

Use structured response blocks when possible rather than only plain text.

An AI response may contain:
- Explanation.
- Financial summary.
- Referenced metrics.
- Chart data.
- Risk indicators.
- Simulation action.
- Approval action.

Do not allow the AI to invoke high-impact operations without proper authorization.

## 15. VOICE AI ASSISTANT

Add a voice interaction mode.

Implement:
- Microphone control.
- Listening indicator.
- Voice recording/transcription flow.
- Transcript confirmation.
- Spoken assistant responses.
- Text/voice switching.
- Accessible fallback to typed input.

Use browser speech capabilities when supported or a configurable transcription service.

Use speech synthesis where supported.

Do not claim universal browser support.

Voice commands must pass through the same authorization and validation pipeline as text commands.

Example:

User says:
"PULSE, can I afford to pay my supplier next Friday?"

PULSE retrieves the financial data, evaluates the cash position, and returns a grounded answer.

No voice command should bypass approval controls.

If speech recognition is unavailable, display a helpful fallback.

## 16. DOCUMENT INTELLIGENCE AND RAG

Create a document intelligence center.

Support:
- PDF upload.
- Text-based PDF extraction.
- CSV upload.
- Invoice documents.
- Supplier terms.
- Financial policies.
- Contract documents.

For scanned PDFs, use an OCR integration only if available.

Never silently invent extracted text.

### RAG architecture

1. Validate file type and size.
2. Extract text.
3. Sanitize and normalize.
4. Chunk documents.
5. Create embeddings.
6. Index chunks in FAISS.
7. Retrieve relevant chunks.
8. Apply tenant filtering.
9. Construct grounded context.
10. Generate responses with document references.

Use per-organization isolated indices or enforce strong retrieval isolation.

Do not rely solely on a global FAISS index with unverified metadata filtering.

Every response about uploaded documents should cite:
- Document name.
- Page where available.
- Relevant extracted content.

Protect against malicious instructions embedded in documents.

Do not automatically turn extracted invoice amounts into financial records without validation and user confirmation.

### Document intelligence UX

Show:
- Uploaded documents.
- Processing status.
- Extracted metadata.
- Document preview.
- Search.
- Citation navigation.
- Associated business records.

Example:

"What does my supplier agreement say about late-payment penalties?"

PULSE must retrieve actual document evidence, not invent a contract clause.

## 17. INVOICE AND RECEIVABLE MANAGEMENT

Create a full invoice workspace.

Support:
- Invoice listing.
- Search and filtering.
- Paid/unpaid/overdue statuses.
- Due-date sorting.
- Customer details.
- Outstanding amount.
- Payment tracking.
- Invoice creation/manual import.
- Overdue risk visibility.
- Reminder drafts.
- Collection prioritization.

Provide an invoice detail drawer.

Build smart reminders based on overdue status and customer relationship.

Never send emails automatically without authorization.

Show exact recipients and content before approval.

## 18. FINANCING INTELLIGENCE

Implement a financing workspace focused on SMEs.

Users should be able to:
- Specify financing amount.
- Explain financing purpose.
- Choose desired repayment horizon.
- Review liquidity situation.
- Compare illustrative financing structures.
- Model repayment impact.
- Assess cash-flow affordability.

Use transparent formulas.

Do not invent bank offers or interest rates presented as current market data.

Mark all unavailable-provider examples as illustrative.

If integrating real lending providers later, require verifiable external data.

Generate a downloadable financing-readiness summary based on actual available records.

Do not claim the platform determines formal loan eligibility.

## 19. N8N AUTOMATION ENGINE

Build an automation module designed around n8n.

Use real HTTP webhook integration.

Workflow configuration must come from environment variables.

Do not assume n8n is already installed.

If n8n is unavailable, store pending actions and allow safe local previews.

### Workflow A — Cash Risk Alert

Trigger:
A computed forecast crosses a configured risk threshold.

Steps:
1. Detect risk.
2. Create alert.
3. Save evidence.
4. Build notification payload.
5. Send configured webhook.
6. Deliver email if provider is configured.
7. Record execution status.

Avoid duplicate alerts through idempotency.

### Workflow B — Invoice Reminder

Trigger:
The authorized user selects overdue invoices.

Steps:
1. Prepare email.
2. Show draft.
3. Request approval.
4. Validate permissions.
5. Trigger n8n.
6. Send through configured provider.
7. Save audit log.

### Workflow C — Financial Digest

Trigger:
A configured daily or weekly schedule.

Steps:
1. Collect financial indicators.
2. Detect material changes.
3. Generate a factual summary.
4. Send to opted-in users.
5. Save delivery status.

### Workflow D — Approved Recovery Plan

Trigger:
A human approves a proposed financial intervention.

Steps:
1. Confirm organization and user permissions.
2. Revalidate action proposal.
3. Execute permitted integration.
4. Persist result.
5. Update the recommendation status.
6. Show execution feedback.

Export functional n8n workflow JSON files into the repository.

Document n8n setup.

Never mark an email "Sent" if no provider confirmed delivery or acceptance.

Use explicit statuses:
DRAFT, PENDING_APPROVAL, APPROVED, QUEUED, SENT, FAILED, CANCELLED.

Use authenticated webhooks and idempotency keys.

## 20. FINANCIAL DECISION APPROVAL SYSTEM

This is a mandatory safety and innovation feature.

Create a central Decision Center.

Every consequential operation must follow:

PROPOSE → EXPLAIN → SIMULATE → REVIEW → APPROVE → EXECUTE → AUDIT.

Each proposal contains:
- Action ID.
- Organization ID.
- Initiating user.
- Action type.
- Target.
- Details.
- Expected result.
- Risks.
- Supporting evidence.
- Approval requirement.
- Expiration time.
- Status.

The user must explicitly approve actions.

For higher-risk actions, require reauthentication or an additional approval mechanism if implemented.

Validate proposal state server-side.

Prevent proposal replay.

Make execution idempotent.

Create a complete audit trail.

Do not implement actual transfers of funds, borrowing, banking transactions, or real investment execution.

Scope executable actions to safe, configured operations such as sending authorized emails and creating internal reminders.

## 21. NOTIFICATIONS AND ALERTS

Implement an in-app notification center.

Notification categories:
- Critical liquidity risk.
- Overdue invoices.
- Forecast changes.
- Action approval requests.
- Workflow results.
- Data import errors.
- System warnings.

Include:
- Read/unread state.
- Notification preferences.
- Link to originating record.
- Severity.
- Timestamp.
- Dismissal.

No fake "live" alerts.

Use persisted notifications generated by actual application events.

## 22. ANALYTICS AND BUSINESS REPORTS

Implement:
- Cash-flow chart.
- Revenue vs. expenses.
- Receivables aging.
- Payment obligations timeline.
- Expense categories.
- Historical cash trends.
- Scenario comparison.

Add export to CSV.

Provide PDF export for at least one financial report if feasible.

Ensure all exported numbers match backend calculations.

Do not display unsupported business benchmarks.

## 23. SECURITY AND RESPONSIBLE FINANCIAL AI

Implement:
- Secure password hashing.
- Server-side authorization.
- Tenant isolation.
- Input validation.
- File upload restrictions.
- Rate limits on expensive AI endpoints.
- Basic authentication abuse protection.
- Token expiry.
- API secret protection.
- Secure error handling.
- CORS configuration.
- Audit logging.
- Sensitive data minimization.
- User-controlled actions.

Avoid logging passwords, authentication tokens, and raw financial documents unnecessarily.

Treat uploaded text and retrieval outputs as untrusted.

Never let an LLM override business rules.

Require human approval for externally consequential actions.

Never describe forecasts as guarantees.

Make it explicit that PULSE is decision support, not a regulated financial adviser.

## 24. API DESIGN

Design RESTful endpoints.

Minimum functional groups:

Authentication:
- POST /auth/register
- POST /auth/login
- GET /auth/me

Organizations:
- POST /organizations
- GET /organizations
- GET /organizations/{id}
- PATCH /organizations/{id}
- GET /organizations/{id}/members

Onboarding:
- GET /onboarding
- PUT /onboarding
- POST /onboarding/complete

Financial data:
- GET /transactions
- POST /transactions/import
- GET /invoices
- GET /financial/summary
- GET /financial/cashflow

Forecasting:
- POST /forecast/run
- GET /forecast/latest

Simulation:
- POST /simulations
- GET /simulations
- GET /simulations/{id}

AI:
- POST /copilot/chat
- GET /copilot/conversations

Documents:
- POST /documents/upload
- GET /documents
- POST /documents/search

Actions:
- POST /actions/propose
- POST /actions/{id}/approve
- POST /actions/{id}/execute
- GET /actions

Automation:
- GET /automations
- POST /automations
- GET /automations/executions

Notifications:
- GET /notifications
- PATCH /notifications/{id}

The endpoints must have validation, authentication, authorization and meaningful error responses.

Use OpenAPI-generated documentation.

These are target routes; keep implementation consistency if route organization changes.

## 25. PROJECT STRUCTURE

Create a clean repository such as:

pulse-ai/
- frontend/
  - src/
    - components/
    - features/
    - pages/
    - layouts/
    - hooks/
    - services/
    - contexts/
    - types/
    - lib/
    - styles/
- backend/
  - app/
    - api/
    - core/
    - models/
    - schemas/
    - services/
    - agents/
    - financial/
    - forecasting/
    - simulations/
    - rag/
    - workflows/
    - security/
    - db/
  - alembic/
  - tests/
  - scripts/
- n8n/
  - workflows/
- demo/
  - datasets/
  - scenarios/
- docs/
- .env.example
- README.md
- docker-compose.yml
- Makefile

Keep domain logic out of API route handlers.

Prefer small, cohesive functions.

Use shared schemas between modules.

## 26. DEMO PRESENTATION MODE

Add a clearly marked "Demo Company" mode.

This must be a real seeded demonstration environment using synthetic data.

It should not be a static fake frontend.

Create an effective walkthrough.

### Demonstration story

1. A user logs into Northstar Studio.
2. The dashboard reveals a financial risk.
3. The user opens the cash-flow forecast.
4. A shortage appears on a future date.
5. PULSE explains what caused it.
6. The user asks the AI for a recovery strategy.
7. The agent analyzes evidence and invokes financial tools.
8. The user opens the Financial Digital Twin.
9. The user simulates alternative actions.
10. The system compares outcomes.
11. The user selects a recommendation.
12. PULSE prepares a customer reminder email.
13. The user approves it.
14. The system executes the configured email workflow or clearly indicates offline demo status.
15. The decision and its execution state appear in the audit timeline.

Make the story reproducible.

Create a deterministic demo-reset function.

Seed a demo user via a safe development-only method.

Do not ship a publicly exposed privileged demo account with a fixed password.

## 27. QUALITY ASSURANCE

Write tests for:

- User registration and login.
- Password verification.
- Organization isolation.
- Role enforcement.
- Onboarding persistence.
- CSV import.
- Financial summary calculations.
- Forecast consistency.
- Scenario isolation.
- Invoice status calculation.
- Approval authorization.
- Action idempotency.
- RAG retrieval isolation.
- AI tool permission enforcement.
- n8n failure handling.

Test key endpoints.

Verify that changes to one organization's data cannot affect another organization.

Verify that financial computations are reproducible.

Run the test suite.

Fix broken imports and runtime errors.

Do not state that tests pass unless they actually ran successfully.

## 28. COMPETITION DOCUMENTATION

Create:

README.md:
- Product overview.
- Competition and chosen topic.
- Problem statement.
- Innovation.
- Architecture.
- Features.
- Technical stack.
- Setup instructions.
- Environment variables.
- Demo scenario.
- AI limitations.
- Security and human approval.
- Testing instructions.
- Screenshots placeholder or actual screenshots if available.

docs/ARCHITECTURE.md:
- Service architecture.
- Agent interaction.
- Data flow.
- Security boundaries.
- RAG retrieval.
- Automation design.

docs/COMPETITION_SUBMISSION.md:
- One-page problem and solution summary.
- Topic E compliance mapping.
- Innovation explanation.
- Technical differentiation.
- Reproducibility.
- Tested functionality.
- Honest list of unavailable integrations.

docs/DEMO_SCRIPT.md:
- A 3–5 minute walkthrough.
- Exact actions to demonstrate.
- Expected backend-computed outcomes.

docs/FEATURE_STATUS.md:
- IMPLEMENTED AND TESTED.
- IMPLEMENTED BUT NOT VERIFIED.
- DEMO ONLY.
- PLANNED.
- BLOCKED.

Do not claim unavailable features are complete.

## 29. EXECUTION STRATEGY — STRICT PRIORITIES

We have a severe deadline.

Do not implement the whole feature wishlist sequentially before testing the product.

Use progressive delivery.

### PHASE P0 — WORKING CORE (MANDATORY)

Build and verify:
1. Repository scaffolding.
2. Backend and frontend startup.
3. Authentication.
4. Organization model and isolation.
5. Demo company seed.
6. Financial summary.
7. Cash-flow forecast.
8. Risk detection.
9. Digital Twin simulation.
10. Working dashboard.
11. Core AI chat connected to financial tools.
12. README and demo instructions.

At the end of P0, the project must be demonstrable end to end.

### PHASE P1 — COMPETITION DIFFERENTIATION

Add:
1. Rescue strategy generation.
2. Decision Center.
3. Human approval.
4. Invoice workspace.
5. Contextual AI explanations.
6. Financial evidence and audit trail.
7. CSV import.
8. Basic financing comparison.
9. Polished demo walkthrough.

### PHASE P2 — ADVANCED EXPERIENCE

Add when P0 and P1 work:
1. Full premium onboarding.
2. Team invitations.
3. Document RAG.
4. Voice interface.
5. Email workflows.
6. n8n export/integration.
7. Advanced notifications.
8. PDF reports.
9. UI animations and refinements.

### PHASE P3 — OPTIONAL ENHANCEMENTS

Only if time allows:
1. Statistical model benchmarking.
2. Light mode.
3. Advanced financing recommendation engine.
4. Advanced voice services.
5. More integrations.

Never sacrifice a functioning financial simulation for decorative features.

## 30. PARALLEL TEAM COLLABORATION

The team has three members.

Design clean interfaces for parallel development.

Suggested ownership:

ENGINEER A:
Backend, financial engine, AI orchestration, simulations.

ENGINEER B:
Frontend, authentication screens, onboarding, dashboard, interactions.

ENGINEER C:
RAG, automation, synthetic data, tests, documentation.

Provide explicit API contracts.

Avoid conflicting files.

Use short-lived feature branches where appropriate.

Ensure frequent integration.

Never overwrite unrelated work from teammates.

## 31. FINAL ACCEPTANCE CRITERIA

The project is acceptable only when:

- The frontend starts successfully.
- The backend starts successfully.
- Authentication works.
- Demo financial data can be loaded.
- The dashboard uses real API data.
- Financial calculations are reproducible.
- At least one genuine forecast runs.
- A user can simulate a financial intervention.
- The simulated result changes correctly.
- The AI can retrieve and explain actual computed values when configured.
- Relevant high-impact actions require approval.
- The UI never pretends that a failed action succeeded.
- Users cannot access another company's data.
- The core demo can be reproduced.
- README instructions are accurate.
- Tests have been executed and their real results documented.

For any feature not completed, clearly label its status rather than disguising a mockup as functionality.

## 32. YOUR FIRST ACTIONS

Start by:

1. Inspecting the existing repository and environment.
2. Identifying available package managers, Python version, and Node version.
3. Creating a concise implementation plan.
4. Defining the canonical backend data schemas.
5. Creating the repository structure.
6. Implementing the P0 vertical slice immediately.
7. Running backend and frontend startup checks.
8. Testing the complete financial crisis simulation.
9. Fixing all blocking errors.
10. Reporting the exact implementation status.

Do not spend excessive time on planning.

Do not ask for routine design decisions; choose sensible defaults.

Only ask for unavailable secrets, credentials, or genuinely blocking external configuration.

If a service requires credentials, implement a clean configuration interface and a meaningful local fallback.

Continue implementing until P0 is fully operational, then advance to P1 and P2 according to remaining time.

**The final result must feel like a coherent, premium financial intelligence product, not a hackathon prototype assembled from unrelated components.**

Build PULSE AI now.
