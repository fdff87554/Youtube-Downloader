"""YouTube service layer wrapping yt-dlp for metadata extraction and streaming."""

from __future__ import annotations

import logging
import re
import subprocess
from collections.abc import Generator
from typing import Any

import yt_dlp

from app.schemas.video import (
    PlaylistEntry,
    PlaylistInfo,
    VideoFormat,
    VideoInfo,
)

logger = logging.getLogger(__name__)

YOUTUBE_URL_PATTERN = re.compile(
    r"^https?://(?:www\.|m\.)?(?:youtube\.com|youtu\.be)/",
)

SOCKET_TIMEOUT = 30
CHUNK_SIZE = 65536


class YouTubeError(Exception):
    """Base exception for YouTube service errors."""


class VideoNotFoundError(YouTubeError):
    """Raised when a video cannot be found or is unavailable."""


class InvalidURLError(YouTubeError):
    """Raised when the provided URL is not a valid YouTube URL."""


def validate_youtube_url(url: str) -> None:
    """Validate that a URL points to YouTube.

    Args:
        url: The URL to validate.

    Raises:
        InvalidURLError: If the URL is not a valid YouTube URL.
    """
    if not YOUTUBE_URL_PATTERN.match(url):
        raise InvalidURLError("URL must be a valid YouTube URL.")


def extract_video_info(url: str) -> VideoInfo:
    """Extract metadata and available formats for a single video.

    Args:
        url: YouTube video URL.

    Returns:
        VideoInfo with metadata and available formats.

    Raises:
        InvalidURLError: If the URL is not a valid YouTube URL.
        VideoNotFoundError: If the video cannot be found.
        YouTubeError: For other extraction failures.
    """
    validate_youtube_url(url)

    ydl_opts = _base_opts() | {"noplaylist": True}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except yt_dlp.utils.DownloadError as e:
        _raise_from_download_error(e)
    except Exception as e:
        raise YouTubeError(f"Failed to extract video info: {e}") from e

    if info is None:
        raise VideoNotFoundError("Could not retrieve video information.")

    formats = _parse_formats(info.get("formats") or [])

    return VideoInfo(
        video_id=info.get("id", ""),
        title=info.get("title", "Unknown"),
        thumbnail=info.get("thumbnail", ""),
        duration=info.get("duration") or 0,
        uploader=info.get("uploader") or info.get("channel", "Unknown"),
        formats=formats,
    )


def extract_playlist_info(url: str) -> PlaylistInfo:
    """Extract metadata for a YouTube playlist.

    Args:
        url: YouTube playlist URL.

    Returns:
        PlaylistInfo with playlist metadata and video entries.

    Raises:
        InvalidURLError: If the URL is not a valid YouTube URL.
        VideoNotFoundError: If the playlist cannot be found.
        YouTubeError: For other extraction failures.
    """
    validate_youtube_url(url)

    ydl_opts = _base_opts() | {
        "extract_flat": "in_playlist",
        "noplaylist": False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except yt_dlp.utils.DownloadError as e:
        _raise_from_download_error(e)
    except Exception as e:
        raise YouTubeError(f"Failed to extract playlist info: {e}") from e

    if info is None:
        raise VideoNotFoundError("Could not retrieve playlist information.")

    raw_entries = info.get("entries") or []
    entries = [
        PlaylistEntry(
            video_id=e.get("id", ""),
            title=e.get("title", "Unknown"),
            duration=e.get("duration") or 0,
            thumbnail=e.get("thumbnail") or e.get("thumbnails", [{}])[0].get("url", ""),
        )
        for e in raw_entries
        if e is not None
    ]

    return PlaylistInfo(
        playlist_id=info.get("id", ""),
        title=info.get("title", "Unknown"),
        uploader=info.get("uploader") or info.get("channel", "Unknown"),
        video_count=len(entries),
        entries=entries,
    )


def stream_download(
    url: str,
    format_type: str = "mp4",
    quality: str = "best",
) -> Generator[bytes, None, None]:
    """Stream a video download as chunks without writing to disk.

    Uses yt-dlp subprocess to pipe output directly to the caller,
    ensuring zero disk I/O on the server.

    Args:
        url: YouTube video URL.
        format_type: Output format, either "mp4" or "mp3".
        quality: Quality selection (best, 1080, 720, 480).

    Yields:
        Chunks of the downloaded media.

    Raises:
        InvalidURLError: If the URL is not a valid YouTube URL.
        YouTubeError: For download failures.
    """
    validate_youtube_url(url)

    cmd = _build_download_command(url, format_type, quality)

    try:
        process = subprocess.Popen(  # noqa: S603
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as e:
        raise YouTubeError("yt-dlp is not installed or not in PATH.") from e

    try:
        assert process.stdout is not None  # noqa: S101
        while True:
            chunk = process.stdout.read(CHUNK_SIZE)
            if not chunk:
                break
            yield chunk
    finally:
        process.stdout.close()
        return_code = process.wait()

    if return_code != 0:
        stderr_msg = ""
        if process.stderr:
            stderr_msg = process.stderr.read().decode(errors="replace")
            process.stderr.close()
        raise YouTubeError(f"Download failed (exit {return_code}): {stderr_msg[:200]}")

    if process.stderr:
        process.stderr.close()


def get_download_filename(url: str, format_type: str = "mp4") -> str:
    """Generate a filename for the download based on video title.

    Args:
        url: YouTube video URL.
        format_type: Output format (mp4 or mp3).

    Returns:
        Sanitized filename with appropriate extension.
    """
    try:
        info = extract_video_info(url)
        title = _sanitize_filename(info.title)
    except YouTubeError:
        title = "download"

    ext = "mp3" if format_type == "mp3" else "mp4"
    return f"{title}.{ext}"


def _build_download_command(
    url: str,
    format_type: str,
    quality: str,
) -> list[str]:
    format_spec = _resolve_format_spec(format_type, quality)

    cmd = [
        "yt-dlp",
        "--no-playlist",
        "-f",
        format_spec,
        "-o",
        "-",
        "--quiet",
        "--no-warnings",
        "--socket-timeout",
        str(SOCKET_TIMEOUT),
    ]

    if format_type == "mp3":
        cmd.extend(["--extract-audio", "--audio-format", "mp3"])
    else:
        cmd.extend(["--merge-output-format", "mp4"])

    cmd.append(url)
    return cmd


def _resolve_format_spec(format_type: str, quality: str) -> str:
    if format_type == "mp3":
        return "bestaudio/best"

    _v = "bestvideo[ext=mp4]"
    _a = "bestaudio[ext=m4a]"
    _fb = "best[ext=mp4]/best"
    quality_map = {
        "best": f"{_v}+{_a}/{_fb}",
        "1080": f"{_v}[height<=1080]+{_a}/best[height<=1080]/best",
        "720": f"{_v}[height<=720]+{_a}/best[height<=720]/best",
        "480": f"{_v}[height<=480]+{_a}/best[height<=480]/best",
    }
    return quality_map.get(quality, quality_map["best"])


def _base_opts() -> dict[str, Any]:
    return {
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": SOCKET_TIMEOUT,
    }


def _parse_formats(raw_formats: list[dict[str, Any]]) -> list[VideoFormat]:
    seen_qualities: set[str] = set()
    formats: list[VideoFormat] = []

    for f in raw_formats:
        height = f.get("height")
        has_video = f.get("vcodec", "none") != "none"
        has_audio = f.get("acodec", "none") != "none"

        if has_video and height:
            quality = f"{height}p"
        elif has_audio and not has_video:
            quality = "audio"
        else:
            continue

        key = f"{quality}-{f.get('ext', '')}"
        if key in seen_qualities:
            continue
        seen_qualities.add(key)

        filesize = f.get("filesize") or f.get("filesize_approx")

        formats.append(
            VideoFormat(
                format_id=f.get("format_id", ""),
                ext=f.get("ext", ""),
                quality=quality,
                has_video=has_video,
                has_audio=has_audio,
                filesize_approx=filesize,
            )
        )

    return formats


def _raise_from_download_error(e: yt_dlp.utils.DownloadError) -> None:
    msg = str(e).lower()
    if "private" in msg or "unavailable" in msg or "not available" in msg:
        raise VideoNotFoundError(f"Video is unavailable: {e}") from e
    raise YouTubeError(f"Download error: {e}") from e


def _sanitize_filename(name: str) -> str:
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", name)
    sanitized = sanitized.strip(". ")
    return sanitized[:200] if sanitized else "download"
