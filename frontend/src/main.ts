import {
  buildDownloadUrl,
  fetchInfo,
  isPlaylistInfo,
  isVideoInfo,
  type VideoInfo,
} from "./api";
import { createDownloadButton } from "./components/download-btn";
import {
  createFormatPicker,
  type FormatSelection,
} from "./components/format-picker";
import { createPlaylistView } from "./components/playlist-view";
import { createUrlInput, setUrlInputLoading } from "./components/url-input";
import { createVideoInfo } from "./components/video-info";
import "./styles/main.css";

const app = document.querySelector<HTMLDivElement>("#app")!;

let currentSelection: FormatSelection = { fmt: "mp4", quality: "best" };

function render(): void {
  app.innerHTML = `
    <main class="min-h-screen bg-gray-50 flex flex-col items-center px-4 py-12">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">YouTube Downloader</h1>
      <p class="text-gray-500 mb-8">Privacy-first video downloader</p>
      <div id="url-section" class="w-full flex justify-center"></div>
      <div id="error-section" class="w-full flex justify-center mt-4"></div>
      <div id="info-section" class="w-full flex justify-center mt-4"></div>
      <div id="format-section" class="w-full flex justify-center mt-4"></div>
      <div id="download-section" class="w-full flex justify-center mt-4"></div>
    </main>
  `;

  const urlSection = app.querySelector<HTMLDivElement>("#url-section")!;
  const urlInput = createUrlInput(handleUrlSubmit);
  urlSection.appendChild(urlInput);
}

async function handleUrlSubmit(url: string): Promise<void> {
  const urlSection = app.querySelector<HTMLDivElement>("#url-section")!;
  const errorSection = app.querySelector<HTMLDivElement>("#error-section")!;
  const infoSection = app.querySelector<HTMLDivElement>("#info-section")!;
  const formatSection = app.querySelector<HTMLDivElement>("#format-section")!;
  const downloadSection =
    app.querySelector<HTMLDivElement>("#download-section")!;

  errorSection.innerHTML = "";
  infoSection.innerHTML = "";
  formatSection.innerHTML = "";
  downloadSection.innerHTML = "";

  setUrlInputLoading(urlSection, true);

  try {
    const info = await fetchInfo(url);

    if (isVideoInfo(info)) {
      renderVideoFlow(info, url, infoSection, formatSection, downloadSection);
    } else if (isPlaylistInfo(info)) {
      const formatPicker = createFormatPicker((selection) => {
        currentSelection = selection;
      });
      formatSection.appendChild(formatPicker);

      const playlistView = createPlaylistView(
        info,
        () => currentSelection,
      );
      infoSection.appendChild(playlistView);
    }
  } catch (err) {
    const message = err instanceof Error ? err.message : "An error occurred";
    errorSection.innerHTML = `
      <div class="w-full max-w-2xl bg-red-50 border border-red-200 rounded-lg p-3">
        <p class="text-sm text-red-700">${escapeHtml(message)}</p>
      </div>
    `;
  } finally {
    setUrlInputLoading(urlSection, false);
  }
}

function renderVideoFlow(
  info: VideoInfo,
  url: string,
  infoSection: HTMLElement,
  formatSection: HTMLElement,
  downloadSection: HTMLElement,
): void {
  infoSection.appendChild(createVideoInfo(info));

  const formatPicker = createFormatPicker((selection) => {
    currentSelection = selection;
  });
  formatSection.appendChild(formatPicker);

  const downloadBtn = createDownloadButton(() => {
    const downloadUrl = buildDownloadUrl(
      url,
      currentSelection.fmt,
      currentSelection.quality,
    );
    window.open(downloadUrl, "_blank");
  });
  downloadSection.appendChild(downloadBtn);
}

function escapeHtml(text: string): string {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

render();
