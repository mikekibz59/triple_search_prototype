# Triple Search Prototype

A minimal prototype for finding mid-sized U.S. shippers by commodity, location, and size.

- `on_demand_prototype/` – live LLM-driven parsing & search  
- `pre_scraped_prototype/` – batch scrape → embed → search  
- `common/` – shared scraping & search modules


# On-demand prototype – simple scorecard

## What we watch
| Focus | Simple check |
|-------|--------------|
| Answers are right | For 10 saved test searches, count how many come back correct. |
| It feels **okay** | We accept up to **3-4 s** per search; live scraping is slower than pre-scraped. |
| Cost | AI tokens used **per search** (fresh scrape every time). |
| Data is fresh | 100 % of pages are scraped on the fly, so always “today’s” info. |

---

## How we measure
* Run the 10 test searches once every night; store right / wrong count and total time.  
* Log each search with **time taken** and **tokens spent**.  
* A tiny daily script turns the logs into one CSV row and pushes it to a dashboard.

---

## When we try a new model
1. **Silent test**: route 1 request out of 20 to the new model; compare accuracy + cost.  
2. **Promote if** it’s at least as accurate *and* either cheaper or not slower than 4 s.

---

## What to remember
* It’s slower than the pre-scraped path because we scrape in real time.  
* But results are always the freshest possible.  
* We have less control over external pages (they can block us or change layout), so error logging is extra important.

---

## Where the logs live
All logs drop into one folder ➜ simple collector ➜ dashboard. Same pipeline as the other prototype, so we can compare side-by-side.

## Notes for the docs – on-demand prototype

### Current pain points
| Area | What happens now | Why it matters |
|------|------------------|----------------|
| **Slow scrapes** | 5 s per link → 20 links ≈ 1 min. | Users wait or the call times out. |
| **Request timeouts** | We removed the hard 20 s timeout to avoid 502s. | Hides the problem, doesn’t solve it. |
| **Retries / rate-limits** | No back-off yet. | External sites can block us; we need 429 handling. |
| **Large responses** | Scraped JSON grows fast; context fed to the LLM is huge. | Burns through the free-tier token budget and slows the model. |
| **Single REST call** | One POST waits for all links. | Better as background job or streaming endpoint. |

### Cost & context size
- Every extra paragraph scraped = more LLM tokens.  
- After the free tier (x tokens/month) we pay **$Y per 1k tokens** — so 20 full pages can eat the daily budget in one hit.  
- Need a **token guard**: truncate or summarise long pages before sending to the model.

### Fix ideas (to-do)
1. **Parallel + async** – scrape 8-10 links at once (httpx/asyncio).  
2. **Chunked streaming** – return each result as soon as it’s ready.  
3. **LangChain helpers** – built-in async, retry, and token-count filters.  
4. **Context trimming** – strip boilerplate, keep only <n> sentences around keywords.  
5. **Caching** – skip re-scrape if page seen in last 24 h.  
6. **Exponential back-off** – retry 3× with 2-4-8 s delays on 429/5xx.

# Pre-scraped + SQLite Prototype

## What We Built

This prototype demonstrates our search API using pre-scraped company data and SQLite for rapid development and validation.

### Core Components

**Data Ingestion (`ingest_sqlite.py`)**
- Processes JSON files from `sample_data/` directory
- Creates and populates `companies.db` with company records
- Handles both single objects and arrays in JSON files
- Runs once during Docker image build

**Search API (`api.py`)**
- **Endpoint**: `POST /search_supplier_db`
- **Input**: commodity, company_size, location, optional top_k (default: 20)
- **Logic**: SQLite queries with case-insensitive substring matching
- **Output**: Array of matching companies with name, domain, description, location, LinkedIn

**Containerized Deployment**
- Built on `python:3.12-slim` for minimal footprint
- Pre-builds database during image creation
- Exposes API on port 8002
- Single-command deployment via Docker Compose

## Design Decisions & Trade-offs

### What We Simplified (And Why)

| Production Component | Prototype Approach | Rationale |
|---------------------|-------------------|-----------|
| **Vector embeddings + FAISS** | Simple `LIKE` queries | Semantic search adds complexity; substring matching proves the API contract works |
| **Live web scraping** | Pre-scraped JSON files | Removes external dependencies; ensures consistent, repeatable demos |
| **PostgreSQL/MongoDB** | SQLite file | Zero infrastructure setup; reviewers can run immediately |
| **Elasticsearch** | Basic SQL filtering | Heavy indexing service vs. lightweight proof-of-concept |
| **Microservices architecture** | Single FastAPI app | Demonstrates end-to-end flow without orchestration complexity |

### Prototype Strengths

**Rapid Validation** 
- Validates exact API contract planned for production
- Demonstrates request/response flow with real-ish data
- Stakeholders can test within minutes of `docker run`

**Development Velocity**
- No external service dependencies
- Deterministic behavior with fixed dataset
- Hot-swappable components (can upgrade to vector search without client changes)

**Deployment Simplicity**
- Single container, single command
- No database migrations or seed scripts
- Built-in health checks and monitoring endpoints

## Current Limitations

### Technical Constraints

| Limitation | Impact | Mitigation Strategy |
|------------|--------|-------------------|
| **Basic text matching** | Misses semantic similarity, typos, synonyms | Acceptable for prototype; production will use embeddings |
| **SQLite concurrency** | Limited concurrent writes, file-locking issues | Fine for demo; production needs PostgreSQL |
| **In-memory scaling** | Single instance, no horizontal scaling | Sufficient for validation; production requires clustering |
| **Data staleness** | Requires image rebuild for new data | Acceptable for prototype; production will have live ingestion |

### Search Quality Gaps

**Missing Features**
- No fuzzy matching ("steal" vs "steel") 
- No semantic understanding ("construction materials" vs "building supplies")
- No relevance scoring or ranking
- No query expansion or suggestion

**Data Coverage**
- Limited to curated sample dataset
- No real-time market data
- Missing company relationships or hierarchies

## Next Steps for Production

### Phase 1: Enhanced Search
- Replace substring matching with vector embeddings
- Add semantic similarity scoring
- Implement query preprocessing and expansion

### Phase 2: Live Data Pipeline  
- Add web scraping scheduler
- Implement incremental data updates
- Add data quality validation and deduplication

### Phase 3: Production Infrastructure
- Migrate to PostgreSQL with proper indexing
- Add caching layer (Redis)
- Implement horizontal scaling and load balancing
- Add comprehensive monitoring and alerting

## Value Delivered

This prototype successfully validates our core assumptions while minimizing development overhead. It proves the API design works, provides a tangible demo for stakeholders, and creates a foundation that can be incrementally upgraded to production quality without breaking client integrations.