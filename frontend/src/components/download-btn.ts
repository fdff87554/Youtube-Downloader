/**
 * Download button component.
 */

export function createDownloadButton(onClick: () => void): HTMLElement {
  const container = document.createElement("div");
  container.className = "w-full max-w-2xl";

  container.innerHTML = `
    <button
      id="download-btn"
      class="w-full py-3 bg-green-600 text-white rounded-lg font-medium text-lg
             hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed
             transition-colors"
    >
      Download
    </button>
  `;

  const button = container.querySelector<HTMLButtonElement>("#download-btn")!;
  button.addEventListener("click", onClick);

  return container;
}
