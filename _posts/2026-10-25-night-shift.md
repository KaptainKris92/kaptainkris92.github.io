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
