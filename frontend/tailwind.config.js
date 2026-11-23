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
          50: '#F5F8FF',
          100: '#EAF0FF',
          600: '#1F4FD8',
          700: '#183EB5',
        },
        brand: '#1F4FD8',
        amber: {
          DEFAULT: '#FFB020',
          50: '#FFFDF5',
          100: '#FEF0C7',
          accent: '#FFB020',
          dark: '#B54708',
        },
        tint: '#EAF0FF',
        grey: {
          DEFAULT: '#475467',
          50: '#F9FAFB',
          100: '#F2F4F7',
          200: '#EAECF0',
          300: '#D0D5DD',
          400: '#98A2B3',
          500: '#667085',
          600: '#475467',
          700: '#344054',
          800: '#1D2939',
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
};
