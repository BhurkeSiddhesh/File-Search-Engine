import React, { useState } from 'react';
import { Search, Loader2 } from 'lucide-react';

const SearchBar = ({ onSearch, isLoading }) => {
    const [query, setQuery] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (query.trim()) {
            onSearch(query);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="w-full max-w-3xl mx-auto mt-8 px-4">
            <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    {isLoading ? (
                        <Loader2 className="h-5 w-5 text-gray-400 animate-spin" />
                    ) : (
                        <Search className="h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
                    )}
                </div>
                <input
                    type="text"
                    className="block w-full pl-11 pr-4 py-4 bg-white dark:bg-gray-800 border-none rounded-2xl shadow-sm ring-1 ring-gray-200 dark:ring-gray-700 focus:ring-2 focus:ring-blue-500 focus:outline-none text-lg text-gray-900 dark:text-white placeholder-gray-400 transition-shadow"
                    placeholder="Search your documents..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    disabled={isLoading}
                />
            </div>
        </form>
    );
};

export default SearchBar;
