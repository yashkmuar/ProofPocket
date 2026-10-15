# ProofPocket

**Your purchases. Your evidence. Your next step.**

ProofPocket is a project to build an evidence-backed purchase and repair assistant. Its goal is to bring receipts, warranties, and repair records into one place, then help people understand their documents and take practical action when something goes wrong.

Instead of searching through emails, paper receipts, and warranty PDFs, a user should be able to ask a question such as **“What does my warranty say about this fault, and what should I prepare before contacting support?”** and receive an answer linked to the relevant evidence.

> **Project status:** Initial scaffold. A frontend landing page, an API health-check helper, backend configuration, and a database Compose definition are present. Uploads, accounts, document management, repair tracking, and AI answers are not implemented yet. The workflows below describe the intended product, not currently available functionality.

## Why this project exists

Buying a product is easy. Managing the evidence that comes with it is often not.

A receipt might be in an email inbox, the warranty in a downloaded PDF, and a repair history in messages with a service center. When a product fails months later, people must reconstruct what they bought, when they bought it, what protection might apply, and what they have already tried.

This creates several real-world problems:

- **Lost proof of purchase:** A missing receipt can make a return, repair, or warranty request harder to support.
- **Difficult warranty language:** Coverage periods, exclusions, registration requirements, and claim procedures may be spread across several documents.
- **Repeated support conversations:** Users may have to explain the same issue and resend the same evidence to different support agents.
- **Fragmented repair histories:** It can be difficult to establish whether a fault is recurring or what work was previously performed.
- **Unreliable generic advice:** A general answer about warranties may not match the user's actual product, policy, purchase date, or location.

ProofPocket aims to reduce that administrative burden by connecting **the purchase, the evidence, and the next action**.

## Who it is for

The initial focus is people managing their own purchases and household records, especially products such as appliances, electronics, tools, and furniture.

It may be useful for:

- People who want a searchable alternative to folders of receipts and PDFs.
- Households managing products bought from several retailers.
- Owners dealing with a failed product or a recurring repair issue.
- People who want to contact support with a clear timeline and supporting documents.

Shared household access and business asset management would require additional design; they are not currently implemented or established as part of the initial scope.

## How ProofPocket aims to solve these problems

| Real-world problem | Planned approach | Intended benefit |
| --- | --- | --- |
| Receipts and warranties are scattered | Group documents under a purchase record | Make the relevant evidence easier to find |
| Warranty terms are difficult to interpret | Answer questions using the user's documents and cite the source passages | Help users check an explanation against the original terms |
| Support requests lack important details | Prepare a reviewable summary of the purchase, fault, and evidence | Reduce time spent assembling a support request |
| Repair information is fragmented | Maintain a repair and support-event timeline | Preserve context across repeated conversations |
| Generic AI answers are hard to trust | Retrieve relevant document passages before generating an answer | Make responses more specific and verifiable |

These are intended outcomes, not measured results. Document quality, extraction accuracy, and the completeness of a user's records will affect how useful the system can be.

## Example: a washing machine stops working

Consider someone whose washing machine develops a fault 18 months after purchase.

**Without ProofPocket**, they might search for the retailer's receipt, find the manufacturer's warranty, read several pages of conditions, and reconstruct an earlier service visit before contacting support.

**With the planned ProofPocket workflow:**

1. The user opens the washing machine's purchase record.
2. The receipt, warranty, and earlier repair record are available together.
3. The user asks, “What do these documents say about coverage for this fault?”
4. The system retrieves relevant terms and explains them with source references.
5. If information is missing—such as the cause of the fault or a registration requirement—the answer identifies that gap rather than assuming eligibility.
6. The user reviews a draft support summary and chooses which evidence to share.

The goal is to help the user prepare an informed request, **not to guarantee warranty coverage or claim approval**. The retailer or manufacturer may need to assess the fault, and applicable consumer rights may differ from the written warranty.

## Planned capabilities

### 1. Purchase and document organization

Create a home for purchase information and its supporting receipts, warranties, and repair records. Documents should remain connected to the product they describe rather than becoming another unstructured folder.

Document upload, storage, supported file types, and extraction tooling still need to be implemented and defined.

### 2. Evidence-backed questions and answers

Use retrieval-augmented generation (RAG) to locate relevant passages before generating an answer. An answer should explain which documents support it and clearly distinguish explicit terms from uncertainty.

For example, “The warranty describes two years of coverage for manufacturing defects” is different from “Your particular fault is definitely covered.” The system should not make the second claim without sufficient evidence.

### 3. Repair history and support preparation

Record problems, service visits, repairs, and support interactions in a timeline. Use those records to help draft a concise support request that the user can review before sharing.

Automatic claim submission or contacting third parties is not part of the current implementation.

## How the intended system works

The target flow is:

**User documents → text extraction → text chunks → embeddings → relevant evidence retrieval → answer with citations**

1. **Organize:** Associate an uploaded document with a purchase.
2. **Extract:** Obtain usable text while preserving source information needed for citations.
3. **Index:** Split the text into chunks, generate embeddings, and store searchable records.
4. **Retrieve:** Find passages relevant to a user's question.
5. **Answer:** Ask a language model to respond using the retrieved evidence.
6. **Verify:** Show source references and highlight missing or conflicting information.

RAG can improve grounding, but it does not eliminate extraction errors, missed passages, or model mistakes. Citation accuracy and unsupported-answer handling will need testing before the feature can be considered reliable.

## Technical architecture

| Layer | Technology present or declared | Role |
| --- | --- | --- |
| Frontend | Next.js 16, React 19, TypeScript | User interface and navigation |
| Styling | Plain CSS | Current landing-page presentation |
| Backend | FastAPI and Uvicorn dependencies | Planned HTTP API |
| Configuration | Pydantic Settings | Centralized environment-based settings |
| Database access | SQLAlchemy and psycopg dependencies | Planned PostgreSQL persistence |
| Vector search | PostgreSQL 16 with pgvector image; pgvector Python dependency | Planned embedding storage and similarity search |
| AI integration | OpenAI and Azure Identity dependencies | Planned Azure OpenAI chat, embeddings, and authentication |
| Local infrastructure | Docker Compose | Database service definition |

Dependencies and configuration show the intended direction; they do not mean those integrations are operational. Document storage and text-extraction technology have not yet been selected in the inspected code.

## Project structure

Paths below are relative to the `ProofPocket` repository directory.

| Path | Purpose and current state |
| --- | --- |
| `README.md` | Project purpose, product direction, architecture, and implementation status |
| `.gitignore` | Currently empty; needs rules for secrets, environments, and generated files |
| `compose.yaml` | Currently empty; not the configured database Compose file |
| `frontend/package.json` | Frontend dependencies and development, build, start, and type-check scripts |
| `frontend/tsconfig.json` | Strict TypeScript configuration and the `@/*` source alias |
| `frontend/next-env.d.ts` | Next.js type references |
| `frontend/public/` | Static asset directory; currently contains a `.gitkeep` placeholder |
| `frontend/src/app/layout.tsx` | Root layout and page metadata |
| `frontend/src/app/page.tsx` | Introductory landing page and product roadmap |
| `frontend/src/app/globals.css` | Global styles and landing-page styling |
| `frontend/src/components/` | Placeholder directory for reusable UI components |
| `frontend/src/lib/api.ts` | Health-check request helper; not currently used by the homepage |
| `backend/requirements.txt` | Pinned Python dependencies |
| `backend/.env.example` | Environment template file; contents were not inspected |
| `backend/compose.yaml` | PostgreSQL/pgvector service, persistent volume, and readiness check |
| `backend/app/config.py` | Application, database, Azure, CORS, and RAG settings; currently contains a syntax error |
| `backend/app/main.py` | Empty placeholder for FastAPI application setup |
| `backend/app/db.py` | Empty placeholder for database connections and sessions |
| `backend/app/models.py` | Empty placeholder for database models |
| `backend/app/schemas.py` | Empty placeholder for API validation schemas |
| `backend/app/routes.py` | Empty placeholder for API endpoints |
| `backend/app/services/__init__.py` | Services package initializer |
| `backend/app/services/rag.py` | Empty placeholder for retrieval and answer-generation logic |

Local `.git/` metadata and the backend `.venv/` directory are not application source code.

## Current implementation and limitations

### Present today

- A Next.js landing page explaining the product direction.
- A frontend `getHealth()` helper that requests `/api/health`, with a 10-second timeout.
- Frontend backend-URL configuration through `NEXT_PUBLIC_API_URL`, defaulting to `http://localhost:8000`.
- Backend settings for database access, CORS, Azure OpenAI, and RAG parameters.
- A database Compose service using `pgvector/pgvector:pg16`, publishing port `5432` and persisting data in `pgdata`.

### Not working or not implemented yet

- `backend/app/config.py` has a malformed `cors_origin_list` property definition that prevents the module from being imported.
- `main.py` does not yet create a FastAPI application.
- The `/api/health` endpoint expected by the frontend helper does not exist.
- Database models, migrations, and application schema initialization are absent.
- Authentication, document uploads, extraction, vector indexing, AI answers, and repair workflows are absent.
- The database Compose file does not start the frontend or backend.
- A pgvector-capable database image does not itself establish that the vector extension has been enabled in the application database.

This README is based on source inspection. Builds, tests, and end-to-end behavior have not been verified as part of this documentation update.

## Privacy, safety, and trust requirements

Receipts and support records can contain names, addresses, purchase details, and other sensitive information. Before real user documents are accepted, the application will need:

- Authentication and authorization that isolate each user's records, including search results.
- Safe upload validation and limits on file size and processing.
- Secure storage, transport, and secrets management.
- Clear disclosure of document content sent to external AI services.
- Defined retention, deletion, and backup policies.
- Logs that avoid unnecessary personal data and document contents.
- Defenses against instructions embedded in uploaded documents; documents must be treated as evidence, not trusted system instructions.
- Evaluation of citation correctness and behavior when evidence is insufficient.

These are development requirements, not claims of existing protections. The database credentials in the development Compose configuration must not be reused in production, and secrets should never be committed to version control.

ProofPocket is intended to support document understanding and preparation. It is not a substitute for professional legal advice and should not present a warranty interpretation as a binding decision.

## Suggested development roadmap

1. **Make the foundation runnable:** Fix configuration syntax, create the FastAPI app, implement the health endpoint, and document local setup.
2. **Add persistence:** Define purchase, document, and repair models; introduce migrations and database tests.
3. **Build secure document ingestion:** Add user isolation, upload validation, storage, extraction, and source metadata.
4. **Implement evidence retrieval:** Add chunking, embeddings, vector indexing, and retrieval evaluation.
5. **Deliver grounded answers:** Add citations, insufficient-evidence responses, and checks for conflicting documents.
6. **Build practical workflows:** Add purchase screens, repair timelines, and user-reviewed support summaries.
7. **Validate with realistic scenarios:** Test usability, privacy boundaries, extraction quality, and end-to-end reliability before wider deployment.

## What success would look like

The project should be evaluated by whether users can:

- Find the correct purchase evidence faster than with their existing process.
- Understand an answer and verify its supporting passages.
- Recognize when their documents do not establish coverage.
- Prepare a clear support request without repeatedly reconstructing the same history.
- Keep control over which personal documents they store and share.

**The aim is not simply to add AI to receipts. It is to make purchase evidence easier to find, understand, and use when a real problem occurs.**
