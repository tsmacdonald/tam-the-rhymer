import embedding
import json
import psycopg
import requests
import db_setup as db

from os import getenv
import dotenv
dotenv.load_dotenv()

LLM_ENDPOINT = getenv('LLM_ENDPOINT')
LLM_API_KEY = getenv('LLM_API_KEY')
LLM_MODEL = getenv('LLM_MODEL')

def get_k_nearest_neighbors(user_embedding, k=5):
  def format_result(res):
      (text, id, document_title, similarity) = res
      return f"""
      # {document_title} [Similarity score: {similarity}]
      {text}
      """
  with psycopg.connect(**db.config()) as conn:
    with conn.cursor() as cur:
      cur.execute(
        """
        SELECT
          text,
          id,
          document_title,
          1 - (embedding <=> %s) AS similarity
        FROM document_chunks
        WHERE 1 - (embedding <=> %s) >= 0.4
        ORDER BY similarity DESC
        LIMIT %s
        """,
        (user_embedding, user_embedding, k)

      )
      return list(map(format_result, cur.fetchall()))

def get_query():
    return input("What do you want? ")

def answer_prompt(user_query):

    blockquoted = "\n\n".join("> " + paragraph for paragraph in user_query.split("\n\n"))
    relevant_docs = get_k_nearest_neighbors(embedding.get_embedding(user_query))
    doc_context = "\n\n".join(relevant_docs) if len(relevant_docs) > 0 else "<no relevant documents were found>"
    user_prompt = f"""
    Here is the user's question:

    {blockquoted}

    And here are some relevant documents:

    {doc_context}
    """

    response = requests.post(LLM_ENDPOINT,
                             headers={
                                 "Authorization": f"Bearer {LLM_API_KEY}",
                                 "Content-Type": "application/json"
                             },
                             json={
                                 "model": LLM_MODEL,
                                 "messages": [
                                     {"role": "system", "content": "You are an academic who is an expert on Scottish music history. Help your PhD student with his questions."},
                                     {"role": "user", "content": user_prompt},
                                 ],
                                 "temperature": 1,
                                 "max_tokens": 600
                             })

    return response.json()["choices"][0]["message"]["content"] + "\n\n\nc.f.\n\n" + doc_context

if __name__=="__main__":
    print(answer_prompt(get_query()))
