from openai import OpenAI
client = OpenAI()

def list_active_batches(statuses=("validating","in_progress","queued","running","finalizing")):
    print("Active batches:")
    found = False
    for b in client.batches.list().data:  # paginated; adjust if you have many
        if b.status in statuses:
            found = True
            perc_completed = b.request_counts.completed / b.request_counts.total if b.request_counts.total > 0 else 0.0
            print(b)
            print(f"- {b.id}  status={b.status}  created_at={b.created_at}  endpoint={b.endpoint}  progress={perc_completed:.1%}")
    if not found:
        print("(none)")

def cancel_batch(batch_id: str):
    print(f"Cancelling {batch_id} ...")
    client.batches.cancel(batch_id)

list_active_batches()
cancel_batch("batch_68b908bbd49c8190bc36056aa2ca8149")

