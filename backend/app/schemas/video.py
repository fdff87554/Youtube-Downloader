"""Pydantic models for video metadata and format information."""

from pydantic import BaseModel


class VideoFormat(BaseModel):
    """A single available format for a video.

    Attributes:
        format_id: yt-dlp internal format identifier.
        ext: File extension (e.g. mp4, webm, m4a).
        quality: Human-readable quality label (e.g. 1080p, 720p).
        has_video: Whether this format includes a video stream.
        has_audio: Whether this format includes an audio stream.
        filesize_approx: Estimated file size in bytes, if available.
    """

    format_id: str
    ext: str
    quality: str
    has_video: bool
    has_audio: bool
    filesize_approx: int | None = None


class VideoInfo(BaseModel):
    """Metadata for a single YouTube video.

    Attributes:
        video_id: YouTube video ID.
        title: Video title.
        thumbnail: URL of the video thumbnail.
        duration: Video duration in seconds.
        uploader: Channel or uploader name.
        formats: List of available download formats.
    """

    video_id: str
    title: str
    thumbnail: str
    duration: int
    uploader: str
    formats: list[VideoFormat]


class PlaylistEntry(BaseModel):
    """Summary of a single video within a playlist.

    Attributes:
        video_id: YouTube video ID.
        title: Video title.
        duration: Video duration in seconds.
        thumbnail: URL of the video thumbnail.
    """

    video_id: str
    title: str
    duration: int
    thumbnail: str


class PlaylistInfo(BaseModel):
    """Metadata for a YouTube playlist.

    Attributes:
        playlist_id: YouTube playlist ID.
        title: Playlist title.
        uploader: Playlist creator name.
        video_count: Number of videos in the playlist.
        entries: List of videos in the playlist.
    """

    playlist_id: str
    title: str
    uploader: str
    video_count: int
    entries: list[PlaylistEntry]


class ErrorResponse(BaseModel):
    """Unified error response format.

    Attributes:
        code: Machine-readable error code.
        message: Human-readable error description.
    """

    code: str
    message: str


class ErrorEnvelope(BaseModel):
    """Wrapper for error responses.

    Attributes:
        error: The error details.
    """

    error: ErrorResponse
