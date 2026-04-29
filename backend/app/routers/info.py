"""API endpoints for video and playlist information."""

from urllib.parse import urlparse

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from app.limiter import limiter
from app.routers.shared import error_response
from app.schemas.video import ErrorEnvelope, PlaylistInfo, VideoFormat, VideoInfo
from app.services.youtube import (
    InvalidURLError,
    VideoNotFoundError,
    YouTubeError,
    extract_playlist_info,
    extract_video_info,
)

router = APIRouter(prefix="/api", tags=["info"])


@router.get(
    "/info",
    response_model=VideoInfo | PlaylistInfo,
    responses={
        400: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        500: {"model": ErrorEnvelope},
    },
)
@limiter.limit("30/minute")
async def get_info(
    request: Request,
    url: str = Query(..., description="YouTube video or playlist URL"),
) -> VideoInfo | PlaylistInfo | JSONResponse:
    """Retrieve metadata for a YouTube video or playlist.

    Args:
        url: YouTube video or playlist URL.

    Returns:
        VideoInfo for single videos, PlaylistInfo for playlists.
    """
    try:
        if _is_playlist_url(url):
            return extract_playlist_info(url)
        return extract_video_info(url)
    except InvalidURLError as e:
        return error_response(400, "invalid_url", str(e))
    except VideoNotFoundError as e:
        return error_response(
            404,
            "not_found",
            "The requested video or playlist is not available.",
            detail=str(e),
        )
    except YouTubeError as e:
        return error_response(
            500,
            "extraction_error",
            "Could not process this URL. Please try a different one.",
            detail=str(e),
        )


@router.get(
    "/formats",
    response_model=list[VideoFormat],
    responses={
        400: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        500: {"model": ErrorEnvelope},
    },
)
@limiter.limit("30/minute")
async def get_formats(
    request: Request,
    url: str = Query(..., description="YouTube video URL"),
) -> list | JSONResponse:
    """List available download formats for a YouTube video.

    Args:
        url: YouTube video URL.

    Returns:
        List of available VideoFormat objects.
    """
    try:
        info = extract_video_info(url)
        return info.formats
    except InvalidURLError as e:
        return error_response(400, "invalid_url", str(e))
    except VideoNotFoundError as e:
        return error_response(
            404,
            "not_found",
            "The requested video is not available.",
            detail=str(e),
        )
    except YouTubeError as e:
        return error_response(
            500,
            "extraction_error",
            "Could not list formats for this URL.",
            detail=str(e),
        )


def _is_playlist_url(url: str) -> bool:
    """Detect playlist URLs by path, not query parameters.

    URLs like watch?v=abc&list=PLxxx are treated as single videos
    since the user's intent is to download that specific video.
    Only /playlist paths are treated as playlist requests.
    """
    parsed = urlparse(url)
    return parsed.path.rstrip("/").endswith("/playlist")
