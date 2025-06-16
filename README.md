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