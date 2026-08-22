"""Experiments API — Control vs Treatment Evaluation Benchmark."""

from pathlib import Path
import json
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.database import get_db
from models.experiment import Experiment

router = APIRouter()
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"


@router.get("")
async def list_experiments(db: AsyncSession = Depends(get_db)):
    """List experiments and held-out test evaluation benchmarks."""
    stmt = select(Experiment)
    res = await db.execute(stmt)
    experiments = res.scalars().all()

    # Load offline test evaluation benchmark results if present
    eval_file = DOCS_DIR / "evaluation_results.json"
    benchmark_data = None
    if eval_file.exists():
        with open(eval_file, "r", encoding="utf-8") as f:
            benchmark_data = json.load(f)

    return {
        "experiments": [
            {
                "id": str(e.id),
                "name": e.name,
                "status": e.status,
                "control_pct": e.control_pct,
                "treatment_pct": e.treatment_pct,
                "results": e.results,
                "started_at": e.started_at.isoformat() if e.started_at else None,
            }
            for e in experiments
        ],
        "test_benchmark": benchmark_data,
    }
