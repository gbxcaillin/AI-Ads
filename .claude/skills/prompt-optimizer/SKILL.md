---
name: prompt-optimizer
description: >-
  Consult this skill whenever the user is working on the wording of a prompt to
  generate something with an AI model — writing one from a rough idea, improving
  or optimizing an existing prompt, or fixing one that gives wrong results
  (garbled text, missing detail, generic output). Covers image models (Flux,
  Midjourney, GPT Image, Nano Banana, Seedream, Qwen Image, Recraft…), video
  models (Veo, Sora, Kling, Seedance, Hailuo, Wan, LTX, PixVerse, Vidu…), and
  text/LLM work including games and single-file HTML apps (Claude, ChatGPT,
  Gemini, Grok). Use it even when the user only pastes an idea and names a
  model, asks "what's a good prompt for X" or "how should I prompt X for Y", or
  hasn't picked a model yet. These per-model conventions aren't obvious from
  general knowledge, so reach for this skill instead of writing the prompt from
  memory. Do NOT use it for writing code that calls a generation API, buying
  camera gear, translating an existing prompt, or comparing model prices.
---

# Prompt Optimizer for Generative AI Models

Different generative models want to be prompted in genuinely different ways. A
phrase that helps Flux hurts Kling; a keyword pile that works on an SDXL
checkpoint is ignored by GPT Image; an XML-structured brief that Claude loves
will confuse a diffusion model. This skill turns a user's rough idea into a
prompt shaped for the **specific model they're targeting**, and — just as
importantly — hands back the *why* so they can refine it themselves.

## The single most important principle

**The optimized prompt is a starting example; the guide is the product.** A
generated prompt full of fixed enhancement phrases ("golden hour rim light…")
looks authoritative but is only a reasonable default. What actually makes
someone better at prompting a model is understanding *how that model wants to
be prompted*. So always deliver two things side by side:

1. **A starting-example prompt**, optimized for the target model.
2. **The prompting guide** for that model — the conventions, vocabulary, and
   gotchas — presented as the main event, not a footnote.

Frame the prompt as "a starting point to tweak using the guide," never as a
finished, optimal artifact.

## Workflow

### 1. Identify the target model, its family, and its type

Ask or infer: which model, and is it **video**, **image**, or **text/LLM**?
Map the model to its *family* (the provider/architecture line), because
conventions are shared within a family, not per version:

| Type | Families (see reference file) |
|------|-------------------------------|
| Video | Seedance, MiniMax/Hailuo, Kling, Veo, Sora, Wan, LTX, PixVerse, Vidu, HappyHorse, Gemini video, Grok Imagine |
| Image | Flux, GPT Image, Nano Banana, Seedream, Qwen Image, Recraft, Kling, Wan, Grok Imagine, Juggernaut, DynaVision, OpenArt, Z-Image |
| Text/LLM | Claude, ChatGPT/GPT, Gemini, Grok |

If the exact model isn't in the references, pick the closest family (e.g. any
SDXL checkpoint → the Juggernaut/SDXL conventions; any Midjourney-style service
→ the image principles below) and say so.

### 2. Read the matching reference file

- Video → `references/video-models.md`
- Image → `references/image-models.md`
- Text/LLM → `references/text-models.md`

Each file has the per-family conventions, negative-prompt behavior, and the
research-backed tips that become the guide.

### 3. Optimize — the method depends on the type

**Image & video** — enhance without overwriting. Keep the user's subject and
intent intact, then *only add what's missing*:

- Detect what the user already specified (lighting, camera, motion, audio,
  materials, style, photography terms, literal text). Never duplicate an
  element they already gave.
- Add missing elements using **mood-appropriate** choices, not blind defaults.
  Read the scene and pick fitting enhancements — see *Mood-aware enhancement*
  below. A neon night alley gets neon lighting; a sunset gets golden light; a
  high-energy action shot gets dynamic lighting. Do **not** staple "golden
  hour" onto everything.
- Apply family-specific rules from the reference file: strip quality tags
  (masterpiece, 4k, best quality) for models that ignore them; strip weight
  syntax `(token:1.4)` for models that don't support it; wrap literal
  text-to-render in double quotes; convert to present tense for video.
- Handle the negative prompt per the model: some support it, some ignore it
  (rewrite negatives as positives — "sharp focus" not "no blur"), some have no
  parameter.

**Text/LLM** — restructure, don't decorate. Rebuild the rough prompt into the
architecture the family responds to (details in `references/text-models.md`):

- **Claude** → XML-tagged sections (`<task>`, `<context>`, `<constraints>`),
  a role line, rationale attached to constraints, an explicit ambition level,
  and a closing self-check.
- **ChatGPT/GPT** → Markdown sections (`# Role and Objective`, `# Instructions`,
  `# Output Format`), no contradictions, an anti-cliché ban-list for creative
  work, explicit verbosity control.
- **Gemini** → concise Persona / Task / Context / Format, context first and the
  ask last.
- **Grok** → a lean, surgical spec plus an "list your assumptions separately"
  clause and an iteration plan.
- If the prompt is about building a **game or interactive app**, inject the
  game formula (core loop, controls, win/lose, the self-contained-HTML
  constraint block, acceptance tests) — see the reference file.

### 4. Deliver the prompt and the guide together

Present the optimized prompt, then the model's prompting guide as prominent
bullets (the actionable vocabulary — camera moves like *dolly/orbit/push*,
structure formulas, emphasis syntax — is what the user should be learning).
Close by noting it's a starting point they shape with the guide.

## Mood-aware enhancement (image & video)

When you need to add lighting/atmosphere, first read the scene's mood and pick
a fitting option instead of a fixed default. Detect from the prompt text:

- **neon** — neon, cyberpunk, synthwave, arcade, hologram → neon/cyberpunk glow
- **energetic** — energy, electric, lightning, magic, evolving, power → dynamic
  high-contrast lighting with glowing accents
- **epic** — fantasy, dragon, battle, storm, space, cosmic → dramatic
  volumetric light, god rays, deep contrast
- **warm** — sunset, sunrise, golden hour, dawn, dusk, cozy, candle → golden
  rim light, warm low sun
- **night** — night, midnight, dark, moonlit, noir → low-key moonlit / cool
  nocturnal lighting
- **nature** — forest, mountain, ocean, meadow, landscape, outdoor → soft
  natural daylight, dappled or overcast
- **studio** (fallback) — portraits, product, indoor, or no cue → clean
  studio / balanced key-and-fill

Phrase the choice in the family's register: **cinematic** for video,
**photographic** for photo-real image models, **stylized** for design/
illustration models (Recraft, DynaVision). Offer to re-roll a different fitting
option if the user wants variation — the point is that it *fits the subject*
and *isn't the same every time*, never that one default is "correct."

## Why this matters

Newer models do exactly what you ask and no more, so unstated scope yields
minimal output; blind defaults produce generic "AI slop"; and a prompt handed
over without its reasoning teaches nothing. Optimizing *with the guide visible*
turns each generation into a lesson in prompting that model well.
