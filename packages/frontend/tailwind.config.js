module.exports = {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(220, 8%, 8%)",
        input: "hsl(220, 7%, 15%)",
        ring: "hsl(200, 100%, 60%)",
        background: "hsl(220, 8%, 8%)",
        foreground: "hsl(0, 0%, 98%)",
        primary: {
          DEFAULT: "hsl(210, 50%, 15%)",
          foreground: "hsl(200, 100%, 95%)",
        },
        secondary: {
          DEFAULT: "hsl(210, 60%, 10%)",
          foreground: "hsl(200, 100%, 90%)",
        },
        tertiary: {
          DEFAULT: "hsl(355, 80%, 40%)",
          foreground: "hsl(0, 0%, 98%)",
        },
        neutral: {
          DEFAULT: "hsl(220, 10%, 10%)",
          foreground: "hsl(0, 0%, 96%)",
        },
        destructive: {
          DEFAULT: "hsl(355, 80%, 45%)",
          foreground: "hsl(0, 0%, 98%)",
        },
        muted: {
          DEFAULT: "hsl(220, 6%, 25%)",
          foreground: "hsl(215, 9%, 85%)",
        },
        accent: {
          DEFAULT: "hsl(210, 100%, 45%)",
          foreground: "hsl(0, 0%, 100%)",
        },
        popover: {
          DEFAULT: "hsl(220, 7%, 15%)",
          foreground: "hsl(0, 0%, 98%)",
        },
        card: {
          DEFAULT: "hsl(210, 50%, 15%)",
          foreground: "hsl(200, 100%, 95%)",
        },
        success: "hsl(145, 60%, 45%)",
        warning: "hsl(40, 95%, 55%)",
        error: "hsl(355, 80%, 45%)",
        gray: {
          50: "hsl(0, 0%, 100%)",
          100: "hsl(210, 10%, 96%)",
          200: "hsl(215, 9%, 85%)",
          300: "hsl(220, 8%, 70%)",
          400: "hsl(220, 7%, 55%)",
          500: "hsl(220, 6%, 45%)",
          600: "hsl(220, 5%, 35%)",
          700: "hsl(220, 6%, 25%)",
          800: "hsl(220, 7%, 15%)",
          900: "hsl(220, 8%, 8%)",
        },
        "gradient-1-start": "hsl(210, 90%, 50%)",
        "gradient-1-end": "hsl(220, 80%, 35%)",
        "gradient-2-start": "hsl(355, 80%, 45%)",
        "gradient-2-end": "hsl(0, 0%, 10%)",
        "cta-primary": {
          DEFAULT: "hsl(210, 100%, 45%)",
          foreground: "hsl(0, 0%, 100%)",
        },
        "cta-secondary": {
          DEFAULT: "hsl(355, 80%, 40%)",
          foreground: "hsl(0, 0%, 100%)",
        },
        "navbar-text": "hsl(200, 100%, 90%)",
        "hero-text": "hsl(0, 0%, 98%)",
      },
      borderRadius: {
        lg: "12px",
        md: "10px",
        sm: "8px",
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
        heading: ['"Space Grotesk"', 'sans-serif'],
      },
      spacing: {
        '4': '1rem',
        '8': '2rem',
        '12': '3rem',
        '16': '4rem',
        '24': '6rem',
        '32': '8rem',
        '48': '12rem',
        '64': '16rem',
      },
      backgroundImage: {
        'gradient-1': 'linear-gradient(135deg, hsl(210, 90%, 50%) 0%, hsl(220, 80%, 35%) 100%)',
        'gradient-2': 'linear-gradient(135deg, hsl(355, 80%, 45%) 0%, hsl(0, 0%, 10%) 100%)',
        'button-border-gradient': 'linear-gradient(90deg, hsl(210, 100%, 60%) 0%, hsl(355, 80%, 45%) 100%)',
      },
    },
  },
  plugins: [],
}
