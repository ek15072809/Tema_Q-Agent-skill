---
name: video-downloader
description: Download videos from YouTube and other platforms (yt-dlp) or extract video URLs from HTML pages (--browser). Save in chosen format/quality for offline viewing, editing, or archiving.
---

# Video-Downloader Skill

## Overview
Two download paths:
1. **yt-dlp** (preferred) — 1000+ platforms (YouTube, Vimeo, Twitch, Twitter, Bilibili, etc.). Requires `yt-dlp` (Python package) + `ffmpeg` (system binary) for format conversion.
2. **--browser HTML scrape** — when the video is embedded in a web page (e.g., `<video>` tag, m3u8 stream) and yt-dlp can't find it. Drive Chromium via the `browser` tool to extract the source URL.

Output path: `/home/z/my-project/download/videos/<filename>.<ext>`

## Required Tools

```bash
# yt-dlp (Python package — usually pre-installed in Tema_Q-Agent env)
python -c "import yt_dlp" 2>/dev/null && echo OK || pip install --break-system-packages yt-dlp

# ffmpeg (system binary — required for format conversion / merging)
which ffmpeg || apt-get install -y ffmpeg
```
The skill auto-detects availability and falls back gracefully.

## Bundled Helper Module
**`skill/video-downloader/scripts/video_downloader.py`** provides:
- `download(url, format_, quality, out_dir, playlist)` — yt-dlp wrapper with sane defaults.
- `list_formats(url)` — print available formats (don't download yet).
- `extract_video_urls_from_html(html)` — regex `<video>` / `<source>` / m3u8 / mp4 links.
- `fetch_page_and_extract(url)` — `urllib` fetch + extract (no browser needed).
- `SUPPORTED_PLATFORMS` — quick reference for what yt-dlp handles.
- `pick_format(formats, target)` — pick the best format string for a goal.

```python
import sys; sys.path.insert(0, "skill/video-downloader/scripts")
from video_downloader import (download, list_formats, extract_video_urls_from_html,
                               fetch_page_and_extract, SUPPORTED_PLATFORMS, pick_format)
```
Run `python skill/video-downloader/scripts/video_downloader.py --help` for CLI usage.

## Path Selection

```
User request
  ├── URL matches a supported platform (YouTube/Vimeo/...)  → yt-dlp
  ├── URL is an HTML page with embedded video               → fetch_page_and_extract()
  │     └── page requires JS / login                        → --browser scrape
  └── URL is a direct .mp4 / .m3u8                          → download directly with urllib
```

## yt-dlp Quick Reference

### Format selection (`-f` flag)
| Goal | Format string |
|---|---|
| Best quality (≤1080p, MP4) | `bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best` |
| Best quality (any) | `bestvideo+bestaudio/best` |
| 720p MP4 | `bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]` |
| Audio only (MP3) | `bestaudio/best` (postprocess to mp3 with `--extract-audio --audio-format mp3`) |
| Subtitle burn-in | add `--write-subs --embed-subs` |

### Quality levels (this skill's `quality` arg)
- `low`    → 360p
- `medium` → 720p
- `high`   → 1080p
- `best`   → no limit
- `audio`  → MP3 192k

### Playlist handling
- Default: download single video only.
- `playlist=True`: download entire playlist.
- `playlist_items="1-5"`: first 5 items.

## --browser HTML Scrape

When yt-dlp fails or the video is embedded:
1. `browser(action="navigate", url=page_url)`
2. `browser(action="snapshot")` to get the rendered HTML
3. `extract_video_urls_from_html(html)` to find `<video src>`, `<source src>`, `.m3u8`, `.mp4`
4. If a `.m3u8` is found: pass it to `download()` (yt-dlp handles HLS).
5. If only `.mp4` chunks: download each and merge with ffmpeg.

## Workflow

1. **Classify** the URL: platform? HTML page? direct video?
2. **Check tools**: yt-dlp available? ffmpeg available?
3. **Pick format**: ask user for quality if not specified; default to `high` (1080p).
4. **Download**: use `download()` wrapper.
5. **Verify**: file exists, size > 100KB, plays (ffprobe check).
6. **Output**: confirm path + size + duration to user.

## Output Format

```markdown
# Video Download — {title}

## Source
- URL: {url}
- Platform: {youtube / vimeo / html-scrape / direct}
- Title: {video title}

## Output
- Path: /home/z/my-project/download/videos/{filename}
- Format: {mp4 / mkv / mp3}
- Quality: {1080p / 720p / audio}
- Size: {N} MB
- Duration: {mm:ss}

## Subtitles
- {list of subtitle languages included, or "none"}

## Errors / Warnings
- {any issues encountered}
```

## Self-Check
- [ ] Tool availability checked (yt-dlp + ffmpeg)?
- [ ] Format string explicit (don't rely on `best`)?
- [ ] Output path under `/home/z/my-project/download/videos/`?
- [ ] File size verified (>100KB after download)?
- [ ] Duration verified with ffprobe?
- [ ] Subtitles requested if user asked?
- [ ] Playlist mode confirmed before mass download?

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| "best" returns weird format | Use explicit `[ext=mp4]` filter |
| Audio/video out of sync | Ensure ffmpeg installed; yt-dlp auto-merges |
| 429 rate limited | Add `--sleep-requests 1` |
| Geo-blocked | Use `--geo-bypass-country JP` (legal depends on jurisdiction) |
| Login required | Use `--cookies-from-browser` or `--browser` scrape |
| HLS stream split | yt-dlp handles m3u8 natively; pass the .m3u8 URL |
| Filename weird | Use `-o "%(title)s.%(ext)s"` template |
| Huge file | Cap with `[height<=720]` or download audio only |
