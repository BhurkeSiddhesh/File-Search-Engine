import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Download, Trash2, Check, Loader2, HardDrive, AlertCircle } from 'lucide-react';

const ModelManager = () => {
    const [availableModels, setAvailableModels] = useState([]);
    const [localModels, setLocalModels] = useState([]);
    const [downloadStatus, setDownloadStatus] = useState({ downloading: false });
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchModels();
        const interval = setInterval(checkDownloadStatus, 2000);
        return () => clearInterval(interval);
    }, []);

    const fetchModels = async () => {
        try {
            const [available, local] = await Promise.all([
                axios.get('http://localhost:8000/api/models/available'),
                axios.get('http://localhost:8000/api/models/local')
            ]);
            setAvailableModels(available.data || []);
            setLocalModels(local.data || []);
        } catch (err) {
            console.error('Failed to fetch models:', err);
        }
    };

    const checkDownloadStatus = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/models/status');
            setDownloadStatus(response.data);

            // Refresh models list when download completes
            if (!response.data.downloading && downloadStatus.downloading) {
                fetchModels();
            }
        } catch (err) {
            // Ignore
        }
    };

    const handleDownload = async (modelId) => {
        setError(null);
        try {
            const response = await axios.post(`http://localhost:8000/api/models/download/${modelId}`);
            if (response.data.status === 'success') {
                setDownloadStatus({ downloading: true, model_id: modelId, progress: 0 });
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Download failed');
        }
    };

    const handleDelete = async (modelPath) => {
        if (!confirm('Delete this model?')) return;
        try {
            await axios.delete('http://localhost:8000/api/models/delete', {
                data: { path: modelPath }
            });
            fetchModels();
        } catch (err) {
            setError('Failed to delete');
        }
    };

    const isDownloaded = (modelId) => {
        return localModels.some(m => m.id === modelId || m.filename?.includes(modelId));
    };

    const formatSize = (bytes) => {
        if (!bytes) return '';
        const gb = bytes / (1024 * 1024 * 1024);
        return gb >= 1 ? `${gb.toFixed(1)} GB` : `${(bytes / (1024 * 1024)).toFixed(0)} MB`;
    };

    return (
        <div className="space-y-4">
            {error && (
                <div className="flex items-center gap-2 p-2 rounded-lg bg-destructive/10 text-destructive text-sm">
                    <AlertCircle className="w-4 h-4" />
                    {error}
                </div>
            )}

            {/* Downloaded Models */}
            <div>
                <h4 className="text-sm font-medium mb-2">Downloaded ({localModels.length})</h4>
                {localModels.length > 0 ? (
                    <div className="space-y-2">
                        {localModels.map((model, idx) => (
                            <div
                                key={idx}
                                className="flex items-center justify-between p-2 rounded-lg border border-border bg-card"
                            >
                                <div className="flex items-center gap-2 min-w-0 flex-1">
                                    <HardDrive className="w-4 h-4 text-green-500 shrink-0" />
                                    <div className="min-w-0">
                                        <p className="text-sm font-medium truncate">{model.filename}</p>
                                        <p className="text-xs text-muted-foreground">{formatSize(model.size)}</p>
                                    </div>
                                </div>
                                <button
                                    onClick={() => handleDelete(model.path)}
                                    className="p-1.5 rounded hover:bg-destructive/10 hover:text-destructive shrink-0"
                                >
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="text-sm text-muted-foreground p-4 text-center">No models downloaded</p>
                )}
            </div>

            {/* Available Models */}
            <div>
                <h4 className="text-sm font-medium mb-2">Available</h4>
                <div className="space-y-2">
                    {availableModels.map((model) => (
                        <div
                            key={model.id}
                            className="flex items-center justify-between p-2 rounded-lg border border-border"
                        >
                            <div className="min-w-0 flex-1">
                                <p className="text-sm font-medium">{model.name}</p>
                                <p className="text-xs text-muted-foreground">{model.size}</p>
                            </div>
                            <div className="shrink-0 ml-2">
                                {isDownloaded(model.id) ? (
                                    <Check className="w-4 h-4 text-green-500" />
                                ) : downloadStatus.downloading && downloadStatus.model_id === model.id ? (
                                    <div className="flex items-center gap-1">
                                        <span className="text-xs">{downloadStatus.progress || 0}%</span>
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                    </div>
                                ) : (
                                    <button
                                        onClick={() => handleDownload(model.id)}
                                        disabled={downloadStatus.downloading}
                                        className="p-1.5 rounded hover:bg-accent disabled:opacity-50"
                                    >
                                        <Download className="w-4 h-4" />
                                    </button>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default ModelManager;
