/**
 * Playlist view component showing video list with individual download.
 */

import {
  buildDownloadUrl,
  formatDuration,
  type PlaylistInfo,
} from "../api";
import { escapeHtml } from "../utils";

export function createPlaylistView(
  info: PlaylistInfo,
  getSelection: () => { fmt: "mp4" | "mp3"; quality: string },
): HTMLElement {
  const container = document.createElement("div");
  container.className = "w-full max-w-2xl bg-white rounded-lg shadow p-4";

  const header = document.createElement("div");
  header.className = "mb-4";
  header.innerHTML = `
    <h2 class="text-lg font-semibold text-gray-900">${escapeHtml(info.title)}</h2>
    <p class="text-sm text-gray-600 mt-1">${escapeHtml(info.uploader)}</p>
    <p class="text-sm text-gray-500 mt-1">${info.video_count} videos</p>
  `;
  container.appendChild(header);

  const list = document.createElement("ul");
  list.className = "divide-y divide-gray-100";

  for (const entry of info.entries) {
    const item = document.createElement("li");
    item.className = "flex items-center gap-3 py-3";

    const thumb = document.createElement("img");
    thumb.src = entry.thumbnail;
    thumb.alt = entry.title;
    thumb.className = "w-24 h-auto rounded flex-shrink-0";
    thumb.loading = "lazy";

    const details = document.createElement("div");
    details.className = "flex-1 min-w-0";
    details.innerHTML = `
      <p class="text-sm font-medium text-gray-800 truncate"
         title="${escapeHtml(entry.title)}">
        ${escapeHtml(entry.title)}
      </p>
      <p class="text-xs text-gray-500">${formatDuration(entry.duration)}</p>
    `;

    const downloadBtn = document.createElement("button");
    downloadBtn.className =
      "flex-shrink-0 px-3 py-1.5 text-sm bg-green-600 text-white rounded " +
      "hover:bg-green-700 transition-colors";
    downloadBtn.textContent = "Download";
    downloadBtn.addEventListener("click", () => {
      const sel = getSelection();
      const videoUrl = `https://www.youtube.com/watch?v=${entry.video_id}`;
      const url = buildDownloadUrl(videoUrl, sel.fmt, sel.quality);
      window.open(url, "_blank");
    });

    item.appendChild(thumb);
    item.appendChild(details);
    item.appendChild(downloadBtn);
    list.appendChild(item);
  }

  container.appendChild(list);
  return container;
}
