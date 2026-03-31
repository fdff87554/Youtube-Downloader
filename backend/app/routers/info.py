"""API endpoints for video and playlist information."""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from app.schemas.video import ErrorEnvelope, PlaylistInfo, VideoInfo
from app.services.youtube import (
    InvalidURLError,
    VideoNotFoundError,
    YouTubeError,
    extract_playlist_info,
    extract_video_info,
)

router = APIRouter(prefix="/api", tags=["info"])

_PLAYLIST_INDICATORS = ("list=", "/playlist")


@router.get(
    "/info",
    response_model=VideoInfo | PlaylistInfo,
    responses={
        400: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        500: {"model": ErrorEnvelope},
    },
)
async def get_info(
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
        return _error_response(400, "invalid_url", str(e))
    except VideoNotFoundError as e:
        return _error_response(404, "not_found", str(e))
    except YouTubeError as e:
        return _error_response(500, "extraction_error", str(e))


@router.get(
    "/formats",
    response_model=list,
    responses={
        400: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        500: {"model": ErrorEnvelope},
    },
)
async def get_formats(
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
        return _error_response(400, "invalid_url", str(e))
    except VideoNotFoundError as e:
        return _error_response(404, "not_found", str(e))
    except YouTubeError as e:
        return _error_response(500, "extraction_error", str(e))


def _is_playlist_url(url: str) -> bool:
    return any(indicator in url for indicator in _PLAYLIST_INDICATORS)


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )
