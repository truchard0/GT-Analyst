---
name: report-writing
description: How GT-Analyst reports are written so they are eloquent and easy to follow - the prose voice for every user-facing report, note and Claude Doc. Fourteen techniques (bottom line first, a cold open on a concrete scene or contradiction, the finding's number in titles, familiar units, arrow-chain mechanisms, worked arithmetic, scenarios with "breaks if", numeric tripwires, the strongest counter-case, a scorecard that keeps its misses, analogies with their limits, one idea per paragraph, plain words, a dated watch-list ending), each with how to apply it and an AI-trade example, plus what not to do. It sets the voice only; the CLAUDE.md REPORT STYLE rule (key-calls table first, no internal machinery in the body, visuals, docx and pdf) still governs structure and delivery.
---

# REPORT WRITING - the house voice

A report is read once, quickly, by someone who has to decide something. After one pass the reader should be able to
say back the call, the reason and what would change it. Every technique below serves that. They are our own practice:
never imitate, quote or cite an outside commentator's voice, phrasing or framing, and never present a view as
someone's "lens". State mechanisms in our own words and cite primary sources (filings, official data, wires).

## The techniques

### 1. Bottom line first
- **What:** the opening paragraph gives the call, its odds and its date. Everything after supports it.
- **Why:** readers stop early, and one paragraph should still give them the answer. It also makes the writer find
  the answer before writing.
- **How:** sit the bottom line right under the key-calls table. Open every section with its own one-line conclusion
  and close it with what that means for the call.
- **Example:** "We expect a slower 2027 for AI building, not a break. The chance that total 2027 capex falls is 20%,
  and the first test is the big buyers' capex guides in late January."

### 2. Cold open on a concrete scene or a contradiction
- **What:** the first section starts with a dated moment, ideally two facts that should not both be true.
- **Why:** a tension makes the reader want the mechanism that resolves it. Abstractions do not.
- **How:** find the day the thesis became visible, state both facts with numbers, then promise the explanation.
- **Example:** "On 17 November the largest AI-chip supplier reported a quarter $6.7bn above forecasts. Five days
  earlier a company that rents out those same chips also beat its forecasts, and by the next morning it had lost about
  a fifth of its value. One sells to buyers with cash; the other borrows to build."

### 3. Put the finding's number in the title
- **What:** titles, subtitles and chart titles state the finding with its number, not the topic.
- **Why:** a reader who skims only the headings still gets the report, and the number makes each claim checkable.
- **How:** rewrite every topic heading as a result. Chart titles are sentences with numbers, which the REPORT STYLE
  rule already requires.
- **Example:** not "Hyperscaler capex" but "Capex now uses almost all operating cash: about 100%, against a 40%
  ten-year norm."

### 4. Convert big numbers into units the reader already holds
- **What:** restate a headline figure as a share, a multiple, a weekly rate or a comparison with something known.
- **Why:** "$108.5bn" means little to most readers; "almost a full quarter of revenue" lands.
- **How:** give every number above a billion, or below one percent, a conversion in the unit the decision uses.
- **Example:** "Nvidia's lease guarantees, $108.5bn, come close to a full quarter of its revenue, $115.8bn. The export
  rule's threshold of 12 million TPP is about 750 H100s, one mid-sized cluster."

### 5. Write the mechanism as an arrow chain
- **What:** before the prose, write one line of cause and effect.
- **Why:** each link can be checked separately, and the reader sees where the argument could break.
- **How:** write one chain per mechanism, 3-6 links, each a measurable thing. Draw it as the diagram, then give one
  paragraph to each weak link.
- **Example:** "Fed hike → 10-year above 5% → dearer debt for builders without spare cash → fewer new sites signed →
  lower 2027 capex guides → slower orders at chip suppliers two to three quarters later."

### 6. Show the arithmetic on one line
- **What:** input, parameter and output in one sentence the reader can redo.
- **Why:** it turns an assertion into a calculation and exposes the assumption.
- **How:** use one parameter where you can, say where it comes from, and round honestly.
- **Example:** "Nvidia guides $130bn for a 14-week quarter, $9.3bn a week. Last quarter was $115.8bn over 13 weeks,
  $8.9bn a week. The weekly pace rises about 4%, not the 12% the headline suggests."

### 7. Scenarios, each with odds and a "breaks if"
- **What:** two to four named futures, each with a probability, what it needs, and the observable that would end it.
- **Why:** the reader sees the whole spread of outcomes and knows which news matters. "Breaks if" is the falsifier in
  plain words.
- **How:** make the odds sum to about 100 and every "breaks if" dated and measurable. Draw the scenarios as a tree.
- **Example:** "Slower 2027 (47%): the big buyers keep building, but at under 25% growth. Breaks if all four guide 2027
  capex up 30% or more in late January."

### 8. Tripwires with numbers
- **What:** a short list of levels that would change the view, each with today's reading.
- **Why:** it gives the reader a dashboard, and it commits the writer in advance.
- **How:** give the level, today's reading and the gap between them. Use closing levels, not intraday touches.
- **Example:** "We change the financing view if two of these trip: CoreWeave's five-year CDS closes above 1,289bp
  (now about 1,113bp); a new neocloud loan prices above 10% (last 7-7.5%); the 10-year closes above 5.25% (now 5.10%)."

### 9. Face the strongest counter-case with its best number
- **What:** give the opposing view its strongest evidence early, then say why the call survives or how it bends.
- **Why:** readers trust a report that has already met the objection they were about to raise.
- **How:** write one paragraph that opens on the other side's best number. Answer with data, not adjectives. If you
  cannot answer it, lower the odds.
- **Example:** "The best case against us: big-buyer capex runs near 100% of operating cash flow, the kind of stretch
  that preceded the 60% cut by debt-funded telecom carriers after 2000. Our answer: the four largest buyers still have
  balance sheets, and the cut risk sits with the borrowers. That is why we put a 2027 decline at 20%, not 50%."

### 10. Keep a scorecard that includes the misses
- **What:** a table of past calls with their odds and outcomes, misses included, each with its lesson.
- **Why:** only a record that shows its misses is worth believing, and it tells the reader how far to trust today's
  odds.
- **How:** every major report carries the calls resolved since the last one. Each miss gets a one-line diagnosis.
- **Example:** "Across 117 revenue reports our number missed by a median 1.5%, closer than the companies' own guides
  (2.4%). It did worse than the guide on Micron, where slowing price gains caught us out."

### 11. Use an analogy only with its limits
- **What:** a historical or everyday comparison, followed by where it fails.
- **Why:** an analogy carries intuition quickly but smuggles in false conclusions when it is left unqualified.
- **How:** one sentence for the likeness, one for the difference, one for what the difference implies.
- **Example:** "The build looks like the 1990s fibre boom: spending ran ahead of revenue and suppliers financed their
  customers. Unlike fibre, today's capacity is rented within months and rents are rising. The risk is a funding
  squeeze, not a glut of idle capacity."

### 12. One idea per paragraph
- **What:** each paragraph makes one point, stated in its first sentence.
- **Why:** readers skim first sentences, so the skim becomes the argument.
- **How:** if a paragraph needs "also", split it. Keep paragraphs under about 80 words and use bullets for parallel
  items.
- **Example:** split one paragraph that covers guarantees, a CEO's exit and an export rule into three, opening "Nvidia
  now underwrites part of its customers' building", "The chief executive who built that system resigned on 12
  November" and "The 16 November rule closes the offshore route".

### 13. Plain words; define a term once
- **What:** short words and active verbs. Define every term at first use and then keep one name for one thing.
- **Why:** the reader gets precision without effort. A defined term is a handle; an undefined one is a wall.
- **How:** write "companies that rent out AI chips (neoclouds)" the first time and "neoclouds" after. Write "funding",
  not "capital formation dynamics".
- **Example:** "A debt-funded builder is a company whose capex exceeds its free cash flow, so every new site needs a
  loan."

### 14. End on a dated watch-list
- **What:** the last section lists the next dated events, what each would show and which call it moves.
- **Why:** the reader knows when to look again, and the report becomes a calendar.
- **How:** in date order, give the date, the event, what we expect and which way it moves the odds. Draw it as the
  catalyst timeline.
- **Example:** "9 Dec, Fed: we expect a hike (93%); holding would ease funding for the debt-funded builders. Late
  January, capex guides: any of the four guiding below 2026 raises our decline odds."

## Words and numbers must agree

| Odds | Say |
|---|---|
| 40-60% | "no call" (state the odds, take no side) |
| 60-75% | "likely", "we lean" |
| 75-90% | "we expect" |
| above 90% | "near-certain"; never "certain", "guaranteed" or "impossible" |

The same bands run downward: a 25% event is "unlikely", not "possible but risky".

## What not to do

- **Hype.** Adjectives instead of numbers ("explosive", "generational"), urgency selling ("the next ten days decide
  everything"). Imminence that keeps not arriving destroys trust in every later call.
- **Undated calls.** "AI will disappoint" has no date and cannot be scored. Every call carries odds, a date and what
  would prove it wrong.
- **Scorecards that keep only hits.** Scoring yourself selectively is worse than not scoring at all.
- **Motive as cause.** "They did it to protect their position" or "it was planned". Explain through incentives and
  procedures, never through imputed intent or plots.
- **Certainty words with odds that disagree.** "Certain" beside 70%, or "likely" beside 30%. Use the table above.
- **Touch-based targets.** Not "the chip index hits 520" but "closes above 520 on 30 June 2027".
- **Unlabelled scenarios.** A future told as a story must say plainly that it is a scenario.
- **Banned calls.** No war-driven oil, energy, defense or tanker price calls, and price direction stays a no-call
  outside the ai-trade exceptions.
- **Borrowed authority.** Never "X argues" or "on Y's view". Restate the mechanism and cite the data.

## How this fits the REPORT STYLE rule in CLAUDE.md

This skill changes the prose voice, not the rules.
- **Order:** the key-calls table still comes first, with the bottom line (1) beside it. The cold open (2) starts the
  first section, and the watch-list (14) and conclusion end the body.
- **No internal machinery in the body:** no "engine", ledger IDs, mechanism-library rule IDs, skill sections, gates or
  conviction tables. They go in the separate appendix of desk records in the repo copy.
- **Visuals:** arrow chains (5) become mechanism diagrams, scenarios (7) become the drawn tree, and the watch-list (14)
  becomes the dated catalyst timeline. Every chart title states its finding with its number (3).
- **Delivery is unchanged:** a Claude Doc with a markdown copy in `reports/`, exported to docx and pdf, with the
  chart-count check on `word/media/`.
