import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Three Kingdoms theme palette
        red: {
          50: '#fff1f0',
          100: '#ffccc7',
          200: '#ffa39e',
          300: '#ff7875',
          400: '#ff4d4f',
          500: '#f5222d',
          600: '#cf1322',
          700: '#a8071a',
          800: '#820014',
          900: '#5c0011',
        },
        gold: {
          50: '#fffbe6',
          500: '#faad14',
          600: '#d48806',
        },
        ink: {
          50: '#f5f5f5',
          100: '#e8e8e8',
          300: '#bfbfbf',
          500: '#595959',
          700: '#262626',
          900: '#141414',
        },
      },
      fontFamily: {
        sans: ['"Microsoft YaHei"', '"PingFang SC"', 'Arial', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'Consolas', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
};

export default config;
