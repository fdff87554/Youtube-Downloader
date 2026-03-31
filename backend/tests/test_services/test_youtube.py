"""Unit tests for the YouTube service layer."""

from unittest.mock import MagicMock, patch

import pytest

from app.services.youtube import (
    InvalidURLError,
    VideoNotFoundError,
    build_download_filename,
    extract_playlist_info,
    extract_video_info,
    validate_youtube_url,
)


class TestValidateYoutubeUrl:
    def test_valid_youtube_url_accepted(self) -> None:
        validate_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    def test_valid_youtu_be_url_accepted(self) -> None:
        validate_youtube_url("https://youtu.be/dQw4w9WgXcQ")

    def test_valid_mobile_url_accepted(self) -> None:
        validate_youtube_url("https://m.youtube.com/watch?v=dQw4w9WgXcQ")

    def test_non_youtube_url_raises_error(self) -> None:
        with pytest.raises(InvalidURLError, match="valid YouTube URL"):
            validate_youtube_url("https://vimeo.com/12345")

    def test_empty_string_raises_error(self) -> None:
        with pytest.raises(InvalidURLError):
            validate_youtube_url("")

    def test_plain_text_raises_error(self) -> None:
        with pytest.raises(InvalidURLError):
            validate_youtube_url("not a url at all")


class TestExtractVideoInfo:
    @patch("app.services.youtube.yt_dlp.YoutubeDL")
    def test_returns_video_info_for_valid_video(self, mock_ydl_cls: MagicMock) -> None:
        # Arrange
        mock_info = {
            "id": "dQw4w9WgXcQ",
            "title": "Test Video",
            "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/0.jpg",
            "duration": 212,
            "uploader": "Test Channel",
            "formats": [
                {
                    "format_id": "137",
                    "ext": "mp4",
                    "height": 1080,
                    "vcodec": "avc1",
                    "acodec": "none",
                    "filesize": 50000000,
                },
                {
                    "format_id": "140",
                    "ext": "m4a",
                    "height": None,
                    "vcodec": "none",
                    "acodec": "mp4a",
                    "filesize": 3000000,
                },
            ],
        }
        mock_ydl = MagicMock()
        mock_ydl.extract_info.return_value = mock_info
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl_cls.return_value = mock_ydl

        # Act
        result = extract_video_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

        # Assert
        assert result.video_id == "dQw4w9WgXcQ"
        assert result.title == "Test Video"
        assert result.duration == 212
        assert result.uploader == "Test Channel"
        assert len(result.formats) == 2

    @patch("app.services.youtube.yt_dlp.YoutubeDL")
    def test_returns_none_info_raises_not_found(self, mock_ydl_cls: MagicMock) -> None:
        mock_ydl = MagicMock()
        mock_ydl.extract_info.return_value = None
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl_cls.return_value = mock_ydl

        with pytest.raises(VideoNotFoundError):
            extract_video_info("https://www.youtube.com/watch?v=nonexistent")

    def test_non_youtube_url_raises_invalid(self) -> None:
        with pytest.raises(InvalidURLError):
            extract_video_info("https://example.com/video")

    @patch("app.services.youtube.yt_dlp.YoutubeDL")
    def test_private_video_raises_not_found(self, mock_ydl_cls: MagicMock) -> None:
        import yt_dlp

        mock_ydl = MagicMock()
        mock_ydl.extract_info.side_effect = yt_dlp.utils.DownloadError(
            "Video unavailable"
        )
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl_cls.return_value = mock_ydl

        with pytest.raises(VideoNotFoundError):
            extract_video_info("https://www.youtube.com/watch?v=private123")


class TestExtractPlaylistInfo:
    @patch("app.services.youtube.yt_dlp.YoutubeDL")
    def test_returns_playlist_with_entries(self, mock_ydl_cls: MagicMock) -> None:
        mock_info = {
            "id": "PLtest123",
            "title": "Test Playlist",
            "uploader": "Playlist Creator",
            "entries": [
                {
                    "id": "vid1",
                    "title": "First Video",
                    "duration": 100,
                    "thumbnail": "https://img.youtube.com/vi/vid1/0.jpg",
                },
                {
                    "id": "vid2",
                    "title": "Second Video",
                    "duration": 200,
                    "thumbnail": "https://img.youtube.com/vi/vid2/0.jpg",
                },
            ],
        }
        mock_ydl = MagicMock()
        mock_ydl.extract_info.return_value = mock_info
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl_cls.return_value = mock_ydl

        result = extract_playlist_info(
            "https://www.youtube.com/playlist?list=PLtest123"
        )

        assert result.playlist_id == "PLtest123"
        assert result.title == "Test Playlist"
        assert result.video_count == 2
        assert result.entries[0].video_id == "vid1"
        assert result.entries[1].title == "Second Video"

    @patch("app.services.youtube.yt_dlp.YoutubeDL")
    def test_skips_none_entries(self, mock_ydl_cls: MagicMock) -> None:
        mock_info = {
            "id": "PLtest",
            "title": "Test",
            "uploader": "Creator",
            "entries": [
                None,
                {
                    "id": "vid1",
                    "title": "Video",
                    "duration": 100,
                    "thumbnail": "https://example.com/thumb.jpg",
                },
            ],
        }
        mock_ydl = MagicMock()
        mock_ydl.extract_info.return_value = mock_info
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl_cls.return_value = mock_ydl

        result = extract_playlist_info("https://www.youtube.com/playlist?list=PLtest")

        assert result.video_count == 1


class TestBuildDownloadFilename:
    def test_returns_sanitized_filename(self) -> None:
        result = build_download_filename('Test: "Video" Title', "mp4")

        assert result == "Test_ _Video_ Title.mp4"
        assert '"' not in result
        assert ":" not in result

    def test_returns_mp3_extension_for_audio(self) -> None:
        result = build_download_filename("Audio Track", "mp3")

        assert result.endswith(".mp3")

    def test_fallback_filename_when_title_is_none(self) -> None:
        result = build_download_filename(None, "mp4")

        assert result == "download.mp4"

    def test_fallback_filename_when_title_is_empty(self) -> None:
        result = build_download_filename("", "mp4")

        assert result == "download.mp4"
