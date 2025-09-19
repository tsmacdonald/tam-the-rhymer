from os import getenv
import psycopg
import sys

SETUP = ["CREATE EXTENSION IF NOT EXISTS vector;"]
TABLES = [
    {
        "create": """CREATE TABLE IF NOT EXISTS document_chunks (
                      id SERIAL PRIMARY KEY,
                      document_id TEXT NOT NULL UNIQUE,
                      document_title TEXT NOT NULL,
                      text TEXT NOT NULL,
                      embedding vector(1024),
                      metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                  );

                  CREATE INDEX IF NOT EXISTS idx_doc_chunks_document_id ON document_chunks (document_id);

                  CREATE INDEX IF NOT EXISTS idx_doc_chunks_embedding
                  ON document_chunks
                  USING hnsw (embedding vector_cosine_ops);
               """,
        "drop": "TRUNCATE TABLE document_chunks;"
    }
]

def config():
    import dotenv
    dotenv.load_dotenv()
    return {
        "dbname": getenv("DB_NAME"),
        "user": getenv("DB_USER"),
        "password": getenv("DB_PASS"),
        "host": getenv("DB_HOST"),
        "port": getenv("DB_PORT")
        }


def setup():
    with psycopg.connect(**config()) as conn:
        with conn.cursor() as cur:
            for stmnt in SETUP + list(map(lambda t: t["create"], TABLES)):
                cur.execute(stmnt)

def drop():
    with psycopg.connect(**config()) as conn:
        with conn.cursor() as cur:
            for stmnt in list(map(lambda t: t["drop"], TABLES)):
                cur.execute(stmnt)


def print_help():
    print("""USAGE:

        python db_setup.py [setup | drop | help | --help]
    """)

if __name__ == "__main__":
    command = sys.argv[1].lower()
    if command == "setup":
        print("Setting up DB...")
        setup()
        print("Done")
    elif command == "drop":
        print("Truncating tables...")
        drop()
        print("Done")
    elif command in ("help", "--help"):
        print_help()
    else:
        print("Command not recognized")
        print_help()
