import inngest
from inngest_client import client


@client.create_function(
    fn_id="say-hello",
    trigger=inngest.TriggerEvent(event="test/hello"),
    retries=2,
)
async def say_hello(ctx: inngest.Context) -> str:
    await ctx.step.sleep("wait-a-moment", 5)
    return "Hello from the background!"


@client.create_function(
    fn_id="make-report",
    trigger=inngest.TriggerEvent(event="report/requested"),
    retries=2,
)
async def make_report(ctx: inngest.Context) -> dict:
    report_id = ctx.event.data["id"]
    topic = ctx.event.data["topic"]

    # Step 1: simulate slow work
    await ctx.step.sleep("do-the-slow-work", 8)

    # Step 2: build the report
    async def build():
        import main
        import sys

        if topic == "fail":
            raise Exception(f"Deliberate failure for topic: {topic}")

        result = {
            "id": report_id,
            "topic": topic,
            "status": "done",
            "summary": f"Report on '{topic}': analysis complete.",
            "word_count": len(topic) * 42,
        }
        main.reports[report_id] = result
        print(f"WROTE TO DICT: {report_id} — dict now has {list(main.reports.keys())}", file=sys.stderr, flush=True)
        return result

    return await ctx.step.run("build-report", build)


@client.create_function(
    fn_id="heartbeat",
    trigger=inngest.TriggerCron(cron="* * * * *"),
)
async def heartbeat(ctx: inngest.Context) -> dict:
    import main

    pending = sum(1 for r in main.reports.values() if r["status"] == "pending")
    done = sum(1 for r in main.reports.values() if r["status"] == "done")
    failed = sum(1 for r in main.reports.values() if r["status"] == "failed")

    summary = f"Heartbeat — pending: {pending}, done: {done}, failed: {failed}"
    print(summary)
    return {"pending": pending, "done": done, "failed": failed}