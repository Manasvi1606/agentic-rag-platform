"""SQL branch — natural language -> SQL over the structured tables.

This is where query-routing earns its keep: some questions ("total revenue in
Q2", "how many orders shipped late") are answered by SQL, not vector search.

Text-to-SQL is YOUR 20%, and it comes with a SECURITY dimension you must not
skip — this is exactly the kind of thing the Adobe security review would flag.
"""
from __future__ import annotations

from agents.state import AgentState


def run_sql(state: AgentState) -> AgentState:
    """Generate SQL from the query, execute it read-only, return rows.

    TODO(you): implement generation + execution. Non-negotiable design points:

      SAFETY (treat as required, not optional):
        - NEVER string-format the LLM's output into a raw query and run it with
          write privileges. Execute against a READ-ONLY role/connection.
        - Constrain to a whitelist of tables/columns; validate the generated SQL
          (parse it, reject anything but SELECT) before execution.
        - Set a statement timeout and a row LIMIT so a bad query can't melt the DB.
        - Parameterize any user-supplied literals.

      QUALITY:
        - Give the LLM the schema (DDL) as context; it can't guess column names.
        - Consider a repair loop: if the query errors, feed the error back once.

    Return state with "sql_result" populated. Write the safety layer yourself —
    understanding *why* each guard exists is the point.
    """
    raise NotImplementedError("Implement guarded text-to-SQL. Read-only + validated, always.")
