from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Float
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from sqlalchemy import ARRAY
from app.db.session import Base


# Base = declarative_base()

class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    model = Column(String, nullable=False)   # e.g. gpt-4.1
    config = Column(JSON, nullable=True)     # temperature, tools, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

class TestCase(Base):
    __tablename__ = "test_cases"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    prompt = Column(Text, nullable=False)
    expected_behavior = Column(Text, nullable=True)  # rubric/description
    created_at = Column(DateTime, default=datetime.utcnow)

class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(Integer, primary_key=True)
    run_name = Column(String, nullable=False)
    status = Column(String, default="created")

    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)



class TestResult(Base):
    __tablename__ = "test_results"
    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("evaluation_runs.id"))
    test_case_id = Column(Integer, ForeignKey("test_cases.id"))
    agent_id = Column(Integer, ForeignKey("agents.id"))
    response = Column(Text)
    score = Column(Float)                         # 0-1 or 0-100
    latency_ms = Column(Float)
    cost_usd = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("EvaluationRun")
    test_case = relationship("TestCase")
    agent = relationship("Agent")

class TelemetryEvent(Base):
    __tablename__ = "telemetry_events"
    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("evaluation_runs.id"))
    test_result_id = Column(Integer, ForeignKey("test_results.id"), nullable=True)
    event_type = Column(String)      # "request", "response", "error", "token_usage"
    payload = Column(JSON)           # arbitrary details
    created_at = Column(DateTime, default=datetime.utcnow)
