/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: '#f8fafc', // Light background (slate-50)
                surface: '#ffffff', // White surface
                primary: '#2563eb', // Blue-600
                secondary: '#0ea5e9', // Sky-500
                text: {
                    main: '#0f172a', // Slate-900
                    muted: '#64748b', // Slate-500
                }
            },
            fontFamily: {
                sans: ['Inter', 'Microsoft YaHei', 'PingFang SC', 'system-ui', 'sans-serif'],
            }
        },
    },
    plugins: [],
}
