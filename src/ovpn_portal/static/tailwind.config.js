/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html", // Add this to purge unused styles in the root HTML file
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
