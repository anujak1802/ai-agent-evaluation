import time
import datetime
from typing import Dict

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models import Agent, TestCase, TestResult, EvaluationRun
from app.core.config import settings
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def execute_test_case(
    db: Session,
    result: TestResult,
    agent: Agent,
    testcase: TestCase,
) -> None:
    """Run a single model request and update the existing TestResult row."""

    start = time.time()

    system_prompt = ""
    if agent.config:
        # agent.config is JSON; be defensive
        system_prompt = agent.config.get("system_prompt", "") or ""

    # Call the model
    response = client.chat.completions.create(
        model=agent.model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": testcase.prompt},
        ],
    )

    # New OpenAI client uses .content, not ["content"]
    output = response.choices[0].message.content
    end = time.time()

    latency_ms = (end - start) * 1000.0

    # Naive scoring: substring match
    expected = (testcase.expected_behavior or "").strip()
    score = 1.0 if expected and expected in output else 0.0

    # TODO: real cost calculation from response.usage
    cost_usd = 0.0

    # Update existing TestResult
    result.response = output
    result.score = score
    result.latency_ms = latency_ms
    result.cost_usd = cost_usd
    result.created_at = datetime.datetime.utcnow()

    db.add(result)
    db.commit()


def worker_loop() -> None:
    """Continuously process evaluation runs."""
    while True:
        db: Session = SessionLocal()

        try:
            # Pick one pending run
            run = (
                db.query(EvaluationRun)
                .filter(EvaluationRun.status == "pending")
                .first()
            )

            if not run:
                db.close()
                time.sleep(3)
                continue

            print(f"Processing run {run.id}")
            run.status = "running"
            db.commit()

            # Get all TestResult rows for this run
            results = (
                db.query(TestResult)
                .filter(TestResult.run_id == run.id)
                .all()
            )

            if not results:
                # Nothing to do; mark as completed
                run.status = "completed"
                db.commit()
                db.close()
                continue

            # Cache agents and testcases
            agent_ids = {r.agent_id for r in results}
            testcase_ids = {r.test_case_id for r in results}

            agents: Dict[int, Agent] = {
                a.id: a
                for a in db.query(Agent).filter(Agent.id.in_(agent_ids)).all()
            }
            testcases: Dict[int, TestCase] = {
                t.id: t
                for t in db.query(TestCase).filter(TestCase.id.in_(testcase_ids)).all()
            }

            for result in results:
                agent = agents.get(result.agent_id)
                testcase = testcases.get(result.test_case_id)

                if not agent or not testcase:
                    # Something is wrong with the DB
                    print(
                        f"Skipping result {result.id} – "
                        f"missing agent {result.agent_id} or testcase {result.test_case_id}"
                    )
                    continue

                execute_test_case(db, result, agent, testcase)

            # All results processed
            run.status = "completed"
            db.commit()

        finally:
            db.close()
            # Small pause before next polling iteration
            time.sleep(3)


if __name__ == "__main__":
    worker_loop()
