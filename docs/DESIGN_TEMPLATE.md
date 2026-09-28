# Design doc: <component>

Copy this to `docs/<phase>-<component>.md` and fill it in **before** you write
code for that component. The point is to commit to a design on paper so you're
the one making the system-design decisions.

## Problem
What does this component do, in one paragraph? What are its inputs and outputs?

## Requirements & constraints
Latency budget, correctness bar, data volume, failure tolerance.

## Options considered
List 2–3 real approaches. For each: how it works, pros, cons.

## Decision
Which one, and **why**. This is the paragraph you'll defend in an interview.

## Failure modes
How does it break? What's the fallback / degraded behavior?

## How I'll measure it
The metric(s) that tell you it works. Tie back to the RAGAS / benchmark tables.

## Open questions / TODO
What you're deferring and why.
