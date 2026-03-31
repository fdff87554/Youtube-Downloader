import "./styles/main.css";

const app = document.querySelector<HTMLDivElement>("#app");

if (app) {
  app.innerHTML = `
    <main class="min-h-screen bg-gray-50 flex items-center justify-center">
      <h1 class="text-2xl font-bold text-gray-800">YouTube Downloader</h1>
    </main>
  `;
}
