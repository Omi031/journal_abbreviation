// Citation Formatter - Main formatting logic
class CitationFormatter {
    constructor(settings = {}) {
        this.settings = {
            et_al_th: 6,
            format: 'tex',
            conf_with_in: false,
            conf_with_proc: true,
            conf_with_year: false,
            title_case_conversion: true,
            auto_detect_proper_nouns: true,
            ...settings
        };
        
        // Initialize dictionaries
        this.joAbbDict = new Map();
        this.joDelWords = [];
        this.moAbbDict = new Map();
        this.properNouns = new Set([
            '6G', 'OFDM', 'Raician', 'IoT', 'AI', 'ML', 'DL', 'CNN', 'LSTM', 'BERT',
            'GPS', 'WiFi', 'Bluetooth', 'LTE', '5G', '4G', '3G', 'MIMO', 'QoS',
            'TCP', 'UDP', 'HTTP', 'HTTPS', 'SSL', 'TLS', 'API', 'REST', 'JSON'
        ]);
        
        // Common English words (for proper noun detection)
        this.commonWords = new Set([
            'the', 'and', 'or', 'with', 'for', 'in', 'on', 'at', 'to', 'from',
            'by', 'of', 'system', 'method', 'approach', 'technique', 'analysis',
            'study', 'research', 'performance', 'evaluation', 'implementation',
            'algorithm', 'model', 'based', 'using', 'proposed', 'novel',
            'efficient', 'enhanced', 'improved', 'optimal', 'design', 'development',
            'application', 'network', 'wireless', 'communication', 'signal',
            'processing', 'detection', 'estimation', 'classification', 'learning',
            'deep', 'machine', 'artificial', 'neural', 'data', 'information', 'control'
        ]);
    }
    
    /**
     * Update formatter settings
     * @param {Object} newSettings - New settings to merge
     */
    updateSettings(newSettings) {
        this.settings = { ...this.settings, ...newSettings };
    }
    
    /**
     * Load dictionaries from dictionary data
     * @param {Object} dictData - Object containing dictionary data arrays
     */
    loadDictionaries(dictData) {
        if (dictData.joAbb) {
            // Convert array of [original, abbreviated] pairs to Map
            this.joAbbDict = new Map(dictData.joAbb);
        }
        if (dictData.joDel) {
            // Convert array of [word] arrays to simple array
            this.joDelWords = dictData.joDel.map(item => Array.isArray(item) ? item[0] : item);
        }
        if (dictData.moAbb) {
            // Convert array of [original, abbreviated] pairs to Map
            this.moAbbDict = new Map(dictData.moAbb);
        }
        if (dictData.properNouns) {
            // Convert array of [noun] arrays to Set, merge with existing
            const properNounsArray = dictData.properNouns.map(item => Array.isArray(item) ? item[0] : item);
            this.properNouns = new Set([...this.properNouns, ...properNounsArray]);
        }
    }
    
    /**
     * Parse RIS format text into citation data objects
     * @param {string} risText - RIS formatted text
     * @returns {Array<Object>} Array of citation data objects
     */
    parseRIS(risText) {
        const citations = [];
        let currentCitation = {};
        
        const lines = risText.split(/\r?\n/);
        
        for (const line of lines) {
            const trimmedLine = line.trim();
            if (!trimmedLine) continue;
            
            if (trimmedLine.match(/^TY\s*-/)) {
                // Start of new citation
                if (Object.keys(currentCitation).length > 0) {
                    citations.push(currentCitation);
                }
                currentCitation = {};
            }
            
            if (trimmedLine.match(/^ER\s*-/)) {
                // End of citation
                if (Object.keys(currentCitation).length > 0) {
                    citations.push(currentCitation);
                    currentCitation = {};
                }
                continue;
            }
            
            // Parse field
            const match = trimmedLine.match(/^([A-Z][A-Z0-9]?)\s*-\s*(.*)$/);
            if (match) {
                const [, field, value] = match;
                if (field && value) {
                    if (currentCitation[field]) {
                        // Multiple values for same field (e.g., multiple authors)
                        if (Array.isArray(currentCitation[field])) {
                            currentCitation[field].push(value.trim());
                        } else {
                            currentCitation[field] = [currentCitation[field], value.trim()];
                        }
                    } else {
                        currentCitation[field] = value.trim();
                    }
                }
            }
        }
        
        // Add final citation if exists
        if (Object.keys(currentCitation).length > 0) {
            citations.push(currentCitation);
        }
        
        return citations;
    }
    
    /**
     * Check if a word is likely a proper noun (automatic detection)
     * @param {string} word - Word to check
     * @returns {boolean} True if likely a proper noun
     */
    isLikelyProperNoun(word) {
        // Pattern 1: All uppercase abbreviations (2-6 characters)
        if (word.match(/^[A-Z]{2,6}$/)) return true;
        
        // Pattern 2: Number + letters or letters + number
        if (word.match(/^\d+[A-Za-z]+$/) || word.match(/^[A-Za-z]+\d+$/)) return true;
        
        // Pattern 3: CamelCase pattern
        if (word.match(/^[A-Z][a-z]*[A-Z]/)) return true;
        
        // Pattern 4: Not a common word and has high ratio of uppercase letters
        if (!this.commonWords.has(word.toLowerCase())) {
            const upperCount = (word.match(/[A-Z]/g) || []).length;
            if (word.length > 2 && upperCount / word.length > 0.5) return true;
        }
        
        return false;
    }
    
    /**
     * Convert title to proper title case
     * @param {string} title - Original title
     * @returns {string} Title case formatted title
     */
    convertToTitleCase(title) {
        if (!this.settings.title_case_conversion || !title) return title;
        
        return title.replace(/\b\w+\b/g, (word, index) => {
            // Check dictionary proper nouns (case insensitive)
            const dictMatch = Array.from(this.properNouns).find(
                noun => noun.toLowerCase() === word.toLowerCase()
            );
            if (dictMatch) return dictMatch;
            
            // Check automatic proper noun detection
            if (this.settings.auto_detect_proper_nouns && this.isLikelyProperNoun(word)) {
                return word; // Keep original case
            }
            
            // First word or not a common word: capitalize first letter
            if (index === 0) {
                return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
            }
            
            // Other words: lowercase
            return word.toLowerCase();
        });
    }
    
    /**
     * Delete specified words from text
     * @param {string} text - Input text
     * @param {Array<string>} delWords - Words to delete
     * @returns {string} Text with words removed
     */
    deleteWords(text, delWords) {
        const words = text.split(/\s+/);
        const filtered = words.filter(word => !delWords.includes(word));
        return filtered.join(' ');
    }
    
    /**
     * Apply abbreviations to text
     * @param {string} text - Input text
     * @param {Map<string, string>} abbDict - Abbreviation dictionary
     * @returns {string} Text with abbreviations applied
     */
    applyAbbreviations(text, abbDict) {
        const words = text.split(/\s+/);
        const abbreviated = words.map(word => {
            if (abbDict.has(word)) {
                const abbrev = abbDict.get(word);
                return abbrev.endsWith('.') ? abbrev : abbrev + '.';
            }
            return word;
        });
        return abbreviated.join(' ');
    }
    
    /**
     * Format author list
     * @param {string|Array<string>} authors - Author(s)
     * @param {string} format - Output format ('tex' or 'plain')
     * @returns {string} Formatted author string
     */
    formatAuthors(authors, format = 'tex') {
        if (typeof authors === 'string') return authors;
        if (!authors || authors.length === 0) return '';
        
        const authorArray = Array.isArray(authors) ? authors : [authors];
        
        if (authorArray.length >= this.settings.et_al_th) {
            if (format === 'plain') {
                return authorArray[0] + ' et al.';
            } else {
                return authorArray[0] + ' \\textit{et al}.';
            }
        }
        
        if (authorArray.length === 1) {
            return authorArray[0];
        } else if (authorArray.length === 2) {
            return authorArray.join(' and ');
        } else {
            return authorArray.slice(0, -1).join(', ') + ', and ' + authorArray[authorArray.length - 1];
        }
    }
    
    /**
     * Format title
     * @param {string} title - Original title
     * @param {string} format - Output format ('tex' or 'plain')
     * @returns {string} Formatted title
     */
    formatTitle(title, format = 'tex') {
        if (!title) return '';
        
        const formattedTitle = this.convertToTitleCase(title);
        
        if (format === 'plain') {
            return `"${formattedTitle},"`;
        } else {
            return `\`\`${formattedTitle},''`;
        }
    }
    
    /**
     * Format journal name
     * @param {string} journal - Original journal name
     * @param {string} format - Output format ('tex' or 'plain')
     * @param {string} type - Citation type ('JOUR' or 'CONF')
     * @returns {string} Formatted journal name
     */
    formatJournal(journal, format = 'tex', type = 'JOUR') {
        if (!journal) return '';
        
        let formatted = journal;
        
        // Apply deletions and abbreviations
        formatted = this.deleteWords(formatted, this.joDelWords);
        formatted = this.applyAbbreviations(formatted, this.joAbbDict);
        
        if (type === 'CONF') {
            // Remove year from beginning if conf_with_year is false
            if (!this.settings.conf_with_year) {
                formatted = formatted.replace(/^\s*\d{4}\s*/, '');
            }
            
            // Add "Proc." if enabled and not already present
            if (this.settings.conf_with_proc && !formatted.startsWith('Proc.')) {
                formatted = 'Proc. ' + formatted;
            }
        }
        
        // Apply TeX formatting
        if (format === 'tex') {
            formatted = `\\textit{${formatted}}`;
        }
        
        // Add "in" for conferences if enabled
        if (type === 'CONF' && this.settings.conf_with_in && !formatted.startsWith('in')) {
            formatted = 'in ' + formatted;
        }
        
        return formatted;
    }
    
    /**
     * Format volume
     * @param {string} volume - Volume number
     * @returns {string|null} Formatted volume or null if empty
     */
    formatVolume(volume) {
        return volume ? `vol. ${volume}` : null;
    }
    
    /**
     * Format issue number
     * @param {string} issue - Issue number
     * @returns {string|null} Formatted issue or null if empty
     */
    formatIssue(issue) {
        return issue ? `no. ${issue}` : null;
    }
    
    /**
     * Format page range
     * @param {string} startPage - Start page
     * @param {string} endPage - End page
     * @param {string} format - Output format ('tex' or 'plain')
     * @returns {string|null} Formatted pages or null if empty
     */
    formatPages(startPage, endPage, format = 'tex') {
        if (!startPage || !endPage) return null;
        
        if (format === 'plain') {
            return `pp. ${startPage}-${endPage}`;
        } else {
            return `pp. ${startPage}--${endPage}`;
        }
    }
    
    /**
     * Format year/date
     * @param {string} year - Year string (may include month)
     * @returns {string} Formatted year
     */
    formatYear(year) {
        if (!year) return '';
        
        // Remove day information (format: YYYY/MM/DD or YYYY/MM)
        let formatted = year.replace(/^\s*\d{1,2}(?:\s*-\s*\d{1,2})?\s*/, '');
        
        // Apply month abbreviations
        formatted = this.applyAbbreviations(formatted, this.moAbbDict);
        
        return formatted;
    }
    
    /**
     * Format DOI
     * @param {string} doi - DOI string
     * @returns {string|null} Formatted DOI or null if empty
     */
    formatDOI(doi) {
        return doi ? `doi: ${doi}` : null;
    }
    
    /**
     * Format a single citation
     * @param {Object} citation - Citation data object
     * @param {string} format - Output format ('tex' or 'plain')
     * @param {Function} yearInputCallback - Callback for missing year input
     * @returns {string|null} Formatted citation or null if unsupported type
     */
    formatCitation(citation, format = 'tex', yearInputCallback = null) {
        const type = citation.TY;
        
        if (type === 'JOUR') {
            return this.formatJournalCitation(citation, format, yearInputCallback);
        } else if (type === 'CONF') {
            return this.formatConferenceCitation(citation, format);
        } else {
            console.warn(`Unsupported citation type: ${type}`);
            return null;
        }
    }
    
    /**
     * Format journal citation
     * @param {Object} citation - Citation data
     * @param {string} format - Output format
     * @param {Function} yearInputCallback - Callback for missing year
     * @returns {string} Formatted journal citation
     */
    formatJournalCitation(citation, format = 'tex', yearInputCallback = null) {
        const authors = this.formatAuthors(citation.AU, format);
        const title = this.formatTitle(citation.TI, format);
        const journal = this.formatJournal(citation.JO || citation.T2, format, 'JOUR');
        const volume = this.formatVolume(citation.VL);
        const issue = this.formatIssue(citation.IS);
        const pages = this.formatPages(citation.SP, citation.EP, format);
        let year = this.formatYear(citation.Y1);
        
        // Handle early access articles (no volume/issue)
        if (!volume && !issue) {
            if (!year) {
                if (yearInputCallback) {
                    const userYear = yearInputCallback();
                    if (userYear) {
                        year = this.formatYear(userYear);
                    } else {
                        year = 'Unknown Year';
                    }
                } else {
                    year = 'Unknown Year';
                }
            }
            const doi = this.formatDOI(citation.DO);
            const parts = [
                authors,
                title ? title + ' ' + journal : journal,
                'early access',
                year,
                doi
            ].filter(Boolean);
            
            return parts.join(', ') + '.';
        } else {
            const parts = [
                authors,
                title ? title + ' ' + journal : journal,
                volume,
                issue,
                pages,
                year
            ].filter(Boolean);
            
            return parts.join(', ') + '.';
        }
    }
    
    /**
     * Format conference citation
     * @param {Object} citation - Citation data
     * @param {string} format - Output format
     * @returns {string} Formatted conference citation
     */
    formatConferenceCitation(citation, format = 'tex') {
        const authors = this.formatAuthors(citation.AU, format);
        const title = this.formatTitle(citation.TI, format);
        const journal = this.formatJournal(citation.JO || citation.T2, format, 'CONF');
        const pages = this.formatPages(citation.SP, citation.EP, format);
        const year = this.formatYear(citation.Y1);
        
        const parts = [
            authors,
            title ? title + ' ' + journal : journal,
            year,
            pages
        ].filter(Boolean);
        
        return parts.join(', ') + '.';
    }
    
    /**
     * Format multiple citations from RIS text or journal names only
     * @param {string} inputText - RIS formatted text or journal names
     * @param {string} format - Output format ('tex' or 'plain')
     * @param {string} mode - Processing mode ('full' or 'journal-only')
     * @returns {Array<Object>} Array of formatting results
     */
    formatMultiple(inputText, format = 'tex', mode = 'full') {
        if (mode === 'journal-only') {
            return this.formatJournalNamesOnly(inputText, format);
        }
        
        if (mode === 'arxiv-bibtex') {
            return this.processArxivBibTeX(inputText, format);
        }
        
        const citations = this.parseRIS(inputText);
        const results = [];
        
        for (const citation of citations) {
            try {
                const formatted = this.formatCitation(citation, format);
                if (formatted) {
                    results.push({
                        success: true,
                        citation: formatted,
                        original: citation
                    });
                } else {
                    results.push({
                        success: false,
                        error: `Unsupported citation type: ${citation.TY}`,
                        original: citation
                    });
                }
            } catch (error) {
                results.push({
                    success: false,
                    error: error.message,
                    original: citation
                });
            }
        }
        
        return results;
    }

    /**
     * Abbreviate journal name with optional formatting
     * @param {string} journalName - Journal name to abbreviate
     * @param {string} format - Output format ('tex' or 'plain')
     * @returns {string} Abbreviated journal name
     */
    abbreviateJournal(journalName, format = 'plain') {
        if (!journalName) return '';
        
        let abbreviated = journalName.trim();
        
        // Apply deletions and abbreviations
        abbreviated = this.deleteWords(abbreviated, this.joDelWords);
        abbreviated = this.applyAbbreviations(abbreviated, this.joAbbDict);
        
        // Apply TeX formatting if requested
        if (format === 'tex') {
            abbreviated = `\\textit{${abbreviated}}`;
        }
        
        return abbreviated;
    }

    /**
     * Format journal names only (no full citation)
     * @param {string} inputText - Text containing journal names (one per line)
     * @param {string} format - Output format ('tex' or 'plain')
     * @returns {Array<Object>} Array of formatting results
     */
    formatJournalNamesOnly(inputText, format = 'plain') {
        const lines = inputText.split('\n')
            .map(line => line.trim())
            .filter(line => line.length > 0);
        
        const results = [];
        
        for (const line of lines) {
            try {
                const abbreviated = this.abbreviateJournal(line, format);
                results.push({
                    success: true,
                    citation: abbreviated,
                    original: { JO: line },
                    mode: 'journal-only'
                });
            } catch (error) {
                results.push({
                    success: false,
                    error: error.message,
                    original: { JO: line },
                    mode: 'journal-only'
                });
            }
        }
        
        return results;
    }
    
    /**
     * Parse BibTeX format and extract fields
     * @param {string} bibtex - BibTeX formatted text
     * @returns {Object} Extracted fields (title, author, year, eprint)
     */
    parseBibTeX(bibtex) {
        const fields = {};
        
        // Extract title
        const titleMatch = bibtex.match(/title\s*=\s*\{([^}]+)\}/i);
        if (titleMatch) {
            fields.title = titleMatch[1].trim();
        }
        
        // Extract author
        const authorMatch = bibtex.match(/author\s*=\s*\{([^}]+)\}/i);
        if (authorMatch) {
            fields.author = authorMatch[1].trim();
        }
        
        // Extract year
        const yearMatch = bibtex.match(/year\s*=\s*\{([^}]+)\}/i);
        if (yearMatch) {
            fields.year = yearMatch[1].trim();
        }
        
        // Extract eprint (arXiv ID)
        const eprintMatch = bibtex.match(/eprint\s*=\s*\{([^}]+)\}/i);
        if (eprintMatch) {
            fields.eprint = eprintMatch[1].trim();
        }
        
        return fields;
    }
    
    /**
     * Format author names for arXiv citation (convert to initials)
     * @param {string} authorStr - Author string from BibTeX (e.g., "Diederik P. Kingma and Jimmy Ba")
     * @returns {string} Formatted author string (e.g., "D. P. Kingma and J. Ba")
     */
    formatArxivAuthors(authorStr) {
        if (!authorStr) return '';
        
        const authors = authorStr.split(/\s+and\s+/i);
        const formatted = authors.map(author => {
            author = author.trim();
            const parts = author.split(/\s+/);
            if (parts.length === 0) return author;
            
            const lastName = parts[parts.length - 1];
            const firstNames = parts.slice(0, -1);
            
            // Convert first and middle names to initials
            const initials = firstNames.map(name => {
                // If already an initial (e.g., "P."), keep it
                if (name.length <= 2 && name.endsWith('.')) return name;
                if (name.length === 1) return name + '.';
                // Full name - take first character
                return name.charAt(0).toUpperCase() + '.';
            }).join(' ');
            
            return initials ? `${initials} ${lastName}` : lastName;
        });
        
        return formatted.join(' and ');
    }
    
    /**
     * Format arXiv citation from BibTeX
     * @param {string} bibtex - BibTeX formatted text
     * @param {string} format - Output format ('tex' or 'plain')
     * @returns {string} Formatted citation
     */
    formatArxivCitation(bibtex, format = 'tex') {
        const fields = this.parseBibTeX(bibtex);
        
        // Validate required fields
        if (!fields.author || !fields.title || !fields.year || !fields.eprint) {
            throw new Error('arXiv BibTeX形式が正しくありません。author, title, year, eprintフィールドが必要です。');
        }
        
        const authors = this.formatArxivAuthors(fields.author);
        const title = this.convertToTitleCase(fields.title);
        const year = fields.year;
        const arxivId = fields.eprint;
        
        if (format === 'tex') {
            // TeX format: D. P. Kingma and J. Ba, ``Title,'' 2017, \textit{arXiv:1412.6980}.
            return `${authors}, \`\`${title},'' ${year}, \\textit{arXiv:${arxivId}}.`;
        } else {
            // Plain format: D. P. Kingma and J. Ba, "Title," 2017, arXiv:1412.6980.
            return `${authors}, "${title}," ${year}, arXiv:${arxivId}.`;
        }
    }
    
    /**
     * Process arXiv BibTeX entries
     * @param {string} text - Input text containing BibTeX entries
     * @param {string} format - Output format ('tex' or 'plain')
     * @returns {Array<Object>} Array of formatted citations
     */
    processArxivBibTeX(text, format = 'tex') {
        const results = [];
        
        // Split by @misc or @article entries
        const entries = text.split(/@(?=misc|article)/i).filter(e => e.trim());
        
        if (entries.length === 0) {
            // If no @ found, treat entire text as single entry
            entries.push(text);
        }
        
        for (let entry of entries) {
            entry = entry.trim();
            if (!entry) continue;
            
            // Add @ back if it was removed
            if (!entry.startsWith('@')) {
                entry = '@' + entry;
            }
            
            try {
                const citation = this.formatArxivCitation(entry, format);
                results.push({
                    success: true,
                    citation: citation,
                    original: entry,
                    mode: 'arxiv-bibtex'
                });
            } catch (error) {
                results.push({
                    success: false,
                    error: error.message,
                    original: entry,
                    mode: 'arxiv-bibtex'
                });
            }
        }
        
        return results;
    }
}