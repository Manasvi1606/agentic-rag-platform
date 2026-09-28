# Evaluation dataset

Put your ~100-question gold set here as `qa.jsonl`, one record per line:

```json
{"question": "What is our data retention period?", "ground_truth": "90 days.", "contexts": ["..."]}
```

Guidance:
- Cover every route (vector, sql, web) and a few deliberately hard/ambiguous ones.
- Include questions the corpus *can't* answer, to test abstention.
- Hand-label this. The quality of your eval ceiling is set by the quality of
  this file — it's worth the afternoon.
