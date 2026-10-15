# Data model

PostgreSQL 16 with pgvector. The runnable DDL is [backend/sql/schema.sql](../backend/sql/schema.sql); this page explains the choices, the retrieval query, and the traps.

## Shape

```
documents ──1:N──> chunks
   id (uuid)         id (bigserial)
   title             document_id ──FK, ON DELETE CASCADE
   source_type       chunk_index          ─┐ unique together
   content_hash      content               │
   char_count        start_char/end_char   │ citation anchors
   chunk_count       page_number           │
   status            token_count           │
   embedding_model   embedding vector(1536) <── HNSW, vector_cosine_ops
   metadata jsonb    created_at
   created_at/updated_at
```

Two tables carry the whole RAG loop. `documents` is what the user manages; `chunks` is what the retriever searches. Everything else in the product (purchases, repairs, users) hangs off `documents` later without changing this core.

## Why these columns

**`chunks.embedding` is `NOT NULL`.** The write path embeds every chunk in one batched call and commits the document and its chunks in a single transaction. A nullable embedding would mean rows that exist but can never be retrieved — a silent, invisible failure. If embedding moves to a background worker, keep the NOT NULL and use `documents.status` to mark the document as not yet searchable.

**`ON DELETE CASCADE`.** `DELETE /api/documents/{id}` deletes the chunks too. Doing it in the database rather than the service means an orphaned vector can't survive a partial failure in application code.

**`UNIQUE (document_id, chunk_index)`.** Makes re-ingest idempotent and guarantees citation `[1]`/`[2]` numbering is stable. It's also a btree whose leading column is `document_id`, so it already serves the cascade delete and per-document lookups — a separate index on `document_id` alone would be dead weight.

**`start_char` / `end_char` / `page_number`.** The README commits to showing users the source passage, not just a snippet. Store the offsets at ingest; reconstructing them later from chunk text is lossy once the chunker's overlap means the same text appears twice.

**`embedding_model`.** Vectors from different models aren't comparable. If you switch deployments, every pre-existing chunk becomes noise in the same index, and cosine scores will look plausible while being meaningless. This column is how you find the rows to re-embed. Changing the model is a backfill, never a config flip.

**`metadata jsonb`.** Extraction will surface merchant, purchase date, warranty length and so on long before you know which deserve columns. Park them here; promote to real columns once a query needs to filter on one.

## The retrieval query

```sql
SELECT
    c.id,
    c.document_id,
    d.title,
    c.content,
    c.chunk_index,
    1 - (c.embedding <=> :query_embedding) AS similarity
FROM chunks c
JOIN documents d ON d.id = c.document_id
ORDER BY c.embedding <=> :query_embedding
LIMIT :top_k;
```

`<=>` is cosine **distance** (0 = identical, 2 = opposite). Similarity is `1 - distance`, which is what your 0.20 cutoff compares against.

Apply the cutoff in `rag.py` on the returned rows, not in a SQL `WHERE`. Ordering by the operator with a `LIMIT` is the shape the HNSW index can serve; adding `WHERE 1 - (...) >= 0.20` makes Postgres keep walking the index past your `top_k` looking for rows that qualify, which is slower for no benefit when you're only taking 5. Fetch `top_k`, filter in Python, and return `grounded: false` if nothing survives.

Two things to verify rather than assume:

- Run `EXPLAIN ANALYZE` on that query once you have a few thousand chunks and confirm you see an `Index Scan using chunks_embedding_hnsw_idx`. A `Seq Scan` means the operator class and the operator disagree, or the planner decided the table is too small to bother — the latter is fine and expected early on.
- `hnsw.ef_search` (default 40) is the recall/latency dial at query time. With `TOP_K = 5` the default is ample. Raise it with `SET LOCAL hnsw.ef_search = 100;` inside the transaction if recall looks poor; never set it below `top_k`.

## Traps worth knowing before you hit them

**Dimension ceiling.** `config.py` offers `text-embedding-3-large` (3072) as an alternative. HNSW and IVFFlat on the plain `vector` type cap out at **2000 dimensions** — `CREATE INDEX` will fail outright at 3072. Your options are to stay at 1536, store `halfvec(3072)` and index with `halfvec_cosine_ops` (supported to 4000 dims, half the storage, negligible recall loss), or ask the API for a reduced dimension via the `dimensions` parameter. Decide before you ingest anything real; changing it means re-embedding everything.

**Filtered search is post-filter.** The moment documents carry a `user_id` and the ask query filters by it, HNSW searches the whole index and *then* drops rows the filter rejects — so a user with 20 chunks in a 500k-chunk corpus can get back fewer than `top_k` results, or none. Denormalise `user_id` onto `chunks` so the filter at least doesn't need a join, then either raise `ef_search` substantially or turn on iterative index scans (`SET hnsw.iterative_scan = relaxed_order;`, pgvector 0.8+). Check what you have with `SELECT extversion FROM pg_extension WHERE extname = 'vector';`. This is the single most common way multi-tenant pgvector apps go quietly wrong.

**Index build memory.** Building HNSW with `maintenance_work_mem` too low makes Postgres fall back to a disk-based build that is dramatically slower. Before a large backfill: `SET maintenance_work_mem = '1GB';`. Bulk-load chunks first and create the index after — building it incrementally during a large ingest is far slower.

**Normalisation.** `text-embedding-3-*` returns unit-length vectors, so cosine and inner product rank identically. `vector_ip_ops` with `<#>` is marginally cheaper, but cosine is harder to get wrong and the difference won't be your bottleneck. Staying with cosine is the right call.

**Storage.** A 1536-dim `vector` is ~6 KB. At ~1000 characters per chunk, embeddings outweigh your text by roughly 6:1 — budget disk by chunk count, not document size.

## Growing into the product

The README describes purchases, repair timelines and per-user isolation. None of that changes the two core tables; it adds parents and a foreign key. When you get there:

```sql
CREATE TABLE users (
    id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email      citext NOT NULL UNIQUE,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE purchases (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       uuid NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    product_name  text NOT NULL,
    merchant      text,
    purchased_at  date,
    warranty_ends date,
    created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE repair_events (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    purchase_id  uuid NOT NULL REFERENCES purchases (id) ON DELETE CASCADE,
    kind         text NOT NULL CHECK (kind IN ('fault', 'contact', 'service', 'resolution')),
    occurred_on  date NOT NULL,
    notes        text,
    created_at   timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE documents
    ADD COLUMN user_id     uuid REFERENCES users (id) ON DELETE CASCADE,
    ADD COLUMN purchase_id uuid REFERENCES purchases (id) ON DELETE SET NULL;

-- Denormalised so filtered vector search doesn't need a join. Keep it in sync
-- from the ingest path; documents never change owner.
ALTER TABLE chunks
    ADD COLUMN user_id uuid REFERENCES users (id) ON DELETE CASCADE;

CREATE INDEX chunks_user_id_idx ON chunks (user_id);
```

Add `user_id` *before* you have real user documents. Retrofitting tenant isolation onto a populated vector index means a backfill plus an audit of every query that could already have leaked across users.

One more table worth adding when you start tuning: an `ask_logs` row per question storing the question, the chunk ids returned, their scores, and whether the answer was grounded. It costs almost nothing and it's the only way to answer "did changing the threshold to 0.25 help?" with evidence rather than impressions.
