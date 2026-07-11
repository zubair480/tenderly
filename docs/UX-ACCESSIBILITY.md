# UX and accessibility plan

## Experience principle

Tenderly should feel like a thoughtful neighbor making a useful introduction—not a dashboard assigning a score. The visual system is warm, calm, and direct. The interface always answers the user’s next question before they need to ask it.

## Visual system

| Token | Direction | Accessibility rule |
| --- | --- | --- |
| Canvas | Cream/off-white, e.g. `#FBF7EF` | Background never carries meaning. |
| Ink | Near-black green, e.g. `#18332A` | Use for primary text; check 4.5:1 contrast on canvas. |
| Primary | Deep forest, e.g. `#205C4D` | Use white text only after contrast check. |
| Accent | Warm terracotta, e.g. `#B8533E` | Use for emphasis, not status alone. |
| Success/urgent | Dark enough semantic colors with icons/text | Never use hue as the only urgency signal. |
| Display type | Fraunces | Headings and moments of warmth only. |
| Body type | Inter | Controls, cards, long-form reading, and metadata. |

The layout uses a single centered content column with `max-width: 1100px`, a generous outer gutter, and a two-column result layout that collapses to one column on smaller screens.

## Interaction design

### Onboarding

- Make the upload zone a real button/label with a hidden file input—not a pointer-only drop target.
- State accepted formats and selected-file feedback in text.
- Chips use `aria-pressed` and clearly visible selected states.
- Segmented availability choices use radio inputs or a semantic radio group.
- Provide one primary submit action and place errors next to the relevant control.

### Profile reveal

- Loading copy rotates calmly; it does not imply that a model has read more than it has.
- Use a status region so assistive technology hears the current stage.
- The completed profile has a heading and a user-controlled next action.

### Recommendation cards

- Lead with the person-facing answer: “Why you” in a distinct quote-style block.
- Put supporting facts in a predictable metadata row.
- Pair each urgency color with words such as “High urgency.”
- Pair every ring/bar with exact percentage text such as “92% match.”
- On scenario changes, show a concise banner above the results: what happened, which kinds of roles moved, and a control to return to normal conditions.

## Accessibility acceptance criteria

### Semantics and keyboard

- Use `header`, `main`, `section`, `form`, `fieldset`, `legend`, headings in order, and button elements for actions.
- Provide a skip link to the onboarding/results content.
- Keep all interactive controls reachable in a logical Tab order; no custom click-only control is allowed.
- Escape closes any future modal; no focus trap is needed in the planned one-page flow.
- Focus state uses a high-contrast, 2px+ visible ring and is never removed without replacement.

### Screen readers and status

- Label each input and icon-only control.
- Use `aria-describedby` for file constraints and validation copy.
- Use `aria-live="polite"` for profile creation stages and match/surge update summaries; do not announce every animated element.
- Use accessible names that say purpose, e.g. “Simulate cold snap in San Francisco,” not “Toggle.”

### Visual and motion

- Maintain at least 4.5:1 text contrast and 3:1 contrast for meaningful UI boundaries/focus indicators.
- Do not use text below 16px for primary reading content.
- Preserve 44×44px minimum pointer targets where practical.
- Respect `prefers-reduced-motion`: render immediate rank changes or opacity-only transitions rather than layout motion.
- Avoid auto-playing media and do not make status copy depend on animation timing.

## Responsive checks

| Viewport | Required behavior |
| --- | --- |
| 375px | One column; full-width CTA; chips wrap cleanly; metadata stacks; no horizontal scroll. |
| 768px | Comfortable card width; pulse can follow results in normal document order. |
| 1440px | Main content remains capped; pulse sits beside rich cards without oversized line lengths. |

## Manual keyboard audit

1. Reload page and press Tab. Confirm skip link and hero CTA are visible.
2. Reach and operate upload using keyboard, then choose chips and availability without a mouse.
3. Submit and confirm the loading status is announced once per change.
4. Proceed to matches; read card content in logical order.
5. Trigger the cold-snap simulation and verify the new summary is announced.
6. Trigger each deliberate error state and reach its retry button.
