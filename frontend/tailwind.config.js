/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        canvas: '#F9F9F7',
        ink: '#1A1C1B',
        muted: '#58423C',
        primary: '#A43716',
        'primary-dark': '#862201',
        'primary-soft': '#FFDBD1',
        peach: '#F7E5DF',
        line: '#DFC0B7',
        slate: '#4E6078',
        teal: '#176479',
        surface: '#FFFFFF',
        fog: '#EEEEEC',
        'urgent-bg': '#FBE8E4',
        'urgent-text': '#8C2811',
        'medium-bg': '#F8EBC8',
        'medium-text': '#765208',
        'low-bg': '#E4F0E7',
        'low-text': '#1F643C'
      },
      fontFamily: {
        display: ['Fraunces', 'Georgia', 'serif'],
        body: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif']
      },
      boxShadow: {
        soft: '0 16px 45px rgba(72, 47, 39, 0.10)',
        card: '0 6px 20px rgba(72, 47, 39, 0.08)'
      },
      borderRadius: {
        '4xl': '2rem'
      }
    }
  },
  plugins: []
};
