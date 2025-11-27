import React from 'react';
import { FileText, Tag } from 'lucide-react';
import { motion } from 'framer-motion';

const SearchResults = ({ results }) => {
    if (!results.length) return null;

    return (
        <div className="w-full max-w-4xl mx-auto mt-8 px-4 pb-12 space-y-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 px-2">
                Search Results ({results.length})
            </h2>
            {results.map((result, index) => (
                <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 hover:shadow-md transition-shadow"
                >
                    <div className="flex items-start gap-4">
                        <div className="p-3 bg-blue-50 dark:bg-blue-900/30 rounded-xl shrink-0">
                            <FileText className="w-6 h-6 text-blue-500" />
                        </div>
                        <div className="flex-1 min-w-0">
                            <div className="prose dark:prose-invert max-w-none mb-4">
                                <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed whitespace-pre-wrap break-words">
                                    {result.document.slice(0, 300)}...
                                </p>
                            </div>

                            {result.summary && (
                                <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700/30 rounded-xl border border-gray-100 dark:border-gray-700/50">
                                    <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                                        💡 AI Summary
                                    </h4>
                                    <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
                                        {result.summary}
                                    </p>
                                </div>
                            )}

                            {result.tags && result.tags.length > 0 && (
                                <div className="mt-4 flex flex-wrap gap-2">
                                    {result.tags.map((tag, i) => (
                                        <span
                                            key={i}
                                            className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
                                        >
                                            <Tag className="w-3 h-3" />
                                            {tag}
                                        </span>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </motion.div>
            ))}
        </div>
    );
};

export default SearchResults;
