# Bakeoff cases

Bakeoff cases compare baseline Claude Code against Claude Code with a Polymath
plugin set installed. This is the evidence path for the claim that Polymath
improves real work rather than merely adding a larger catalog.

Static validation:

```bash
python3 tools/bakeoff.py check
```

Live run, requiring an authenticated `claude` CLI:

```bash
python3 tools/bakeoff.py run feature-from-idea-rate-limit
```

Each case has a 10-point regex rubric. The rubric is intentionally simple so
the same output gets the same score during review. It is not a replacement for
human review; it is a cheap gate that decides whether a result is worth deeper
inspection.
