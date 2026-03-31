/**
 * API client for communicating with the YouTube Downloader backend.
 */

const API_BASE = "/api";

export interface VideoFormat {
  format_id: string;
  ext: string;
  quality: string;
  has_video: boolean;
  has_audio: boolean;
  filesize_approx: number | null;
}

export interface VideoInfo {
  video_id: string;
  title: string;
  thumbnail: string;
  duration: number;
  uploader: string;
  formats: VideoFormat[];
}

export interface PlaylistEntry {
  video_id: string;
  title: string;
  duration: number;
  thumbnail: string;
}

export interface PlaylistInfo {
  playlist_id: string;
  title: string;
  uploader: string;
  video_count: number;
  entries: PlaylistEntry[];
}

export interface ApiError {
  error: {
    code: string;
    message: string;
  };
}

export type InfoResponse = VideoInfo | PlaylistInfo;

export function isPlaylistInfo(info: InfoResponse): info is PlaylistInfo {
  return "playlist_id" in info;
}

export function isVideoInfo(info: InfoResponse): info is VideoInfo {
  return "video_id" in info && !("playlist_id" in info);
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body: ApiError = await response.json();
    throw new Error(body.error.message);
  }
  return response.json();
}

export async function fetchInfo(url: string): Promise<InfoResponse> {
  const response = await fetch(
    `${API_BASE}/info?${new URLSearchParams({ url })}`,
  );
  return handleResponse<InfoResponse>(response);
}

export async function fetchFormats(url: string): Promise<VideoFormat[]> {
  const response = await fetch(
    `${API_BASE}/formats?${new URLSearchParams({ url })}`,
  );
  return handleResponse<VideoFormat[]>(response);
}

export function buildDownloadUrl(
  url: string,
  fmt: "mp4" | "mp3" = "mp4",
  quality: string = "best",
): string {
  const params = new URLSearchParams({ url, fmt, quality });
  return `${API_BASE}/download?${params}`;
}

export function formatDuration(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) {
    return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  }
  return `${m}:${String(s).padStart(2, "0")}`;
}

export function formatFileSize(bytes: number | null): string {
  if (bytes === null) return "";
  const mb = bytes / (1024 * 1024);
  if (mb >= 1024) {
    return `${(mb / 1024).toFixed(1)} GB`;
  }
  return `${mb.toFixed(1)} MB`;
}
