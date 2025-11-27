import React from 'react';
import { Settings, Moon, Sun } from 'lucide-react';

const Header = ({ darkMode, toggleDarkMode, openSettings }) => {
    return (
        <div className="flex justify-between items-center p-6 border-b border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-[#1d1d1f]/80 backdrop-blur-md sticky top-0 z-40">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">
                File Search Engine
            </h1>
            <div className="flex gap-4">
                <button
                    onClick={toggleDarkMode}
                    className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-gray-600 dark:text-gray-300"
                    title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
                >
                    {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
                </button>
                <button
                    onClick={openSettings}
                    className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-gray-600 dark:text-gray-300"
                    title="Settings"
                >
                    <Settings className="w-5 h-5" />
                </button>
            </div>
        </div>
    );
};

export default Header;
