from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import TestCase

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TestCaseCreate(BaseModel):
    name: str
    prompt: str
    expected_behavior: str | None = None

@router.post("/", response_model=dict)
def create_testcase(payload: TestCaseCreate, db: Session = Depends(get_db)):
    tc = TestCase(
        name=payload.name,
        prompt=payload.prompt,
        expected_behavior=payload.expected_behavior
    )
    db.add(tc)
    db.commit()
    db.refresh(tc)
    return {"id": tc.id, "name": tc.name}

# GET /testcases
@router.get("/", response_model=list[dict])
def list_testcases(db: Session = Depends(get_db)):
    testcases = db.query(TestCase).all()
    return [
        {
            "id": tc.id,
            "name": tc.name,
            "prompt": tc.prompt,
            "expected_behavior": tc.expected_behavior,
            "created_at": tc.created_at,
        }
        for tc in testcases
    ]
