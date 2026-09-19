# AI-Ads

Video and image ads for GBX Professional Services, made from AI-generated clips (OpenArt), real screen captures of the product, one generated narration take and one generated music bed, stitched with ffmpeg.

The workflow is the `ai-commercial` skill in `.claude/skills/ai-commercial/`. `CLAUDE.md` says how this repo uses it and which connectors do what.

## Spots

| Spot | Status | Length | Notes |
|---|---|---|---|
| `spots/gbx-commercial/` | reference cut approved (720p) | 36.6 s | six clips, one narrator, one bed; see its `spot.json` |

## Setup

```bash
scripts/setup.sh          # ffmpeg only
scripts/setup.sh --full   # plus faster-whisper and playwright-core
```

## Rebuilding a cut

1. Put the six clip files, `narration-all-lines.m4a`, `narration-lines.txt` and `music-bed.m4a` in one folder (for example `spots/gbx-commercial/clips/`).
2. Set `CLIPS` and the knobs at the top of `.claude/skills/ai-commercial/scripts/stitch-commercial.py` to match `spot.json`.
3. `python3 .claude/skills/ai-commercial/scripts/stitch-commercial.py spots/gbx-commercial/clips spots/gbx-commercial/out/cut.mp4`
4. Verify (frame strip, silencedetect, loudness) before sending, as SKILL.md Phase 7 describes.

## Starting a new spot

Copy `templates/spot.template.json` to `spots/<name>/spot.json`, fill in the script and direction first, and agree the clip table before generating anything.
