// Data Manager - Handle built-in dictionaries and user customizations
class DataManager {
    constructor() {
        // Default journal abbreviations (built-in data)
        this.defaultJournalAbbreviations = {
            'Acoustics': 'Acoust',
            'Advances': 'Adv',
            'Analysis': 'Anal',
            'Application': 'Appl',
            'Applications': 'Appl',
            'Architecture': 'Archit',
            'Artifical': 'Artif',
            'Automation': 'Autom',
            'Automatic': 'Autom',
            'Biomedical': 'Biomed',
            'Cognitive': 'Cognit',
            'Communication': 'Commun',
            'Communications': 'Commun',
            'Computational': 'Comput',
            'Computer': 'Comput',
            'Computing': 'Comput',
            'Conference': 'Conf',
            'Consumer': 'Consum',
            'Cybernetics': 'Cybern',
            'Distributed': 'Distrib',
            'Education': 'Educ',
            'Electrical': 'Electr',
            'Electronic': 'Electron',
            'Electronics': 'Electron',
            'Engineering': 'Eng',
            'Engineers': 'Eng',
            'Frequency': 'Freq',
            'Geoscience': 'Geosci',
            'Imaging': 'Imag',
            'Industrial': 'Ind',
            'Information': 'Inf',
            'Intelligent': 'Intell',
            'Intelligence': 'Intell',
            'International': 'Int',
            'Journal': 'J',
            'Learning': 'Learn',
            'Letters': 'Lett',
            'Machine': 'Mach',
            'Magazine': 'Mag',
            'Management': 'Manag',
            'Manufacturing': 'Manuf',
            'Measurement': 'Meas',
            'Measurements': 'Meas',
            'Medicine': 'Med',
            'Microwave': 'Microw',
            'Network': 'Netw',
            'Networking': 'Netw',
            'Optical': 'Opt',
            'Proceedings': 'Proc',
            'Processing': 'Process',
            'Propagation': 'Propag',
            'Recognition': 'Recognit',
            'Reliability': 'Rel',
            'Reports': 'Rep',
            'Review': 'Rev',
            'Robotics': 'Robot',
            'Scientific': 'Sci',
            'Selected': 'Sel',
            'Semiconductor': 'Semicond',
            'Sensing': 'Sens',
            'Software': 'Softw',
            'Standards': 'Stand',
            'Survey': 'Surv',
            'Surveys': 'Surv',
            'System': 'Syst',
            'Systems': 'Syst',
            'Technical': 'Tech',
            'Technology': 'Technol',
            'Technologies': 'Technol',
            'Transactions': 'Trans',
            'Tutorial': 'Tut',
            'Tutorials': 'Tut',
            'Ultrasonics': 'Ultrason',
            'Vehicle': 'Veh',
            'Vehicular': 'Veh',
            'Vision': 'Vis'
        };
        
        // Default deletion words (built-in data)
        this.defaultDeletionWords = [
            'and', 'in', 'of', 'on', '&', 'the', 'a', 'an'
        ];
        
        // Default month abbreviations (built-in data)
        this.defaultMonthAbbreviations = {
            'January': 'Jan',
            'February': 'Feb',
            'March': 'Mar',
            'April': 'Apr',
            'June': 'Jun',
            'July': 'Jul',
            'August': 'Aug',
            'September': 'Sep',
            'October': 'Oct',
            'November': 'Nov',
            'December': 'Dec'
        };
        
        // Default proper nouns (built-in data)
        this.defaultProperNouns = [
            'WiFi', 'IoT', 'AI', 'ML', 'DL', 'CNN', 'LSTM', 'BERT',
            'GPS', 'Bluetooth', 'LTE', '5G', '4G', '3G', '6G',
            'MIMO', 'QoS', 'TCP', 'UDP', 'HTTP', 'HTTPS', 'SSL', 'TLS',
            'API', 'REST', 'JSON', 'XML', 'HTML', 'CSS', 'JavaScript',
            'OFDM', 'Rayleigh', 'Rician', 'AWGN', 'SNR', 'BER', 'SINR',
            'IEEE', 'ACM', 'USB', 'PCIe', 'SATA', 'NVMe', 'SSD', 'HDD',
            'CPU', 'GPU', 'RAM', 'ROM', 'FPGA', 'ASIC', 'DSP'
        ];
        
        // Initialize current dictionaries
        this.currentData = this.loadDataFromStorage();
    }
    
    /**
     * Load data from localStorage, falling back to defaults
     * @returns {Object} Complete data object
     */
    loadDataFromStorage() {
        const defaultData = {
            journalAbbreviations: { ...this.defaultJournalAbbreviations },
            deletionWords: [...this.defaultDeletionWords],
            monthAbbreviations: { ...this.defaultMonthAbbreviations },
            properNouns: [...this.defaultProperNouns],
            lastModified: new Date().toISOString(),
            version: '1.0.0'
        };
        
        try {
            const savedData = localStorage.getItem('journalAbbreviationData');
            if (savedData) {
                const parsed = JSON.parse(savedData);
                return {
                    journalAbbreviations: { ...defaultData.journalAbbreviations, ...parsed.journalAbbreviations },
                    deletionWords: parsed.deletionWords || defaultData.deletionWords,
                    monthAbbreviations: { ...defaultData.monthAbbreviations, ...parsed.monthAbbreviations },
                    properNouns: [...new Set([...defaultData.properNouns, ...(parsed.properNouns || [])])],
                    lastModified: parsed.lastModified || defaultData.lastModified,
                    version: parsed.version || defaultData.version
                };
            }
        } catch (error) {
            console.warn('Failed to load data from localStorage:', error);
        }
        
        return defaultData;
    }
    
    /**
     * Save current data to localStorage
     */
    saveDataToStorage() {
        try {
            this.currentData.lastModified = new Date().toISOString();
            localStorage.setItem('journalAbbreviationData', JSON.stringify(this.currentData));
            
            // Dispatch update event
            document.dispatchEvent(new CustomEvent('dataUpdated', {
                detail: this.currentData
            }));
            
            return true;
        } catch (error) {
            console.error('Failed to save data to localStorage:', error);
            return false;
        }
    }
    
    /**
     * Get current data in format expected by CitationFormatter
     * @returns {Object} Formatted data for formatter
     */
    getFormatterData() {
        return {
            joAbbDict: new Map(Object.entries(this.currentData.journalAbbreviations)),
            joDelWords: [...this.currentData.deletionWords],
            moAbbDict: new Map(Object.entries(this.currentData.monthAbbreviations)),
            properNouns: new Set(this.currentData.properNouns)
        };
    }

    /**
     * Get all current data (for dictionary editor)
     * @returns {Object} Current data object
     */
    getAllData() {
        return {
            journalAbbreviations: { ...this.currentData.journalAbbreviations },
            deletionWords: [...this.currentData.deletionWords],
            monthAbbreviations: { ...this.currentData.monthAbbreviations },
            properNouns: [...this.currentData.properNouns]
        };
    }

    /**
     * Add or update journal abbreviation
     * @param {string} original - Original journal name/word
     * @param {string} abbreviation - Abbreviated form
     */
    addJournalAbbreviation(original, abbreviation) {
        this.currentData.journalAbbreviations[original] = abbreviation;
        this.saveDataToStorage();
    }
    
    /**
     * Remove journal abbreviation
     * @param {string} original - Original journal name/word to remove
     */
    removeJournalAbbreviation(original) {
        delete this.currentData.journalAbbreviations[original];
        this.saveDataToStorage();
    }
    
    /**
     * Add deletion word
     * @param {string} word - Word to add to deletion list
     */
    addDeletionWord(word) {
        if (!this.currentData.deletionWords.includes(word)) {
            this.currentData.deletionWords.push(word);
            this.saveDataToStorage();
        }
    }
    
    /**
     * Remove deletion word
     * @param {string} word - Word to remove from deletion list
     */
    removeDeletionWord(word) {
        this.currentData.deletionWords = this.currentData.deletionWords.filter(w => w !== word);
        this.saveDataToStorage();
    }
    
    /**
     * Add or update month abbreviation
     * @param {string} original - Original month name
     * @param {string} abbreviation - Abbreviated form
     */
    addMonthAbbreviation(original, abbreviation) {
        this.currentData.monthAbbreviations[original] = abbreviation;
        this.saveDataToStorage();
    }
    
    /**
     * Remove month abbreviation
     * @param {string} original - Original month name to remove
     */
    removeMonthAbbreviation(original) {
        delete this.currentData.monthAbbreviations[original];
        this.saveDataToStorage();
    }
    
    /**
     * Add proper noun
     * @param {string} noun - Proper noun to add
     */
    addProperNoun(noun) {
        if (!this.currentData.properNouns.includes(noun)) {
            this.currentData.properNouns.push(noun);
            this.saveDataToStorage();
        }
    }
    
    /**
     * Remove proper noun
     * @param {string} noun - Proper noun to remove
     */
    removeProperNoun(noun) {
        this.currentData.properNouns = this.currentData.properNouns.filter(n => n !== noun);
        this.saveDataToStorage();
    }
    
    /**
     * Reset to default data
     */
    resetToDefaults() {
        this.currentData = {
            journalAbbreviations: { ...this.defaultJournalAbbreviations },
            deletionWords: [...this.defaultDeletionWords],
            monthAbbreviations: { ...this.defaultMonthAbbreviations },
            properNouns: [...this.defaultProperNouns],
            lastModified: new Date().toISOString(),
            version: '1.0.0'
        };
        this.saveDataToStorage();
    }
    
    /**
     * Import data from JSON object
     * @param {Object} data - Data to import
     */
    importData(data) {
        try {
            // Validate data structure
            if (this.validateImportData(data)) {
                this.currentData = {
                    journalAbbreviations: { ...this.defaultJournalAbbreviations, ...data.journalAbbreviations },
                    deletionWords: [...new Set([...this.defaultDeletionWords, ...(data.deletionWords || [])])],
                    monthAbbreviations: { ...this.defaultMonthAbbreviations, ...data.monthAbbreviations },
                    properNouns: [...new Set([...this.defaultProperNouns, ...(data.properNouns || [])])],
                    lastModified: new Date().toISOString(),
                    version: data.version || '1.0.0'
                };
                this.saveDataToStorage();
                return true;
            }
        } catch (error) {
            console.error('Failed to import data:', error);
        }
        return false;
    }
    
    /**
     * Export current data as JSON
     * @returns {Object} Current data
     */
    exportData() {
        return {
            ...this.currentData,
            exportedAt: new Date().toISOString()
        };
    }
    
    /**
     * Validate import data structure
     * @param {Object} data - Data to validate
     * @returns {boolean} True if valid
     */
    validateImportData(data) {
        if (!data || typeof data !== 'object') return false;
        
        // Check optional fields
        if (data.journalAbbreviations && typeof data.journalAbbreviations !== 'object') return false;
        if (data.deletionWords && !Array.isArray(data.deletionWords)) return false;
        if (data.monthAbbreviations && typeof data.monthAbbreviations !== 'object') return false;
        if (data.properNouns && !Array.isArray(data.properNouns)) return false;
        
        return true;
    }
    
    /**
     * Import data from CSV format (for backward compatibility)
     * @param {string} csvType - Type of CSV ('joAbb', 'joDel', 'moAbb', 'properNouns')
     * @param {string} csvText - CSV text content
     */
    importFromCSV(csvType, csvText) {
        try {
            const data = CSVParser.parse(csvText);
            
            switch (csvType) {
                case 'joAbb':
                    data.slice(1).forEach(row => {
                        if (row.length >= 2 && row[0] && row[1]) {
                            this.currentData.journalAbbreviations[row[0].trim()] = row[1].trim();
                        }
                    });
                    break;
                    
                case 'joDel':
                    data.slice(1).forEach(row => {
                        if (row.length >= 1 && row[0]) {
                            this.addDeletionWord(row[0].trim());
                        }
                    });
                    break;
                    
                case 'moAbb':
                    data.slice(1).forEach(row => {
                        if (row.length >= 2 && row[0] && row[1]) {
                            this.currentData.monthAbbreviations[row[0].trim()] = row[1].trim();
                        }
                    });
                    break;
                    
                case 'properNouns':
                    data.slice(1).forEach(row => {
                        if (row.length >= 1 && row[0]) {
                            this.addProperNoun(row[0].trim());
                        }
                    });
                    break;
            }
            
            this.saveDataToStorage();
            return true;
        } catch (error) {
            console.error(`Failed to import ${csvType} CSV:`, error);
            return false;
        }
    }
    
    /**
     * Get data statistics
     * @returns {Object} Statistics about current data
     */
    getStatistics() {
        return {
            journalAbbreviations: Object.keys(this.currentData.journalAbbreviations).length,
            deletionWords: this.currentData.deletionWords.length,
            monthAbbreviations: Object.keys(this.currentData.monthAbbreviations).length,
            properNouns: this.currentData.properNouns.length,
            lastModified: this.currentData.lastModified,
            version: this.currentData.version
        };
    }
    
    /**
     * Search within dictionaries
     * @param {string} query - Search query
     * @returns {Object} Search results
     */
    search(query) {
        const results = {
            journalAbbreviations: [],
            deletionWords: [],
            monthAbbreviations: [],
            properNouns: []
        };
        
        const lowerQuery = query.toLowerCase();
        
        // Search journal abbreviations
        Object.entries(this.currentData.journalAbbreviations).forEach(([key, value]) => {
            if (key.toLowerCase().includes(lowerQuery) || value.toLowerCase().includes(lowerQuery)) {
                results.journalAbbreviations.push({ original: key, abbreviation: value });
            }
        });
        
        // Search deletion words
        this.currentData.deletionWords.forEach(word => {
            if (word.toLowerCase().includes(lowerQuery)) {
                results.deletionWords.push(word);
            }
        });
        
        // Search month abbreviations
        Object.entries(this.currentData.monthAbbreviations).forEach(([key, value]) => {
            if (key.toLowerCase().includes(lowerQuery) || value.toLowerCase().includes(lowerQuery)) {
                results.monthAbbreviations.push({ original: key, abbreviation: value });
            }
        });
        
        // Search proper nouns
        this.currentData.properNouns.forEach(noun => {
            if (noun.toLowerCase().includes(lowerQuery)) {
                results.properNouns.push(noun);
            }
        });
        
        return results;
    }
}