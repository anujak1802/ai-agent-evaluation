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
