/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                apple: {
                    gray: '#8e8e93',
                    blue: '#007AFF',
                    light: '#f5f5f7',
                    dark: '#1d1d1f',
                    separator: '#d2d2d7',
                }
            }
        },
    },
    plugins: [],
}
