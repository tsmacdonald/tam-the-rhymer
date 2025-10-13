# Structure

```
input files -> generating embeddings -> storing them in Postgres (pgvector) -> finding relevant ones for prompt -> providing them in a prompt to an LLM ->  accessing that via REST
```

First couple steps are invoked by `document_processor.py`, prompt stuff is `warlock.py`, `server.py` is the REST server.

The embeddings are made with Ollama (running locally); the prompt is currently ChatGPT (requires API key in .env).

Ollama and Postgres are provided by Docker; `cd environment; docker compose up -d` to get them going. Might need to download the model for Ollama; it'll tell you what's up.

`db_setup.py` for migrating the DB.


```
uv run flask --app server run --host 0.0.0.0 --port 5000
```

or

```
uv run python main.py
```



for starting the server


# Future plans

Better interface for generating embeddings; implement a work queue; store the SHA for the file to detect changes
