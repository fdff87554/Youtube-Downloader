"""Tests for playlist-related API behavior."""

from unittest.mock import MagicMock, patch

from app.schemas.video import PlaylistEntry, PlaylistInfo


class TestPlaylistInfoEndpoint:
    @patch("app.routers.info.extract_playlist_info")
    def test_returns_playlist_info_for_playlist_url(
        self, mock_extract: MagicMock, client
    ) -> None:
        mock_extract.return_value = PlaylistInfo(
            playlist_id="PLtest123",
            title="Test Playlist",
            uploader="Creator",
            video_count=2,
            entries=[
                PlaylistEntry(
                    video_id="vid1",
                    title="First Video",
                    duration=120,
                    thumbnail="https://example.com/1.jpg",
                ),
                PlaylistEntry(
                    video_id="vid2",
                    title="Second Video",
                    duration=240,
                    thumbnail="https://example.com/2.jpg",
                ),
            ],
        )

        response = client.get(
            "/api/info",
            params={"url": "https://www.youtube.com/playlist?list=PLtest123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["playlist_id"] == "PLtest123"
        assert data["video_count"] == 2
        assert len(data["entries"]) == 2
        assert data["entries"][0]["video_id"] == "vid1"

    @patch("app.routers.info.extract_playlist_info")
    def test_returns_404_for_unavailable_playlist(
        self, mock_extract: MagicMock, client
    ) -> None:
        from app.services.youtube import VideoNotFoundError

        mock_extract.side_effect = VideoNotFoundError("Playlist not found")

        response = client.get(
            "/api/info",
            params={"url": "https://www.youtube.com/playlist?list=PLgone"},
        )

        assert response.status_code == 404
        assert response.json()["error"]["code"] == "not_found"

    def test_watch_url_with_list_param_treated_as_video(self, client) -> None:
        """URLs like watch?v=abc&list=PLxxx should be treated as single videos."""
        with patch("app.routers.info.extract_video_info") as mock_video:
            from app.schemas.video import VideoInfo

            mock_video.return_value = VideoInfo(
                video_id="abc",
                title="Test",
                thumbnail="",
                duration=60,
                uploader="Test",
                formats=[],
            )

            response = client.get(
                "/api/info",
                params={"url": "https://www.youtube.com/watch?v=abc&list=PL123"},
            )

            assert response.status_code == 200
            mock_video.assert_called_once()
