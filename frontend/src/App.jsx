import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import SearchResults from './components/SearchResults';
import SettingsModal from './components/SettingsModal';
import axios from 'axios';

function App() {
    const [darkMode, setDarkMode] = useState(false);
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const [searchResults, setSearchResults] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        // Check system preference
        if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            setDarkMode(true);
        }
    }, []);

    useEffect(() => {
        if (darkMode) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }, [darkMode]);

    const handleSearch = async (query) => {
        setIsLoading(true);
        try {
            const response = await axios.post('http://localhost:8000/api/search', { query });
            setSearchResults(response.data);
        } catch (error) {
            console.error('Search failed:', error);
            alert('Search failed. Please check if the backend is running and the index is loaded.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-[#1d1d1f] transition-colors duration-300">
            <Header
                darkMode={darkMode}
                toggleDarkMode={() => setDarkMode(!darkMode)}
                openSettings={() => setIsSettingsOpen(true)}
            />

            <main className="container mx-auto pb-20">
                <div className="flex flex-col items-center justify-center pt-20 pb-10 px-4">
                    <h2 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4 text-center tracking-tight">
                        Find anything, instantly.
                    </h2>
                    <p className="text-gray-500 dark:text-gray-400 text-lg text-center max-w-2xl">
                        Search through your documents with the power of AI.
                    </p>
                </div>

                <SearchBar onSearch={handleSearch} isLoading={isLoading} />

                <SearchResults results={searchResults} />
            </main>

            <SettingsModal
                isOpen={isSettingsOpen}
                onClose={() => setIsSettingsOpen(false)}
                onSave={() => {
                    // Optional: Reload config or clear results
                }}
            />
        </div>
    );
}

export default App;
