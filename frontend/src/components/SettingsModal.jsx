import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X, Settings, FolderOpen, Loader2, Save, ChevronDown, ChevronUp, Key, Cpu, Trash2 } from 'lucide-react';
import ModelManager from './ModelManager';

const SettingsModal = ({ isOpen, onClose, onSave }) => {
    const [config, setConfig] = useState({
        folder: '',
        auto_index: false,
        provider: 'local',
        // API Keys for different providers
        openai_api_key: '',
        gemini_api_key: '',
        anthropic_api_key: '',
        grok_api_key: '',
        // Local model settings
        local_model_path: '',
        local_model_type: 'ollama'  // ollama, llamacpp, huggingface
    });
    const [isLoading, setIsLoading] = useState(false);
    const [isIndexing, setIsIndexing] = useState(false);
    const [expandedSection, setExpandedSection] = useState(null);

    useEffect(() => {
        if (isOpen) {
            fetchConfig();
        }
    }, [isOpen]);

    const fetchConfig = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/config');
            setConfig(prev => ({ ...prev, ...response.data }));
        } catch (error) {
            console.error('Failed to fetch config:', error);
        }
    };

    const handleSave = async () => {
        setIsLoading(true);
        try {
            await axios.post('http://localhost:8000/api/config', config);
            onSave();
            onClose();
        } catch (error) {
            console.error('Failed to save config:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleBrowseFolder = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/browse');
            if (response.data.folder) {
                setConfig(prev => ({ ...prev, folder: response.data.folder }));
            }
        } catch (error) {
            console.error('Failed to browse:', error);
        }
    };

    const handleIndex = async () => {
        await handleSave();
        setIsIndexing(true);
        try {
            await axios.post('http://localhost:8000/api/index');
            alert('Indexing started!');
        } catch (error) {
            console.error('Failed to index:', error);
        } finally {
            setIsIndexing(false);
        }
    };

    const handleDeleteAllHistory = async () => {
        if (confirm('Delete all search history?')) {
            try {
                await axios.delete('http://localhost:8000/api/search/history');
                alert('History cleared!');
            } catch (error) {
                console.error('Failed to clear history:', error);
            }
        }
    };

    const toggleSection = (section) => {
        setExpandedSection(expandedSection === section ? null : section);
    };

    const apiProviders = [
        { id: 'openai', name: 'OpenAI (ChatGPT)', key: 'openai_api_key', placeholder: 'sk-...' },
        { id: 'gemini', name: 'Google Gemini', key: 'gemini_api_key', placeholder: 'AIza...' },
        { id: 'anthropic', name: 'Anthropic (Claude)', key: 'anthropic_api_key', placeholder: 'sk-ant-...' },
        { id: 'grok', name: 'xAI (Grok)', key: 'grok_api_key', placeholder: 'xai-...' },
    ];

    const localModels = [
        { id: 'ollama', name: 'Ollama', desc: 'Easy local models (llama3, mistral, etc.)' },
        { id: 'llamacpp', name: 'LlamaCpp (GGUF)', desc: 'Run .gguf model files directly' },
        { id: 'huggingface', name: 'HuggingFace', desc: 'Sentence transformers for embeddings' },
    ];

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <div className="bg-background w-full max-w-xl max-h-[85vh] overflow-y-auto rounded-xl border border-border shadow-2xl">
                {/* Header */}
                <div className="sticky top-0 z-10 flex items-center justify-between p-4 border-b border-border bg-background">
                    <h2 className="text-lg font-semibold flex items-center gap-2">
                        <Settings className="w-5 h-5" />
                        Settings
                    </h2>
                    <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-accent">
                        <X className="w-4 h-4" />
                    </button>
                </div>

                <div className="p-4 space-y-4">
                    {/* Folder Section */}
                    <section className="space-y-3">
                        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
                            Document Folder
                        </h3>
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={config.folder}
                                onChange={(e) => setConfig({ ...config, folder: e.target.value })}
                                className="flex-1 px-3 py-2 text-sm rounded-lg border border-input bg-background"
                                placeholder="Select a folder to index..."
                            />
                            <button
                                onClick={handleBrowseFolder}
                                className="px-3 py-2 rounded-lg border border-input hover:bg-accent transition-colors"
                            >
                                <FolderOpen className="w-4 h-4" />
                            </button>
                        </div>
                        <button
                            onClick={handleIndex}
                            disabled={!config.folder || isIndexing}
                            className="w-full py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 text-sm font-medium flex items-center justify-center gap-2"
                        >
                            {isIndexing ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
                            {isIndexing ? 'Indexing...' : 'Index Folder'}
                        </button>
                    </section>

                    {/* AI Provider Selection */}
                    <section className="space-y-3">
                        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
                            AI Provider
                        </h3>
                        <select
                            value={config.provider}
                            onChange={(e) => setConfig({ ...config, provider: e.target.value })}
                            className="w-full px-3 py-2 text-sm rounded-lg border border-input bg-background"
                        >
                            <option value="local">Local Models (Free)</option>
                            <option value="openai">OpenAI (ChatGPT)</option>
                            <option value="gemini">Google Gemini</option>
                            <option value="anthropic">Anthropic (Claude)</option>
                            <option value="grok">xAI (Grok)</option>
                        </select>
                    </section>

                    {/* Local Model Options */}
                    {config.provider === 'local' && (
                        <section className="space-y-3">
                            <button
                                onClick={() => toggleSection('local')}
                                className="w-full flex items-center justify-between text-sm font-medium text-muted-foreground uppercase tracking-wide"
                            >
                                <span className="flex items-center gap-2">
                                    <Cpu className="w-4 h-4" />
                                    Local Model Settings
                                </span>
                                {expandedSection === 'local' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                            </button>

                            {expandedSection === 'local' && (
                                <div className="space-y-3 pl-2 border-l-2 border-border ml-2">
                                    <div className="space-y-2">
                                        <label className="text-sm">Model Type</label>
                                        <div className="space-y-2">
                                            {localModels.map(model => (
                                                <label key={model.id} className="flex items-start gap-3 p-3 rounded-lg border border-border hover:bg-accent cursor-pointer">
                                                    <input
                                                        type="radio"
                                                        name="localModelType"
                                                        value={model.id}
                                                        checked={config.local_model_type === model.id}
                                                        onChange={(e) => setConfig({ ...config, local_model_type: e.target.value })}
                                                        className="mt-0.5"
                                                    />
                                                    <div>
                                                        <div className="font-medium text-sm">{model.name}</div>
                                                        <div className="text-xs text-muted-foreground">{model.desc}</div>
                                                    </div>
                                                </label>
                                            ))}
                                        </div>
                                    </div>

                                    {config.local_model_type === 'llamacpp' && (
                                        <div className="space-y-2">
                                            <label className="text-sm">Model File Path</label>
                                            <input
                                                type="text"
                                                value={config.local_model_path}
                                                onChange={(e) => setConfig({ ...config, local_model_path: e.target.value })}
                                                className="w-full px-3 py-2 text-sm rounded-lg border border-input bg-background"
                                                placeholder="models/mistral-7b.gguf"
                                            />
                                        </div>
                                    )}

                                    <ModelManager />
                                </div>
                            )}
                        </section>
                    )}

                    {/* API Keys Section */}
                    <section className="space-y-3">
                        <button
                            onClick={() => toggleSection('apikeys')}
                            className="w-full flex items-center justify-between text-sm font-medium text-muted-foreground uppercase tracking-wide"
                        >
                            <span className="flex items-center gap-2">
                                <Key className="w-4 h-4" />
                                API Keys
                            </span>
                            {expandedSection === 'apikeys' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        </button>

                        {expandedSection === 'apikeys' && (
                            <div className="space-y-3 pl-2 border-l-2 border-border ml-2">
                                {apiProviders.map(provider => (
                                    <div key={provider.id} className="space-y-1">
                                        <label className="text-sm font-medium">{provider.name}</label>
                                        <input
                                            type="password"
                                            value={config[provider.key] || ''}
                                            onChange={(e) => setConfig({ ...config, [provider.key]: e.target.value })}
                                            className="w-full px-3 py-2 text-sm rounded-lg border border-input bg-background"
                                            placeholder={provider.placeholder}
                                        />
                                    </div>
                                ))}
                                <p className="text-xs text-muted-foreground">
                                    API keys are stored locally and used only when that provider is selected.
                                </p>
                            </div>
                        )}
                    </section>

                    {/* Data Management */}
                    <section className="space-y-3 pt-3 border-t border-border">
                        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
                            Data Management
                        </h3>
                        <button
                            onClick={handleDeleteAllHistory}
                            className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-destructive hover:bg-destructive/10 transition-colors"
                        >
                            <Trash2 className="w-4 h-4" />
                            Clear Search History
                        </button>
                    </section>
                </div>

                {/* Footer */}
                <div className="sticky bottom-0 p-4 border-t border-border bg-background flex justify-end gap-2">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 rounded-lg text-sm hover:bg-accent transition-colors"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleSave}
                        disabled={isLoading}
                        className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 flex items-center gap-2"
                    >
                        {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                        Save
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SettingsModal;
