// Main Application Logic
class JournalAbbreviationApp {
    constructor() {
        this.settingsManager = new SettingsManager();
        this.dataManager = new DataManager();
        this.dictionaryEditor = new DictionaryEditor(this.dataManager);
        this.formatter = new CitationFormatter();
        
        // Initialize the application
        this.init();
        
        // Add notification styles
        this.addNotificationStyles();
    }
    
    /**
     * Show notification popup
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const icon = this.getNotificationIcon(type);
        notification.innerHTML = `<span class="notification-icon">${icon}</span><span class="notification-message">${message}</span>`;
        
        document.body.appendChild(notification);
        
        // Trigger animation
        setTimeout(() => notification.classList.add('show'), 10);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
    
    /**
     * Get icon for notification type
     */
    getNotificationIcon(type) {
        const icons = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        };
        return icons[type] || icons['info'];
    }
    
    /**
     * Add notification styles to the page
     */
    addNotificationStyles() {
        if (document.getElementById('notification-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 12px 16px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 10000;
                min-width: 250px;
                max-width: 400px;
                opacity: 0;
                transform: translateX(100%);
                transition: all 0.3s ease;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
                font-size: 14px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .notification.show {
                opacity: 1;
                transform: translateX(0);
            }
            .notification-success { border-left: 4px solid #10b981; }
            .notification-error { border-left: 4px solid #ef4444; }
            .notification-warning { border-left: 4px solid #f59e0b; }
            .notification-info { border-left: 4px solid #3b82f6; }
            .notification-icon {
                font-size: 16px;
                flex-shrink: 0;
            }
            .notification-message {
                flex: 1;
                word-break: break-word;
            }
        `;
        document.head.appendChild(style);
    }
    
    /**
     * Initialize the application
     */
    async init() {
        // Load settings
        const settings = this.settingsManager.loadSettings();
        this.formatter.updateSettings(settings);
        
        // Setup event listeners
        this.setupEventListeners();
        this.settingsManager.setupEventListeners();
        
        // Update UI for current processing mode
        this.settingsManager.updateUIForProcessingMode(settings.processing_mode);
        
        // Load built-in dictionaries
        this.loadBuiltInDictionaries();
        
        // Update status
        this.updateStatus('準備完了 - 内蔵辞書使用中', 'info');
        
        console.log('Journal Abbreviation App initialized');
    }
    
    /**
     * Setup event listeners for UI elements
     */
    setupEventListeners() {
        // Format button
        const formatButton = document.getElementById('format-button');
        if (formatButton) {
            formatButton.addEventListener('click', () => this.formatCitations());
        }
        
        // Clear button
        const clearButton = document.getElementById('clear-button');
        if (clearButton) {
            clearButton.addEventListener('click', () => this.clearAll());
        }
        
        // Copy button
        const copyButton = document.getElementById('copy-button');
        if (copyButton) {
            copyButton.addEventListener('click', () => this.copyToClipboard());
        }
        
        // Paste button
        const pasteButton = document.getElementById('paste-button');
        if (pasteButton) {
            pasteButton.addEventListener('click', () => this.pasteFromClipboard());
        }
        

        
        // Dictionary management is handled by DictionaryEditor
        
        // Settings update listener
        document.addEventListener('settingsUpdated', (event) => {
            this.formatter.updateSettings(event.detail);
        });
        
        // Data update listener
        document.addEventListener('dataUpdated', (event) => {
            const formatterData = this.dataManager.getFormatterData();
            this.formatter.loadDictionaries({
                joAbb: Array.from(formatterData.joAbbDict.entries()),
                joDel: formatterData.joDelWords.map(word => [word]),
                moAbb: Array.from(formatterData.moAbbDict.entries()),
                properNouns: Array.from(formatterData.properNouns).map(noun => [noun])
            });

        });
        
        // Dictionary management buttons
        const editDictBtn = document.getElementById('edit-dictionaries');
        const exportDictBtn = document.getElementById('export-dictionaries');
        const importDictBtn = document.getElementById('import-dictionaries');
        
        if (editDictBtn) {
            editDictBtn.addEventListener('click', () => {
                this.dictionaryEditor.showModal();
            });
        }
        
        if (exportDictBtn) {
            exportDictBtn.addEventListener('click', () => {
                this.exportDictionaries();
            });
        }
        
        if (importDictBtn) {
            importDictBtn.addEventListener('click', () => {
                this.importDictionaries();
            });
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (event) => {
            if (event.ctrlKey) {
                switch (event.key) {
                    case 'Enter':
                        event.preventDefault();
                        this.formatCitations();
                        break;
                    case 'k':
                        event.preventDefault();
                        this.clearAll();
                        break;
                    case 'c':
                        if (event.shiftKey) {
                            event.preventDefault();
                            this.copyToClipboard();
                        }
                        break;
                    case 'v':
                        // Ctrl+V paste handling is done via paste event listener
                        break;
                }
            }
        });
        
        // Paste event listener for input area
        const inputText = document.getElementById('input-text');
        if (inputText) {
            inputText.addEventListener('paste', (event) => {
                // Wait for paste to complete, then check for auto-formatting
                setTimeout(() => {
                    this.handlePasteAutoFormat();
                }, 200);
            });
        }
    }
    

    
    /**
     * Load built-in dictionaries from DataManager
     */
    loadBuiltInDictionaries() {
        try {
            // Get formatted data for the formatter
            const formatterData = this.dataManager.getFormatterData();
            
            // Convert to the format expected by CitationFormatter.loadDictionaries()
            const dictionaryData = {
                joAbb: Array.from(formatterData.joAbbDict.entries()),
                joDel: formatterData.joDelWords.map(word => [word]),
                moAbb: Array.from(formatterData.moAbbDict.entries()),
                properNouns: Array.from(formatterData.properNouns).map(noun => [noun])
            };
            
            // Load into formatter
            this.formatter.loadDictionaries(dictionaryData);
            

            
            console.log('✓ Built-in dictionaries loaded successfully');
            
        } catch (error) {
            console.error('Failed to load built-in dictionaries:', error);
            this.updateStatus('内蔵辞書の読み込みに失敗しました', 'error');
        }
    }
    

    
    /**
     * Export dictionaries
     */
    exportDictionaries() {
        try {
            const data = this.dataManager.exportData();
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `journal-abbreviation-dictionaries-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            this.updateStatus('辞書データをエクスポートしました', 'success');
        } catch (error) {
            console.error('Export failed:', error);
            this.updateStatus('エクスポートに失敗しました', 'error');
        }
    }
    
    /**
     * Import dictionaries
     */
    importDictionaries() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        
        input.addEventListener('change', async (event) => {
            const file = event.target.files[0];
            if (!file) return;
            
            try {
                const text = await this.readFileAsText(file);
                const data = JSON.parse(text);
                
                if (this.dataManager.importData(data)) {
                    this.updateStatus('辞書データをインポートしました', 'success');

                } else {
                    this.updateStatus('インポートに失敗しました。ファイル形式を確認してください。', 'error');
                }
            } catch (error) {
                console.error('Import failed:', error);
                this.updateStatus('ファイルの読み込みに失敗しました', 'error');
            }
        });
        
        input.click();
    }
    
    /**
     * Read file as text
     * @param {File} file - File to read
     * @returns {Promise<string>} File content
     */
    readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(e);
            reader.readAsText(file, 'utf-8');
        });
    }
    
    /**
     * Format citations from input text
     */
    async formatCitations() {
        const inputText = document.getElementById('input-text');
        const outputText = document.getElementById('output-text');
        const formatButton = document.getElementById('format-button');
        
        if (!inputText || !outputText) return;
        
        const input = inputText.value.trim();
        if (!input) {
            this.updateStatus('入力テキストが空です', 'warning');
            return;
        }
        
        try {
            // Show loading state
            formatButton.classList.add('format-processing');
            this.updateStatus('フォーマット中...', 'loading');
            
            // Get current settings
            const settings = this.settingsManager.getSettings();
            
            // Format citations based on processing mode
            const results = this.formatter.formatMultiple(input, settings.format, settings.processing_mode);
            
            if (results.length === 0) {
                let modeText = 'RIS形式のデータ';
                if (settings.processing_mode === 'journal-only') {
                    modeText = '雑誌名';
                } else if (settings.processing_mode === 'arxiv-bibtex') {
                    modeText = 'arXiv BibTeX形式のデータ';
                }
                outputText.value = `フォーマット可能な文献が見つかりませんでした。\n\n${modeText}を入力してください。`;
                this.updateStatus('フォーマット可能な文献が見つかりません', 'warning');
                this.showNotification(`フォーマット可能な文献が見つかりませんでした。${modeText}を入力してください。`, 'warning');
                return;
            }
            
            // Build output text - only successful results
            const successResults = results.filter(r => r.success);
            const errorResults = results.filter(r => !r.success);
            
            let output = '';
            
            // Show only the formatted citations without headers or numbering
            if (successResults.length > 0) {
                const formattedCitations = successResults.map(result => result.citation);
                output = formattedCitations.join('\n\n');
            } else {
                output = 'フォーマット可能な文献が見つかりませんでした。';
            }
            
            // If there are errors, show them in console for debugging but not in UI
            if (errorResults.length > 0) {
                console.warn('Citation formatting errors:', errorResults);
                
                // Only show error summary in output if no successful results
                if (successResults.length === 0) {
                    output += '\n\n' + errorResults.map((result, index) => {
                        let errorText = `エラー: ${result.error}`;
                        if (result.original && result.original.TI) {
                            errorText += `\nタイトル: ${result.original.TI}`;
                        }
                        return errorText;
                    }).join('\n\n');
                }
            }
            
            outputText.value = output;
            
            // Auto-copy to clipboard if enabled
            if (settings.auto_copy_to_clipboard && successResults.length > 0) {
                await this.copyToClipboard(true);
            }
            
            // Update status and show notification
            const successCount = successResults.length;
            const errorCount = errorResults.length;
            this.updateStatus(
                `完了: 成功 ${successCount}件, エラー ${errorCount}件`,
                errorCount > 0 ? 'warning' : 'success'
            );
            
            // Show notification
            if (successCount > 0 && errorCount === 0) {
                this.showNotification(`${successCount}件の文献をフォーマットしました`, 'success');
            } else if (successCount > 0 && errorCount > 0) {
                this.showNotification(`${successCount}件成功、${errorCount}件エラー`, 'warning');
            } else {
                const settings = this.settingsManager.getSettings();
                let modeText = 'RIS形式のデータ';
                if (settings.processing_mode === 'journal-only') {
                    modeText = '雑誌名';
                } else if (settings.processing_mode === 'arxiv-bibtex') {
                    modeText = 'arXiv BibTeX形式のデータ';
                }
                this.showNotification(`フォーマット可能な文献が見つかりませんでした。${modeText}を入力してください。`, 'warning');
            }
            
        } catch (error) {
            console.error('Format error:', error);
            outputText.value = `エラーが発生しました: ${error.message}\n\n入力データの形式を確認してください。`;
            this.updateStatus(`フォーマットエラー: ${error.message}`, 'error');
            this.showNotification(`フォーマットエラー: ${error.message}`, 'error');
            
        } finally {
            formatButton.classList.remove('format-processing');
        }
    }
    
    /**
     * Clear all input and output
     */
    clearAll() {
        const inputText = document.getElementById('input-text');
        const outputText = document.getElementById('output-text');
        
        if (inputText) {
            inputText.value = '';
            inputText.focus();
        }
        if (outputText) {
            outputText.value = '';
        }
        
        this.updateStatus('入力・出力をクリアしました', 'info');
        this.showNotification('入力・出力をクリアしました', 'info');
    }
    
    /**
     * Paste text from clipboard to input area
     */
    async pasteFromClipboard() {
        const inputText = document.getElementById('input-text');
        const pasteButton = document.getElementById('paste-button');
        
        if (!inputText) return;
        
        try {
            // Disable button during operation
            if (pasteButton) {
                pasteButton.disabled = true;
                pasteButton.textContent = 'ペースト中...';
            }
            
            // Check if clipboard API is available
            if (!navigator.clipboard || !navigator.clipboard.readText) {
                throw new Error('クリップボードAPIがサポートされていません');
            }
            
            // Read from clipboard
            const clipboardText = await navigator.clipboard.readText();
            
            if (!clipboardText.trim()) {
                this.updateStatus('クリップボードにテキストがありません', 'warning');
                return;
            }
            
            // Check if current input has content
            const currentValue = inputText.value.trim();
            let shouldPaste = true;
            
            if (currentValue) {
                shouldPaste = confirm(
                    '入力エリアにテキストが既に存在します。\n' +
                    '上書きしますか？\n\n' +
                    'OK: 上書き\n' +
                    'キャンセル: 追記'
                );
                
                if (shouldPaste) {
                    inputText.value = clipboardText;
                } else {
                    // Append with proper spacing
                    const separator = currentValue.endsWith('\n') ? '' : '\n\n';
                    inputText.value = currentValue + separator + clipboardText;
                }
            } else {
                inputText.value = clipboardText;
            }
            
            // Focus and scroll to end
            inputText.focus();
            inputText.scrollTop = inputText.scrollHeight;
            
            // Show success message with text length
            const textLength = clipboardText.length;
            const lineCount = clipboardText.split('\n').length;
            this.updateStatus(
                `クリップボードから貼り付けました (${textLength}文字, ${lineCount}行)`, 
                'success'
            );
            
            // Auto-detect and format based on current mode
            const settings = this.settingsManager.getSettings();
            if (settings.processing_mode === 'journal-only' || this.detectRISFormat(clipboardText)) {
                setTimeout(() => {
                    this.formatCitations();
                }, 300);
            }
            
        } catch (error) {
            console.error('Paste from clipboard failed:', error);
            
            // Provide fallback instructions
            let errorMessage = 'クリップボードからの貼り付けに失敗しました';
            
            if (error.name === 'NotAllowedError') {
                errorMessage = 'クリップボードアクセスが拒否されました。Ctrl+V で手動貼り付けしてください';
            } else if (error.message.includes('サポートされていません')) {
                errorMessage = 'このブラウザはクリップボードAPIをサポートしていません。Ctrl+V で手動貼り付けしてください';
            }
            
            this.updateStatus(errorMessage, 'error');
            
            // Focus input area for manual paste
            inputText.focus();
            
        } finally {
            // Re-enable button
            if (pasteButton) {
                pasteButton.disabled = false;
                pasteButton.textContent = 'ペースト';
            }
        }
    }
    
    /**
     * Handle paste auto-formatting (for Ctrl+V)
     */
    handlePasteAutoFormat() {
        const inputText = document.getElementById('input-text');
        if (!inputText) return;
        
        const pastedText = inputText.value.trim();
        if (!pastedText) return;
        
        // Get current settings
        const settings = this.settingsManager.getSettings();
        
        // Auto-format based on processing mode or RIS detection
        if (settings.processing_mode === 'journal-only' || this.detectRISFormat(pastedText)) {
            this.updateStatus('貼り付けを検出 - 自動変換を開始します...', 'info');
            setTimeout(() => {
                this.formatCitations();
            }, 300);
        } else {
            this.updateStatus('貼り付けました - 必要に応じてフォーマット実行ボタンを押してください', 'info');
        }
    }

    /**
     * Detect if text contains RIS format data
     * @param {string} text - Text to analyze
     * @returns {boolean} True if RIS format is detected
     */
    detectRISFormat(text) {
        const risPatterns = [
            /^TY\s*-\s*/m,  // Type field
            /^AU\s*-\s*/m,  // Author field
            /^TI\s*-\s*/m,  // Title field
            /^JO\s*-\s*/m,  // Journal field
            /^ER\s*-\s*/m   // End record field
        ];
        
        let matchCount = 0;
        for (const pattern of risPatterns) {
            if (pattern.test(text)) {
                matchCount++;
            }
        }
        
        // Consider it RIS format if at least 3 common fields are found
        return matchCount >= 3;
    }
    
    /**
     * Copy output text to clipboard
     * @param {boolean} silent - Don't show status message if true
     */
    async copyToClipboard(silent = false) {
        const outputText = document.getElementById('output-text');
        if (!outputText || !outputText.value.trim()) {
            if (!silent) {
                this.updateStatus('コピーするテキストがありません', 'warning');
                this.showNotification('コピーするテキストがありません', 'warning');
            }
            return;
        }
        
        try {
            // Since output now contains only the formatted citations, copy as-is
            const textToCopy = outputText.value.trim();
            
            // Skip copying if it's just an error message
            if (textToCopy.startsWith('フォーマット可能な文献が見つかりませんでした') ||
                textToCopy.startsWith('エラーが発生しました')) {
                if (!silent) {
                    this.updateStatus('コピー可能な結果がありません', 'warning');
                    this.showNotification('コピー可能な結果がありません', 'warning');
                }
                return;
            }
            
            await navigator.clipboard.writeText(textToCopy);
            
            if (!silent) {
                this.updateStatus('クリップボードにコピーしました', 'success');
                this.showNotification('クリップボードにコピーしました', 'success');
            }
            
        } catch (error) {
            console.error('Copy to clipboard failed:', error);
            if (!silent) {
                this.updateStatus('クリップボードへのコピーに失敗', 'error');
                this.showNotification('クリップボードへのコピーに失敗しました', 'error');
            }
        }
    }
    
    /**
     * Update status message
     * @param {string} message - Status message
     * @param {string} type - Message type ('info', 'success', 'warning', 'error', 'loading')
     */
    updateStatus(message, type = 'info') {
        const statusElement = document.getElementById('status-message');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = type;
            
            // Auto-clear status after delay (except for loading states)
            if (type !== 'loading') {
                setTimeout(() => {
                    if (statusElement.className === type && statusElement.textContent === message) {
                        statusElement.textContent = '準備完了';
                        statusElement.className = 'info';
                    }
                }, type === 'error' || type === 'warning' ? 5000 : 3000);
            }
        }
    }
    
    /**
     * Update file status display
     */
    updateFileStatus() {
        const fileStatusElement = document.getElementById('file-status');
        if (fileStatusElement) {
            const stats = this.dataManager.getStatistics();
            const totalEntries = stats.journalAbbreviations + stats.deletionWords + 
                               stats.monthAbbreviations + stats.properNouns;
            
            fileStatusElement.textContent = `辞書: ${totalEntries}エントリ (内蔵 + カスタム)`;
        }
    }
    
    /**
     * Show example RIS data in input
     */
    showExample() {
        const inputText = document.getElementById('input-text');
        if (inputText) {
            const exampleData = `TY  - JOUR
AU  - Smith, J.
AU  - Johnson, A.
TI  - A Study on Machine Learning Applications in Neural Networks
JO  - IEEE Transactions on Neural Networks and Learning Systems
VL  - 30
IS  - 5
SP  - 1234
EP  - 1245
Y1  - 2023/05/
DO  - 10.1109/example.2023.1234567
ER  -

TY  - CONF
AU  - Brown, M.
AU  - Davis, K.
TI  - Deep Learning for Signal Processing Applications
JO  - 2023 International Conference on Acoustics, Speech and Signal Processing
SP  - 100
EP  - 105
Y1  - 2023/06/
ER  -`;
            
            inputText.value = exampleData;
            inputText.focus();
            this.updateStatus('サンプルデータを入力しました', 'info');
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.journalApp = new JournalAbbreviationApp();
    

    
    // Add help tooltips
    const helpElements = document.querySelectorAll('[data-help]');
    helpElements.forEach(element => {
        element.title = element.getAttribute('data-help');
    });
    
    // Focus on input area
    const inputText = document.getElementById('input-text');
    if (inputText) {
        inputText.focus();
    }
});