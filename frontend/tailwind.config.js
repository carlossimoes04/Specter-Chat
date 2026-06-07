/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#030712', // Deepest gray/black
        foreground: '#e5e7eb',
        accent: '#06b6d4', // Cyan / Neon blue
        panel: '#111827', // Slate dark
      },
      fontFamily: {
        sans: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', '"Liberation Mono"', '"Courier New"', 'monospace'],
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography')
  ],
}
