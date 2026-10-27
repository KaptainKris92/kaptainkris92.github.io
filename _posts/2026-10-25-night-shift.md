---
title: Night Shift, a trail camera for things that don't exist
description: How I built a pipeline that invents a creature, films it as infrared trail-cam footage, asks me on Telegram whether to post it, then puts it on Instagram, YouTube and Facebook. All on GitHub Actions, for about the price of a coffee per video. A.K.A 'My contribution to the AI slop epidemic'.
project: Night Shift
date: 2026-10-25 12:00:00 +0000
image: /assets/posts/night-shift/nightshift-iso.light.svg
image_dark: /assets/posts/night-shift/nightshift-iso.dark.svg
image_fit: contain
image_alt: Isometric map of the Night Shift pipeline
image_credit: 'The pipeline in isometric view. <a href="/assets/posts/night-shift/nightshift-iso.html">Open the interactive version</a> to zoom and pan. Diagram made with <a href="https://github.com/evoclock/pi-bowerbird">pi-bowerbird</a> by Julen Gamboa (<a href="https://github.com/evoclock">evoclock</a>).'
thumb: /assets/posts/night-shift/profile.jpg
charts: true
---
Every evening, a short video goes up on Instagram ([@nightshift.cam](https://www.instagram.com/nightshift.cam/)), YouTube ([@nightshift_cam](https://www.youtube.com/@nightshift_cam)) and the Night Shift Facebook Page. It looks like grainy infrared footage from a trail camera strapped to a fence post. Something walks into frame that shouldn't exist, does one strange thing, and leaves.

None of it is real, and every post says so. What I wanted to find out was whether I could build something that makes and posts these on its own, with me doing nothing but tapping Approve/Reject or providing suggestions for improvement on my phone. Twelve days in, it has made 18 videos and posted 12 of them to three platforms. This is how it works, what it cost, and what I've learnt so far.

* Contents
{:toc}

## The idea

Since I've been seeing a lot of cool AI videos on Instagram over the past year, I decided to see if I could do something similar, but with minimal effort, as a proof-of-concept. I had the idea to do trail-cam clips as they don't require voice acting, any narrative, and are a single scene. The low-quality grainy green-grey infrared look also hides a lot of Gen AI video imperfections.

The rules I set at the start, and still keep:

- **The footage must look real.** The setting, lighting and physics should be believable. Only the creature anatomy/behaviour is impossible.
- **The creatures are original.** No Slenderman, no Wendigo, no greys, and never AI humans.
- **Always disclosed.** Every post carries the platform's AI label, and the profile bios say "AI-generated". The mystery comes from the footage, not from hiding what it is. The goal isn't to deceive people, it's just to generate cool creatures. 
- **Nothing goes out without my approval.**
- **Minimum spend.** Pay-per-use APIs only, no new subscriptions, until the channel earns something.

### Inspiration

The idea to post creature videos wasn't fully original and stemmed from admiring much higher quality channels such as:
- [tamsy.land](https://www.instagram.com/tamsy.land/)
- [dreamsweeper_](https://www.instagram.com/dreamsweeper_/)
- [creaturopedia_cg](https://www.instagram.com/creaturopedia_cg/)
- Probably many others I forgot the name of.

## The map

Here's the whole system. It was drawn with [pi-bowerbird](https://github.com/evoclock/pi-bowerbird), a diagramming tool made by my friend [Julen Gamboa (evoclock)](https://github.com/evoclock). It draws the map from a single JSON file that lives in the repo. I describe the components, zones and connections once, and it renders an interactive HTML page plus animated light and dark SVGs. Unlike Mermaid, it routes the lines cleanly, never puts a label on top of a box, and can show which parts are built and which are only planned. The animated trace follows one video from start to finish.

<figure class="figure wide">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="/assets/posts/night-shift/nightshift.dark.svg">
    <img src="/assets/posts/night-shift/nightshift.light.svg" alt="Night Shift system map: plan (music and concept), film (fal.ai and FFmpeg), approve (Telegram), publish (evening window) and monitor (stats).">
  </picture>
  <figcaption>The pipeline in five zones: plan, film, approve, publish and monitor. <a href="/assets/posts/night-shift/nightshift.html">Open the interactive version</a> to zoom and pan. Diagram made with <a href="https://github.com/evoclock/pi-bowerbird">pi-bowerbird</a> by Julen Gamboa (<a href="https://github.com/evoclock">evoclock</a>).</figcaption>
</figure>

Rendering it was two commands:

```sh
bowerbird render docs/diagrams/nightshift.bower.json
bowerbird render docs/diagrams/nightshift.bower.json --view iso
```

The second one gives the isometric version at the top of this post. Because the diagram is a file in the repo, it gets updated in the same commit as the code it describes, rather than going stale in a slide deck.

## How a video gets made

Each morning a GitHub Actions workflow runs `python -m nightshift make`. The stages run in this order.

### 1. Music first

This was the decision that made the videos feel edited rather than generated. The pipeline picks one of the Suno-generated tracks from the repo and analyses it with **librosa** to find the tempo, the beats and the drop. It then lays the video out on whole bars, with the drop landing about 40% of the way in. That's where the creature does its 'big moment'.

It also logs which section of which track each video used, so no section is ever reused. When I'm running low on unused music, the bot tells me. I used my entire month's Suno downloads to generate ~30 3-5 minute songs, which allows me to generate at least a year's worth of videos. 

#### Generating the music
I am a fan of psytrance and, given the creepy nature of trailcam footage, thought it would fit the footage fairly well. I asked Opus 5.5 to generate me a variety of prompts for psytrance music mixed with nature. It generated styles it termed 'dark dorest psy', 'psydub', 'psybient', and 'swamp acid'. Prior to that, I also tried some prompts for 'analog/minimal horror' and 'eerie forest ambience' scores as well as 'slow dark techno', 'witch house', 'trip-hop', and 'phonk'. Neither of which I really liked.

I used `v6 Pro` to generate all the music. For some of the tracks, I used the `v6-wild` model and cranked Suno's 'Weirdness' setting up all the way. Unfortunately, this resulted in pure noise halfway through these tracks so I reverted back to `v6 Pro`.

Ultimately, the generated songs were *good enough* but aren't anything amazing. With some extra time and motivation, I wouldn't mind producing my own songs in Ableton at some point, if the channels ever become monetisable. 


### 2. The concept

**Claude** (Opus 5.5, via the API) invents the creature, the location and what it does. It writes the image prompt, the video prompt, the caption and the values for the camera's on-screen info bar. Each time it reads:

- `style_guide.md`, the rules for the channel,
- `data/guidance.md`, every note I've given it, newest last,
- the last 30 sightings, so it doesn't repeat itself,
- the music brief: tempo, energy, and where the drop is.

This costs a few cents.

### 3. The keyframe and the video

Both come from **fal.ai**, which lets me pay per generation and swap models with a one-line config change.

- **FLUX.2 Pro** makes a realistic infrared still of the empty scene. **FLUX.2 Pro Edit** then adds the creature to it.
- **Kling O3 Pro** films one continuous take of up to 15 seconds, from the creature frame to the empty one. Because the last frame is the empty scene, the background can't drift, and the creature always leaves.

I started on **Veo 3.1**, chaining several short clips together. Each clip started from the last frame of the one before, but the background drifted between them, and the content checker occasionally blocked a segment for no clear reason. On day four I tried Kling as a single take and preferred it straight away. The old mode is still in the code behind a config switch.

This is the expensive bit: about $2 to $3 per video.

### 4. The edit

**FFmpeg** does the rest, for free on the Actions runner:

- an infrared grade on top of the generated footage,
- the trail-cam info bar (camera number, date, time, temperature, moon phase), drawn by FFmpeg because video models garble text,
- sensor glitches and clock jumps timed to the beat,
- IR-flash pulses on the drop, on about a third of videos,
- the music, mixed over the clip's own rustles.

It also keeps the file under 20 MB, because that's the most a Telegram bot can download.

### 5. The caption check

The caption is written before anything is filmed, so it sometimes describes things that didn't happen. After the edit, Claude looks at 12 frames of the finished video and rewrites the caption to match. Captions are a short hook plus a line of deadpan humour, written as a lone farmer or hunter who keeps finding these things on their cameras.

## Approving on Telegram

The finished video arrives in a Telegram chat with **Approve** and **Reject** buttons. I can also reply to a video with notes. Notes are appended to `data/guidance.md` and steer every future video.

There's no server behind the bot. A second workflow polls Telegram every few hours (hourly in the evening), reads my taps and replies, and commits the results back into the repo as JSON. The repo is the database. All the workflows share one concurrency group, so two runs can never write to it at once.

If yesterday's video is still waiting for a decision, the morning run skips making a new one and reminds me instead. Nothing gets spent on a backlog I haven't looked at.

## Posting

Approved videos go out in the evening, between 20:00 and 03:00 UK time, when short-form viewing peaks. That's also the US afternoon. Each platform gets at most one post a day, oldest approval first:

- **Instagram Graph API**, as a Reel. It only accepts a public URL, so the video is hosted on fal.ai storage first.
- **YouTube Data API**, as a Short, uploaded with the altered or synthetic content flag set.
- **Facebook Graph API**, as a Page Reel.

Instagram and Facebook have no API switch for the AI label, so their captions get `#aigenerated`. Failed posts are retried up to three times before the bot tells me.

## Running it on GitHub Actions

Everything runs on the free Actions minutes of a private repo. The catch is that GitHub delays, and sometimes drops, scheduled runs. My fixes:

- The "make a sighting" workflow is scheduled **five times** between 05:23 and 13:23 UTC. The first run of the day makes the video; the rest see it's done and skip.
- Two Claude routines also start the workflows each day, as a backup in case GitHub skips them all.

## Under the hood

The sections above are the overview. If you want the actual signal processing, FFmpeg filter graphs and API plumbing, open this up. Everything here is lifted from the code.

<details class="deep-dive">
<summary>Show the technical details</summary>

<h3>1. Finding the beat and the drop (librosa + NumPy)</h3>

<p>Everything starts in <code>music.py</code>. A track is loaded as mono at 22,050 Hz, and librosa computes an <strong>onset strength envelope</strong>: a curve of how much new energy appears in each frame (spectral flux, 512-sample hop, so about 43 values a second). Peaks in it are kicks, snares and other hits.</p>

<pre><code>y, sr = librosa.load(track, sr=22050, mono=True)
onset_env = librosa.onset.onset_strength(y=y, sr=sr)
tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)</code></pre>

<p><strong>librosa's beat tracker on its own wasn't good enough.</strong> It snaps to a quantised tempo and can skip beats through a noisy section, so over 30 seconds its beats drift visibly off the music, and glitches land between kicks. So the pipeline only uses it for a rough beat period (the median gap between its beats), then fits its own perfectly steady grid with a brute-force search:</p>

<ul>
<li>161 candidate periods spread over ±4% of the rough period,</li>
<li>24 phase offsets for each period,</li>
<li>for each of those 3,864 grids, the mean onset strength at the frames where its beats land.</li>
</ul>

<p>The grid with the highest score wins. A steady grid works because Suno's tracks are machine-tempo, so there's no human drift to follow.</p>

<pre><code>for period in np.linspace(rough * 0.96, rough * 1.04, 161):
    for phase in np.linspace(0, period, 24, endpoint=False):
        frames = np.round(np.arange(phase, duration, period) * frame_rate).astype(int)
        score = onset_env[frames[frames &lt; n]].mean()</code></pre>

<p><strong>The drop</strong> is found from loudness instead. librosa computes the RMS level every 0.1 s, and for each candidate beat the pipeline takes the mean level over the next 2 seconds minus the mean over the previous 2. The biggest jump is the drop.</p>

<p><strong>Bars</strong> were the hard part. Telling a bar's first beat apart from the other three by onset strength doesn't work for four-on-the-floor music, because every kick is equally loud. But drops and section changes almost always land on the first beat of a bar, so the drop is assumed to be one, and bars are counted every four beats either side of it.</p>

<h3>2. Laying the video out on the music</h3>

<p>With a beat grid and a drop, the video is planned in whole bars. Kling films at most 15 seconds and the creature needs 1.5 seconds to leave the frame at the end, so the music part aims for 13 seconds. The drop lands 40% of the way in.</p>

<p>For a 145 bpm psytrance track: a beat is 0.414 s, a bar is 1.655 s, 13 s rounds to <strong>8 bars (13.24 s)</strong>, the drop comes after 3 bars (<strong>4.97 s</strong>), and the take is rounded up to 15 s to leave room for the exit. The plan records where in the track to start, and the beat and bar times inside the video. Each run saves this as <code>plan.json</code>.</p>

<p>The plan also gives the concept agent a written brief: genre, tempo, and an energy level. Under 90 bpm is "calm" (slow, deliberate movement), 128 bpm and up (or psytrance from 120) is "frantic" (fast, jerky and wrong after the drop), and anything else is "driving". The drop time becomes "the creature's most startling action happens at 4.97 s".</p>

<p><strong>Never reusing a section:</strong> every video appends its track, start and end to <code>data/music_usage.jsonl</code>. When planning, any window that overlaps a used one (plus 4 seconds of room for the exit) is ruled out. If a track has nothing left, the next random track is tried. After each video, the free gaps in every track are added up to estimate how many videos' worth of music are left, and the bot warns me below 10.</p>

<h3>3. Prompts with a fixed shape (Claude structured output)</h3>

<p>Both Claude calls use the Anthropic SDK's <code>messages.parse</code> with a <strong>Pydantic model as the output format</strong>, so the answer comes back as a validated object instead of text to scrape. The concept model has typed fields for the creature, location, behaviour, keyframe prompt, opening-frame edit prompt, video prompt, caption, hashtags and the HUD values. The HUD values are themselves typed: a timestamp between 22:00 and 05:30, a whole-degree temperature, and a moon phase that must be one of eight values.</p>

<p>The code then checks what a schema can't: the right number of video prompts, an opening prompt whenever the video opens on the creature, and a HUD date that isn't in the future (it's moved back a day at a time until it's before today). Server-side fallbacks retry with a fallback model if the main one refuses.</p>

<p>The system prompt is assembled from <code>style_guide.md</code>, every note in <code>data/guidance.md</code>, the music brief and a description of how the footage will be made. The last 30 sightings go in as JSON lines from <code>data/history.jsonl</code>, so it can't repeat a creature or location. Camera numbers (CAM 01, CAM 02…) count up across the channel, and rejected videos don't use up a number.</p>

<h3>4. One continuous take (fal.ai)</h3>

<ol>
<li><strong>FLUX.2 Pro</strong> makes the empty scene at 1080×1920.</li>
<li><strong>FLUX.2 Pro Edit</strong> gets that image plus "add the creature here, keep everything else exactly the same". Because it's an edit of the same image, the background matches perfectly.</li>
<li><strong>Kling O3 Pro</strong> gets the creature frame as <code>image_url</code> and the empty scene as <code>end_image_url</code>. It has to animate from one to the other, so the creature has to leave, and the background can't drift.</li>
</ol>

<p>The older Veo mode chains clips instead. FFmpeg pulls the exact frame where clip 1 will be cut (<code>-ss</code> to the cut time, <code>-frames:v 1</code>, or <code>-sseof -0.1</code> for the last frame) and that becomes clip 2's first frame. When Veo's content checker rejects a harmless prompt, which it does inconsistently, the same request is retried on Veo Fast.</p>

<h3>5. The FFmpeg edit</h3>

<p><code>editor.py</code> runs FFmpeg in three passes.</p>

<p><strong>Pass 1: normalise each clip.</strong> Scale to cover 1080×1920 and centre-crop, 30 fps, square pixels, <code>yuv420p</code>. If a clip is shorter than its slot, <code>tpad=stop_mode=clone</code> holds the last frame. Clips with no sound get a silent stereo track from <code>anullsrc</code>, so every clip has identical streams.</p>

<pre><code>scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,
fps=30,setsar=1,format=yuv420p,tpad=stop_mode=clone:stop_duration=…</code></pre>

<p><strong>Pass 2: join without re-encoding.</strong> Because every clip now has identical streams, the concat demuxer joins them with <code>-c copy</code>. It's instant and loses no quality.</p>

<p><strong>Pass 3: one filter graph</strong> does the grade, the glitches, the overlay and the audio mix. It's long enough to be written to a file and passed with <code>-filter_complex_script</code>.</p>

<p><em>The infrared grade.</em> Four filters, all scaled by one <code>grade_strength</code> setting (0.6):</p>

<pre><code>eq=saturation=0.40:contrast=1.09,
colorchannelmixer=rr=0.82:gg=1:bb=0.82,
noise=alls=14:allf=t,
vignette=angle=PI/4.40</code></pre>

<p>Cutting colour saturation, then turning red and blue down to 82% while green stays at 100%, gives the green-grey night-vision tint. <code>allf=t</code> makes the noise change every frame, like real sensor grain, instead of a fixed pattern. The vignette darkens the corners like a cheap lens.</p>

<p><em>Glitches on the beat.</em> The IR flashes and sensor dropouts are one <code>eq</code> filter whose brightness is an expression evaluated on every frame (<code>eval=frame</code>). Each flash adds a term that jumps up on its beat and fades out linearly over 0.2 s. Each dropout subtracts 0.7 for the two frames before a cut or the drop.</p>

<pre><code>eq=brightness='0.45*between(t,4.970,5.170)*(1-(t-4.970)/0.2)
             + 0.12*between(t,5.384,5.584)*(1-(t-5.384)/0.2) + …
             - 0.7*between(t,4.903,4.969)':eval=frame</code></pre>

<p>How busy it gets depends on the music. The drop always flashes at 0.45. In a "frantic" track, every beat after the drop flashes at 0.12 and every bar at 0.2. In a "driving" one, only the bars flash, at 0.16. Only about a third of videos get flashes at all, picked at random, so it doesn't become a gimmick.</p>

<p><em>The trail-cam info bar.</em> A <code>drawbox</code> paints a black bar at 82% opacity over the bottom 5.5% of the frame. <code>drawtext</code> filters write the camera number, the temperature in °C and °F (worked out in Python) and a moon-phase glyph. The clock is the clever bit: FFmpeg's <code>%{pts:gmtime:EPOCH:…}</code> adds each frame's presentation time to a start time in Unix seconds, so the clock genuinely ticks with the footage.</p>

<pre><code>drawtext=fontfile=DejaVuSansMono.ttf:x=w-text_w-37:
  text='%{pts\:gmtime\:1792378034\:%Y-%m-%d %H\\\:%M\\\:%S}'</code></pre>

<p>In the chained-clip mode, each segment gets its own clock (switched on with <code>enable='between(t,a,b)'</code>) whose start time jumps forward 3 to 40 random seconds at each cut. That's what a motion-triggered camera does when it re-triggers.</p>

<p><em>Audio.</em> The music is a second input, seeked straight to the planned spot with <code>-ss</code>. It's mixed under the clip's own sound with <code>amix</code> (<code>normalize=0</code>, so FFmpeg doesn't quietly halve both volumes). After that come a 30 ms fade-in so it doesn't click, a 1-second fade-out, and <code>alimiter</code> at 0.9 to stop clipping.</p>

<p><em>Encode.</em> H.264 at CRF 20, capped with <code>-maxrate 8M -bufsize 16M</code>. The cap matters because film grain is noise, which costs a lot of bits, and a Telegram bot can only download files up to 20 MB. 15 s at 8 Mb/s plus 192 kb/s of AAC audio comes to at most about 15.4 MB. <code>-movflags +faststart</code> puts the index at the front so the video starts playing before it has fully downloaded.</p>

<h3>6. Checking the caption against the video</h3>

<p>FFmpeg grabs 12 evenly spaced frames from the finished video, one from the middle of each twelfth of its length, as small 360 px JPEGs. They're sent to Claude as base64 images, each labelled with its time, alongside the planned caption and the creature description. The structured output returns the corrected caption and a YouTube title. The prompt includes the last 10 titles, so the wording varies.</p>

<h3>7. Telegram as the approval UI, and git as the database</h3>

<ul>
<li><strong>No server.</strong> The bot is a few hundred lines of standard-library Python calling the Telegram Bot API over HTTPS. Videos are sent as hand-built <code>multipart/form-data</code>. A scheduled workflow calls <code>getUpdates</code> with a saved <code>offset</code>, so each tap or reply is read exactly once, even though nothing is listening in between.</li>
<li><strong>Buttons.</strong> I started with inline buttons, but Telegram dropped taps that the hourly poll didn't collect quickly enough. They're now ordinary keyboard buttons, which just send a normal message saying "✅ Approve", and Telegram keeps those until the next poll reads them.</li>
<li><strong>Matching replies to videos.</strong> A reply to a video is matched to its run by <code>message_id</code>. A bare "approve" goes to the latest video waiting. If a run crashed after sending its video but before saving, a later reply to that video rebuilds the missing record from the video's own caption.</li>
<li><strong>State in git.</strong> Every decision, note, post ID and stat lives in <code>data/approvals.json</code>. Each workflow ends with a script that commits <code>data/</code> and pushes, with a <code>git pull --rebase</code> and retry if another push got there first. All the workflows share one concurrency group, so they never run at the same time.</li>
<li><strong>No big files in git.</strong> The finished video is never committed. Telegram keeps it, and the publisher downloads it again by its <code>file_id</code> when it's time to post.</li>
</ul>

<h3>8. Posting to three APIs</h3>

<ul>
<li><strong>Instagram</strong> (Graph API with Instagram Login) won't take an upload, only a public URL. So the file is uploaded to fal.ai's storage first. Then a <code>REELS</code> media container is created, polled every 15 seconds until <code>status_code</code> is <code>FINISHED</code>, and published.</li>
<li><strong>YouTube</strong> trades the stored refresh token for a fresh access token on each run, then does a <strong>resumable upload</strong>. A POST with the metadata (title, description, tags, <code>containsSyntheticMedia: true</code>) returns an upload URL, and a PUT sends the bytes. If YouTube reports anything other than public, the bot tells me.</li>
<li><strong>Facebook</strong> uses the Page Reels API's three phases: <code>start</code> returns a video ID, the bytes go to <code>rupload.facebook.com</code>, and <code>finish</code> with <code>video_state=PUBLISHED</code> posts it.</li>
</ul>

<p>Each platform's result or error is stored separately on the run, so a failure on one never causes a duplicate post on another. Posting only happens inside the 20:00 to 03:00 window (a window that crosses midnight, worked out in <code>Europe/London</code> time with <code>zoneinfo</code>), at most once per platform every 20 hours. All HTTP goes through a tiny wrapper around <code>urllib</code> whose error messages drop the query string, because some of these APIs put the access token in the URL.</p>

<h3>9. Reading the stats</h3>

<p>Every morning the latest 10 posts are checked on each platform:</p>

<ul>
<li><strong>Instagram:</strong> media insights (views, reach, skip rate, average watch time, likes, shares, saves).</li>
<li><strong>YouTube:</strong> the Data API's live view and like counts, plus the Analytics API's average view duration and shares. The analytics run a day or two behind.</li>
<li><strong>Facebook:</strong> video insights. If Facebook rejects the batch, the metrics are requested one at a time, skipping any it rejects for a Reel.</li>
</ul>

<p>A platform that fails is reported and skipped, without hiding the others.</p>

<h3>10. Testing without spending money</h3>

<p>There are 73 tests, and none of them calls a paid API. The fal.ai runner, the Claude client, Telegram and the HTTP layer are all passed in, so the tests swap in fakes. Test media is generated rather than committed. Videos come from FFmpeg's <code>testsrc2</code> pattern with a <code>sine</code> tone. The music tests build a synthetic dance track in NumPy and write it as a WAV: a 60 Hz sine kick with an exponential decay on every beat, accented on the first beat of each bar, quiet before a known drop and loud with noise hi-hats after it. So the beat-grid fitting and drop detection are checked against a track where the right answer is known. The test suite runs on every push.</p>

</details>

## Twelve days of building

I built the first version in a single day with Claude Code. Most of what came after was tuning.

| Date | What changed |
|---|---|
| 13 Oct | Concept, video, editor, Telegram bot and all three publishers. First video posted that afternoon. |
| 14 Oct | Daily schedule, evening posting window, and the "skip while one is waiting" rule. |
| 15 Oct | IR flashes, endings where the creature leaves, re-makes, and tracking music use. |
| 16 Oct | Switched from chained Veo clips to a single Kling take. Added the caption check. |
| 17 Oct | Captions became a hook plus dry humour, instead of simply describing the video. |
| 20 Oct | Every video from the next day opens on the creature. Daily stats report on Telegram. |
| 24 Oct | A stricter style guide after two weak videos, and [evoclock](https://github.com/evoclock)'s bowerbird map. |

## The numbers

<div class="stats-row">
  <p class="stat"><span class="stat__value">18</span><span class="stat__label">videos made</span></p>
  <p class="stat"><span class="stat__value">13</span><span class="stat__label">approved</span></p>
  <p class="stat"><span class="stat__value">36</span><span class="stat__label">posts across three platforms</span></p>
  <p class="stat"><span class="stat__value">~$45</span><span class="stat__label">rough fal.ai spend, at $2 to $3 a video</span></p>
</div>

Of the five videos that didn't make it, three were rejected and two were earlier takes of the same creature, Tail Waltzer, from before I switched to Kling.

{% include charts/nightshift-views.html %}

The obvious outlier is **Sett Grub**, which reached 83,037 views on Instagram, about six times every other video put together. I'd been worried about low views that week, and the same morning I changed every video to open with the creature already in frame, rather than on an empty scene that's easy to scroll past. But Sett Grub had been made a few hours before that change. It opened on an empty scene like all the others. The videos that did open on the creature got 166, 3,395, 2,289 and 1,446 views. One viral video is not a trend, and I still can't fully explain this one.

YouTube is the stranger story. It was doing better than Instagram for the first week, then fell to almost nothing from 20 October. The uploads still go through fine, so I don't know why yet. That's top of my list to dig into.

Facebook has barely registered at all. The same 12 videos went up as Facebook Page Reels and got 27 plays between them, never more than 7 for a single Reel. The API also won't give me reach for Page Reels, so plays are the only count I have. I haven't done anything to grow the Page, so my guess is that Facebook just isn't showing the Reels to anyone yet.

{% include charts/nightshift-watch.html %}

Watch time is the number I care about most, because it decides how far each platform pushes a video. On Instagram, most videos hold people for 7 to 9 seconds out of 15. Opening on the creature hasn't moved that much yet. Fourjaw Wader still holds the record at 11.2 seconds, three days before the change.

YouTube's averages were higher in the first week, between 10 and 19 seconds, so some people watched the loop more than once. Since its views collapsed, though, each average comes from a handful of people. Facebook's averages swing from about 1 to 16 seconds, but with only a few plays per Reel, one person rewatching or scrolling past changes the number completely. I wouldn't read much into either yet.

## Taste is the hard part

The code was the easy bit. Getting videos I actually wanted to post took far more effort, and almost all of it went into two text files: the style guide and the guidance notes. A few lessons from rejected videos:

- **Moth Glove:** the flying looked fake and its body was vague. Creatures now need a clear anatomy (an obvious head, limbs and way of moving), and no floating or gliding.
- **Stove Toad:** smoke in the background stayed frozen while everything else moved. Video models render mist, smoke and glows badly, so the scenes are now plain.
- **Bale Folder:** nothing happened except some hay falling. Every creature now has to do something with a visible result: dig something up, rearrange an object, hunt.
- **The creel and the skep:** two creatures based on objects I had to Google. Non-animal creatures now come from things everyone recognises, like a tree stump, a boulder or a fence.


## What's next

- Find out why YouTube views collapsed, and why Facebook Reels get almost no plays.
- Re-make a rejected sighting automatically, using my notes on it.
- Warn me before the Instagram token expires. It lasts 60 days, and Actions can't rewrite its own secrets.
- A proper performance monitor: comment summaries, a look at similar channels, and experiments with Instagram's trial Reels. The daily stats report is the first piece of it.
- Two videos a day, if watch time holds after the first four weeks.
- Overall, I'm still not overly thrilled about the quality of the posts and there is huge room for improvement. Since this is a hobby experiment project that I'm just doing for fun and wish to spend minimal time and money on, I will just be iteratively improving the style guide as videos come in every day. Mostly, I'm just enjoying receiving weird creatures on my phone every morning. 

The repo is private for now, because it holds the channel's state and history. If you have questions about any part of it, the Night Shift accounts are the best place to find me.
