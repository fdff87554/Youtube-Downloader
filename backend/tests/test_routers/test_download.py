"""Tests for the download streaming API endpoint."""

from unittest.mock import MagicMock, patch

import pytest


class TestDownloadVideo:
    @patch("app.routers.download.stream_download")
    def test_download_with_mp4_returns_streaming_video_response(
        self,
        mock_stream: MagicMock,
        client,
    ) -> None:
        mock_stream.return_value = iter([b"fake video data"])

        response = client.get(
            "/api/download",
            params={
                "url": "https://www.youtube.com/watch?v=test",
                "fmt": "mp4",
                "quality": "best",
                "title": "Test Video",
            },
        )

        assert response.status_code == 200
        assert "attachment" in response.headers.get("content-disposition", "")
        assert response.headers.get("content-type") == "video/mp4"

    @patch("app.routers.download.stream_download")
    def test_download_with_mp3_returns_audio_mpeg_response(
        self,
        mock_stream: MagicMock,
        client,
    ) -> None:
        mock_stream.return_value = iter([b"fake audio data"])

        response = client.get(
            "/api/download",
            params={
                "url": "https://www.youtube.com/watch?v=test",
                "fmt": "mp3",
            },
        )

        assert response.status_code == 200
        assert response.headers.get("content-type") == "audio/mpeg"

    def test_download_with_invalid_url_returns_400(self, client) -> None:
        response = client.get(
            "/api/download",
            params={"url": "https://example.com/video"},
        )

        assert response.status_code == 400
        assert response.json()["error"]["code"] == "invalid_url"

    @patch("app.routers.download.stream_download")
    def test_download_when_stream_fails_returns_500(
        self,
        mock_stream: MagicMock,
        client,
    ) -> None:
        from app.services.youtube import YouTubeError

        mock_stream.side_effect = YouTubeError("download failed")

        response = client.get(
            "/api/download",
            params={"url": "https://www.youtube.com/watch?v=test"},
        )

        assert response.status_code == 500
        assert response.json()["error"]["code"] == "download_error"

    def test_download_without_url_returns_422(self, client) -> None:
        response = client.get("/api/download")

        assert response.status_code == 422

    @patch("app.routers.download.stream_download")
    def test_download_with_title_uses_it_in_content_disposition(
        self,
        mock_stream: MagicMock,
        client,
    ) -> None:
        mock_stream.return_value = iter([b"data"])

        response = client.get(
            "/api/download",
            params={
                "url": "https://www.youtube.com/watch?v=test",
                "title": "My Video",
            },
        )

        assert response.status_code == 200
        disposition = response.headers.get("content-disposition", "")
        assert "My%20Video" in disposition

    @patch("app.routers.download.stream_download")
    def test_download_without_title_uses_default_filename(
        self,
        mock_stream: MagicMock,
        client,
    ) -> None:
        mock_stream.return_value = iter([b"data"])

        response = client.get(
            "/api/download",
            params={"url": "https://www.youtube.com/watch?v=test"},
        )

        assert response.status_code == 200
        disposition = response.headers.get("content-disposition", "")
        assert "download.mp4" in disposition

    @patch("app.routers.download.stream_download")
    def test_download_failure_mid_stream_does_not_become_json_envelope(
        self,
        mock_stream: MagicMock,
        client,
    ) -> None:
        """Once StreamingResponse starts, a generator-time failure cannot
        be turned into the standard JSON 5xx envelope -- HTTP headers
        have already been written.

        In a real ASGI deployment the client sees a truncated body /
        ERR_INCOMPLETE_CHUNKED_ENCODING. Under TestClient the exception
        propagates to the caller (see anyio task-group surface). Either
        way the response cannot be a JSON envelope claiming success.

        This test pins that contract so future contributors do not add
        a try/except around StreamingResponse and assume it can yield
        a JSON 5xx body.
        """
        from app.services.youtube import YouTubeError

        def failing_generator():
            yield b"partial"
            raise YouTubeError("simulated yt-dlp crash mid-stream")

        mock_stream.return_value = failing_generator()

        with (
            pytest.raises(YouTubeError, match="simulated yt-dlp"),
            client.stream(
                "GET",
                "/api/download",
                params={"url": "https://www.youtube.com/watch?v=test"},
            ) as response,
        ):
            # Headers were already on the wire before the failure.
            assert response.status_code == 200
            assert response.headers["content-type"] == "video/mp4"
            for _ in response.iter_bytes():
                pass
