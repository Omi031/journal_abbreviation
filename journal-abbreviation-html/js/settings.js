// Settings Management
class SettingsManager {
    constructor() {
        this.defaultSettings = {
            cite_style: 'ris',
            processing_mode: 'full',
            conf_with_in: false,
            conf_with_proc: true,
            conf_with_year: false,
            et_al_th: 6,
            format: 'tex',
            input_font_family: 'Consolas',
            input_font_size: 16,
            jo_abb_path: 'data/jo_abb.csv',
            jo_del_path: 'data/jo_del.csv',
            mo_abb_path: 'data/mo_abb.csv',
            proper_nouns_path: 'data/proper_nouns.csv',
            title_case_conversion: true,
            auto_detect_proper_nouns: true,
            output_font_family: 'Consolas',
            output_font_size: 16,
            ui_font_family: 'Segoe UI',
            ui_font_size: 16,
            auto_copy_to_clipboard: true
        };
        
        this.currentSettings = { ...this.defaultSettings };
    }
    
    /**
     * Load settings from localStorage or default values
     */
    loadSettings() {
        try {
            const savedSettings = localStorage.getItem('journalAbbreviationSettings');
            if (savedSettings) {
                const parsed = JSON.parse(savedSettings);
                this.currentSettings = { ...this.defaultSettings, ...parsed };
            }
        } catch (error) {
            console.warn('Failed to load settings from localStorage:', error);
            this.currentSettings = { ...this.defaultSettings };
        }
        
        this.applySettingsToUI();
        return this.currentSettings;
    }
    
    /**
     * Save current settings to localStorage
     */
    saveSettings() {
        try {
            const settingsToSave = JSON.stringify(this.currentSettings, null, 2);
            localStorage.setItem('journalAbbreviationSettings', settingsToSave);
            return true;
        } catch (error) {
            console.error('Failed to save settings to localStorage:', error);
            return false;
        }
    }
    
    /**
     * Update specific setting
     * @param {string} key - Setting key
     * @param {any} value - Setting value
     */
    updateSetting(key, value) {
        this.currentSettings[key] = value;
    }
    
    /**
     * Get current settings
     * @returns {Object} Current settings object
     */
    getSettings() {
        return { ...this.currentSettings };
    }
    
    /**
     * Reset to default settings
     */
    resetToDefaults() {
        this.currentSettings = { ...this.defaultSettings };
        this.applySettingsToUI();
    }
    
    /**
     * Apply settings to UI elements
     */
    applySettingsToUI() {
        // Processing mode
        const processingMode = document.getElementById('processing-mode');
        if (processingMode) {
            processingMode.value = this.currentSettings.processing_mode;
        }
        
        // Format selection
        const formatSelect = document.getElementById('format-select');
        if (formatSelect) {
            formatSelect.value = this.currentSettings.format;
        }
        
        // Et al threshold
        const etAlThreshold = document.getElementById('et-al-threshold');
        if (etAlThreshold) {
            etAlThreshold.value = this.currentSettings.et_al_th;
        }
        
        // Checkboxes
        const checkboxSettings = {
            'conf-with-proc': 'conf_with_proc',
            'conf-with-in': 'conf_with_in',
            'conf-with-year': 'conf_with_year',
            'title-case-conversion': 'title_case_conversion',
            'auto-detect-proper-nouns': 'auto_detect_proper_nouns',
            'auto-copy-clipboard': 'auto_copy_to_clipboard'
        };
        
        for (const [elementId, settingKey] of Object.entries(checkboxSettings)) {
            const element = document.getElementById(elementId);
            if (element) {
                element.checked = this.currentSettings[settingKey];
            }
        }
        
        // Apply font settings
        this.applyFontSettings();
    }
    
    /**
     * Read settings from UI elements
     */
    readSettingsFromUI() {
        // Processing mode
        const processingMode = document.getElementById('processing-mode');
        if (processingMode) {
            this.updateSetting('processing_mode', processingMode.value);
        }
        
        // Format selection
        const formatSelect = document.getElementById('format-select');
        if (formatSelect) {
            this.updateSetting('format', formatSelect.value);
        }
        
        // Et al threshold
        const etAlThreshold = document.getElementById('et-al-threshold');
        if (etAlThreshold) {
            this.updateSetting('et_al_th', parseInt(etAlThreshold.value, 10));
        }
        
        // Checkboxes
        const checkboxSettings = {
            'conf-with-proc': 'conf_with_proc',
            'conf-with-in': 'conf_with_in',
            'conf-with-year': 'conf_with_year',
            'title-case-conversion': 'title_case_conversion',
            'auto-detect-proper-nouns': 'auto_detect_proper_nouns',
            'auto-copy-clipboard': 'auto_copy_to_clipboard'
        };
        
        for (const [elementId, settingKey] of Object.entries(checkboxSettings)) {
            const element = document.getElementById(elementId);
            if (element) {
                this.updateSetting(settingKey, element.checked);
            }
        }
    }
    
    /**
     * Apply font settings to UI elements
     */
    applyFontSettings() {
        const inputText = document.getElementById('input-text');
        const outputText = document.getElementById('output-text');
        
        if (inputText) {
            inputText.style.fontFamily = this.currentSettings.input_font_family;
            inputText.style.fontSize = this.currentSettings.input_font_size + 'px';
        }
        
        if (outputText) {
            outputText.style.fontFamily = this.currentSettings.output_font_family;
            outputText.style.fontSize = this.currentSettings.output_font_size + 'px';
        }
        
        // Apply UI font settings to body
        document.body.style.fontFamily = this.currentSettings.ui_font_family;
        document.body.style.fontSize = this.currentSettings.ui_font_size + 'px';
    }
    
    /**
     * Export settings as JSON file
     */
    exportSettings() {
        const settingsJson = JSON.stringify(this.currentSettings, null, 2);
        const blob = new Blob([settingsJson], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = 'journal-abbreviation-settings.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    /**
     * Import settings from JSON file
     * @param {File} file - JSON settings file
     * @returns {Promise<boolean>} Success status
     */
    async importSettings(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = (event) => {
                try {
                    const importedSettings = JSON.parse(event.target.result);
                    
                    // Validate imported settings
                    if (this.validateSettings(importedSettings)) {
                        this.currentSettings = { ...this.defaultSettings, ...importedSettings };
                        this.applySettingsToUI();
                        this.saveSettings();
                        resolve(true);
                    } else {
                        reject(new Error('Invalid settings format'));
                    }
                } catch (error) {
                    reject(new Error(`Failed to parse settings file: ${error.message}`));
                }
            };
            
            reader.onerror = () => {
                reject(new Error('Failed to read settings file'));
            };
            
            reader.readAsText(file);
        });
    }
    
    /**
     * Validate settings object
     * @param {Object} settings - Settings object to validate
     * @returns {boolean} True if valid
     */
    validateSettings(settings) {
        if (!settings || typeof settings !== 'object') {
            return false;
        }
        
        // Check for required numeric values
        const numericKeys = ['et_al_th', 'input_font_size', 'output_font_size', 'ui_font_size'];
        for (const key of numericKeys) {
            if (settings[key] !== undefined && typeof settings[key] !== 'number') {
                return false;
            }
        }
        
        // Check for required boolean values
        const booleanKeys = [
            'conf_with_in', 'conf_with_proc', 'conf_with_year',
            'title_case_conversion', 'auto_detect_proper_nouns', 'auto_copy_to_clipboard'
        ];
        for (const key of booleanKeys) {
            if (settings[key] !== undefined && typeof settings[key] !== 'boolean') {
                return false;
            }
        }
        
        // Check format value
        if (settings.format !== undefined && !['tex', 'plain'].includes(settings.format)) {
            return false;
        }
        
        return true;
    }
    
    /**
     * Load default CSV files from data directory
     * @returns {Promise<Object>} Promise resolving to CSV data object
     */
    async loadDefaultCSVFiles() {
        const csvData = {};
        const csvFiles = {
            joAbb: this.currentSettings.jo_abb_path,
            joDel: this.currentSettings.jo_del_path,
            moAbb: this.currentSettings.mo_abb_path,
            properNouns: this.currentSettings.proper_nouns_path
        };
        
        console.log('Loading default CSV files...');
        
        // Load files in parallel with individual error handling
        const loadPromises = Object.entries(csvFiles).map(async ([key, path]) => {
            try {
                console.log(`Loading ${key} from ${path}...`);
                const data = await CSVParser.loadFromURL(path);
                console.log(`✓ Successfully loaded ${key} (${data.length} rows)`);
                return { key, data, success: true };
            } catch (error) {
                console.warn(`✗ Failed to load ${key} from ${path}:`, error.message);
                return { key, success: false, error: error.message };
            }
        });
        
        const results = await Promise.allSettled(loadPromises);
        
        // Process results
        let successCount = 0;
        let totalCount = 0;
        
        results.forEach((result) => {
            totalCount++;
            if (result.status === 'fulfilled' && result.value.success) {
                csvData[result.value.key] = result.value.data;
                successCount++;
            }
        });
        
        console.log(`CSV loading completed: ${successCount}/${totalCount} files loaded successfully`);
        
        // Show status message
        if (successCount === totalCount) {
            this.showMessage(`全てのCSVファイルを読み込みました (${successCount}ファイル)`, 'success');
        } else if (successCount > 0) {
            this.showMessage(`CSVファイルを部分的に読み込みました (${successCount}/${totalCount}ファイル)`, 'warning');
        } else {
            this.showMessage('CSVファイルの読み込みに失敗しました。ローカルサーバーで実行していることを確認してください。', 'error');
        }
        
        return csvData;
    }
    
    /**
     * Check if running under a web server (not file:// protocol)
     * @returns {boolean} True if running under web server
     */
    isRunningUnderWebServer() {
        return location.protocol === 'http:' || location.protocol === 'https:';
    }
    
    /**
     * Get CSV loading status message based on environment
     * @returns {string} Status message
     */
    getCSVLoadingStatusMessage() {
        if (this.isRunningUnderWebServer()) {
            return 'デフォルトCSVファイルを自動読み込み中...';
        } else {
            return 'ファイルプロトコルで実行中 - CSVファイルは手動アップロードしてください';
        }
    }
    
    /**
     * Create settings UI event listeners
     */
    setupEventListeners() {
        // Settings change listeners
        const elements = [
            'processing-mode',
            'format-select',
            'et-al-threshold',
            'conf-with-proc',
            'conf-with-in',
            'conf-with-year',
            'title-case-conversion',
            'auto-detect-proper-nouns',
            'auto-copy-clipboard'
        ];
        
        elements.forEach(elementId => {
            const element = document.getElementById(elementId);
            if (element) {
                element.addEventListener('change', () => {
                    this.readSettingsFromUI();
                    this.saveSettings();
                    
                    // Apply font settings if needed
                    if (['input-font-size', 'output-font-size', 'ui-font-size'].includes(elementId)) {
                        this.applyFontSettings();
                    }
                    
                    // Update UI based on processing mode
                    if (elementId === 'processing-mode') {
                        this.updateUIForProcessingMode(element.value);
                    }
                    
                    // Trigger settings update event
                    document.dispatchEvent(new CustomEvent('settingsUpdated', {
                        detail: this.getSettings()
                    }));
                });
            }
        });
        
        // Load/Save settings buttons
        const loadSettingsBtn = document.getElementById('load-settings');
        if (loadSettingsBtn) {
            loadSettingsBtn.addEventListener('click', () => {
                const input = document.createElement('input');
                input.type = 'file';
                input.accept = '.json';
                input.addEventListener('change', async (event) => {
                    const file = event.target.files[0];
                    if (file) {
                        try {
                            await this.importSettings(file);
                            this.showMessage('設定を正常に読み込みました', 'success');
                        } catch (error) {
                            this.showMessage(`設定の読み込みに失敗しました: ${error.message}`, 'error');
                        }
                    }
                });
                input.click();
            });
        }
        
        const saveSettingsBtn = document.getElementById('save-settings');
        if (saveSettingsBtn) {
            saveSettingsBtn.addEventListener('click', () => {
                this.exportSettings();
                this.showMessage('設定をダウンロードしました', 'success');
            });
        }
    }
    
    /**
     * Update UI elements based on processing mode
     * @param {string} mode - Processing mode ('full' or 'journal-only')
     */
    updateUIForProcessingMode(mode) {
        const inputText = document.getElementById('input-text');
        const inputHeader = document.querySelector('.input-header h3');
        
        if (mode === 'journal-only') {
            if (inputText) {
                inputText.placeholder = `雑誌名をここに入力してください（1行に1つ）...

例:
IEEE Transactions on Neural Networks and Learning Systems
Journal of Machine Learning Research
Nature Communications
Science
Cell
Physical Review Letters
...`;
            }
            if (inputHeader) {
                inputHeader.textContent = '雑誌名入力';
            }
        } else {
            if (inputText) {
                inputText.placeholder = `RIS形式の文献データをここに貼り付けてください...

例:
TY  - JOUR
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
            }
            if (inputHeader) {
                inputHeader.textContent = '入力文献データ (RIS形式)';
            }
        }
    }

    /**
     * Show status message
     * @param {string} message - Message text
     * @param {string} type - Message type ('success', 'error', 'info')
     */
    showMessage(message, type = 'info') {
        const statusElement = document.getElementById('status-message');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = type;
            
            // Clear message after 3 seconds
            setTimeout(() => {
                statusElement.textContent = '準備完了';
                statusElement.className = '';
            }, 3000);
        }
    }
}