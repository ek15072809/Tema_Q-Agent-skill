"""video_downloader.py — yt-dlp wrapper + HTML video URL scraper.

Standard-library only EXCEPT for `yt_dlp` (which the SKILL.md instructs to
install). ffmpeg is invoked via subprocess; if absent, conversion is skipped
with a clear warning.

Provides:
  * SUPPORTED_PLATFORMS          — quick reference table.
  * QUALITY_TO_FORMAT            — quality name -> yt-dlp format string.
  * list_formats(url)            — print available formats without downloading.
  * download(url, ...)           — download with sane defaults.
  * extract_video_urls_from_html — regex for <video>/<source>/m3u8/mp4.
  * fetch_page_and_extract(url)  — urllib fetch + extract.
  * pick_format(formats, target) — pick a format string for a goal.
  * main(argv)                   — CLI entry: python video_downloader.py URL [options]
"""
from __future__ import annotations
import argparse
import re
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Iterable


# ---- Quick reference -----------------------------------------------------

SUPPORTED_PLATFORMS: dict[str, str] = {
    "YouTube":      "https://www.youtube.com/",
    "YouTube Music": "https://music.youtube.com/",
    "Vimeo":        "https://vimeo.com/",
    "Twitch":       "https://www.twitch.tv/",
    "Twitter / X":  "https://twitter.com/ or https://x.com/",
    "Instagram":    "https://www.instagram.com/",
    "TikTok":       "https://www.tiktok.com/",
    "Facebook":     "https://www.facebook.com/",
    "Bilibili":     "https://www.bilibili.com/",
    "SoundCloud":   "https://soundcloud.com/",
    "Streamable":   "https://streamable.com/",
    "Reddit video": "https://www.reddit.com/",
}

# quality -> yt-dlp -f format string
QUALITY_TO_FORMAT: dict[str, str] = {
    "low":    "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best[height<=360]",
    "medium": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[height<=720]",
    "high":   "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best[height<=1080]",
    "best":   "bestvideo+bestaudio/best",
    "audio":  "bestaudio/best",
}


# ---- yt-dlp wrappers -----------------------------------------------------

def _check_yt_dlp() -> bool:
    try:
        import yt_dlp  # noqa: F401
        return True
    except ImportError:
        return False


def _check_ffmpeg() -> bool:
    try:
        r = subprocess.run(["ffmpeg", "-version"],
                            capture_output=True, text=True, timeout=5)
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def list_formats(url: str) -> list[dict]:
    """Print available formats for the URL without downloading. Returns the
    parsed list of format dicts from yt-dlp."""
    if not _check_yt_dlp():
        print("ERROR: yt-dlp not installed. Run: pip install yt-dlp", file=sys.stderr)
        return []
    import yt_dlp
    opts = {"quiet": True, "skip_download": True, "listformats": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return info.get("formats", []) if isinstance(info, dict) else []


def download(url: str,
             quality: str = "high",
             out_dir: str = "/home/z/my-project/download/videos",
             playlist: bool = False,
             playlist_items: str | None = None,
             extra_opts: dict | None = None) -> Path:
    """Download a video using yt-dlp.

    quality: 'low' / 'medium' / 'high' / 'best' / 'audio'.
    Returns the output directory (yt-dlp may produce multiple files).
    """
    if not _check_yt_dlp():
        raise RuntimeError("yt-dlp not installed. Run: pip install yt-dlp")

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    fmt = QUALITY_TO_FORMAT.get(quality, QUALITY_TO_FORMAT["high"])
    opts: dict = {
        "format": fmt,
        "outtmpl": str(out_path / "%(title).80s.%(ext)s"),
        "merge_output_format": "mp4" if quality != "audio" else None,
        "noplaylist": not playlist,
        "writethumbnail": False,
        "ignoreerrors": True,
        "no_warnings": True,
        "quiet": False,
    }
    if playlist_items:
        opts["playlist_items"] = playlist_items
    if quality == "audio":
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    if not _check_ffmpeg() and quality != "low":
        print("WARNING: ffmpeg not found — cannot merge/separate streams. "
              "Falling back to single-file best.", file=sys.stderr)
        opts["format"] = "best[ext=mp4]/best"

    if extra_opts:
        opts.update(extra_opts)

    import yt_dlp
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    return out_path


# ---- HTML scraping (fallback for embedded videos) -----------------------

# Match common video URL patterns inside HTML attributes / text.
_VIDEO_PATTERNS: list[re.Pattern] = [
    re.compile(r'<video[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE),
    re.compile(r'<source[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE),
    re.compile(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', re.IGNORECASE),
    re.compile(r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*', re.IGNORECASE),
    re.compile(r'https?://[^\s"\'<>]+\.webm[^\s"\'<>]*', re.IGNORECASE),
    re.compile(r'https?://[^\s"\'<>]+\.mov[^\s"\'<>]*', re.IGNORECASE),
]


def extract_video_urls_from_html(html: str) -> list[str]:
    """Extract candidate video URLs from an HTML string.

    Returns deduped list, preserving order. Includes <video src>, <source src>,
    and any bare .m3u8/.mp4/.webm/.mov URLs found in the text.
    """
    seen: set[str] = set()
    out: list[str] = []
    for pat in _VIDEO_PATTERNS:
        for m in pat.finditer(html):
            url = m.group(1) if m.groups() else m.group(0)
            if url not in seen:
                seen.add(url)
                out.append(url)
    return out


def fetch_page_and_extract(url: str,
                            headers: dict | None = None,
                            timeout: int = 20) -> list[str]:
    """Fetch a URL with urllib and extract candidate video URLs.

    Use this when yt-dlp fails AND the page does not require JS rendering.
    For JS-heavy pages, use the --browser tool to get the rendered HTML
    and pass it to extract_video_urls_from_html().
    """
    hdrs = {"User-Agent": "Mozilla/5.0 (video-downloader skill)"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code} fetching {url}: {exc.reason}")
    return extract_video_urls_from_html(html)


# ---- Format picker -------------------------------------------------------

def pick_format(formats: list[dict],
                target: str = "high") -> str:
    """Pick the best yt-dlp -f format string given available formats.

    Conservative: if the requested quality isn't available, falls back
    to 'best' rather than failing.
    """
    if not formats:
        return QUALITY_TO_FORMAT.get(target, QUALITY_TO_FORMAT["high"])

    # Inspect heights present.
    heights = sorted({f.get("height") for f in formats if f.get("height")},
                     reverse=True)
    if not heights:
        # Audio-only stream.
        return "bestaudio/best"

    target_h = {"low": 360, "medium": 720, "high": 1080, "best": 9999}.get(target, 1080)
    available = [h for h in heights if h <= target_h]
    chosen_h = max(available) if available else max(heights)
    return (f"bestvideo[height<={chosen_h}][ext=mp4]+bestaudio[ext=m4a]"
            f"/best[height<={chosen_h}][ext=mp4]/best[height<={chosen_h}]")


# ---- CLI -----------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Download videos via yt-dlp or scrape HTML for video URLs.",
    )
    ap.add_argument("url", help="Video URL or HTML page URL.")
    ap.add_argument("-q", "--quality", default="high",
                    choices=list(QUALITY_TO_FORMAT.keys()),
                    help="Quality target (default: high)")
    ap.add_argument("-o", "--out-dir", default="/home/z/my-project/download/videos",
                    help="Output directory (default: /home/z/my-project/download/videos)")
    ap.add_argument("--playlist", action="store_true",
                    help="Download entire playlist if URL is a playlist.")
    ap.add_argument("--list-formats", action="store_true",
                    help="List available formats and exit (no download).")
    ap.add_argument("--scrape-only", action="store_true",
                    help="Only scrape the URL for embedded video URLs (no download).")
    args = ap.parse_args(argv)

    if args.list_formats:
        fmts = list_formats(args.url)
        for f in fmts:
            print(f"  {f.get('format_id','?'):>6} | "
                  f"{f.get('ext','?'):>5} | "
                  f"{f.get('height','—') or '—':>5}p | "
                  f"{f.get('filesize','?') or '?'} bytes | "
                  f"{f.get('vcodec','?')}/{f.get('acodec','?')}")
        return 0

    if args.scrape_only:
        urls = fetch_page_and_extract(args.url)
        if not urls:
            print("No video URLs found in page. Try the --browser tool for JS-rendered pages.")
            return 1
        print(f"Found {len(urls)} video URL(s):")
        for u in urls:
            print(f"  - {u}")
        return 0

    out = download(args.url, quality=args.quality,
                   out_dir=args.out_dir, playlist=args.playlist)
    print(f"\nDownloaded to: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
