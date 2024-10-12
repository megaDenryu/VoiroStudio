import react from "@vitejs/plugin-react-swc";
import { resolve } from "path";
import { defineConfig } from "vite";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: "./",
  build: {
    rollupOptions: {
      input: {
        // ここに出力する html ファイルを書きます
        // このファイル(vite.config.js)を変更した場合は `npm run build:watch` を実行し直す必要があります
        index: resolve(__dirname, "index.html"),
        option: resolve(__dirname, "option.html"),
      },
    },
  },
});
