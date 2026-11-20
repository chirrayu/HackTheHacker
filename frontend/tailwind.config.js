/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        background: {
          DEFAULT: '#0a0e17',
          light: '#111827',
        },
        surface: {
          DEFAULT: '#1a1f2e',
          light: '#1f2937',
        },
        border: {
          DEFAULT: '#2d3748',
        },
        'accent-cyan': {
          DEFAULT: '#06b6d4',
          light: '#22d3ee',
        },
        'accent-amber': {
          DEFAULT: '#f59e0b',
          light: '#fbbf24',
        },
        critical: {
          DEFAULT: '#ef4444',
        },
        success: {
          DEFAULT: '#10b981',
        },
        'text-primary': {
          DEFAULT: '#f1f5f9',
        },
        'text-secondary': {
          DEFAULT: '#94a3b8',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
};
