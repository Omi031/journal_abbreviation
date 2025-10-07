// CSV Parser utility functions
class CSVParser {
    /**
     * Parse CSV text into array of arrays
     * @param {string} text - CSV text content
     * @param {string} delimiter - Field delimiter (default: ',')
     * @returns {Array<Array<string>>} Parsed CSV data
     */
    static parse(text, delimiter = ',') {
        const lines = text.split(/\r?\n/);
        const result = [];
        
        for (let line of lines) {
            line = line.trim();
            if (!line) continue;
            
            const fields = this.parseLine(line, delimiter);
            result.push(fields);
        }
        
        return result;
    }
    
    /**
     * Parse a single CSV line handling quotes properly
     * @param {string} line - Single CSV line
     * @param {string} delimiter - Field delimiter
     * @returns {Array<string>} Array of field values
     */
    static parseLine(line, delimiter = ',') {
        const fields = [];
        let current = '';
        let inQuotes = false;
        let i = 0;
        
        while (i < line.length) {
            const char = line[i];
            const nextChar = line[i + 1];
            
            if (char === '"') {
                if (inQuotes && nextChar === '"') {
                    // Escaped quote
                    current += '"';
                    i += 2;
                } else {
                    // Toggle quote state
                    inQuotes = !inQuotes;
                    i++;
                }
            } else if (char === delimiter && !inQuotes) {
                // Field separator
                fields.push(current.trim());
                current = '';
                i++;
            } else {
                current += char;
                i++;
            }
        }
        
        // Add the last field
        fields.push(current.trim());
        
        return fields;
    }
    
    /**
     * Load CSV from file input element
     * @param {File} file - File object from input element
     * @returns {Promise<Array<Array<string>>>} Promise resolving to parsed CSV data
     */
    static async loadFromFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = (event) => {
                try {
                    const text = event.target.result;
                    const data = this.parse(text);
                    resolve(data);
                } catch (error) {
                    reject(new Error(`CSV parse error: ${error.message}`));
                }
            };
            
            reader.onerror = () => {
                reject(new Error('File reading failed'));
            };
            
            reader.readAsText(file, 'utf-8');
        });
    }
    
    /**
     * Load CSV from URL
     * @param {string} url - URL to CSV file
     * @returns {Promise<Array<Array<string>>>} Promise resolving to parsed CSV data
     */
    static async loadFromURL(url) {
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const text = await response.text();
            return this.parse(text);
        } catch (error) {
            throw new Error(`Failed to load CSV from URL: ${error.message}`);
        }
    }
    
    /**
     * Convert parsed CSV data to dictionary format
     * @param {Array<Array<string>>} data - Parsed CSV data
     * @param {number} keyColumn - Column index for keys (default: 0)
     * @param {number} valueColumn - Column index for values (default: 1)
     * @returns {Map<string, string>} Dictionary mapping
     */
    static toDict(data, keyColumn = 0, valueColumn = 1) {
        const dict = new Map();
        
        // Skip header row (index 0)
        for (let i = 1; i < data.length; i++) {
            const row = data[i];
            if (row.length > Math.max(keyColumn, valueColumn)) {
                const key = (row[keyColumn] || '').trim();
                const value = (row[valueColumn] || '').trim();
                if (key) {
                    dict.set(key, value);
                }
            }
        }
        
        return dict;
    }
    
    /**
     * Convert parsed CSV data to array format (first column only)
     * @param {Array<Array<string>>} data - Parsed CSV data
     * @param {number} column - Column index to extract (default: 0)
     * @returns {Array<string>} Array of values from specified column
     */
    static toArray(data, column = 0) {
        const result = [];
        
        // Skip header row (index 0)
        for (let i = 1; i < data.length; i++) {
            const row = data[i];
            if (row.length > column) {
                const value = (row[column] || '').trim();
                if (value) {
                    result.push(value);
                }
            }
        }
        
        return result;
    }
    
    /**
     * Validate CSV structure
     * @param {Array<Array<string>>} data - Parsed CSV data
     * @param {number} expectedColumns - Expected number of columns
     * @returns {Object} Validation result
     */
    static validate(data, expectedColumns = null) {
        const result = {
            valid: true,
            errors: [],
            warnings: []
        };
        
        if (!data || data.length === 0) {
            result.valid = false;
            result.errors.push('CSV data is empty');
            return result;
        }
        
        if (data.length < 2) {
            result.warnings.push('CSV contains only header row');
        }
        
        if (expectedColumns !== null) {
            const headerColumns = data[0]?.length || 0;
            if (headerColumns !== expectedColumns) {
                result.warnings.push(`Expected ${expectedColumns} columns, found ${headerColumns}`);
            }
            
            // Check each data row
            for (let i = 1; i < data.length; i++) {
                const rowColumns = data[i]?.length || 0;
                if (rowColumns !== expectedColumns) {
                    result.warnings.push(`Row ${i + 1} has ${rowColumns} columns, expected ${expectedColumns}`);
                }
            }
        }
        
        return result;
    }
}