/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        rig: {
          bg: '#0d0d0d',
          panel: '#1a1a1a',
          card: '#1f1f1f',
          border: '#2a2a2a',
          'border-light': '#333333',
          amber: '#f59e0b',
          'amber-dark': '#d97706',
          'amber-light': '#fbbf24',
          orange: '#ea580c',
          muted: '#6b7280',
          'muted-light': '#9ca3af',
          text: '#f3f4f6',
          'text-dim': '#d1d5db',
          warning: '#f59e0b',
          critical: '#ef4444',
          success: '#22c55e',
          info: '#3b82f6',
          'sidebar-w': '220px',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-in': 'slideIn 0.25s ease-out',
        'pulse-amber': 'pulseAmber 2s ease-in-out infinite',
        'typing': 'typing 1.4s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideIn: {
          '0%': { opacity: '0', transform: 'translateX(-10px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        pulseAmber: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
        typing: {
          '0%, 60%, 100%': { transform: 'translateY(0)' },
          '30%': { transform: 'translateY(-6px)' },
        }
      },
      boxShadow: {
        'amber-glow': '0 0 20px rgba(245, 158, 11, 0.15)',
        'card': '0 2px 8px rgba(0,0,0,0.4)',
        'card-hover': '0 4px 16px rgba(0,0,0,0.6)',
      }
    },
  },
  plugins: [],
}
