# Video model prompting reference

Each family below lists its **negative prompt** behavior and the research-backed
**tips** that form the guide you hand the user. When optimizing:

- Keep the user's subject and intent; add only missing elements (camera move,
  motion, lighting, audio, style) using mood-appropriate choices — see the
  mood taxonomy in SKILL.md, never a fixed default for every scene.
- Most video families want present tense and one camera move per shot.
- If a family's negative prompt is `null`, the model ignores negatives — rewrite
  them as positives (e.g. "stable proportions" not "no deformed limbs").
- Map any model not listed to its closest family (e.g. any new ByteDance video
  model → Seedance).

### Seedance
Negative prompt: "blurry, low quality, jittery motion, inconsistent lighting, audio desync, character drift between shots"
Tips:
- Use 8-part formula: Format, Subject, Action, Environment, Camera, Look, Timing, Audio + Constraints
- Write as director's briefs, not captions. Specify cause before reaction and include physics (friction, weight, momentum)
- Reference tagging: @Image1, @Video1 with one job per reference
- 2.5 supports 30-second continuous single-pass video with up to 50 multimodal references
- Structure narrative in four beats: establishing wide (0-6s), primary action (6-14s), escalation (14-24s), resolution (24-30s)
- For continuation: extract final frame, feed as @Image1 for next generation
- Region-level editing in 2.5 lets you patch props/backgrounds without re-rendering

### MiniMax
Negative prompt: "blurry, distorted, low quality, jittery, audio desync, character drift, tonal shift between cuts"
Tips:
- H3 uses three dedicated prompt fields: main visual, overall_soundscape (ambient/physical audio), and non_diegetic_music
- Full multimodal context: text + up to 9 images + 3 video clips + 3 audio clips in one request
- Use timecoded shot lists: [0-2s] High-angle overhead... [2-4s] Smoothly push in...
- Reliable on-screen text/UI rendering in video
- Describe transitions as physical events: circular wipes, vertical car-door cuts, flash-to-white
- Specify exposure/stock effects: fine grain, halation, VHS glitches, scanlines, chromatic aberration
- Up to 7,000-character prompts supported

### Gemini
Negative prompt: null (not supported — rewrite negatives as positives)
Tips:
- Use directional prompts over specifications: 'shoot it like a Sofia Coppola film' beats a camera spec list
- Place camera movements at the END of the prompt for maximum impact
- One focused moment per prompt; do not chain events
- Max 10 seconds at 720p with native audio synthesis
- Multi-turn editing is the defining feature (up to 3 sequential edits)
- Describe the scene as if telling a story; natural conversational language works best
- Include context and purpose of the video

### Flux
Negative prompt: null (not supported — rewrite negatives as positives)
Tips:
- Write descriptive sentences, not keyword lists; FLUX uses a 24B vision-language model
- Word order matters: lead with the main subject, it gets the most attention
- Quality tags (masterpiece, best quality, 4k) have minimal benefit; use descriptive language instead
- No weight syntax support; (beautiful:1.4) is ignored. Use natural emphasis instead
- Specify camera and lens: 'Shot on Sony A7IV, 35mm lens, golden hour' for photorealism
- Add one strong lighting description; vague lighting produces vague results
- Keep under 80 words for standard work; up to 300 for complex multi-subject scenes

### Kling
Negative prompt: "blur, distort, low quality, warping fingers, frozen lips, jittery eyes, face swap, character merge, identity drift, extra limbs, moonwalk sliding feet"
Tips:
- 5-part spine: [Camera Movement] + [Scene/Environment] + [Subject & Action] + [Lighting/Mood/Style] + [Audio/Time]
- Sweet spot: 50-150 words. Over 300 words causes model to ignore and hallucinate
- One camera move per shot: 'dolly push', 'tracking shot', 'orbit'; never combine multiple moves
- Use ++keyword++ emphasis on 2-4 critical elements only
- Multi-shot: label as 'Shot 1 (0-3s):' format. Supports up to 6 shots in Kling 3.0
- Dialogue: [Character A: Description, voice tone]: 'Dialogue text'
- SFX: prefix for sound effects. Describe ambient acoustics plainly
- Always specify action endpoints: 'picks up the cup, then settles back into place'
- Translate emotions into observable physics: 'shoulders drop and she exhales' not 'looks relieved'
- Texture keywords prevent plastic look: film grain, skin pores, fabric creases, condensation

### PixVerse
Negative prompt: "blurry, distorted faces, extra limbs, watermark, low quality, jerky motion, morphing, flickering"
Tips:
- 50-80 words structured as: Sentence 1 (subject + action + location), Sentence 2 (camera + style), Sentence 3 (constraints)
- Lead with your subject; the model parses sequentially, early elements get more weight
- One primary action per clip. Specify physical motion: 'feet strike ground with force'
- Replace 'cinematic' with specific film language: rim light, tungsten side light, 35mm lens, low-angle
- Write positive constraints: 'hands remain stable and move naturally, body proportions stay intact'
- C1: Use @ref_name for reference images (up to 7). Supports storyboard-to-video pipeline
- Duration: 5, 8, or 10 seconds. C1 up to 15 seconds at 1080p
- Enable generate_audio_switch for BGM, SFX, or dialogue

### HappyHorse
Negative prompt: null (not supported — rewrite negatives as positives)
Tips:
- Keep prompts under 30 words for 1.0; longer prompts risk being partially ignored
- 1.1 shot-brief format: Subject + Motion + Camera + Audio + Format
- Audio MUST be named explicitly in every prompt (1.1); leaving it unnamed produces random audio
- One main motion per clip. One strong camera or lighting cue, not five
- Excels at: vehicles, fabric motion, fire, reflections, aerial landscapes
- 1.1 adds native lip-sync in 7 languages (EN, ZH, JA, KO, DE, FR, Cantonese)
- Place camera directions at the END of the prompt for maximum impact
- Replace generic terms: 'soft golden backlight with rim glow on shoulder' instead of 'beautiful lighting'
- Timed dialogue: '0-4s: character1 says in French, "Tu as vu ca?"; 4-8s: character2 laughs'

### Wan
Negative prompt: "blurry, distorted, low quality, jitter, flicker, morphing"
Tips:
- Formula: Subject + Action + Environment + Camera + Lighting + Style + Motion + Output Intent
- Use one camera verb per shot: push, orbit, track, tilt, crane; avoid vague 'cinematic'
- Separate primary motion (main action) from secondary motion (environment) to prevent visual noise
- Wan 2.6+ supports timing brackets: [0-3s] establishing wide, [3-6s] close-up push; with multi_shots: true
- CFG scheduling: start at 7 for composition, lower to 4 for detail pass
- For image-to-video: prompt ONLY motion and camera; the image defines entity, scene, and style
- Maintain consistent visual style from start to end with explicit style anchoring

### Veo
Negative prompt: "blurry, low quality, distorted, glitchy, unnatural motion"
Tips:
- Structure: Subject + Action + Scene + Camera + Style + Audio + Negative prompts (3-6 sentences, 100-150 words)
- Dialogue trick: write it as Character says: 'dialogue' to prevent unwanted subtitles
- Camera placement: include '(that's where the camera is)' for precise camera positioning
- 8-second dialogue rule: keep speech segments under 8 seconds for natural pacing
- Veo 3.1: timestamp prompting [00:00-00:02] Shot A, [00:02-00:04] Shot B for multi-beat sequences
- Excels at water physics, fabric, lighting reflections, and professional cinematography terms
- Always generates audio; specify exactly what you want to hear, including 'silence' if needed
- Veo 3.1 has 40-60% improved frame consistency over Veo 3

### Grok Imagine
Negative prompt: null (not supported — rewrite negatives as positives)
Tips:
- Video formula: Subject + Action + Camera Movement + Motion Detail + Mood + Duration
- Lead with subject in 30-80 words of plain English. Commit to ONE aesthetic per prompt
- Negative prompts are IGNORED; use positive framing only
- Motion verbs: turns, smiles, blinks, walks, leaps, sways, spins, ripples, flickers
- Camera: push in, pull back, orbit, pan, rise, static. Use 'camera not moving' (not 'stable camera') to lock frame
- Native audio: physical impacts (footsteps, door slams) work best; emotion-led prompts often produce music only
- Speed modifiers: 'quickly', 'violently', 'with large amplitude', 'powerfully'
- Video resolution: 480p or 720p, duration 6-30 seconds

### Sora
Negative prompt: null (not supported — rewrite negatives as positives)
Tips:
- 2-5 sentences structured as: scene / cinematography / actions / audio
- Sora treats prompts as 'creative wish lists, not contracts'; same prompt yields different results each time
- Shorter clips (4s) follow instructions more reliably; stitch two 4s clips rather than one 8s clip
- Native audio generation; ALWAYS specify sound or the model decides for you
- Duration set via API parameter (4/8/12/16/20s), not in prose text
- Excels at single-action sequences with specific camera language
- Struggles with: hands, text rendering, object permanence, and physics past 20 seconds
- Each prompt should focus on a single clear moment with one action

### LTX
Negative prompt: null (not supported — rewrite negatives as positives)
Tips:
- 6-part shot scaffold (single prose paragraph): Shot + Scene + Action + Character + Camera + Audio
- Write prose paragraphs, NOT comma-separated tags; tags fail on LTX
- 4-8 descriptive sentences as a single flowing paragraph. Up to 5,000 characters supported
- Joint audio-video diffusion in single pass; always describe the soundscape
- Audio format: 'The audio is [ambient bed]: [specific effects], [additional textures], no music'
- Separate camera movement from subject motion in distinct clauses
- Duration: 6-20s on Fast tier, 6-10s on Pro tier. FPS: 24 (cinematic), 48/50 (slow-mo)
- For multi-shot (LTX-2.5): name transitions explicitly; 'hard cut transitions to', 'dissolve', 'match cut'
- Physical cues for emotion: 'shoulders drop, jaw tightens'; not labeled emotions

### Hailuo
Negative prompt: "cartoon, anime, illustration, blur, distort, low quality, jitter"
Tips:
- Formula: [Camera Shot + Motion] + [Subject + Description] + [Action] + [Scene + Description] + [Lighting] + [Style/Mood]
- Use double parentheses ((red dress)) to force priority on critical visual features
- Write in present tense. Prompts should read like short directing notes, not prose descriptions
- Excels at: motion generation, temporal flow, body movement, facial micro-expressions, physical realism
- Hailuo 2.3: expanded stylization; anime, ink-wash painting, game-CG styles
- Translate emotions into observable behavior: 'shoulders drop and she exhales' not 'looks relieved'
- Counter cartoonish output with: 'photorealistic, hyper-detailed, shot on Arri Alexa, cinematic movie style'
- Overload limit: prioritize 2-3 action beats per clip

### Vidu
Negative prompt: "blurry, distorted, flickering background, morphing, extra limbs"
Tips:
- Concise prompts work best; single-sentence intent statements perform well
- One-Pass Rule: single subject, one clear action, one camera movement per 5-second clip
- Physics-driven language: 'steam rising, fabric fluttering, wet pavement reflections'
- Prefer slow camera moves: slow push-in, slow arcs, subtle parallax, micro-dolly
- Q3: 1-16 seconds, sweet spot is 5-second clips. Native audio generation included
- Q2: Reference2V accepts up to 7 distinct images for character consistency
- Remove 2-3 adjectives and add 'Stable background' to eliminate flickering
- Fast whips, wild handheld, and hyper-detailed reflections cause shimmer; avoid them
- For best faces: use Image-to-Video with high-quality Start Frame instead of text-to-video

