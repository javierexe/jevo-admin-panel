/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#1d1f21',
          card: '#2a2d31',
          border: '#3a3d41',
          text: '#e4e6eb',
          'text-secondary': '#b0b3b8',
        }
      }
    },
  },
  plugins: [],
}
