import time
import datetime
from typing import Dict

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models import Agent, TestCase, TestResult, EvaluationRun
from app.core.config import settings

from openai import OpenAI, APIError, RateLimitError

client = OpenAI(api_key=settings.OPENAI_API_KEY)


# -----------------------------------------------------------
# EXECUTE ONE TEST CASE
# -----------------------------------------------------------
def execute_test_case(db: Session, result: TestResult, agent: Agent, testcase: TestCase):
    """Runs one evaluation and updates the TestResult row safely."""

    start = time.time()
    system_prompt = (agent.config or {}).get("system_prompt", "")

    # --------------------------------------------------------------------------
    # OFFLINE SIMULATION MODE (no API calls)
    # --------------------------------------------------------------------------
    if agent.model == "offline-simulator":
        simulated = f"[SIMULATED RESPONSE] for testcase: {testcase.prompt}"
        output = simulated
        latency_ms = 30.0
        score = 0.0
        cost_usd = 0.0

    else:
        # ----------------------------------------------------------------------
        # REAL OPENAI MODEL CALL WITH ERROR HANDLING
        # ----------------------------------------------------------------------
        try:
            response = client.chat.completions.create(
                model=agent.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": testcase.prompt},
                ],
            )
            output = response.choices[0].message.content

        except RateLimitError as e:
            output = f"[ERROR] Rate limited or no quota: {str(e)}"
        except APIError as e:
            output = f"[ERROR] OpenAI API failure: {str(e)}"
        except Exception as e:
            output = f"[ERROR] Unexpected exception: {str(e)}"

        end = time.time()
        latency_ms = (end - start) * 1000

        # scoring rule (simple substring)
        expected = (testcase.expected_behavior or "").strip()
        score = 1.0 if expected and expected in output else 0.0

        # placeholder cost until usage is added
        cost_usd = 0.0

    # ----------------------------------------------------------------------
    # WRITE RESULTS BACK TO DATABASE
    # ----------------------------------------------------------------------
    result.response = output
    result.score = score
    result.latency_ms = latency_ms
    result.cost_usd = cost_usd
    result.created_at = datetime.datetime.utcnow()

    db.add(result)
    db.commit()


# -----------------------------------------------------------
# MAIN WORKER LOOP
# -----------------------------------------------------------
def worker_loop():
    """Continuously picks pending runs and evaluates testcases."""
    print("🔥 Worker is alive and polling for jobs...")

    while True:
        db: Session = SessionLocal()

        try:
            run = (
                db.query(EvaluationRun)
                .filter(EvaluationRun.status == "pending")
                .first()
            )

            if not run:
                time.sleep(2)
                continue

            print(f"🚀 Processing run {run.id}")
            run.status = "running"
            db.commit()

            # Fetch results
            results = db.query(TestResult).filter(TestResult.run_id == run.id).all()

            if not results:
                print(f"⚠️ No TestResult rows found for run {run.id}. Marking completed.")
                run.status = "completed"
                db.commit()
                continue

            # Pre-cache agents and testcases
            agent_ids = {r.agent_id for r in results}
            testcase_ids = {r.test_case_id for r in results}

            agents: Dict[int, Agent] = {
                a.id: a for a in db.query(Agent).filter(Agent.id.in_(agent_ids)).all()
            }
            testcases: Dict[int, TestCase] = {
                t.id: t
                for t in db.query(TestCase)
                .filter(TestCase.id.in_(testcase_ids))
                .all()
            }

            # Execute each test result
            for result in results:
                agent = agents.get(result.agent_id)
                testcase = testcases.get(result.test_case_id)

                if not agent or not testcase:
                    print(
                        f"❌ Skipping result {result.id}: missing "
                        f"agent {result.agent_id} or testcase {result.test_case_id}"
                    )
                    continue

                print(
                    f"→ Running test: result={result.id}, agent={agent.name}, testcase={testcase.id}"
                )
                execute_test_case(db, result, agent, testcase)

            run.status = "completed"
            db.commit()
            print(f"✅ Finished run {run.id}")

        except Exception as e:
            print(f"💥 Worker crashed but recovered: {e}")

        finally:
            db.close()
            time.sleep(2)


if __name__ == "__main__":
    worker_loop()
