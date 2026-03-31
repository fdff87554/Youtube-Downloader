"""API endpoint for streaming video/audio downloads."""

from enum import StrEnum
from urllib.parse import quote

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, StreamingResponse

from app.schemas.video import ErrorEnvelope
from app.services.youtube import (
    InvalidURLError,
    VideoNotFoundError,
    YouTubeError,
    get_download_filename,
    stream_download,
)

router = APIRouter(prefix="/api", tags=["download"])


class FormatType(StrEnum):
    """Supported download format types."""

    MP4 = "mp4"
    MP3 = "mp3"


class Quality(StrEnum):
    """Supported video quality levels."""

    BEST = "best"
    Q1080 = "1080"
    Q720 = "720"
    Q480 = "480"


MEDIA_TYPES = {
    FormatType.MP4: "video/mp4",
    FormatType.MP3: "audio/mpeg",
}


@router.get(
    "/download",
    response_model=None,
    responses={
        200: {"content": {"video/mp4": {}, "audio/mpeg": {}}},
        400: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        500: {"model": ErrorEnvelope},
    },
)
async def download_video(
    url: str = Query(..., description="YouTube video URL"),
    fmt: FormatType = FormatType.MP4,
    quality: Quality = Quality.BEST,
) -> StreamingResponse | JSONResponse:
    """Stream a YouTube video or audio download.

    Pipes yt-dlp output directly to the HTTP response with zero disk I/O.

    Args:
        url: YouTube video URL.
        fmt: Output format (mp4 or mp3).
        quality: Video quality (best, 1080, 720, 480).

    Returns:
        StreamingResponse with the media content.
    """
    try:
        filename = get_download_filename(url, fmt.value)
        media_type = MEDIA_TYPES[fmt]
        encoded_filename = quote(filename)

        return StreamingResponse(
            content=stream_download(url, fmt.value, quality.value),
            media_type=media_type,
            headers={
                "Content-Disposition": (
                    f"attachment; "
                    f'filename="{encoded_filename}"; '
                    f"filename*=UTF-8''{encoded_filename}"
                ),
            },
        )
    except InvalidURLError as e:
        return _error_response(400, "invalid_url", str(e))
    except VideoNotFoundError as e:
        return _error_response(404, "not_found", str(e))
    except YouTubeError as e:
        return _error_response(500, "download_error", str(e))


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )
