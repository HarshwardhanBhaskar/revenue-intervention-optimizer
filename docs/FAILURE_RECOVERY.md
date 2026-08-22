# Failure Recovery Log & Self-Correction Incidents

This document records the actual engineering failure modes encountered during development, root cause analyses, solutions, and regression tests.

---

### Incident 1: Windows Unicode / CP-1252 Encoding Crash in CLI Training Scripts
- **Problem**: When running `ml/training/train.py` on Windows powershell, the script crashed with `UnicodeEncodeError: 'charmap' codec can't encode character '\u20b9'` when printing the Indian Rupee symbol `₹`.
- **Root Cause**: Windows PowerShell console default code page (CP-1252) cannot encode Unicode currency glyphs.
- **Fix**: Replaced console stdout characters in standalone scripts with ASCII-safe formatting (`INR`) while preserving `₹` in UI layers, and configured standard UTF-8 stream writers.
- **Regression Test**: Executed ML training and test benchmark scripts in Windows environment with 0 errors.

---

### Incident 2: NumPy JSON Serialization Error in Action Ranking Storage
- **Problem**: Saving action rankings to the database or returning API responses failed with `TypeError: Object of type int64 is not JSON serializable`.
- **Root Cause**: Scikit-learn feature transformers and NumPy calculations produced `np.float64` and `np.int64` datatypes that standard Python `json.dumps` and FastAPI serializers reject.
- **Fix**: Implemented explicit casting (`float(x)` and `int(x)`) in `backend/domain/decision_engine.py` and `backend/ml/model_registry.py`.
- **Regression Test**: Unit test `test_ranking_serialization` validates that all dictionary outputs are JSON-serializable.

---

### Incident 3: Test Webhook Idempotency Key Collision on Persistent SQLite Database
- **Problem**: Integration test `test_webhook_ingestion_and_deduplication` failed on repeated test runs because the hardcoded test event ID `evt_test_failure_101` was already marked as ingested.
- **Root Cause**: SQLite `rio_dev.db` persisted the previous test run's records, causing the first delivery in the new test run to return `duplicate_ignored` instead of `processed`.
- **Fix**: Dynamically generate a fresh event UUID (`evt_test_{uuid.uuid4().hex[:8]}`) in the test so the first delivery is guaranteed fresh and the second delivery tests deduplication.
- **Regression Test**: Full pytest integration suite runs cleanly with 100% pass rate.

---

### Incident 4: Next.js App Router Suspense Boundary Requirement for `useSearchParams`
- **Problem**: Next.js production build (`next build`) failed on static page generation for `/decision-lab` and `/lab` with `Error: useSearchParams() should be wrapped in a suspense boundary at page "/decision-lab"`.
- **Root Cause**: Next.js 14 requires components consuming search query parameters during static generation to be enclosed in a React `<Suspense>` boundary to allow client-side hydration bailout.
- **Fix**: Refactored `DecisionLabPage` into an outer `<Suspense>` wrapper enclosing the inner `DecisionLabContent` component.
- **Regression Test**: `npm run build` completed successfully across all 17 routes with 0 errors.
