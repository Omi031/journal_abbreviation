// Dictionary Editor - UI for managing dictionaries
class DictionaryEditor {
    constructor(dataManager) {
        this.dataManager = dataManager;
        this.currentView = 'journalAbb';
        this.setupUI();
    }
    
    /**
     * Setup dictionary editor UI
     */
    setupUI() {
        // Create modal HTML if it doesn't exist
        if (!document.getElementById('dictionary-modal')) {
            this.createModalHTML();
        }
        
        this.setupEventListeners();
    }
    
    /**
     * Create modal HTML structure
     */
    createModalHTML() {
        const modalHTML = `
            <div id="dictionary-modal" class="modal" style="display: none;">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>辞書編集</h3>
                        <span class="modal-close">&times;</span>
                    </div>
                    
                    <div class="modal-body">
                        <div class="dictionary-tabs">
                            <button class="tab-button active" data-view="journalAbb">雑誌略語</button>
                            <button class="tab-button" data-view="deletionWords">削除語</button>
                            <button class="tab-button" data-view="monthAbb">月略語</button>
                            <button class="tab-button" data-view="properNouns">固有名詞</button>
                        </div>
                        
                        <div class="dictionary-controls">
                            <div class="search-box">
                                <input type="text" id="dict-search" placeholder="検索...">
                                <button id="dict-search-btn">🔍</button>
                            </div>
                            
                            <div class="add-entry">
                                <div id="add-pair-inputs" class="add-inputs">
                                    <input type="text" id="add-original" placeholder="元の語">
                                    <input type="text" id="add-abbreviation" placeholder="略語">
                                    <button id="add-pair-btn">追加</button>
                                </div>
                                <div id="add-single-inputs" class="add-inputs" style="display: none;">
                                    <input type="text" id="add-word" placeholder="単語">
                                    <button id="add-word-btn">追加</button>
                                </div>
                            </div>
                        </div>
                        
                        <div class="dictionary-content">
                            <div class="dictionary-stats">
                                <span id="dict-stats">項目数: 0</span>
                                <button id="dict-export">エクスポート</button>
                                <button id="dict-import">インポート</button>
                                <button id="dict-reset">リセット</button>
                            </div>
                            
                            <div id="dictionary-list" class="dictionary-list"></div>
                        </div>
                    </div>
                </div>
            </div>`;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Modal controls
        const modal = document.getElementById('dictionary-modal');
        const closeBtn = modal.querySelector('.modal-close');
        
        closeBtn.addEventListener('click', () => this.hideModal());
        modal.addEventListener('click', (e) => {
            if (e.target === modal) this.hideModal();
        });
        
        // Tab switching
        modal.querySelectorAll('.tab-button').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchView(e.target.dataset.view);
            });
        });
        
        // Search
        const searchInput = document.getElementById('dict-search');
        const searchBtn = document.getElementById('dict-search-btn');
        
        searchInput.addEventListener('input', () => this.performSearch());
        searchBtn.addEventListener('click', () => this.performSearch());
        
        // Add entries
        document.getElementById('add-pair-btn').addEventListener('click', () => this.addPairEntry());
        document.getElementById('add-word-btn').addEventListener('click', () => this.addWordEntry());
        
        // Enter key support
        document.getElementById('add-original').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') document.getElementById('add-abbreviation').focus();
        });
        document.getElementById('add-abbreviation').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.addPairEntry();
        });
        document.getElementById('add-word').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.addWordEntry();
        });
        
        // Dictionary controls
        document.getElementById('dict-export').addEventListener('click', () => this.exportDictionary());
        document.getElementById('dict-import').addEventListener('click', () => this.importDictionary());
        document.getElementById('dict-reset').addEventListener('click', () => this.resetDictionary());
    }
    
    /**
     * Show dictionary editor modal
     */
    showModal() {
        const modal = document.getElementById('dictionary-modal');
        modal.style.display = 'block';
        this.refreshView();
    }
    
    /**
     * Hide dictionary editor modal
     */
    hideModal() {
        const modal = document.getElementById('dictionary-modal');
        modal.style.display = 'none';
    }
    
    /**
     * Switch dictionary view
     * @param {string} view - View type
     */
    switchView(view) {
        this.currentView = view;
        
        // Update tab buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-view="${view}"]`).classList.add('active');
        
        // Show/hide appropriate input controls
        const pairInputs = document.getElementById('add-pair-inputs');
        const singleInputs = document.getElementById('add-single-inputs');
        
        if (view === 'deletionWords' || view === 'properNouns') {
            pairInputs.style.display = 'none';
            singleInputs.style.display = 'flex';
        } else {
            pairInputs.style.display = 'flex';
            singleInputs.style.display = 'none';
        }
        
        this.refreshView();
    }
    
    /**
     * Refresh current view
     */
    refreshView() {
        this.clearSearch();
        this.updateStats();
        this.renderDictionaryList();
    }
    
    /**
     * Update statistics display
     */
    updateStats() {
        const stats = this.dataManager.getStatistics();
        let count = 0;
        
        switch (this.currentView) {
            case 'journalAbb':
                count = stats.journalAbbreviations;
                break;
            case 'deletionWords':
                count = stats.deletionWords;
                break;
            case 'monthAbb':
                count = stats.monthAbbreviations;
                break;
            case 'properNouns':
                count = stats.properNouns;
                break;
        }
        
        document.getElementById('dict-stats').textContent = `項目数: ${count}`;
    }
    
    /**
     * Render dictionary list
     */
    renderDictionaryList() {
        const listContainer = document.getElementById('dictionary-list');
        const data = this.dataManager.currentData;
        let items = [];
        
        switch (this.currentView) {
            case 'journalAbb':
                items = Object.entries(data.journalAbbreviations).map(([original, abbr]) => ({
                    type: 'pair',
                    original,
                    abbreviation: abbr
                }));
                break;
            case 'deletionWords':
                items = data.deletionWords.map(word => ({
                    type: 'single',
                    word
                }));
                break;
            case 'monthAbb':
                items = Object.entries(data.monthAbbreviations).map(([original, abbr]) => ({
                    type: 'pair',
                    original,
                    abbreviation: abbr
                }));
                break;
            case 'properNouns':
                items = data.properNouns.map(word => ({
                    type: 'single',
                    word
                }));
                break;
        }
        
        // Sort items
        items.sort((a, b) => {
            const aKey = a.original || a.word;
            const bKey = b.original || b.word;
            return aKey.localeCompare(bKey);
        });
        
        // Render items
        listContainer.innerHTML = '';
        items.forEach(item => {
            const itemElement = this.createListItem(item);
            listContainer.appendChild(itemElement);
        });
    }
    
    /**
     * Create list item element
     * @param {Object} item - Item data
     * @returns {HTMLElement} List item element
     */
    createListItem(item) {
        const div = document.createElement('div');
        div.className = 'dict-item';
        
        if (item.type === 'pair') {
            div.innerHTML = `
                <div class="dict-item-content">
                    <span class="original">${this.escapeHtml(item.original)}</span>
                    <span class="arrow">→</span>
                    <span class="abbreviation">${this.escapeHtml(item.abbreviation)}</span>
                </div>
                <button class="dict-item-delete" data-original="${this.escapeHtml(item.original)}">削除</button>
            `;
        } else {
            div.innerHTML = `
                <div class="dict-item-content">
                    <span class="word">${this.escapeHtml(item.word)}</span>
                </div>
                <button class="dict-item-delete" data-word="${this.escapeHtml(item.word)}">削除</button>
            `;
        }
        
        // Add delete event listener
        const deleteBtn = div.querySelector('.dict-item-delete');
        deleteBtn.addEventListener('click', () => {
            this.deleteItem(item);
        });
        
        return div;
    }
    
    /**
     * Delete dictionary item
     * @param {Object} item - Item to delete
     */
    deleteItem(item) {
        // Show confirmation dialog
        let confirmMessage;
        if (item.type === 'pair') {
            confirmMessage = `「${item.original}」→「${item.abbreviation}」を削除しますか？`;
        } else {
            confirmMessage = `「${item.word}」を削除しますか？`;
        }
        
        if (!confirm(confirmMessage)) {
            return; // User cancelled deletion
        }
        
        if (item.type === 'pair') {
            switch (this.currentView) {
                case 'journalAbb':
                    this.dataManager.removeJournalAbbreviation(item.original);
                    this.showNotification(`雑誌略語「${item.original}」→「${item.abbreviation}」を削除しました`, 'success');
                    break;
                case 'monthAbb':
                    this.dataManager.removeMonthAbbreviation(item.original);
                    this.showNotification(`月略語「${item.original}」→「${item.abbreviation}」を削除しました`, 'success');
                    break;
            }
        } else {
            switch (this.currentView) {
                case 'deletionWords':
                    this.dataManager.removeDeletionWord(item.word);
                    this.showNotification(`削除語「${item.word}」を削除しました`, 'success');
                    break;
                case 'properNouns':
                    this.dataManager.removeProperNoun(item.word);
                    this.showNotification(`固有名詞「${item.word}」を削除しました`, 'success');
                    break;
            }
        }
        
        this.refreshView();
    }
    
    /**
     * Add pair entry (original → abbreviation)
     */
    addPairEntry() {
        const originalInput = document.getElementById('add-original');
        const abbreviationInput = document.getElementById('add-abbreviation');
        
        const original = originalInput.value.trim();
        const abbreviation = abbreviationInput.value.trim();
        
        if (!original || !abbreviation) {
            alert('元の語と略語の両方を入力してください。');
            return;
        }
        
        // Check if the original word already exists
        let existingAbbreviation = null;
        let shouldProceed = true;
        
        switch (this.currentView) {
            case 'journalAbb':
                const journalData = this.dataManager.getAllData();
                if (journalData.journalAbbreviations[original]) {
                    existingAbbreviation = journalData.journalAbbreviations[original];
                }
                break;
            case 'monthAbb':
                const monthData = this.dataManager.getAllData();
                if (monthData.monthAbbreviations[original]) {
                    existingAbbreviation = monthData.monthAbbreviations[original];
                }
                break;
        }
        
        if (existingAbbreviation) {
            const confirmMessage = `「${original}」は既に「${existingAbbreviation}」として登録されています。\n「${abbreviation}」で上書きしますか？`;
            shouldProceed = confirm(confirmMessage);
        }
        
        if (!shouldProceed) {
            return;
        }
        
        switch (this.currentView) {
            case 'journalAbb':
                this.dataManager.addJournalAbbreviation(original, abbreviation);
                break;
            case 'monthAbb':
                this.dataManager.addMonthAbbreviation(original, abbreviation);
                break;
        }
        
        // Show success notification
        try {
            const actionText = existingAbbreviation ? '更新' : '追加';
            this.showNotification(`「${original}」→「${abbreviation}」を${actionText}しました`, 'success');
        } catch (error) {
            console.error('Notification error:', error);
        }
        
        originalInput.value = '';
        abbreviationInput.value = '';
        originalInput.focus();
        
        this.refreshView();
    }
    
    /**
     * Add single word entry
     */
    addWordEntry() {
        const wordInput = document.getElementById('add-word');
        const word = wordInput.value.trim();
        
        if (!word) {
            alert('単語を入力してください。');
            return;
        }
        
        // Check if the word already exists
        let alreadyExists = false;
        let shouldProceed = true;
        
        const allData = this.dataManager.getAllData();
        switch (this.currentView) {
            case 'deletionWords':
                alreadyExists = allData.deletionWords.includes(word);
                break;
            case 'properNouns':
                alreadyExists = allData.properNouns.includes(word);
                break;
        }
        
        if (alreadyExists) {
            const confirmMessage = `「${word}」は既に登録されています。\n重複登録を続行しますか？`;
            shouldProceed = confirm(confirmMessage);
        }
        
        if (!shouldProceed) {
            return;
        }
        
        switch (this.currentView) {
            case 'deletionWords':
                this.dataManager.addDeletionWord(word);
                break;
            case 'properNouns':
                this.dataManager.addProperNoun(word);
                break;
        }
        
        // Show success notification
        try {
            const actionText = alreadyExists ? '重複追加' : '追加';
            const categoryText = this.currentView === 'deletionWords' ? '削除語' : '固有名詞';
            this.showNotification(`${categoryText}「${word}」を${actionText}しました`, 'success');
        } catch (error) {
            console.error('Notification error:', error);
        }
        
        wordInput.value = '';
        wordInput.focus();
        
        this.refreshView();
    }
    
    /**
     * Perform search
     */
    performSearch() {
        const query = document.getElementById('dict-search').value.trim();
        
        if (!query) {
            this.renderDictionaryList();
            return;
        }
        
        const results = this.dataManager.search(query);
        const listContainer = document.getElementById('dictionary-list');
        
        let items = [];
        switch (this.currentView) {
            case 'journalAbb':
                items = results.journalAbbreviations.map(item => ({
                    type: 'pair',
                    original: item.original,
                    abbreviation: item.abbreviation
                }));
                break;
            case 'deletionWords':
                items = results.deletionWords.map(word => ({
                    type: 'single',
                    word
                }));
                break;
            case 'monthAbb':
                items = results.monthAbbreviations.map(item => ({
                    type: 'pair',
                    original: item.original,
                    abbreviation: item.abbreviation
                }));
                break;
            case 'properNouns':
                items = results.properNouns.map(word => ({
                    type: 'single',
                    word
                }));
                break;
        }
        
        listContainer.innerHTML = '';
        items.forEach(item => {
            const itemElement = this.createListItem(item);
            listContainer.appendChild(itemElement);
        });
    }
    
    /**
     * Clear search
     */
    clearSearch() {
        document.getElementById('dict-search').value = '';
    }
    
    /**
     * Export current dictionary view
     */
    exportDictionary() {
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
        
        this.showNotification('辞書データをエクスポートしました', 'success');
    }
    
    /**
     * Import dictionary data
     */
    importDictionary() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json,.csv';
        
        input.addEventListener('change', async (event) => {
            const file = event.target.files[0];
            if (!file) return;
            
            try {
                const text = await this.readFileAsText(file);
                
                if (file.name.endsWith('.json')) {
                    const data = JSON.parse(text);
                    if (this.dataManager.importData(data)) {
                        this.showNotification('辞書データをインポートしました', 'success');
                        this.refreshView();
                    } else {
                        this.showNotification('インポートに失敗しました。ファイル形式を確認してください', 'error');
                    }
                } else if (file.name.endsWith('.csv')) {
                    // CSV import for backward compatibility
                    const csvType = this.getCsvTypeFromView();
                    if (this.dataManager.importFromCSV(csvType, text)) {
                        this.showNotification('CSVファイルをインポートしました', 'success');
                        this.refreshView();
                    } else {
                        this.showNotification('CSVインポートに失敗しました', 'error');
                    }
                }
            } catch (error) {
                console.error('Import error:', error);
                this.showNotification('ファイルの読み込みに失敗しました', 'error');
            }
        });
        
        input.click();
    }
    
    /**
     * Reset current dictionary to defaults
     */
    resetDictionary() {
        if (confirm('現在の辞書をデフォルト値にリセットしますか？\n（この操作は元に戻せません）')) {
            this.dataManager.resetToDefaults();
            this.refreshView();
            alert('辞書をリセットしました。');
        }
    }
    
    /**
     * Get CSV type based on current view
     * @returns {string} CSV type
     */
    getCsvTypeFromView() {
        switch (this.currentView) {
            case 'journalAbb': return 'joAbb';
            case 'deletionWords': return 'joDel';
            case 'monthAbb': return 'moAbb';
            case 'properNouns': return 'properNouns';
            default: return 'joAbb';
        }
    }
    
    /**
     * Read file as text
     * @param {File} file - File to read
     * @returns {Promise<string>} File content as text
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
     * Show notification popup
     * @param {string} message - Notification message
     * @param {string} type - Notification type ('success', 'error', 'info')
     */
    showNotification(message, type = 'info') {
        // Create notification popup
        const notification = document.createElement('div');
        notification.className = `notification-popup notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${this.getNotificationIcon(type)}</span>
                <span class="notification-message">${this.escapeHtml(message)}</span>
            </div>
        `;
        
        // Add styles if not already added
        this.addNotificationStyles();
        
        // Add to page
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => notification.classList.add('show'), 10);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
    
    /**
     * Get icon for notification type
     * @param {string} type - Notification type
     * @returns {string} Icon
     */
    getNotificationIcon(type) {
        switch (type) {
            case 'success': return '✅';
            case 'error': return '❌';
            case 'warning': return '⚠️';
            default: return 'ℹ️';
        }
    }
    
    /**
     * Add notification styles to page
     */
    addNotificationStyles() {
        if (document.getElementById('notification-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification-popup {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                padding: 16px;
                max-width: 400px;
                z-index: 10000;
                opacity: 0;
                transform: translateX(100%);
                transition: all 0.3s ease;
                border-left: 4px solid #ccc;
            }
            
            .notification-popup.show {
                opacity: 1;
                transform: translateX(0);
            }
            
            .notification-popup.notification-success {
                border-left-color: #4CAF50;
            }
            
            .notification-popup.notification-error {
                border-left-color: #f44336;
            }
            
            .notification-popup.notification-warning {
                border-left-color: #ff9800;
            }
            
            .notification-popup.notification-info {
                border-left-color: #2196F3;
            }
            
            .notification-content {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .notification-icon {
                font-size: 20px;
                flex-shrink: 0;
            }
            
            .notification-message {
                font-size: 14px;
                color: #333;
                line-height: 1.4;
            }
        `;
        
        document.head.appendChild(style);
    }

    /**
     * Escape HTML content
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}