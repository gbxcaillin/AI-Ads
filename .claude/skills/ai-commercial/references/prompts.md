# Prompts that worked

Every clip prompt starts with SHARED_STYLE and, when it carries a voice, VOICE_DIRECTION. Substitute the paragraphs below verbatim. All text is plain, no em dashes.

## SHARED_STYLE

Cinematic brand film, editorial and premium. Dark charcoal and deep teal palette with warm off-white highlights, fine film grain, soft directional light, shallow depth of field, slow deliberate camera movement. Real-feeling Australian professionals in their thirties to fifties, diverse, natural and unposed, in a modern Melbourne office with the city skyline through glass. No stock-photo smiles, no pointing at screens, no logos, no text of any kind on screen. Minimal music: a low ambient pad with a soft piano motif, quiet room tone. Voice always clear above the music.

## VOICE_DIRECTION

One male voiceover across all six clips: mature, in his sixties, warm and unhurried, friendly with a wry edge, the wisdom of someone who has seen a few cycles and is still curious about new technology. Measured baritone, precise diction, neutral accent with a light Australian and New Zealand lean. Sounds like a trusted mentor explaining something over a coffee, not a presenter. No sales energy, no echo, natural pauses.

Describe the voice; never name a real person. The line in the JSON reads: Do not name a real actor or public figure in the prompt. OpenArt models do not reproduce a specific person's voice or likeness, and a request to imitate one can be refused. The description above gets the same feel.

## The script (one line per clip)

1. Most businesses don't need more advice. They need a clearer picture.
2. GBX Professional Services helps firms run sharper. The numbers, the process, the pipeline.
3. And AI that actually earns its keep. Practical, governed, and only where it helps.
4. We also teach people about money. Plainly, at work, in language a whole team can follow.
5. Free tools before you ever hire us. A ten-day Diagnostic when you're ready.
6. GBX Professional Services. Combining insight with impact, for sustainable business growth. G B X P S dot com.

Spell out anything a reader would say as letters (G B X P S dot com); the model reads it as written.

## Picture-only clip prompts (Seedance 2.5, text2video, 7 s, 16:9, 480p, generateAudio false)

Model settings: `{"duration": 7, "aspectRatio": "16:9", "resolution": "480p", "generateAudio": false, "videoCount": 1}`. Use 1080p only for approved finals.

### Clip 1, the empty desk at dawn (no people, safest opener)

SHARED_STYLE. Dawn over the Melbourne skyline seen from a high office window, the city still quiet, first light arriving on the glass. One slow push-in toward an empty desk by the window with a closed notebook and a cup of coffee. No people, no text.

### Clip 2, two colleagues at a whiteboard (one continuous scene)

SHARED_STYLE. One continuous shot, one scene, no cuts. Soft morning light. A woman in her forties and a man in his fifties stand together at a whiteboard in an open office, working through a simple process flow of boxes and arrows drawn in black marker, no readable words. He draws one more arrow while she talks it through with him; they are clearly in conversation with each other, glancing between the board and one another, nodding. A third colleague sits at a nearby desk, half out of focus, listening in. The camera drifts slowly sideways around them. Nobody looks at the camera; nobody speaks aloud.

### Clip 3, the office lights up as a network and the printer delivers

SHARED_STYLE. Silent film, no dialogue, no narration. One continuous shot, one scene, no cuts. Absolutely no readable text, letters, words or numbers anywhere, on any wall, screen or paper. Dawn, a modern Melbourne office still dark, several desks, the city skyline through glass. A man in his fifties walks in from the left carrying a coffee. As he passes, the room quietly comes alive around him: the ceiling lights lift softly, and thin glowing teal pathways begin to trace across the long glass wall behind the desks, spreading node to node, branching and linking across every desk and doorway into one connected network of soft teal lines with small bright nodes pulsing where they meet. The pathways all flow toward one point: a modern office laser printer on a side table. The last bright pulse travels down into the printer, the printer wakes with a soft glow, and a single printed sheet slides out toward the camera. The man steps over, lifts the freshly printed page from the printer's output tray, uncaps a pen, and reads it with a small nod, unhurried, nobody looking at the camera. Camera drifts slowly with him. Purely abstract lines and dots, nothing legible. Near-future, grounded, elegant, no robots, no holograms.

### Clip 4, a boardroom with a silent presenter and one line of slide text

SHARED_STYLE (but the one slide below may carry text). Silent film, no dialogue, no narration. Documentary feel, nobody looks at the camera. A modern corporate boardroom in a Melbourne office, long timber table, twelve staff of all ages seated along it in relaxed working clothes, seen in profile and from behind, all facing a relaxed presenter in his sixties who stands at the far end beside a wall screen. The wall screen shows a plain soft teal slide with only one line of clean white sans-serif text, large and centred, reading exactly: Tax basics for employees. No other text, numbers or logos anywhere. The presenter is quietly talking to the room in the background, his lips moving naturally as he explains something, gesturing with one open hand, easy and unhurried. Camera tracks slowly along the side of the table past the backs and profiles of listeners: one takes a note, one leans back and nods slightly, one turns to a colleague with a small smile. Natural, attentive, warm.

Clip 4 shows the one exception to the no-text rule: a single short slide title rendered correctly when asked for exactly that text, large, centred, nothing else. Keep the presenter silent (picture only) or the model lip-syncs the narration to him.

## Screen captures (not prompts)

Clip 5 (the product) and clip 6 (the end card) are recorded from the live build with the bundled recorders. Do not generate anything that has to show the real site or logo.

## Narration carrier (one take of all lines, 30 s, generateAudio true)

A plain, very slow drifting gradient of dark charcoal and deep teal light, soft film grain, no people, no objects, no text, no letters, no logos. Audio: no music, no sound effects, no ambience, a silent studio. The only sound is one narrator. VOICE_DIRECTION He reads the six lines below in order, slowly and evenly, with a clear pause of about a second and a half between each line, every word completed, never rushed or cut off, finishing before the end. NARRATOR: "<line 1> ... <line 2> ... <line 3> ... <line 4> ... <line 5> ... <line 6>"

The read came back continuous with only short pauses, so the lines are split by transcript, not by silence alone (see scripts/narration-lines.py).

## Music bed carrier (30 s, generateAudio true)

Rejected by the audio moderation filter as possible copyright:

> instrumental only ... understated cinematic brand music ... a low warm ambient pad, a soft sparse piano motif that returns every few bars, a gentle sustained string layer ...

Passed:

> A plain, very slow drifting gradient of dark charcoal and deep teal light, soft film grain, no people, no objects, no text, no letters, no logos. Sound: an original, simple, quiet synthesiser drone. A single warm sustained pad tone that breathes slowly, with an occasional soft single piano note, very sparse, calm and unchanging, no melody, no rhythm, no drums, no voices, no words, no singing, no sound effects, the same soft texture from the first second to the last, gently fading out at the very end.

The bed is used as one take stretched to the cut length, never looped.

## End card (recorded, not generated)

Order on screen: the animated mark alone, then the eyebrow OUR PHILOSOPHY and the philosophy line in the site's serif italic, then www.gbxps.com in the mono face, on black, with a slow push-in throughout. The narration line for it is the closing line; its sentence onsets set the caption timings:

T6='{"up":2.0,"phil":2.5,"url":5.9}' node scripts/record-endcard-clip.mjs

`up` is when the mark eases upward, `phil` when the philosophy fades in, `url` when the address fades in, all in seconds from the start of the clip.

