---
name: i18n-audit
description: Audit software for i18n readiness — hardcoded strings, locale date/number/currency formatting, ICU plurals, pseudolocalization, RTL/bidi, fallback chain. Internationalization, not UX copywriting.
---

# i18n-audit

> Internationalization is an architecture property, not a translation task. Find the places the code assumes one language, one region, one text direction — before a locale launch does.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A product is going (or might go) multi-locale and you need an i18n-readiness assessment.
- The user asks about i18n/l10n, translations, RTL, pluralization, or locale formatting.
- A workflow invokes `polymath-frontend:i18n-audit`.

This audits *internationalization readiness*. It is not UX writing/microcopy (design), accessibility (`polymath-design:a11y-audit`), or general localization-of-content marketing.

## Inputs

- The codebase or paths to audit (required) and the i18n library in use, if any (react-intl, i18next, ICU4J, gettext, …) — detect it from dependencies before assuming none.
- Target locales (optional, default: the next planned locale plus one RTL locale, so RTL readiness is always assessed).
- Translation workflow facts (optional): TMS, who translates, release cadence.

## What to check

- **Hardcoded strings** — user-facing text in code/templates instead of resource bundles; concatenated sentences (untranslatable word order).
- **Locale formatting** — dates, numbers, currency, units, time zones formatted with hardcoded patterns instead of locale-aware APIs (ICU/Intl).
- **Plurals & gender** — `count + " items"` instead of ICU MessageFormat plural/select; languages have 1–6 plural forms.
- **Text expansion** — fixed-width UI that breaks when German/Finnish run +35%; truncation/clipping risk.
- **RTL / bidi** — Arabic/Hebrew mirroring, logical vs physical CSS properties, bidi isolation of interpolated values.
- **Fallback chain** — locale → language → default; missing-translation behavior (no blank/​key-leak).
- **TMS workflow** — how strings get extracted, sent for translation, and re-imported; pseudolocalization in CI to catch hardcoding early.

## Procedure

1. Scan for hardcoded user-facing strings and sentence concatenation; cite locations.
2. Flag non-locale-aware date/number/currency formatting.
3. Check pluralization/gender handling against ICU MessageFormat.
4. Assess UI for text-expansion and RTL/bidi readiness.
5. Verify a fallback chain and missing-translation behavior.
6. Recommend the extraction → TMS → import loop and pseudolocalization in CI.
7. Rank findings by launch-blocking severity (BLOCKER → MAJOR → MINOR), then by file path, and write them in the Output shape.

## Output

```text
i18n audit: web-checkout (react, react-intl present but partly unused)   targets: de-DE, ar-SA

BLOCKER  src/cart/Summary.tsx:41      `${count} items` concatenation → <FormattedMessage id="cart.items"
                                     defaultMessage="{count, plural, one {# item} other {# items}}" />
BLOCKER  src/checkout/Total.tsx:18    price.toFixed(2) + " €" → new Intl.NumberFormat(locale, {style: "currency", currency})
MAJOR    src/layout/*.css (14 rules)  margin-left/right → margin-inline-start/end (RTL mirroring)
MAJOR    src/cart/Promo.tsx:9         fixed 120px button width → min-width; de-DE runs ~35% longer
MINOR    src/i18n/index.ts:5          missing-key fallback shows the key → fall back to en-US, log the miss

Fallback chain: ar-SA → ar → en-US (en-US is the source locale)
Pipeline: extract with formatjs CLI in CI → TMS → import on merge; pseudolocalization (en-XA, ar-XB) run in CI e2e
Counts: 23 hardcoded strings · 4 non-locale-aware formats · 2 plural bugs · 14 physical CSS properties
```

## Quality bar

- Every finding cites a location/pattern and a concrete fix, not "add i18n".
- Pluralization is judged against ICU forms, not naive `+ "s"`.
- RTL/bidi and text-expansion are assessed, not just string extraction.
- A pseudolocalization-in-CI recommendation is included so regressions are caught automatically.
