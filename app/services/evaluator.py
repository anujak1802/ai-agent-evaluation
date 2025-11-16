from sqlalchemy.orm import Session
from time import perf_counter
from app.db.models import EvaluationRun, TestCase, Agent, TestResult, TelemetryEvent
from app.services.openai_client import call_agent

def simple_scorer(response: str, expected: str | None) -> float:
    # Very naive binary scorer – later you can use an LLM-as-judge
    if not expected:
        return 0.0
    return 1.0 if expected.lower() in response.lower() else 0.0

def process_pending_runs(db: Session):
    pending_runs = db.query(EvaluationRun).filter(EvaluationRun.status == "pending").all()
    
    for run in pending_runs:
        run.status = "running"
        db.commit()

        test_cases = db.query(TestCase).all()
        agents = db.query(Agent).all()

        for tc in test_cases:
            for agent in agents:
                start = perf_counter()

                # telemetry: outgoing request
                request_event = TelemetryEvent(
                    run_id=run.id,
                    event_type="request",
                    payload={"agent_id": agent.id, "test_case_id": tc.id}
                )
                db.add(request_event)
                db.commit()

                result = call_agent(agent.model, tc.prompt, agent.config)
                latency_ms = (perf_counter() - start) * 1000

                # naive cost estimate – you’ll refine this
                tokens = result["usage"]["total_tokens"]
                cost_usd = tokens * 0.000002  # placeholder

                score = simple_scorer(result["content"], tc.expected_behavior)

                test_result = TestResult(
                    run_id=run.id,
                    test_case_id=tc.id,
                    agent_id=agent.id,
                    response=result["content"],
                    score=score,
                    latency_ms=latency_ms,
                    cost_usd=cost_usd,
                )
                db.add(test_result)
                db.commit()
                db.refresh(test_result)

                # telemetry: response event
                response_event = TelemetryEvent(
                    run_id=run.id,
                    test_result_id=test_result.id,
                    event_type="response",
                    payload={
                        "usage": result["usage"],
                        "latency_ms": latency_ms,
                        "score": score,
                        "cost_usd": cost_usd,
                    }
                )
                db.add(response_event)
                db.commit()

        run.status = "completed"
        db.commit()
