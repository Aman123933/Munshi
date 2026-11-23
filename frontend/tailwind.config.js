/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: '#0B1220',
        blue: {
          DEFAULT: '#1F4FD8',
          600: '#1F4FD8',
        },
        brand: '#1F4FD8',
        amber: {
          DEFAULT: '#FFB020',
        },
        tint: '#EAF0FF',
        grey: {
          DEFAULT: '#475467',
          500: '#475467',
        },
        line: '#D0D5DD',
        status: {
          ok: '#067647',
          review: '#B54708',
          block: '#B42318',
        },
      },
      fontFamily: {
        heading: ['Archivo', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
