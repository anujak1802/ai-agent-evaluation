from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models

router = APIRouter()

@router.get("/{run_id}")
def get_results(run_id: int, db: Session = Depends(get_db)):
    results = (
        db.query(models.TestResult)
          .filter(models.TestResult.run_id == run_id)
          .all()
    )

    if not results:
        raise HTTPException(status_code=404, detail="No results found.")

    return results

@router.get("/", response_model=list[dict])
def list_results(run_id: int, db: Session = Depends(get_db)):
    results = db.query(models.TestResult).filter(models.TestResult.run_id == run_id).all()
    return [
        {
            "id": r.id,
            "testcase_id": r.test_case_id,
            "agent_id": r.agent_id,
            "score": r.score,
            "latency_ms": r.latency_ms,
            "cost_usd": r.cost_usd,
            "response": r.response
        }
        for r in results
    ]
