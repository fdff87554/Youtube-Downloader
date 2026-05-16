import { afterEach, describe, expect, it, vi } from "vitest";
import { type PlaylistInfo } from "../api";
import { createPlaylistView } from "./playlist-view";

const samplePlaylist: PlaylistInfo = {
  playlist_id: "PLtest",
  title: "Test Playlist",
  uploader: "Tester",
  video_count: 1,
  entries: [
    {
      video_id: "abc123",
      title: "Entry One",
      duration: 60,
      thumbnail: "https://example.com/t.jpg",
    },
  ],
};

describe("createPlaylistView download button", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("opens download URL in a new tab with noopener and noreferrer", () => {
    const openSpy = vi.spyOn(window, "open").mockReturnValue(null);
    const view = createPlaylistView(samplePlaylist, () => ({
      fmt: "mp4",
      quality: "best",
    }));

    const button = view.querySelector<HTMLButtonElement>("button");
    expect(button).not.toBeNull();
    button!.click();

    expect(openSpy).toHaveBeenCalledTimes(1);
    const [, target, features] = openSpy.mock.calls[0];
    expect(target).toBe("_blank");
    expect(features).toBe("noopener,noreferrer");
  });
});
