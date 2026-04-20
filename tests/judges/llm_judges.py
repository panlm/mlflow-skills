from __future__ import annotations

import json
import os

from openai import OpenAI
from mlflow.entities import Feedback
from mlflow.genai.scorers import scorer


def _call_llm(client, question, trace_excerpt):
    resp = client.chat.completions.create(
        model=os.environ.get("JUDGE_MODEL", "opus-4-6"),
        max_tokens=256,
        messages=[
            {
                "role": "user",
                "content": (
                    f"{question}\n\n"
                    "Answer ONLY with a JSON object: "
                    '{"answer": "yes", "rationale": "..."} '
                    'or {"answer": "no", "rationale": "..."}.\n\n'
                    f"Trace:\n{trace_excerpt}"
                ),
            }
        ],
    )
    text = resp.choices[0].message.content.strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        if "yes" in text.lower():
            data = {"answer": "yes", "rationale": text}
        else:
            data = {"answer": "no", "rationale": text}
    return Feedback(
        value=data.get("answer", "no"),
        rationale=data.get("rationale", ""),
    )


def _extract_trace(trace):
    trace_json = trace.to_json() if hasattr(trace, "to_json") else json.dumps(trace.to_dict())
    head = trace_json[:120000]
    tail = trace_json[-40000:] if len(trace_json) > 160000 else ""
    return head + ("\n...[TRUNCATED]...\n" + tail if tail else "")


def get_judges() -> list:
    raw = os.environ.get("JUDGE_DEFINITIONS", "[]")
    definitions = json.loads(raw)

    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        base_url=os.environ.get("OPENAI_BASE_URL"),
    )

    judges = []
    for j in definitions:

        def make_scorer(name, question):
            @scorer(name=name)
            def _judge(trace) -> Feedback:
                return _call_llm(client, question, _extract_trace(trace))
            return _judge

        judges.append(make_scorer(j["name"], j["question"]))

    return judges
