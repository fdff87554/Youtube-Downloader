/**
 * Video information display component.
 */

import { formatDuration, type VideoInfo } from "../api";
import { escapeHtml } from "../utils";

export function createVideoInfo(info: VideoInfo): HTMLElement {
  const container = document.createElement("div");
  container.className = "w-full max-w-2xl bg-white rounded-lg shadow p-4 flex gap-4";

  const durationStr = formatDuration(info.duration);

  container.innerHTML = `
    <img
      src="${escapeHtml(info.thumbnail)}"
      alt="${escapeHtml(info.title)}"
      class="w-48 h-auto rounded object-cover flex-shrink-0"
      loading="lazy"
    />
    <div class="flex flex-col justify-center min-w-0">
      <h2 class="text-lg font-semibold text-gray-900 truncate"
          title="${escapeHtml(info.title)}">
        ${escapeHtml(info.title)}
      </h2>
      <p class="text-sm text-gray-600 mt-1">${escapeHtml(info.uploader)}</p>
      <p class="text-sm text-gray-500 mt-1">${durationStr}</p>
    </div>
  `;

  return container;
}
