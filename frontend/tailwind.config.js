/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        surface: {
          50: '#f8fafc',
          100: '#f1f5f9',
          900: '#0f172a',
          950: '#020617',
        },
      },
      boxShadow: {
        soft: '0 10px 40px -20px rgba(15, 23, 42, 0.3)',
      },
    },
  },
  plugins: [],
}
