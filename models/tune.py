import openai
from time import sleep
from api import client


def tune_friend(fingerprint: str):
    res = openai.File.create(
        file=open("models/datasets/counsellor.jsonl", "r"), purpose="fine-tune"
    )

    file_id = res["id"]
    res = openai.FineTuningJob.create(training_file=file_id, model="gpt-3.5-turbo")
    job_id = res["id"]
    while True:
        res = openai.FineTuningJob.retrieve(job_id)
        if res["finished_at"] != None:
            break
        else:
            print(".", end="")
            sleep(100)
    ft_model = res["fine_tuned_model"]

    db = client.get_db()
    model_collections = db["models"]
    model_collections.insert_one(
        {
            "fingerprint": fingerprint,
            "conversation_type": "friend",
            "models": [{"id": job_id, "name": ft_model}],
        }
    )

    return {
        "status": "success",
        "status_code": 200,
        "message": "Fine-tuned model for friend conversation",
    }
