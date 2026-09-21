# Lessons from the drafts

Each of these cost at least one re-render. The number is the order we learned it. `references/prompts.md` shows the wording that resulted.

## Text and screens

- (1) Any visible screen, slide or paper invites made-up lettering. Turn screens away, blur them, or keep them as a plain gradient.
- (4) Generated laptop and phone screens always render gibberish text. Anything that must show the product is a real screen capture, not a generation.
- (5) Even with 'no text' in the prompt, dashboards and whiteboards still grow tiny labels. At 480p they are unreadable; check them again at 1080p before the final render.
- (8) A laptop facing the camera grows a screen on its lid. Say the lid is plain, matte, with no display on it, and the screen faces the person.
- (9) A single short line of on-screen text (Tax basics for employees) rendered correctly at 7 seconds when asked for exactly that text, large, centred, and nothing else on the slide.

## People and performance

- (2) Rooms of people facing the camera read as a group photo. Ask for profiles and backs, a tracking move, and 'nobody looks at the camera'.
- (6) When a person on screen is meant to be talking, say so and say their voice is never heard, and label the read NARRATOR, off screen. Otherwise the model lip-syncs the voice-over to whoever is visible.
- (7) Two half-scenes in one prompt come out disjointed. Ask for one continuous shot, one scene, no cuts, and describe the people as in conversation with each other.
- (10) If someone on screen is meant to be talking, the model lip-syncs the narration to them no matter what the prompt says. Generate that clip as picture only (generateAudio false) and mux the narration on afterwards with ffmpeg.

## Scene design

- (11) Abstract props (cards in slots) read as nonsense. Show the outcome people recognise instead: for AI, the work done and someone leaving on time.

## Length and pacing

- (3) Five-second clips cut words off. Seven seconds with 'a beat of quiet before the first word and after the last' gives the read room without the model drifting off script.
- (13) Hard 0.3 second cross-fades between narrated clips feel rushed: the next line starts before the last has landed. A short hold plus a one-second dissolve through black reads as the narrator pausing for breath.
- (17) Playing full 7s clips under 4-5s lines left long silent tails that felt slow for an ad. Trim each clip to LEAD + line + a short tail; keep the bed continuous so the gaps are never dead silence.

## Narration and sound

- (12) For an end card, generate the narration on a plain carrier clip with no people or text, find the sentence onsets with ffmpeg silencedetect, and time the on-screen text to them.
- (14) Music prompts that sound like a genre or a score get rejected by the audio moderation filter as possible copyright. Ask for an original, simple synthesiser drone and it passes.
- (15) Word timestamps from a transcript end early. Cut narration lines in the middle of the detected pauses, not at the word boundaries, or the last syllable is clipped.
- (16) Mute the clips and run one bed under the whole ad, or the music jumps at every join and the ad reads as six separate clips.

## ffmpeg

- (18) Trimming clips inside one big xfade filtergraph (with tpad and re-applied fps) produced a broken chain: the end card jumped in at 6 seconds and the rest went black. The fix is to pre-render each clip to a clean, constant-frame-rate file of an exact length first, then dissolve those staged files.

## Framing for the 9:16 crop

- (19) A 9:16 column is the middle 32 percent of a 16:9 frame. A pair spread across the width (the whiteboard scene) loses one of them in the crop; the fix that worked was a 100 pixel offset, and the fix that would have avoided it is blocking both people at the centre in the prompt.
- (20) A lateral camera drift slides the subject across the frame; in the crop that becomes a pan to write, or a lost subject. A push-in, a static frame or a move that follows the subject keeps the crop still.
- (21) Desktop page captures and the end card do not crop. Record portrait versions natively and bring them in inside a join the 16:9 cut already has (the white flash into the product clip), so the edit gains no new transition.
- (22) A change of crop offset between two clips is invisible when it eases across the dissolve and a jolt when it jumps mid-dissolve. The reframe script eases every gap between pan segments for this reason.
- (23) `tpad` inside an `xfade` graph fails the constant-frame-rate check the same way trimming did (lesson 18). Stage each portrait clip to a clean file with its fade and pad applied, then dissolve the files.
- (24) Check the centre-column strip at draft time. Both GBX pans were found after approval; a second strip per clip costs nothing and would have caught them in Phase 2.

- (25) Captions from the script, timing from the transcript. Whisper wrote "10 -day" and "gbxps .com"; the script says "ten-day" and the card carries the address. Match the script's words onto the transcript's timestamps rather than showing the transcript.
- (26) Caption size and chunking trade off. 58 px was too small on a phone; 76 px holds about 42 characters on two lines, so split longer sentences at a comma. Splitting to 30 characters made phrases that flashed for under a second; hold each caption to the next one's start instead.
- (27) The site's fonts in the CSS are variable fonts whose default instance is Thin. Freeze a static instance at the weight you want before handing it to libass, or the captions render hairline.

- (28) Cutting narration lines in the middle of a long pause leaves half the pause inside each line, and the stitch adds LEAD and CLIP_TAIL on top, so the gaps between lines ran near two seconds and the ad felt slow. narration-lines.py now ends a line 0.2 s into the pause and starts the next 0.08 s before the pause ends; the gap is then just LEAD plus CLIP_TAIL.
- (29) A beat before the first word (LEAD_EXTRA on clip 1) lets the opening image land before the voice; 1.4 s let the blind open and the light arrive on the Brightday spot.
- (30) In ffmpeg 7, amix takes its timestamps from its first input. With a delayed narration line first the mix emitted frames without timestamps and the muxer dropped the audio after the delay (1.79 s of sound in a 35 s file). The bed, which runs from zero, goes first; the check that caught it was the audio stream length, not the loudness line.

## Things that were fine and stayed fine

- 7-second clips at 480p are enough to judge composition, motion and the read. Do not pay for 1080p until a clip is approved.
- A dawn skyline and an empty desk make a safe opening clip: no people, no screens, nothing to get wrong.
- Frame strips (five or six frames tiled into one image) catch almost every defect before the user sees it: text on lids, a group photo, a scanner instead of a printer, the end card arriving early.
- Word-level transcription of the narration is worth the install. It proved the read was complete and gave the sentence onsets that time the end card.

## Verification habits that caught real bugs

- Tile frames every 3 seconds across the whole cut: the end card showed up at 6 seconds and the rest was black once, and the strip made it obvious.
- `silencedetect` on the full mix at -45 dB: found the loop seam dip at 27 seconds and confirmed the fix.
- Mean luminance sampled across a join: confirmed the white-to-black fade actually peaked white.
- Check the container is yuv420p; one build came out 4:4:4 and some players will not decode it.

## 31. Native 9:16 social pieces from app-generated clips (Flux 3, 2026-09-22)

- A model that is only in the OpenArt app (Flux 3 while it was unlimited) still reaches the repo: every app generation appears in `openart_creation_list` with its prompt and a download url, so paste the prompts in the app and match on prompt text when picking the clips up.
- Flux 3 returned 704x1280 at 5.04 s whatever the plan asked for. Plan two clips per line and let `stitch-social-9x16.py` trim the first clip so the dissolve lands on the line's second sentence.
- Flux ignores negatives; the prompt-optimizer skill's Flux entry (subject first, under 80 words, camera body and lens, one lighting line, positives only) gave seven usable clips on the first take.
- Reuse the approved narration take for social: each piece takes one line from it and line 6 over the end card, so no new voice generation and the brand close matches the master.
- Take line boundaries from silencedetect, not from Whisper word times, when a line starts with spelt-out letters (GBX came back 0.4 s early).
