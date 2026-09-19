---
name: ai-commercial
description: End-to-end recipe for producing a short brand commercial (30 to 45 seconds) from AI-generated video clips, real screen captures of the product, one generated narration take and one generated music bed, stitched with ffmpeg into a reviewable cut. Use this whenever the user asks for a commercial, advert, promo video, brand film, explainer video, TV spot, social video ad, sizzle reel, or "a video for the website" from OpenArt, Seedance, Veo, Kling or any text-to-video model, even if they only ask for the prompts, only for one clip, only for the voice-over, or only to stitch clips they already have. Also use it when a generated clip has gibberish text, a lip-synced narrator, a wrong logo, jarring cuts, music that jumps or drops out, or pacing that feels rushed or slow. Those are the failure modes this skill was built to fix.
---

# AI commercial: from script to reviewable cut

This is the workflow that produced the GBX Professional Services spot: six clips of about seven seconds, one narrator, one music bed, about 36 seconds. It took many rounds of feedback to get right. Follow the order below and you skip most of those rounds.

The shape of the deliverable never changed, only the parts inside it:

1. A script of N short lines, one per clip (six worked well).
2. N picture clips, each about 7 seconds. Generated where nothing real needs to appear, screen-captured where the product does.
3. One narration take of all the lines in a single generation, split into lines afterwards.
4. One instrumental bed, a single take, stretched rather than looped.
5. A stitch that trims each clip to its line, dissolves between them, and mixes narration over the bed.
6. A verified 720p preview sent to the user for each round; 1080p finals only once clips are approved.

Keep a single JSON file as the source of truth for the spot (script, voice direction, shared style, every clip's prompt and mode, edit notes, lessons). Update it every round. It is what a future session reads to pick the work up.

## Professional defaults (apply without being asked)

These are the conventions broadcast and agency editors work to; the reasons and sources are in `references/conventions.md`. Defaulting to them removes most of the "it feels rushed / slow / messy" rounds.

- **Hook first, logo last.** No mark, name or product card in the first 3 seconds; about half an ad's value is decided there. The mark closes the spot on a 3 to 5 second end card, held at least 3 seconds.
- **Word budget.** A 30-second spot is 60 to 75 words at 2 to 2.5 words per second; a third of the runtime has no words at all. Time a read aloud, with the pauses, before trusting a count. For a 40-second web film the same script simply breathes more.
- **Shot rhythm.** Ads cut every 2 to 5 seconds and a shot needs 1.5 seconds to register. A 7-second clip that changes beat halfway (wide, then detail) sits closer to the convention than one held shot; ask for it in the prompt when the scene allows.
- **Cuts by default, dissolves as ellipsis.** Straight cuts when two shots share light and palette; a short dissolve (0.5 to 0.8 seconds) between generations that do not, which is most AI joins. Dip to black only around the end card; dip through white to leave a bright scene for a dark card.
- **Let the voice lead the picture.** A J-cut: each line starts while the previous picture is still dissolving out, so joins feel intended. Editors cut picture to the track, not the other way round.
- **Bed 18 to 20 dB under the voice.** Under 15 the music masks speech on phones; over 25 it disappears. Measure against the narration, not the mix.
- **Deliver to a loudness target.** Web: -14 LUFS, -1 dBTP. Broadcast: -24 LKFS, -2 dBTP (Australia OP-59 also wants 12 frames of silence head and tail and exactly 30.00 seconds). The stitch normalises in two passes; say which target you used in the caption.
- **Finish AI footage to match.** Lock palette and light in the prompt, then in the edit: upscale, 0.3 to 0.6 px blur, 8 to 15 percent grain, a film LUT at 60 to 80 percent, and match every clip to one hero frame. The stitch does not grade; note it as the editor's pass.

## Tools you need

- A text-to-video model with audio. The spot used OpenArt's `byte-plus-seedance-2-5` (text2video, 4 to 30 seconds, 480p drafts, 1080p finals). Check `openart_model_form_get` for the exact params before the first call, and `openart_model_cost` so you can tell the user what a round costs.
- ffmpeg. If it is not on PATH, `pip install imageio-ffmpeg` and use `python3 -c "import imageio_ffmpeg as f; print(f.get_ffmpeg_exe())"`. The bundled scripts do this automatically.
- Headless Chromium plus `playwright-core` for screen captures (Chromium cannot decode H.264, so the site's MP4 logo falls back to a GIF; the end card recorder sidesteps this by using extracted frames).
- `pip install faster-whisper` to transcribe the narration with word timestamps. It downloads the `small` model on first use.

Bundled in `scripts/`: `stitch-commercial.py`, `narration-lines.py`, `record-tools-clip.mjs`, `record-endcard-clip.mjs`, and `fonts/site-embedded.css` (the site's web fonts as data URIs, so headless Chromium renders real type; rebuild this file for a different site).

## Phase 1: script and direction first

Write the lines before any picture. Each line is one thought, 10 to 16 words, spoken in about 4 to 6 seconds; six lines is 60 to 75 words, the budget for a 30 that breathes at 36 to 40 on the web. Read them aloud in order with the pauses; the ad is the narration, the pictures illustrate it. Open on an image or a tension, never the mark; close on the mark, one line and one action.

Write two paragraphs that every prompt will reuse verbatim:

- **Shared style**: palette, grain, light, camera movement, who the people are, where they are, and the negatives (no stock smiles, no logos, no text of any kind on screen). Keep it under 90 words; it is prepended to every clip prompt.
- **Voice direction**: age, warmth, pace, accent lean, what it sounds like ("a trusted mentor over a coffee, not a presenter"). Describe the voice; never name a real actor or public figure. Models refuse or drift when asked to imitate a person, and the description gets the same feel.

Put both in the JSON under `shared_style` and `voice.direction`, and reference them in prompts as SHARED_STYLE and VOICE_DIRECTION. `references/prompts.md` has the ones that worked.

Agree the clip list with the user as a table: number, name, what is on screen, the line, and whether it is generated or captured. Anything that must show the real product, site, app or logo is a capture, not a generation.

## Phase 2: picture clips

Generate every clip as picture only (`generateAudio: false`) at 480p and 7 seconds. Audio comes later from the one-take narration, and five-second clips clip words. Cost per draft is a few hundred credits; say so before a batch.

Prompt rules that came out of the drafts (full list with reasons in `references/lessons.md`):

- Say "one continuous shot, one scene, no cuts" and describe people as in conversation with each other. Two half-scenes in one prompt come out disjointed.
- Say "absolutely no readable text, letters, words or numbers anywhere, on any wall, screen or paper". Screens still grow tiny labels; keep them turned away, blurred, or a plain gradient. A laptop facing the camera grows a screen on its lid unless you say "plain matte lid, no display on it, the screen faces the person".
- Rooms of people facing the lens read as a group photo. Ask for profiles and backs, a slow tracking move, "nobody looks at the camera".
- If someone on screen is meant to be talking, say their lips move and their voice is never heard, and generate picture only. The model lip-syncs any generated voice to whoever is visible.
- Where the scene allows, ask for two beats inside the one continuous shot (a wide that settles into a detail, or an arrival then an action) so the clip has the 2 to 5 second rhythm ads are cut to, without a second generation.
- Show outcomes people recognise, not abstract props. "Cards in slots" read as nonsense; "the office lights up as a network and the printer hands him the page" read instantly.
- One short line of on-screen text (a slide title) renders correctly if you ask for exactly that text, large, centred, and nothing else on the slide.

After each render, do not trust the thumbnail. Download it and build a check strip:

```bash
ffmpeg -y -i clip.mp4 -vf "select='eq(n\,6)+eq(n\,40)+eq(n\,80)+eq(n\,120)+eq(n\,160)',scale=512:-1,tile=5x1" -frames:v 1 check.png
```

Look at the strip yourself, then send the clip to the user with `SendUserFile` and a one-line caption of what it shows. Expect two or three rounds per clip. Record the prompt that finally worked in the JSON, and add a lesson if the fix was general.

## Phase 3: screen captures

Anything showing the real product is captured from the live build, frame by frame, at 24 fps. Playwright's video recorder freezes on first paint and Google Fonts do not load headless, so the recorders take one screenshot per frame with the fonts intercepted and served from `fonts/site-embedded.css`, then ffmpeg assembles the frames.

- `scripts/record-tools-clip.mjs`: a scroll through a page with a fake cursor, clicks, and a couple of wizard steps. Pace it to the line: total about 7 seconds, smooth eased scrolls, short holds. Serve the built site with `npx vite preview --port 4173` first.
- `scripts/record-endcard-clip.mjs`: the end card. Extract the real animated logo to frames first (`ffmpeg -i logo-animation.mp4 -vf fps=24 logoframes/l%04d.png`), then the recorder plays those frames, eases the mark up, fades in the philosophy line and the address, and runs a slow push-in the whole time so the card never sits as a frozen frame. It needs no server; everything is served from an intercept. Its text timings come from the `T6` environment variable so they can follow the narration (Phase 4).

Assemble with `ffmpeg -framerate 24 -i frames/f%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 out.mp4`. Never let a generated logo stand in for the real one; the user will notice immediately.

## Phase 4: one narration take

Generate all the lines in one 30-second text2video call on a silent-studio carrier: a plain drifting gradient, no people, no text, "no music, no sound effects, no ambience, the only sound is one narrator", VOICE_DIRECTION, then the lines separated by ellipses with "a clear pause between each line, every word completed, finishing before the end". One take means one consistent voice across the whole ad; per-clip generations each invent a slightly different voice.

Verify the read before using it. Transcribe with word timestamps and check every word is present and the last word ends before the file does:

```bash
python3 scripts/narration-lines.py narration.mp4 narration-lines.txt "first words of line 2" "first words of line 3" ...
```

That script transcribes with faster-whisper, finds where each line begins, and cuts each boundary in the middle of the nearest pause found by `silencedetect`. Do not cut at the word timestamps: they end early and clip the last syllable. The output file is one `start<TAB>end` per line and is what the stitch reads.

For the end card, take the onsets of the sentences inside its line (from the word list) and pass them to the recorder as `T6='{"up":2.0,"phil":2.5,"url":5.9}'` so each caption appears as it is spoken.

## Phase 5: one music bed

Generate a 30-second instrumental carrier with the same gradient picture. Prompts that read like a genre or a score ("ambient pad, piano motif, strings") get rejected by the output audio moderation filter as possible copyright. What passed: "an original, simple, quiet synthesiser drone, a single warm sustained pad tone that breathes slowly, with an occasional soft single piano note, no melody, no rhythm, no drums, no voices". Confirm it is instrumental by transcribing it; a "You You" hallucination on silence is fine, sentences are not.

Never loop a bed to cover the cut. The crossfade seam dips to near silence and lands in a voice gap where it is obvious. The stitch instead slows the single take slightly (`atempo`) to fill the whole length; a drone stretched 15 percent is imperceptible and seamless.

If moderation blocks every attempt, `ffmpeg -f lavfi -i aevalsrc=...` can synthesise a stacked-sine pad as a placeholder so the cut can still be reviewed.

## Phase 6: stitch

`scripts/stitch-commercial.py <clips-dir> <out.mp4>` does all of this from a folder holding the clip files, `narration-all-lines.m4a`, `narration-lines.txt` and `music-bed.m4a`. Set `CLIPS` at the top to the file names, then the knobs:

| Knob | Meaning | Value that worked |
|---|---|---|
| `LEAD` | seconds into a clip before its line starts | 0.35 |
| `CLIP_TAIL` | picture after the line ends, before the dissolve | 0.55 |
| `CLIP_EXTRA` | per-clip extra screen time, 0-based index | `{2: 0.5}` |
| `XFADE` | dissolve length | 0.7 |
| `WHITE_FADES` | 1-based clips whose dissolve into them goes through white | `{5}` (bright page into a black end card) |
| `BED_UNDER_DB` | bed level below the narration, measured against it | 18 (env; 18 to 20 is convention) |
| `LOUDNESS` | final two-pass normalisation target | `web` (-14 LUFS, true peak -1.5 so the codec lands under -1), `broadcast` (-24, -2.5) or `none` (env) |

Each clip is trimmed to `LEAD + line + CLIP_TAIL` plus one dissolve of real footage; the last clip keeps its full length so the end card can resolve. `LEAD` is smaller than `XFADE`, so every line starts while the previous picture is still dissolving out (a J-cut). After the mix, the file is loudness-normalised to the `LOUDNESS` target, video copied, so the level is right on the platform without touching the balance. Clips are pre-rendered to clean constant-frame-rate files first and only then dissolved. Trimming inside one big xfade graph (with `tpad` and a re-applied `fps`) produced variable frame rate and a broken chain that jumped to the end card at 6 seconds and went black; do not go back to that.

## Phase 7: verify, then send

Before every send, prove the cut with three checks, because the user cannot hear or see what you skipped:

```bash
# picture order: every clip in sequence, end card only at the end
ffmpeg -y -i cut.mp4 -vf "fps=1/3,scale=200:-1,tile=12x1" -frames:v 1 strip.png
# sound: no dead patch (expect only the final fade)
ffmpeg -i cut.mp4 -af "silencedetect=n=-45dB:d=0.8" -f null - 2>&1 | grep silence_
# a join that should flash: mean luminance across it
ffmpeg -ss 28.0 -i cut.mp4 -frames:v 1 -vf "scale=8:8,format=gray" -f rawvideo - | od -An -tu1
```

Also confirm the container is `yuv420p` (some players choke on 4:4:4), and read the loudness line the stitch prints (measured and normalised LUFS and true peak) so the caption can state the delivery target. Then `SendUserFile` the cut with a caption that says the running time and what changed since last round. Never describe a fix you have not rendered and checked.

## Reading feedback

The user reviews by watching, so complaints arrive as symptoms. What each one meant in practice:

| They said | It meant | Fix |
|---|---|---|
| "voice over barely stops before the next clip" | full-length clips under short lines, tiny crossfades | trim clips to their lines; longer dissolve |
| "pauses too long for an ad" | dead tails after each line | `CLIP_TAIL` down, dissolve 0.7 |
| "cuts are jarring", "fade to black is jarring" | dips through black between narrated clips | plain dissolve, no black |
| "music fades out too", "seems like six clips" | each clip's own music under its line | mute clips, one bed |
| "music cuts at 27 s" | loop crossfade seam in a voice gap | stretch the single take, never loop |
| "the presenter is doing the dialogue" | lip-sync to the visible speaker | picture only, mux the narration |
| "that isn't my logo" | generated mark | real logo frames in the end card |
| "clip 6 is just a frame" | end card holds after it builds | continuous push-in |
| "transition looks messy" (bright page to black card) | busy dissolve | `fadewhite` on that join |
| "clip N needs another half second" | line lands close to the cut | `CLIP_EXTRA[N-1]` |

Every fix is a rebuild of the whole cut, verified, and re-sent. Update the JSON edit notes and lessons in the same commit.

## Costs, credits and moderation

Quote costs before a batch. At 480p, a 7-second picture-only draft is the cheapest unit; a 30-second carrier with audio is about six times that; 1080p finals are roughly four times a 480p draft. Generated screens and lettering are always wrong, so plan captures for them rather than paying for re-rolls. Music prompts are the one thing moderation blocks; keep the drone wording handy.

## Repo hygiene

- The JSON is the record. Prompts, modes, per-clip notes, edit notes, lessons, asset list.
- Commit the narration and bed as `.m4a` (extract with `-vn -c:a copy`), the captures as MP4, and the recorder and stitch scripts. Do not commit the preview cut or the generated clips; they live in OpenArt and the editor's project.
- Log the finished cut in the content review log before publishing, and apply the house rules of the site to every caption and prompt (for this site: write the firm's name in full, no em dashes, no financial advice claims).

See `references/prompts.md` for the exact prompts, `references/lessons.md` for the full list of what went wrong and why, and `references/conventions.md` for the professional conventions with sources.
