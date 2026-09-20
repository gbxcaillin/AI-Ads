# AI-Ads

Video and image ads for GBX Professional Services, made from AI-generated clips (OpenArt), real screen captures of the product, one generated narration take and one generated music bed, stitched with ffmpeg.

The workflow is the `ai-commercial` skill in `.claude/skills/ai-commercial/`. `CLAUDE.md` says how this repo uses it and which connectors do what.

## Spots

| Spot | Status | Length | Notes |
|---|---|---|---|
| `spots/gbx-commercial/` | reference cut approved (720p) | 36.6 s | six clips, one narrator, one bed; see its `spot.json` |
| `spots/brightday-every-stage/` | script and clip table drafted, awaiting sign-off and assets | about 38 s | Brightday brand film, direction A; nothing generated yet |

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

## 9:16 social version

Compose the 16:9 clips for the centre third from the first draft (SKILL.md, "Compose every 16:9 clip for the 9:16 crop"), then build the portrait cut from the approved landscape cut:

```bash
cd spots/gbx-commercial
python3 ../../.claude/skills/ai-commercial/scripts/reframe-9x16.py reference/gbx-commercial-cut-720p-1.mp4 reframe-9x16.json out/gbx-commercial-9x16.mp4
```

## Starting a new spot

Copy `templates/spot.template.json` to `spots/<name>/spot.json`, fill in the script and direction first, and agree the clip table before generating anything.
