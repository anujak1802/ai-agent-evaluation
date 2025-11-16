from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import EvaluationRun, TestResult, Agent, TestCase

router = APIRouter()

class EvalRequest(BaseModel):
    agent_ids: list[int]      # 👈 list instead of single agent
    testcase_ids: list[int]
    run_name: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=dict)
def start_eval(payload: EvalRequest, db: Session = Depends(get_db)):
    # For backward-compat we still store one agent_id on the run (first one)
    run = EvaluationRun(
        run_name=payload.run_name,
        agent_id=payload.agent_ids[0],  # baseline / first agent
        status="pending",
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    # Create a TestResult row for each (agent, testcase) combination
    for agent_id in payload.agent_ids:
        for tc_id in payload.testcase_ids:
            result = TestResult(
                run_id=run.id,
                test_case_id=tc_id,
                agent_id=agent_id,
                response="",
                score=0.0,
                latency_ms=0.0,
                cost_usd=0.0,
            )
            db.add(result)

    db.commit()

    return {"run_id": run.id, "status": "created"}

@router.get("/", response_model=list[dict])
def list_runs(db: Session = Depends(get_db)):
    runs = db.query(EvaluationRun).all()
    return [
        {
            "id": r.id,
            "run_name": r.run_name,
            "status": r.status,
            "agent_id": r.agent_id,
        }
        for r in runs
    ]