---
name: component-design
description: Design a UI component's contract — props, state, side effects, a11y, and the smallest set of tests that locks the contract.
---

# component-design

> Design a component before writing its implementation. Output is a contract sketch the implementer can build from in one pass.

## When to use

- A new component needs to be designed before code.
- An existing component has unclear responsibilities ("what does this do?").
- A workflow invokes `polymath-frontend:component-design`.

## Inputs

- Component name + purpose (one sentence).
- Where it lives in the screen / flow.
- Known design-system primitives to reuse.

## Procedure

1. **Single responsibility** — what is this component for, in one sentence. If you need "and", split it.
2. **Props contract** — required vs optional, with type. Discriminate against:
   - String props that should be enums.
   - Booleans that should be enums (e.g. `variant: "primary" | "secondary"` beats `isPrimary + isSecondary`).
   - "God object" props that smuggle in unrelated concerns.
3. **State ownership** — does state live here, in a parent, in a store, or in the URL? Default to "the highest level that needs it".
4. **Side effects** — list them. Each one names the trigger and the cleanup.
5. **Accessibility contract** — role, name, keyboard reachability, focus management. Reference WCAG 2.2 AA SC numbers if relevant.
6. **Test contract** — three tests that lock the contract:
   - Renders required content with required props.
   - One state transition (the most user-visible).
   - One a11y assertion (role + name).
7. **Empty / error / loading states** — define each explicitly. "No data" is a state, not a bug.

## Output

```text
Component: <Name>

Responsibility: <one sentence>

Props:
  required
    - <name>: <type> — <purpose>
  optional
    - <name>: <type> — <purpose>

State: <where it lives, why>

Side effects:
  - on <trigger> → <effect>; cleanup: <how>

A11y:
  - role: <role>
  - name: <derived from prop or aria-label>
  - keyboard: <key bindings>
  - focus: <management>

Tests (3, contract-locking):
  1. <test name>
  2. <test name>
  3. <test name>

States:
  loading: <visual> 
  empty:   <visual> 
  error:   <visual> 
```

## Anti-patterns to avoid

- Two booleans where an enum would do.
- Components named for their position (`LeftPanel`) instead of their purpose.
- Tests that snapshot the whole DOM instead of asserting behaviors.
