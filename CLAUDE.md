# AI-Ads

This repository is the workshop for GBX Professional Services video and image ads built from AI generation (OpenArt) plus real screen captures, and finished with ffmpeg. One folder per spot under `spots/`. The workflow lives in the `ai-commercial` skill under `.claude/skills/`; read its SKILL.md before touching a spot.

## What is where

| Path | Purpose |
|---|---|
| `.claude/skills/ai-commercial/` | The production recipe: SKILL.md, `references/` (conventions with sources, prompts that worked, lessons from the drafts), `scripts/` (stitch, narration splitter, screen recorders, embedded site fonts) |
| `spots/<spot>/spot.json` | Source of truth for a spot: script, voice direction, shared style, every clip's prompt and mode, OpenArt ids, edit knobs, edit notes, lessons. Update it every round. |
| `spots/<spot>/audio/` | The committed one-take narration and music bed as `.m4a` |
| `spots/<spot>/reference/` | Approved cuts kept for reference (the only rendered video committed) |
| `spots/<spot>/captures/`, `reframe-9x16.json` | Screen captures (landscape and portrait) and the spec that turns the approved 16:9 cut into the 9:16 social version |
| `spots/<spot>/clips/`, `out/`, `frames*/` | Generated clips and preview renders. Ignored by git; they live in OpenArt and the editor's project. |
| `templates/spot.template.json` | Starting point for a new spot |
| `scripts/setup.sh` | Installs ffmpeg (via imageio-ffmpeg); `--full` adds faster-whisper and playwright-core |

## Connectors and what each is for

- **OpenArt** (`openart_*`): all generation. Video drafts on `byte-plus-seedance-2-5` text2video at 480p, 7 s, `generateAudio: false`; 1080p only for approved finals. Narration and music are one 30 s take each on a plain gradient carrier. Call `openart_model_cost` and quote the price before any batch. Past generations are listed with `openart_creation_list`; downloads come from the `url` in each item.
- **Canva**: static ad formats, social tiles and end-card artwork from the brand kit. Export at the size the platform wants.
- **AdWhispr Ads**: competitor ad research and campaign launch on Meta, TikTok and Google once a cut is approved. Never launch or change budgets without an explicit ask.
- **Dropbox / Google Drive / SharePoint**: delivering finals and collecting client assets (logo animation, brand fonts, product screenshots).
- **Microsoft 365**: review threads in Teams and Outlook; do not send mail unless asked.
- **GitHub** (`mcp__github__*`): this repo. No `gh` CLI in remote sessions.

## Working rules

- Follow the phases in SKILL.md in order: script and direction, picture clips, screen captures, one narration take, one music bed, stitch, verify, send. Do not generate before the script and clip table are agreed.
- Every clip prompt starts with the spot's `shared_style`; every voiced prompt includes `voice.direction`. Describe voices, never name a real person.
- Anything that must show the real product, site or logo is a screen capture, never a generation.
- Before sending any render: frame strip, silencedetect, loudness line, `yuv420p` check. Send with `SendUserFile` and a caption that states running time, loudness target and what changed.
- Quote OpenArt credits before a batch (reference prices in `spots/gbx-commercial/spot.json` under `costs`).
- Commit `spot.json`, the `.m4a` audio, capture MP4s and scripts. Do not commit generated clips or preview cuts.

## House style (GBX Professional Services)

- Write the firm's name in full: GBX Professional Services. Spell the address as G B X P S dot com in narration; www.gbxps.com on screen.
- No em dashes anywhere: prompts, captions, scripts, commit messages, this file.
- No financial advice claims. The firm teaches people about money and helps businesses run; it does not tell viewers what to invest in.
- Palette: dark charcoal, deep teal, warm off-white. Fonts on the site: Cormorant Garamond (serif italic for the philosophy line), Montserrat (eyebrows), DM Mono (address).
- The end card order is fixed: animated mark alone, then "Our philosophy" and the line "Combining insight with impact for sustainable business growth.", then www.gbxps.com.
