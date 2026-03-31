"""Tests for the download streaming API endpoint."""

from unittest.mock import MagicMock, patch


class TestDownloadVideo:
    @patch("app.routers.download.stream_download")
    def test_returns_streaming_response_for_mp4(
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
    def test_returns_audio_mpeg_for_mp3(
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

    def test_returns_400_for_invalid_url(self, client) -> None:
        response = client.get(
            "/api/download",
            params={"url": "https://example.com/video"},
        )

        assert response.status_code == 400
        assert response.json()["error"]["code"] == "invalid_url"

    @patch("app.routers.download.stream_download")
    def test_returns_500_for_download_failure(
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

    def test_returns_422_for_missing_url(self, client) -> None:
        response = client.get("/api/download")

        assert response.status_code == 422

    @patch("app.routers.download.stream_download")
    def test_uses_title_for_filename(
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
    def test_fallback_filename_without_title(
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
