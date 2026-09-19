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
