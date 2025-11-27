import React, { useState, useEffect } from 'react';
import { X, Save, Folder, Key, Cpu } from 'lucide-react';
import axios from 'axios';

const SettingsModal = ({ isOpen, onClose, onSave }) => {
    const [config, setConfig] = useState({
        folder: '',
        auto_index: false,
        openai_api_key: '',
        model_path: '',
        provider: 'openai'
    });
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (isOpen) {
            fetchConfig();
        }
    }, [isOpen]);

    const fetchConfig = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/config');
            setConfig(response.data);
        } catch (error) {
            console.error('Failed to load config:', error);
        }
    };

    const handleSave = async () => {
        setLoading(true);
        try {
            await axios.post('http://localhost:8000/api/config', config);
            onSave();
            onClose();
        } catch (error) {
            console.error('Failed to save config:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleIndex = async () => {
        try {
            await axios.post('http://localhost:8000/api/index');
            alert('Indexing started in background');
        } catch (error) {
            console.error('Failed to trigger indexing:', error);
            alert('Failed to start indexing');
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 animate-in fade-in duration-200">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh] animate-in zoom-in-95 duration-200">
                <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white">Settings</h2>
                    <button onClick={onClose} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors">
                        <X className="w-5 h-5 text-gray-500" />
                    </button>
                </div>

                <div className="p-6 overflow-y-auto space-y-6">
                    {/* General Settings */}
                    <div className="space-y-4">
                        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
                            <Folder className="w-4 h-4" /> General
                        </h3>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                Folder to Index
                            </label>
                            <input
                                type="text"
                                value={config.folder}
                                onChange={(e) => setConfig({ ...config, folder: e.target.value })}
                                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition-shadow"
                                placeholder="C:/path/to/documents"
                            />
                        </div>
                        <div className="flex items-center gap-2">
                            <input
                                type="checkbox"
                                id="auto_index"
                                checked={config.auto_index}
                                onChange={(e) => setConfig({ ...config, auto_index: e.target.checked })}
                                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 w-4 h-4"
                            />
                            <label htmlFor="auto_index" className="text-sm text-gray-700 dark:text-gray-300 select-none">
                                Enable automatic background indexing
                            </label>
                        </div>
                        <button
                            onClick={handleIndex}
                            className="text-sm text-blue-600 hover:text-blue-700 font-medium hover:underline"
                        >
                            Trigger Re-indexing Now
                        </button>
                    </div>

                    {/* API Keys */}
                    <div className="space-y-4">
                        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
                            <Key className="w-4 h-4" /> API Keys
                        </h3>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                OpenAI API Key
                            </label>
                            <input
                                type="password"
                                value={config.openai_api_key}
                                onChange={(e) => setConfig({ ...config, openai_api_key: e.target.value })}
                                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition-shadow"
                                placeholder="sk-..."
                            />
                        </div>
                    </div>

                    {/* Local LLM */}
                    <div className="space-y-4">
                        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
                            <Cpu className="w-4 h-4" /> Local LLM
                        </h3>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                Provider
                            </label>
                            <div className="flex gap-4">
                                <label className="flex items-center gap-2 cursor-pointer">
                                    <input
                                        type="radio"
                                        name="provider"
                                        value="openai"
                                        checked={config.provider === 'openai'}
                                        onChange={(e) => setConfig({ ...config, provider: e.target.value })}
                                        className="text-blue-600 focus:ring-blue-500 w-4 h-4"
                                    />
                                    <span className="text-sm text-gray-700 dark:text-gray-300">OpenAI</span>
                                </label>
                                <label className="flex items-center gap-2 cursor-pointer">
                                    <input
                                        type="radio"
                                        name="provider"
                                        value="local"
                                        checked={config.provider === 'local'}
                                        onChange={(e) => setConfig({ ...config, provider: e.target.value })}
                                        className="text-blue-600 focus:ring-blue-500 w-4 h-4"
                                    />
                                    <span className="text-sm text-gray-700 dark:text-gray-300">Local</span>
                                </label>
                            </div>
                        </div>
                        {config.provider === 'local' && (
                            <div className="animate-in slide-in-from-top-2 duration-200">
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    Model Path
                                </label>
                                <input
                                    type="text"
                                    value={config.model_path}
                                    onChange={(e) => setConfig({ ...config, model_path: e.target.value })}
                                    className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition-shadow"
                                    placeholder="C:/path/to/model.gguf"
                                />
                            </div>
                        )}
                    </div>
                </div>

                <div className="p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 flex justify-end gap-3">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleSave}
                        disabled={loading}
                        className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors flex items-center gap-2 disabled:opacity-50 shadow-sm"
                    >
                        {loading ? 'Saving...' : <><Save className="w-4 h-4" /> Save Changes</>}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SettingsModal;
