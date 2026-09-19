# Professional conventions for a short commercial

What broadcast and agency editors do by default, so the skill does not have to rediscover it. Numbers are from the sources at the end; where sources disagree the range is given. Apply these before the user has to ask.

## Structure of a 30-second spot

- Four beats: hook, problem or tension, solution or turn, payoff with call to action. Every 30-second spot tells the whole arc.
- **Hook in the first 3 seconds, and not with a logo.** Meta's research puts about 47 percent of a video ad's value in the first three seconds. Opening on a logo or brand card burns those seconds on something the viewer does not care about yet and signals "ad"; open on a striking image, a question or a relatable pain point instead. WARC's attention work: 1.4 seconds of attention lifts awareness, prompted recall needs about 3.9 seconds.
- **End tag last.** The end card or end tag runs 3 to 5 seconds in a 30 (5 to 10 in longer spots), holds the logo for at least 3 seconds, and carries at most three things: mark, one line, one action (URL, number or offer). TikTok's own guidance reports a clear end-card call to action lifts click-through by about 45 percent.
- **Broadcast length is exact.** Some networks want exactly 30.00 seconds, not one frame more or less; others accept 29.5. Web has no such rule; 30 to 45 seconds is normal for a brand film, 15 for social.

## Words and voice

- **Word budget.** A 30-second spot carries 60 to 75 words at a natural pace (up to 80 to 85 for a brisk read, 90 for a hard-sell read). A 15 takes 30 to 38, a 60 takes 130 to 150.
- **Pace.** Conversational narration runs about 2.5 words per second (150 wpm). A deliberate, premium read drops to 2 words per second, which cuts the usable word count by a fifth for the same length.
- **A third of the runtime has no words.** Product shots, the logo hold and reaction beats take up to a third of a 30 without dialogue, so a script written to the full word ceiling still runs long once the visual pacing is added. Always time a full read aloud, with the planned pauses, before trusting a word count.
- **Air.** Leave room for pauses, sound and music in the count; 70 to 80 words is the range that still lets the talent breathe.

## Picture rhythm and transitions

- **Shot length.** Commercials cut at 2 to 5 seconds per shot; cinema averages 4 to 6. A shot held 1.5 seconds or longer is recognised and remembered; shorter reads as texture, not content. Two beats inside a 7-second clip (a wide, then a detail) is closer to the convention than one held shot.
- **The cut is the default.** In a feature with 10,000 transitions, about 9,990 are straight cuts; the eye only notices the ones that are not. Use a plain cut when two shots share light and palette and the line moves to the next thought.
- **The dissolve is an ellipsis.** It says time or place has moved on; 24 to 48 frames (1 to 2 seconds) is the classic length, shorter (0.5 to 0.8 seconds) for a spot. Because AI clips are born independently and rarely share a lighting continuity, a short dissolve is the honest join between them; a straight cut works when two generations happen to match.
- **Fade to black is a chapter break.** It signals finality, so it belongs before or after the end card, not between narrated beats; a dip between beats reads as the ad stopping. A dip through white is the conventional way to leave a bright scene for a dark card.
- **J-cuts and L-cuts.** Let the next line begin under the outgoing picture (J) or let the current line finish over the incoming picture (L). Audio leading picture by a quarter to half a second is the standard way to make a join feel intended rather than mechanical.
- **Audio-first editing.** Editors trim the music and voice to length first and cut picture to the track, not the reverse. When shortening a 30 to a 15, expect to re-edit or drop the voice-over entirely.

## Sound and levels

- **Bed under voice: 18 to 20 dB.** The working consensus for narration over music is a bed 18 to 20 dB below the voice. Under 15 dB the music masks speech on phones and small speakers; over 25 dB it vanishes on the same devices. Broadcast "dipped" stems duck the music further under dialogue; "undipped" stems keep it level.
- **Loudness targets.** Broadcast: -24 LKFS integrated (US CALM Act, ATSC A/85, ±2 LU; Australia Free TV OP-59 ±1 LU with a -2 dBTP true-peak ceiling and 12 frames of silence at head and tail, measured to ITU-R BS.1770-3); Europe EBU R128 -23 LUFS. Streaming and web: -14 LUFS with -1 dBTP is the safe universal target (YouTube normalises to -14; Instagram and TikTok publish nothing and are commonly mixed louder, -10 to -13). Dialogue-heavy content sits at the quieter end of a platform's range.
- **Anchor on the voice.** Measure loudness on the narration, not the full mix; a full-programme number hides quiet dialogue under loud music.
- **Commercials at the legal ceiling.** Spots are routinely mixed right at the limit (-23 to -24) to sit as loud as allowed against programme material; do not exceed it.

## Finishing AI footage

- **Continuity is the craft.** Every generated shot is born alone; lock palette, lighting language, lens feel and the people's descriptions in the prompt so the grade has less to correct.
- **Takes.** Agencies budget 5 to 10 generations per scene and pick; one clean take on the first try is luck, not a plan.
- **The finishing recipe, in order:** upscale first (so detail can be softened deliberately), a light Gaussian blur of 0.3 to 0.6 px to kill the AI micro-sharpening on skin and edges, film grain at 8 to 15 percent, then grade: neutralise white balance per clip, a film-emulation LUT at 60 to 80 percent, and finally match every clip to one hero frame for shadow tint, highlight warmth, saturation and contrast. Skipping any of blur, grain or grade leaves footage in the uncanny zone.
- **Delivery.** 1920 by 1080 minimum, H.264 or H.265 for review, a ProRes master for broadcast; 25 fps in Australia and Europe, 29.97 in the US; captions for social, where autoplay is silent.

## How the skill applies these

| Convention | Where it lands in the workflow |
|---|---|
| No logo in the first 3 seconds | clip 1 is an image, the mark is last |
| 60 to 75 words, 2 to 2.5 words per second | Phase 1 word budget and the read-aloud check |
| a third of runtime without words | LEAD and CLIP_TAIL leave picture around each line |
| 2 to 5 second shots | optional two-beat clips; captures pace their scrolls to it |
| cuts by default, short dissolves between unrelated generations | XFADE 0.5 to 0.8 |
| dip to white or black only around the end card | WHITE_FADES on the join into the card |
| J-cut | LEAD starts the line while the previous picture is still dissolving |
| bed 18 to 20 dB under the voice | BED_UNDER_DB, measured against the narration |
| -14 LUFS / -1 dBTP web, -24 LKFS / -2 dBTP broadcast | LOUDNESS=web or broadcast, two-pass loudnorm on the final mix |
| end card 3 to 5 seconds, logo held 3 | end card recorder length and the push-in |
| grain and grade to match | optional ffmpeg pass noted in SKILL.md; proper grade in an editor |

## Sources

- [PremiumBeat: Cutting Commercials, editing 15, 30 and 60-second spots](https://www.premiumbeat.com/blog/cutting-commercials-editing-15-30-and-60-second-spots/)
- [Celtx: How to write a TV commercial script](https://blog.celtx.com/how-to-write-a-tv-commercial-script/)
- [Boords: How to write a TV commercial script](https://boords.com/blog/how-to-write-a-tv-commercial-script)
- [ScreenWeaver: Commercial script length and timing](https://www.screenweaver.ai/blog/commercial-script-length-timing)
- [Abe's Audio: How many words fit in a 30-second voice over](https://www.abesaudio.com.au/knowledge-base/voice-over-artists/how-many-words-fit-in-a-30-second-voice-over)
- [Killerspots: How long is a 30-second script](https://killerspots.com/blog/radio-script-timer-how-long-is-a-30-second-script)
- [StudioBinder: Types of editing transitions](https://www.studiobinder.com/blog/types-of-editing-transitions-in-film/)
- [Filmpac: Dissolves versus cuts](https://filmpac.com/the-difference-between-dissolves-and-cuts-in-video-edit/)
- [Wikipedia: Film transition](https://en.wikipedia.org/wiki/Film_transition) and [J cut](https://en.wikipedia.org/wiki/J_cut)
- [Videomaker: The J cut explained](https://www.videomaker.com/how-to/editing/editing-technique/pro-editing-transitions-the-j-cut-explained/)
- [Vidpros: Video clip length guide](https://vidpros.com/video-clip-length/)
- [ResearchGate: Camera shot length in TV commercials, memorability and persuasiveness](https://www.researchgate.net/publication/393493575_Camera_Shot_Length_in_TV_Commercials_and_Their_Memorability_and_Persuasiveness)
- [Pure Audio Insight: Background music volume](https://pureaudioinsight.com/blogs/content-production/background-music-volume-how-loud-should-it-be)
- [Storyblocks: Music behind a voice track](https://www.storyblocks.com/resources/tutorials/how-to-adjust-music-behind-a-voice-track-in-premiere-pro)
- [Frame.io: Broadcast audio spec sheet terms](https://blog.frame.io/2017/08/09/audio-spec-sheet/)
- [iZotope: The mixer's guide to loudness for broadcast](https://www.izotope.com/en/learn/the-mixers-guide-to-loudness-for-broadcast.html)
- [Free TV Australia OP-59: Measurement and management of loudness](https://www.freetv.com.au/wp-content/uploads/2019/08/OP-59-Measurement-and-Managemnt-of-Loudness-for-TV-Broadcasting-Issue-4-October-2018.pdf) and [Nine HD delivery specifications](https://www.nineforbrands.com.au/wp-content/uploads/2020/04/TVC-AD-Spec-AU-HD.pdf)
- [Wikipedia: LUFS](https://en.wikipedia.org/wiki/LUFS) and [EBU R 128](https://en.wikipedia.org/wiki/EBU_R_128)
- [Critical Listening Lab: Social media loudness](https://www.criticallisteninglab.com/en/learn/loudness/social-media)
- [Fuse Animation: Finish memorably with a killer end tag](https://www.fuseanimation.com/finish-memorably-with-a-killer-end-tag/)
- [RocketShip HQ: What makes a good end card](https://www.rocketshiphq.com/good-end-card-mobile-app-ads/)
- [Adlibrary: Hook rate and Meta's 3-second filter](https://adlibrary.com/posts/hook-rate)
- [Predictive Marketing: Video ad hook frameworks](https://predictive-marketing.com/2025/11/17/video-ad-hook-frameworks-3-seconds-that-decide-your-roi/)
- [InVideo: Colour grading workflow for AI-generated video](https://invideo.io/faq/what-is-the-best-color-grading-workflow-for-ai-generated/)
- [Social Operator: AI TV commercial, the 2026 broadcast production guide](https://socialoperator.ai/learn/ai-tv-commercial-2026/)
- [Dreamina: AI video workflow for creative agencies in 2026](https://dreamina.capcut.com/ai-video/ai-videos-build-finished-commercials)
