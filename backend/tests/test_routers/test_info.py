"""Tests for the video info and format listing API endpoints."""

from unittest.mock import MagicMock, patch

from app.schemas.video import VideoFormat, VideoInfo


class TestGetInfo:
    @patch("app.routers.info.extract_video_info")
    def test_returns_video_info_for_valid_url(
        self, mock_extract: MagicMock, client
    ) -> None:
        mock_extract.return_value = VideoInfo(
            video_id="test123",
            title="Test Video",
            thumbnail="https://example.com/thumb.jpg",
            duration=120,
            uploader="Test Channel",
            formats=[],
        )

        response = client.get(
            "/api/info",
            params={"url": "https://www.youtube.com/watch?v=test123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["video_id"] == "test123"
        assert data["title"] == "Test Video"

    @patch("app.routers.info.extract_video_info")
    def test_returns_400_for_invalid_url(self, mock_extract: MagicMock, client) -> None:
        from app.services.youtube import InvalidURLError

        mock_extract.side_effect = InvalidURLError("URL must be a valid YouTube URL.")

        response = client.get(
            "/api/info",
            params={"url": "https://example.com/video"},
        )

        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "invalid_url"

    @patch("app.routers.info.extract_video_info")
    def test_returns_404_for_unavailable_video(
        self, mock_extract: MagicMock, client
    ) -> None:
        from app.services.youtube import VideoNotFoundError

        mock_extract.side_effect = VideoNotFoundError("Video is unavailable")

        response = client.get(
            "/api/info",
            params={"url": "https://www.youtube.com/watch?v=gone"},
        )

        assert response.status_code == 404
        assert response.json()["error"]["code"] == "not_found"

    @patch("app.routers.info.extract_playlist_info")
    def test_returns_playlist_info_for_playlist_url(
        self, mock_extract: MagicMock, client
    ) -> None:
        from app.schemas.video import PlaylistInfo

        mock_extract.return_value = PlaylistInfo(
            playlist_id="PLtest",
            title="Test Playlist",
            uploader="Creator",
            video_count=0,
            entries=[],
        )

        response = client.get(
            "/api/info",
            params={"url": "https://www.youtube.com/playlist?list=PLtest"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["playlist_id"] == "PLtest"


class TestGetFormats:
    @patch("app.routers.info.extract_video_info")
    def test_returns_format_list(self, mock_extract: MagicMock, client) -> None:
        mock_extract.return_value = VideoInfo(
            video_id="test",
            title="Test",
            thumbnail="",
            duration=60,
            uploader="Channel",
            formats=[
                VideoFormat(
                    format_id="137",
                    ext="mp4",
                    quality="1080p",
                    has_video=True,
                    has_audio=False,
                    filesize_approx=50000000,
                ),
            ],
        )

        response = client.get(
            "/api/formats",
            params={"url": "https://www.youtube.com/watch?v=test"},
        )

        assert response.status_code == 200
        formats = response.json()
        assert len(formats) == 1
        assert formats[0]["quality"] == "1080p"

    @patch("app.routers.info.extract_video_info")
    def test_returns_400_for_invalid_url(self, mock_extract: MagicMock, client) -> None:
        from app.services.youtube import InvalidURLError

        mock_extract.side_effect = InvalidURLError("invalid")

        response = client.get(
            "/api/formats",
            params={"url": "not-a-youtube-url"},
        )

        assert response.status_code == 400
