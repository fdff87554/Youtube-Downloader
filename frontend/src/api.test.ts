import { describe, expect, it } from "vitest";
import {
  buildDownloadUrl,
  formatDuration,
  formatFileSize,
  isPlaylistInfo,
  isVideoInfo,
  type PlaylistInfo,
  type VideoInfo,
} from "./api";

const sampleVideo: VideoInfo = {
  video_id: "v1",
  title: "Test",
  thumbnail: "https://example.com/t.jpg",
  duration: 60,
  uploader: "Channel",
  formats: [],
};

const samplePlaylist: PlaylistInfo = {
  playlist_id: "p1",
  title: "List",
  uploader: "Creator",
  video_count: 0,
  entries: [],
};

describe("isVideoInfo / isPlaylistInfo", () => {
  it("identifies a video response", () => {
    expect(isVideoInfo(sampleVideo)).toBe(true);
    expect(isPlaylistInfo(sampleVideo)).toBe(false);
  });

  it("identifies a playlist response", () => {
    expect(isPlaylistInfo(samplePlaylist)).toBe(true);
    expect(isVideoInfo(samplePlaylist)).toBe(false);
  });
});

describe("formatDuration", () => {
  it("formats seconds shorter than an hour as m:ss", () => {
    expect(formatDuration(125)).toBe("2:05");
  });

  it("formats seconds longer than an hour as h:mm:ss", () => {
    expect(formatDuration(3661)).toBe("1:01:01");
  });

  it("renders zero as 0:00", () => {
    expect(formatDuration(0)).toBe("0:00");
  });
});

describe("formatFileSize", () => {
  it("returns empty string for null", () => {
    expect(formatFileSize(null)).toBe("");
  });

  it("formats megabyte-scale sizes in MB", () => {
    expect(formatFileSize(1024 * 1024 * 5)).toBe("5.0 MB");
  });

  it("formats gigabyte-scale sizes in GB", () => {
    expect(formatFileSize(1024 * 1024 * 1024 * 2.5)).toBe("2.5 GB");
  });
});

describe("buildDownloadUrl", () => {
  it("uses mp4/best by default", () => {
    const url = buildDownloadUrl("https://www.youtube.com/watch?v=x");
    expect(url).toContain("fmt=mp4");
    expect(url).toContain("quality=best");
    expect(url).not.toContain("title=");
  });

  it("includes the title query parameter when provided", () => {
    const url = buildDownloadUrl(
      "https://www.youtube.com/watch?v=x",
      "mp3",
      "best",
      "My Video",
    );
    expect(url).toContain("fmt=mp3");
    expect(url).toContain("title=My+Video");
  });
});
