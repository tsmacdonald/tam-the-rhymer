import requests
import dotenv

from os import getenv

dotenv.load_dotenv()

EMBED_URL = getenv("EMBED_URL")
EMBED_MODEL = getenv("EMBED_MODEL")


def get_embedding(text: str):
    response = requests.post(EMBED_URL, json={"model": EMBED_MODEL, "input": text})
    try:
        emb = response.json()["embeddings"][0]
    except Exception as e:
        print("Bad response")
        print(response)
        print(e)
    return '[' + ','.join(map(str, emb)) + ']'
