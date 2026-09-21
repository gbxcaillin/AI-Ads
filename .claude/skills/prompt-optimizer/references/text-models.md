# Text / LLM prompting reference

For LLMs you **restructure** the rough prompt into the architecture the family
responds to — you do not append decorative phrases. Templates below; the
family tips (with the negative-prompt note, which is always "not applicable")
follow as the guide.

## Restructuring templates

**Claude** — XML-tagged, role-led, rationale-attached, ambition stated:
```
You are [role].

<task>
[user's request]. Deliver a complete, [ambition level] result.
</task>

<constraints>
- [each constraint, with the why attached]
</constraints>

<guidelines>
- Commit to distinctive, specific choices over safe generic ones.
- Go beyond the basics: deliver a complete, fully-realized result.
</guidelines>

If anything is ambiguous, make the most reasonable assumption and note it.
Before finishing, verify the result against the task above.
```

**ChatGPT / GPT** — Markdown sections, contradiction-free, verbosity controlled.
Reasoning models (GPT-5 Thinking) get a high-level goal and NO step-by-step;
fast models (Instant, 4o) get an explicit "First plan…, then build…, then verify":
```
# Role and Objective
You are [role]. Build exactly what is specified; where unspecified, choose the
most reasonable option and state it.

# Task
[user's request]

# Requirements / Style Rules
- [concrete requirements]
- (creative work) Avoid "not just X, but Y" reframes; replace rhetorical
  emphasis with a fact, example, or mechanism. Vary sentence length.

# Output Format
[what to produce; "no preamble, no recap"]

# Final Instructions
Keep going until fully resolved; make reasonable assumptions and note them.
```

**Gemini** — concise Persona / Task / Context / Format, context first, ask last,
no filler:
```
Persona: You are [role].
Task: [imperative goal].
Context:
[all reference material]
Format: [output shape]; deliver the length the work deserves. If a sentence
sounds like a template, rewrite it. Verify every requirement before finishing.
```

**Grok** — lean, surgical, tone locked, assumptions listed separately, built to
iterate:
```
Role: You are [role]. Tone: [explicit].
Goal: [request]
Constraints:
- [only the relevant context; convert every adjective to a specification]
Output: the result, then any assumptions listed separately from what was
specified. We will refine in short follow-ups, so keep it easy to revise.
```

## Game / interactive-app formula (inject when the prompt is about a game)

Detect game intent (game, platformer, shooter, arcade, roguelike, RPG, puzzle,
playable, etc.) and fold this into whichever family template applies:

- **Role**: a developer who ships polished [genre] browser games.
- **Goal**: one sentence naming the game and the feeling/player fantasy.
- **Core loop**: the repeated ~60-second cycle (spawn → action → resolve → score).
- **Controls**: exact inputs (keyboard + touch), shown on screen at load.
- **Win/lose**: explicit victory and failure states; what game-over and restart do.
- **Must ship**: 3–5 mechanics, no more.
- **Tech constraints** (highest-leverage line): "One self-contained HTML file,
  inline CSS, vanilla JS, no external libraries, no build step. No image or
  audio files — draw all graphics with canvas primitives and synthesize sound
  with the Web Audio API, so it runs offline from a double-click.
  requestAnimationFrame with a fixed timestep. High score in localStorage."
- **Do-not-build list** to prevent scope creep (menus, settings, multiplayer…).
- **Edge cases**: name the genre's tricky rules (duplicate-letter coloring,
  solvable maze generation, precise collision — no tunneling or sticking).
- **Acceptance tests**: "Done when: [input] starts the game, the lose condition
  triggers, and restart fully resets score and state."

Common failure modes and the phrasing that prevents each: asset hallucination
(ban external files), scope creep (do-not-build list + "change only X"), silent
broken loops (acceptance tests + visible score from build one), physics bugs
(fixed timestep + precise-collision clause), unwinnable states (name the edge
case). Reliable fixes are structural constraints, not cleverer wishes.

## Comparative strengths (1–10, for recommending a model)

| Model | Creative writing | Game/app coding | Worldbuilding | Brainstorming | Instruction-following | Long documents |
|-------|:---:|:---:|:---:|:---:|:---:|:---:|
| Claude (Opus/Fable) | 10 | 9 | 9–10 | 8–9 | 10 | 10 |
| Gemini 3 Pro | 8 | 10 | 8 | 8 | 9 | 10 |
| ChatGPT / GPT-5 | 6 | 9 | 7 | 8 | 9 | 7 |
| Grok 4.1 | 9 | 7 | 9 | 9 | 7 | 6 |

Rough guide: Claude for prose and agentic coding; Gemini for one-shot web games
and huge-context work; GPT for spec-to-working-code; Grok for wild ideation and
worldbuilding, prompted lean and iterated fast.

## Family tips (the guide)

### Claude
Negative prompt: null (not supported — rewrite negatives as positives)
Tips:
- Claude follows instructions literally; state the ambition level ('go beyond the basics, fully-featured') or you get the minimum
- Structure prompts with XML tags: <task>, <context>, <constraints>, <examples>; Claude is trained to parse them
- Give Claude a role in the first line; one sentence measurably focuses tone and quality
- Put long reference material at the top and the actual request at the end (up to ~30% quality gain on long inputs)
- Attach the why to every hard constraint ('no external assets, because this must run offline'); Claude generalizes from rationale
- Say what to do, not what to avoid: 'write flowing prose paragraphs' beats 'do not use bullet points'
- For creative voice, paste a 2-3 paragraph writing sample to match rather than adjectives like 'vivid'
- Fight generic output with explicit aesthetic direction: named palette, typography, motion; ban the safe defaults
- Provide 3-5 diverse examples in <example> tags when format matters
- End with a self-check: 'Before finishing, verify the result against the constraints above'
- Use plain firm language; ALL-CAPS and 'CRITICAL: YOU MUST' cause over-triggering on newer Claude models
- For big builds, chain: design doc first message, implementation second, one targeted feature per message after

### ChatGPT
Negative prompt: null (not supported — rewrite negatives as positives)
Tips:
- Structure prompts with Markdown headers: # Role and Objective, # Instructions, # Output Format, # Context
- GPT-5 burns reasoning on contradictions; scan your prompt and resolve any conflicting instructions before sending
- In long prompts, state critical instructions at the beginning AND repeat them at the end
- Reasoning models (GPT-5 Thinking) want a high-level goal like briefing a senior colleague; skip 'think step by step'
- Fast chat models (Instant, 4o) want explicit steps spelled out: 'First plan..., then build..., then verify'
- Control verbosity explicitly: 'no preamble, no recap, at most 3 sentences after the code'
- Add persistence lines for multi-step work: 'keep going until fully resolved; make reasonable assumptions rather than asking'
- Ban the AI-voice patterns by name: 'avoid not-just-X-but-Y constructions; replace rhetorical emphasis with a fact, example, or mechanism'
- Anchor creative voice with a 100-300 word sample to match, never adjectives alone
- For iteration turns, scope the edit: name the exact element to change and cap the blast radius ('change only the jump physics')
- Use a self-reflection rubric for one-shot builds: 'first define what makes a world-class result, then meet that bar'
- Re-state formatting and style rules every few messages in long chats; compliance decays

### Gemini
Negative prompt: null (not supported — rewrite negatives as positives)
Tips:
- Use the PTCF structure Google recommends: Persona, Task, Context, Format
- Be concise and direct; Gemini 3 over-analyzes verbose, persuasion-heavy prompts, so keep instructions tight imperatives
- Context first, ask last: put all reference material above and the instruction at the very end
- Gemini defaults to terse output; explicitly ask for length or a conversational voice when you want it
- Include 1-2 few-shot examples with identical formatting; inconsistent example formatting produces malformed output
- Separate instructions from data with XML-style tags or Markdown headers
- Top-ranked at one-shot web games: give the full spec in one structured prompt and it follows every part
- Exploit the 1M-token context: paste an entire lore bible or design doc as context for consistent continuations
- Kill AI voice explicitly: 'avoid corporate jargon; if a sentence sounds like a template, rewrite it'
- If output disappoints, rephrase or reorder the prompt rather than adding pleading; strip filler words entirely
- End with a self-check: 'verify the result runs without errors and meets every requirement above'

### Grok
Negative prompt: null (not supported — rewrite negatives as positives)
Tips:
- Iterate fast instead of perfecting: three quick attempts with refinements beat one 30-minute mega-prompt
- Be surgical with context; include only the relevant material, never a whole project dump
- Grok is literal: convert every adjective into a specification ('fun' becomes 'tight controls, escalating waves, combo multiplier')
- Lock tone explicitly ('direct, no jokes') or Grok keeps its default wit
- Counter its confidence bias: require assumptions listed separately from confirmed behavior
- Structure with the community template: Role, Context, Goal, Constraints, Output Format, Tone
- Standout at worldbuilding systems: ask for histories, faction agendas, timelines, and family trees explicitly
- Lean into unconventional ideation: 'give me 10 mechanics no shipped game has tried'
- For code, get the working core loop first with placeholder shapes; polish in separate turns
- Steer with short corrective follow-ups: 'tighten this', 'fix the collision bug, change nothing else'
- For prose, supply a voice sample; Grok's default register drifts flat or jokey without one

