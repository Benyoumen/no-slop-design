---
name: design-tokens-starter
description: A minimal set of design tokens that keeps a mockup consistent when there is no design system yet: one or two type families, a five-step type scale, two weights, a spacing scale from 4 to 48, one accent plus alpha grays plus four state colors, two radii, one shadow, with light and dark values. Use at the start of any mockup or prototype, when a generated page has drifted into many sizes and colors, or to decide what to adapt when a real design system exists.
license: MIT
metadata:
  version: "1.0"
  author: Benjamin Tayar
  method: no-slop-design
---

# Design tokens starter

> Consistency is a small number of decisions made once. Tokens are where they live.

## When to use

- Starting a mockup or a prototype with no design system to inherit.
- A generated page has nine font sizes and six pastels and nobody chose any of them.
- Handing a mockup to a developer who asks "which blue".
- Adapting the mockup to a company's real design system.

## Inputs

1. The screen type: operator screen used all day, or a page read once. Density differs; the tokens do not.
2. The accent, if the brand has one, and the ink and paper it must sit on.
3. The real design system's tokens, if one exists, to map onto these names.

## Procedure

1. **Copy [`templates/tokens.css`](../../templates/tokens.css)** to the top of the generator's stylesheet. Change values, not names.
2. **Pick the ink and the paper first.** Measure their contrast; the body pair must be above 7:1 so that alpha grays derived from the ink still pass at 4.5:1.
3. **Pick one accent.** Measure white and black on it; use whichever ink passes 4.5:1. The accent appears on the one control that commits the action, nowhere else.
4. **Keep the type scale closed**: five steps for a tool (13, 15, 18, 24, 32 px is the starter), two weights (400 and 600). A size outside the scale becomes a step or goes back.
5. **Use the spacing scale everywhere**, including inside components: 4, 8, 12, 16, 24, 32, 48.
6. **Derive grays from the ink with alpha**, never as separate hex values, so they survive a change of surface.
7. **State colors mean state.** Success, warning, danger, and one neutral. Never decoration.
8. **Write the dark values** at the same time, under `prefers-color-scheme: dark`, and check the same contrast pairs.
9. **When a real design system exists**, map its tokens onto these names and delete the starter values. The names stay, so the generator does not change.

## Rules

- One file holds every color, size, space, radius and shadow. Nothing literal elsewhere.
- One accent. A second accent is a decision written into the rule, not a habit.
- Grays are alpha of the ink.
- Two weights. Bold is hierarchy; a third weight is noise.
- One shadow, for the one layer that floats. Flat at rest.
- Contrast is measured for every pair, light and dark, before the first screen is rendered.
- Tabular numbers in any column of numbers.

## Checklist

- [ ] Ink on paper measured above 7:1 in both schemes.
- [ ] Accent ink chosen by measurement, above 4.5:1.
- [ ] Five type steps, two weights, nothing outside them.
- [ ] Spacing scale used in components, not only between sections.
- [ ] Grays as alpha of the ink.
- [ ] Four state colors measured on paper and on surface.
- [ ] Dark values present and measured.
- [ ] Mapping to the real design system written, if one exists.

## Example

Acme Field Sales Assistant.

Weak: the generator has `#333`, `#444`, `#555` and `#666` for text, `#7C3AED` on buttons and `#A78BFA` on badges and `#EDE9FE` on chips, sizes 11, 12, 13, 14, 15, 16, 18, 20, 22 and 28. Dark mode was never tried.

Corrected: ink `#1C2230` on paper `#F5F6F8` (14.7:1), grays as `rgba(28, 34, 48, .72 / .56 / .30 / .12)` where only the .72 gray carries body text (6.1:1) and the .56 gray is kept for large text and icons (3.7:1), one accent `#2446A6` with white ink (8.4:1) on the one button that writes to the CRM, success, warning, danger and neutral measured on paper (5.1:1 to 6.2:1), five sizes, two weights, and the dark scheme with the same pairs measured (7.3:1 and above). The gallery screens on this site are rendered from exactly these values.

## Definition of done

One tokens file, every pair measured in light and dark, no literal color or size outside it, and a written mapping if a real design system exists.

## Related

- [`html-mockup`](../html-mockup/SKILL.md): where the tokens are used.
- [`visual-slop-audit`](../visual-slop-audit/SKILL.md): tells 8, 9 and 10 are what these tokens prevent.
- [dense-operations-ui](https://github.com/Benyoumen/agent-design-principles/tree/main/skills/dense-operations-ui): the single accent, ink on accent, alpha grays and closed scale rules this starter implements.
- Template: [`templates/tokens.css`](../../templates/tokens.css).
