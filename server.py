import json
import warlock

from flask import Flask, request

app = Flask(__name__)


@app.route('/answer', methods=['POST'])
def answer():
    query = json.loads(request.data)['input']
    return warlock.answer_prompt(query)
