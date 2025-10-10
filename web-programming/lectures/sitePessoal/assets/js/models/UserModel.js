/**
 * @file UserModel.js
 * @author Rafael Passos Domingues
 * @version 3.0.0
 * @brief Model responsible for managing user personal and contact data.
 * @description Provides methods for retrieving and updating user information,
 * including contacts, academic background, professional profile, and preferences
 * with validation, caching, and extensible architecture.
 */

/**
 * @constant {Object} VALIDATION_SCHEMAS
 * @brief Validation rules and schemas for user data integrity
 * @description Defines validation patterns, required fields, and constraints for user data
 */
const VALIDATION_SCHEMAS = {
    PERSONAL_INFO: {
        requiredFields: ['fullName', 'professionalTitle'],
        fullName: {
            pattern: /^[A-Za-zÀ-ÿ\s]{2,100}$/,
            maxLength: 100
        },
        professionalTitle: {
            pattern: /^[A-Za-zÀ-ÿ\s&]{5,50}$/,
            maxLength: 50
        },
        summary: {
            maxLength: 500
        }
    },
    CONTACT_INFO: {
        email: {
            pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            maxLength: 254
        },
        phone: {
            pattern: /^[\+]?[0-9\s\-\(\)]{10,15}$/,
            maxLength: 20
        },
        url: {
            pattern: /^https?:\/\/.+\..+$/,
            maxLength: 200
        }
    },
    EDUCATION: {
        requiredFields: ['degree', 'institution', 'startYear'],
        degree: {
            maxLength: 100
        },
        institution: {
            maxLength: 100
        },
        status: {
            allowedValues: ['completed', 'in-progress', 'paused', 'planned']
        }
    }
};

/**
 * @constant {Object} DEFAULT_USER_DATA
 * @brief Default user data structure with comprehensive information
 * @description Provides complete user profile with all supported fields and structure
 */
const DEFAULT_USER_DATA = {
    personalInfo: {
        fullName: 'Rafael Passos Domingues',
        professionalTitle: 'Physicist & Computer Scientist',
        summary: 'Combining physics background with computer science expertise. Experienced in galactic astrophysics, data analysis, education, and technology innovation. Currently pursuing Computer Science degree while working in innovation ecosystems.',
        profileImage: {
            url: 'assets/images/profile.jpg',
            alt: 'Professional portrait of Rafael Passos Domingues',
            width: 400,
            height: 400
        },
        location: {
            city: 'Alfenas',
            state: 'Minas Gerais',
            country: 'Brazil',
            timezone: 'America/Sao_Paulo'
        },
        languages: [
            {
                language: 'Portuguese',
                proficiency: 'native',
                level: 100
            },
            {
                language: 'English',
                proficiency: 'advanced',
                level: 85
            },
            {
                language: 'Spanish',
                proficiency: 'intermediate',
                level: 60
            }
        ]
    },
    contactInfo: {
        primaryEmail: 'rafaelpassosdomingues@gmail.com',
        secondaryEmail: null,
        phone: null,
        socialNetworks: [
            {
                platform: 'GitHub',
                username: 'passosdomingues',
                url: 'https://github.com/passosdomingues',
                icon: 'github',
                isPublic: true,
                priority: 1
            },
            {
                platform: 'LinkedIn',
                username: 'rafaelpassosdomingues',
                url: 'https://www.linkedin.com/in/rafaelpassosdomingues/',
                icon: 'linkedin',
                isPublic: true,
                priority: 2
            },
            {
                platform: 'Instagram',
                username: '@rafaelpassosdomingues',
                url: 'https://instagram.com/rafaelpassosdomingues',
                icon: 'instagram',
                isPublic: true,
                priority: 3
            }
        ],
        websites: [
            {
                name: 'Personal Website',
                url: 'https://sites.google.com/view/pandefisica/',
                description: 'Academic and professional portfolio',
                isPrimary: true
            }
        ],
        availability: {
            status: 'available',
            responseTime: '24-48 hours',
            preferredContactMethod: 'email'
        }
    },
    academicBackground: {
        degrees: [
            {
                id: 'computer-science-bachelor',
                degree: 'Bachelor of Computer Science',
                institution: 'UNIFAL-MG',
                location: 'Alfenas, MG, Brazil',
                startYear: 2023,
                endYear: 2029,
                status: 'in-progress',
                currentSemester: 2,
                totalSemesters: 12,
                gpa: null,
                highlights: [
                    'Software Engineering',
                    'Data Structures and Algorithms',
                    'Database Systems',
                    'Artificial Intelligence'
                ],
                thesis: null,
                advisor: null
            },
            {
                id: 'physics-master',
                degree: 'Master of Physics',
                institution: 'UNIFEI',
                location: 'Itajubá, MG, Brazil',
                startYear: 2021,
                endYear: 2023,
                status: 'completed',
                gpa: 4.2,
                thesis: 'Analysis of Active Galactic Nuclei Characteristics',
                advisor: 'Dr. Professor Name',
                researchArea: 'Extragalactic Astrophysics',
                publications: [
                    {
                        title: 'Research on AGN Emission Patterns',
                        conference: 'Brazilian Physics Society',
                        year: 2023,
                        link: 'https://example.com/publication'
                    }
                ],
                highlights: [
                    'Advanced Data Analysis',
                    'Scientific Computing',
                    'Research Methodology',
                    'Academic Writing'
                ]
            },
            {
                id: 'physics-bachelor',
                degree: 'Bachelor of Physics',
                institution: 'UNIFAL-MG',
                location: 'Alfenas, MG, Brazil',
                startYear: 2014,
                endYear: 2018,
                status: 'completed',
                gpa: 3.8,
                thesis: 'Galactic Rotation Curves and Dark Matter',
                advisor: 'Dr. Professor Name',
                researchArea: 'Galactic Astrophysics',
                highlights: [
                    'Astrophysics Research',
                    'Mathematical Modeling',
                    'Experimental Physics',
                    'Scientific Outreach'
                ]
            }
        ],
        certifications: [
            {
                id: 'data-science-cert',
                name: 'Data Science Professional Certificate',
                issuer: 'Example Platform',
                issueDate: '2023-05-15',
                expiryDate: null,
                credentialId: 'DS-12345',
                credentialUrl: 'https://example.com/certificate',
                skills: ['Python', 'Machine Learning', 'Data Analysis']
            }
        ]
    },
    professionalProfile: {
        currentRole: 'Computer Science Student & Innovation Enthusiast',
        areasOfExpertise: [
            {
                category: 'Scientific Research',
                skills: ['Astrophysics Data Analysis', 'Statistical Modeling', 'Research Methodology']
            },
            {
                category: 'Technology',
                skills: ['Software Development', 'Data Science', 'Web Technologies']
            },
            {
                category: 'Education',
                skills: ['Teaching', 'Curriculum Development', 'Scientific Outreach']
            }
        ],
        careerObjectives: [
            'Bridge the gap between scientific research and software engineering',
            'Develop innovative solutions using data-driven approaches',
            'Contribute to open-source scientific computing projects'
        ],
        employmentStatus: 'student',
        openToOpportunities: true,
        preferredWorkTypes: ['internship', 'part-time', 'remote', 'research']
    },
    preferences: {
        communication: {
            language: 'en-US',
            dateFormat: 'MM/DD/YYYY',
            timeFormat: '12h',
            temperatureUnit: 'celsius'
        },
        privacy: {
            showEmail: true,
            showPhone: false,
            showLocation: true,
            showBirthDate: false
        },
        notifications: {
            emailNotifications: true,
            projectUpdates: true,
            newsletter: false,
            securityAlerts: true
        }
    },
    metadata: {
        profileCreated: '2024-01-01T00:00:00Z',
        lastUpdated: '2024-01-15T10:30:00Z',
        profileVersion: '3.0.0',
        dataSource: 'local-storage'
    }
};

/**
 * @class UserModel
 * @brief Centralized user data management system
 * @description Handles user personal information, contact details, academic background,
 * professional profile, and preferences with validation, caching, and update tracking
 */
class UserModel {
    /**
     * @brief Creates an instance of UserModel
     * @constructor
     * @param {Object} options - Configuration options for user model
     * @param {boolean} options.enableValidation - Whether to enable data validation
     * @param {boolean} options.enableCaching - Whether to enable response caching
     * @param {string} options.storageKey - Key for localStorage persistence
     */
    constructor(options = {}) {
        const {
            enableValidation = true,
            enableCaching = true,
            storageKey = 'userProfileData'
        } = options;

        /**
         * @private
         * @type {Object}
         * @brief Complete user data structure with all profile information
         */
        this.userData = this.initializeUserData();

        /**
         * @private
         * @type {Object}
         * @brief Configuration options for user model behavior
         */
        this.configuration = {
            enableValidation,
            enableCaching,
            storageKey,
            cacheTimeout: 300000, // 5 minutes
            maxCacheSize: 50
        };

        /**
         * @private
         * @type {Map}
         * @brief Cache storage for optimized data retrieval
         */
        this.responseCache = new Map();

        /**
         * @private
         * @type {Array}
         * @brief Change history for tracking user data modifications
         */
        this.changeHistory = [];

        /**
         * @private
         * @type {boolean}
         * @brief Tracks whether user data has been modified since last save
         */
        this.hasUnsavedChanges = false;

        this.initializeUserModel();
    }

    /**
     * @brief Initializes the user model with data from localStorage or defaults
     * @private
     * @returns {Promise<void>} Resolves when user model is fully initialized
     */
    async initializeUserModel() {
        try {
            await this.loadUserData();
            this.initializeChangeTracking();
            console.info('UserModel: User model successfully initialized.');
        } catch (error) {
            console.error('UserModel: Failed to initialize user model:', error);
            throw error;
        }
    }

    /**
     * @brief Initializes user data from localStorage or uses default data
     * @private
     * @returns {Object} Initialized user data object
     */
    initializeUserData() {
        try {
            if (this.configuration.storageKey && typeof window !== 'undefined' && window.localStorage) {
                const storedData = localStorage.getItem(this.configuration.storageKey);
                if (storedData) {
                    const parsedData = JSON.parse(storedData);
                    console.debug('UserModel: Loaded user data from localStorage.');
                    return this.migrateUserData(parsedData);
                }
            }
        } catch (error) {
            console.warn('UserModel: Failed to load user data from localStorage, using defaults:', error);
        }

        console.debug('UserModel: Using default user data structure.');
        return this.deepClone(DEFAULT_USER_DATA);
    }

    /**
     * @brief Migrates user data from older versions to current structure
     * @private
     * @param {Object} legacyData - User data from previous versions
     * @returns {Object} Migrated user data in current structure
     */
    migrateUserData(legacyData) {
        // Handle data migration from previous versions
        if (!legacyData.metadata || !legacyData.metadata.profileVersion) {
            console.debug('UserModel: Migrating legacy user data structure.');
            return this.migrateFromLegacyStructure(legacyData);
        }

        return legacyData;
    }

    /**
     * @brief Migrates from legacy flat structure to current nested structure
     * @private
     * @param {Object} legacyData - Legacy flat user data structure
     * @returns {Object} Migrated nested user data structure
     */
    migrateFromLegacyStructure(legacyData) {
        const migratedData = this.deepClone(DEFAULT_USER_DATA);

        // Map legacy fields to new structure
        if (legacyData.name) {
            migratedData.personalInfo.fullName = legacyData.name;
        }
        if (legacyData.title) {
            migratedData.personalInfo.professionalTitle = legacyData.title;
        }
        if (legacyData.summary) {
            migratedData.personalInfo.summary = legacyData.summary;
        }
        if (legacyData.profileImage) {
            migratedData.personalInfo.profileImage.url = legacyData.profileImage;
        }

        // Migrate contact information
        if (legacyData.contact) {
            if (legacyData.contact.email) {
                migratedData.contactInfo.primaryEmail = legacyData.contact.email;
            }
            // Migrate social networks
            const socialNetworks = [];
            if (legacyData.contact.github) {
                socialNetworks.push({
                    platform: 'GitHub',
                    username: this.extractUsernameFromUrl(legacyData.contact.github),
                    url: legacyData.contact.github,
                    icon: 'github',
                    isPublic: true,
                    priority: 1
                });
            }
            if (legacyData.contact.linkedin) {
                socialNetworks.push({
                    platform: 'LinkedIn',
                    username: this.extractUsernameFromUrl(legacyData.contact.linkedin),
                    url: legacyData.contact.linkedin,
                    icon: 'linkedin',
                    isPublic: true,
                    priority: 2
                });
            }
            if (legacyData.contact.instagram) {
                socialNetworks.push({
                    platform: 'Instagram',
                    username: legacyData.contact.instagram,
                    url: `https://instagram.com/${legacyData.contact.instagram.replace('@', '')}`,
                    icon: 'instagram',
                    isPublic: true,
                    priority: 3
                });
            }
            migratedData.contactInfo.socialNetworks = socialNetworks;
        }

        // Migrate education
        if (Array.isArray(legacyData.education)) {
            migratedData.academicBackground.degrees = legacyData.education.map(edu => ({
                id: this.generateIdFromText(edu.degree),
                degree: edu.degree,
                institution: edu.institution,
                startYear: this.extractYearFromPeriod(edu.period),
                endYear: this.extractYearFromPeriod(edu.period, false),
                status: this.mapEducationStatus(edu.status),
                highlights: []
            }));
        }

        migratedData.metadata.lastUpdated = new Date().toISOString();
        migratedData.metadata.dataSource = 'migrated';

        return migratedData;
    }

    /**
     * @brief Extracts username from social media URL
     * @private
     * @param {string} url - Social media profile URL
     * @returns {string} Extracted username
     */
    extractUsernameFromUrl(url) {
        try {
            const pathParts = new URL(url).pathname.split('/').filter(part => part);
            return pathParts[pathParts.length - 1] || 'username';
        } catch {
            return 'username';
        }
    }

    /**
     * @brief Extracts year from period string
     * @private
     * @param {string} period - Period string (e.g., "2023-2029")
     * @param {boolean} isStart - Whether to extract start year
     * @returns {number|null} Extracted year or null
     */
    extractYearFromPeriod(period, isStart = true) {
        if (!period) return null;
        const years = period.split('-').map(y => parseInt(y.trim()));
        return isStart ? years[0] : (years[1] || null);
    }

    /**
     * @brief Maps legacy education status to current status values
     * @private
     * @param {string} legacyStatus - Legacy status value
     * @returns {string} Mapped status value
     */
    mapEducationStatus(legacyStatus) {
        const statusMap = {
            'Cursando': 'in-progress',
            'Concluído': 'completed'
        };
        return statusMap[legacyStatus] || 'completed';
    }

    /**
     * @brief Initializes change tracking system
     * @private
     */
    initializeChangeTracking() {
        this.changeHistory.push({
            timestamp: new Date().toISOString(),
            action: 'initialized',
            dataSnapshot: this.deepClone(this.userData)
        });
    }

    /**
     * @brief Loads user data from persistent storage
     * @private
     * @returns {Promise<void>} Resolves when user data is loaded
     */
    async loadUserData() {
        // Additional loading logic can be added here (e.g., from API)
        console.debug('UserModel: User data loading completed.');
    }

    /**
     * @brief Retrieves complete user data with optional caching
     * @public
     * @param {Object} options - Retrieval options
     * @param {boolean} options.includeSensitive - Whether to include sensitive data
     * @param {boolean} options.useCache - Whether to use cached data
     * @returns {Object} Complete user data object
     */
    getUserData(options = {}) {
        const {
            includeSensitive = false,
            useCache = true
        } = options;

        const cacheKey = `userData-${includeSensitive}`;
        
        if (useCache && this.configuration.enableCaching) {
            const cachedData = this.getCachedData(cacheKey);
            if (cachedData) {
                return cachedData;
            }
        }

        let userData = this.deepClone(this.userData);

        // Filter sensitive data if requested
        if (!includeSensitive) {
            userData = this.filterSensitiveData(userData);
        }

        if (this.configuration.enableCaching) {
            this.cacheData(cacheKey, userData);
        }

        return userData;
    }

    /**
     * @brief Filters out sensitive user data
     * @private
     * @param {Object} userData - Complete user data object
     * @returns {Object} Filtered user data without sensitive information
     */
    filterSensitiveData(userData) {
        const filteredData = this.deepClone(userData);
        
        // Remove sensitive contact information
        if (filteredData.contactInfo) {
            filteredData.contactInfo.phone = null;
            filteredData.contactInfo.secondaryEmail = null;
        }

        // Remove sensitive preference data
        if (filteredData.preferences) {
            delete filteredData.preferences.privacy;
            delete filteredData.preferences.notifications;
        }

        return filteredData;
    }

    /**
     * @brief Retrieves specific user data by path
     * @public
     * @param {string} dataPath - Dot notation path to desired data (e.g., 'personalInfo.fullName')
     * @returns {*} Requested data value or undefined if not found
     */
    getUserDataByPath(dataPath) {
        if (!dataPath || typeof dataPath !== 'string') {
            console.warn('UserModel: Invalid data path provided.');
            return undefined;
        }

        const pathParts = dataPath.split('.');
        let currentData = this.userData;

        for (const part of pathParts) {
            if (currentData && typeof currentData === 'object' && part in currentData) {
                currentData = currentData[part];
            } else {
                return undefined;
            }
        }

        return this.deepClone(currentData);
    }

    /**
     * @brief Updates user data with validation and change tracking
     * @public
     * @param {Object} updates - Object containing updates to apply
     * @param {Object} options - Update options
     * @param {boolean} options.validate - Whether to validate updates
     * @param {boolean} options.autoSave - Whether to auto-save to storage
     * @returns {Object} Updated user data
     * @throws {Error} When validation fails or updates are invalid
     */
    updateUserData(updates, options = {}) {
        const {
            validate = true,
            autoSave = true
        } = options;

        if (!updates || typeof updates !== 'object' || Array.isArray(updates)) {
            throw new Error('UserModel: Updates must be a non-null object.');
        }

        // Create deep clone for validation and update
        const updatesClone = this.deepClone(updates);
        const previousData = this.deepClone(this.userData);

        try {
            if (validate) {
                this.validateUserDataUpdates(updatesClone);
            }

            // Apply updates
            this.applyUserDataUpdates(updatesClone);

            // Update metadata
            this.userData.metadata.lastUpdated = new Date().toISOString();
            this.hasUnsavedChanges = true;

            // Track change history
            this.recordDataChange('update', previousData, updatesClone);

            // Clear cache since data has changed
            this.clearCache();

            if (autoSave) {
                this.saveUserData();
            }

            console.debug('UserModel: User data updated successfully.');
            return this.getUserData();

        } catch (error) {
            console.error('UserModel: Failed to update user data:', error);
            // Restore previous data on failure
            this.userData = previousData;
            throw error;
        }
    }

    /**
     * @brief Validates user data updates against schemas
     * @private
     * @param {Object} updates - Updates to validate
     * @throws {Error} When validation fails
     */
    validateUserDataUpdates(updates) {
        if (updates.personalInfo) {
            this.validatePersonalInfo(updates.personalInfo);
        }

        if (updates.contactInfo) {
            this.validateContactInfo(updates.contactInfo);
        }

        if (updates.academicBackground && updates.academicBackground.degrees) {
            updates.academicBackground.degrees.forEach(degree => {
                this.validateEducationItem(degree);
            });
        }
    }

    /**
     * @brief Validates personal information updates
     * @private
     * @param {Object} personalInfo - Personal info to validate
     * @throws {Error} When validation fails
     */
    validatePersonalInfo(personalInfo) {
        if (personalInfo.fullName) {
            if (!VALIDATION_SCHEMAS.PERSONAL_INFO.fullName.pattern.test(personalInfo.fullName)) {
                throw new Error('UserModel: Full name contains invalid characters.');
            }
            if (personalInfo.fullName.length > VALIDATION_SCHEMAS.PERSONAL_INFO.fullName.maxLength) {
                throw new Error(`UserModel: Full name exceeds maximum length of ${VALIDATION_SCHEMAS.PERSONAL_INFO.fullName.maxLength} characters.`);
            }
        }

        if (personalInfo.professionalTitle) {
            if (personalInfo.professionalTitle.length > VALIDATION_SCHEMAS.PERSONAL_INFO.professionalTitle.maxLength) {
                throw new Error(`UserModel: Professional title exceeds maximum length of ${VALIDATION_SCHEMAS.PERSONAL_INFO.professionalTitle.maxLength} characters.`);
            }
        }
    }

    /**
     * @brief Validates contact information updates
     * @private
     * @param {Object} contactInfo - Contact info to validate
     * @throws {Error} When validation fails
     */
    validateContactInfo(contactInfo) {
        if (contactInfo.primaryEmail && !VALIDATION_SCHEMAS.CONTACT_INFO.email.pattern.test(contactInfo.primaryEmail)) {
            throw new Error('UserModel: Primary email address is invalid.');
        }

        if (contactInfo.phone && !VALIDATION_SCHEMAS.CONTACT_INFO.phone.pattern.test(contactInfo.phone)) {
            throw new Error('UserModel: Phone number format is invalid.');
        }

        if (contactInfo.socialNetworks) {
            contactInfo.socialNetworks.forEach(network => {
                if (network.url && !VALIDATION_SCHEMAS.CONTACT_INFO.url.pattern.test(network.url)) {
                    throw new Error(`UserModel: Social network URL is invalid: ${network.url}`);
                }
            });
        }
    }

    /**
     * @brief Validates education item structure
     * @private
     * @param {Object} educationItem - Education item to validate
     * @throws {Error} When validation fails
     */
    validateEducationItem(educationItem) {
        VALIDATION_SCHEMAS.EDUCATION.requiredFields.forEach(field => {
            if (!educationItem[field]) {
                throw new Error(`UserModel: Education item missing required field: ${field}`);
            }
        });

        if (educationItem.status && !VALIDATION_SCHEMAS.EDUCATION.status.allowedValues.includes(educationItem.status)) {
            throw new Error(`UserModel: Invalid education status: ${educationItem.status}`);
        }
    }

    /**
     * @brief Applies validated updates to user data
     * @private
     * @param {Object} updates - Validated updates to apply
     */
    applyUserDataUpdates(updates) {
        Object.keys(updates).forEach(section => {
            if (this.userData[section] && typeof this.userData[section] === 'object' && !Array.isArray(this.userData[section])) {
                // Merge object sections
                this.userData[section] = {
                    ...this.userData[section],
                    ...updates[section]
                };
            } else {
                // Replace other values
                this.userData[section] = updates[section];
            }
        });
    }

    /**
     * @brief Records data changes for history tracking
     * @private
     * @param {string} action - Type of change action
     * @param {Object} previousData - Data before changes
     * @param {Object} updates - Applied updates
     */
    recordDataChange(action, previousData, updates) {
        this.changeHistory.push({
            timestamp: new Date().toISOString(),
            action,
            previousData: this.deepClone(previousData),
            updates: this.deepClone(updates),
            currentData: this.deepClone(this.userData)
        });

        // Limit history size
        if (this.changeHistory.length > 100) {
            this.changeHistory = this.changeHistory.slice(-50);
        }
    }

    /**
     * @brief Saves user data to persistent storage
     * @public
     * @returns {Promise<boolean>} Resolves with success status
     */
    async saveUserData() {
        try {
            if (this.configuration.storageKey && typeof window !== 'undefined' && window.localStorage) {
                localStorage.setItem(this.configuration.storageKey, JSON.stringify(this.userData));
                this.hasUnsavedChanges = false;
                console.debug('UserModel: User data saved to localStorage.');
                return true;
            }
            return false;
        } catch (error) {
            console.error('UserModel: Failed to save user data:', error);
            throw error;
        }
    }

    /**
     * @brief Resets user data to default values
     * @public
     * @param {boolean} confirm - Safety confirmation flag
     * @returns {Object} Reset user data
     * @throws {Error} When confirmation is not provided
     */
    resetUserData(confirm = false) {
        if (!confirm) {
            throw new Error('UserModel: Reset operation requires confirmation.');
        }

        const previousData = this.deepClone(this.userData);
        this.userData = this.deepClone(DEFAULT_USER_DATA);
        this.userData.metadata.lastUpdated = new Date().toISOString();
        this.userData.metadata.dataSource = 'reset';

        this.recordDataChange('reset', previousData, this.userData);
        this.clearCache();
        this.hasUnsavedChanges = true;

        console.info('UserModel: User data reset to defaults.');
        return this.getUserData();
    }

    /**
     * @brief Caches data for optimized retrieval
     * @private
     * @param {string} key - Cache key identifier
     * @param {*} data - Data to cache
     */
    cacheData(key, data) {
        if (!this.configuration.enableCaching) return;

        if (this.responseCache.size >= this.configuration.maxCacheSize) {
            const firstKey = this.responseCache.keys().next().value;
            this.responseCache.delete(firstKey);
        }

        const cacheEntry = {
            data: this.deepClone(data),
            timestamp: Date.now(),
            expires: Date.now() + this.configuration.cacheTimeout
        };

        this.responseCache.set(key, cacheEntry);
    }

    /**
     * @brief Retrieves cached data if valid
     * @private
     * @param {string} key - Cache key to retrieve
     * @returns {*|null} Cached data or null if expired/missing
     */
    getCachedData(key) {
        if (!this.configuration.enableCaching) return null;

        const cacheEntry = this.responseCache.get(key);
        if (!cacheEntry) return null;

        if (Date.now() > cacheEntry.expires) {
            this.responseCache.delete(key);
            return null;
        }

        return this.deepClone(cacheEntry.data);
    }

    /**
     * @brief Clears all cached data
     * @public
     * @returns {number} Number of items cleared from cache
     */
    clearCache() {
        const cacheSize = this.responseCache.size;
        this.responseCache.clear();
        console.debug(`UserModel: Cleared ${cacheSize} items from cache.`);
        return cacheSize;
    }

    /**
     * @brief Creates a deep clone of an object
     * @private
     * @param {*} obj - Object to clone
     * @returns {*} Deep cloned object
     */
    deepClone(obj) {
        if (obj === null || typeof obj !== 'object') return obj;
        if (obj instanceof Date) return new Date(obj.getTime());
        if (obj instanceof Array) return obj.map(item => this.deepClone(item));
        
        const clonedObj = {};
        Object.keys(obj).forEach(key => {
            clonedObj[key] = this.deepClone(obj[key]);
        });
        return clonedObj;
    }

    /**
     * @brief Generates ID from text for consistent identification
     * @private
     * @param {string} text - Text to generate ID from
     * @returns {string} Generated ID
     */
    generateIdFromText(text) {
        return text
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/(^-|-$)/g, '');
    }

    /**
     * @brief Gets user data change history
     * @public
     * @param {Object} options - History retrieval options
     * @param {number} options.limit - Maximum number of history entries to return
     * @returns {Array} Change history entries
     */
    getChangeHistory(options = {}) {
        const { limit = 10 } = options;
        return this.deepClone(this.changeHistory.slice(-limit));
    }

    /**
     * @brief Checks if there are unsaved changes
     * @public
     * @returns {boolean} True if there are unsaved changes
     */
    hasUnsavedChanges() {
        return this.hasUnsavedChanges;
    }

    /**
     * @brief Gets user data statistics
     * @public
     * @returns {Object} User data statistics
     */
    getUserDataStatistics() {
        return {
            personalInfo: {
                hasProfileImage: !!this.userData.personalInfo.profileImage?.url,
                languagesCount: this.userData.personalInfo.languages?.length || 0
            },
            contactInfo: {
                socialNetworksCount: this.userData.contactInfo.socialNetworks?.length || 0,
                websitesCount: this.userData.contactInfo.websites?.length || 0
            },
            academicBackground: {
                degreesCount: this.userData.academicBackground.degrees?.length || 0,
                certificationsCount: this.userData.academicBackground.certifications?.length || 0
            },
            lastUpdated: this.userData.metadata.lastUpdated,
            changeHistoryCount: this.changeHistory.length
        };
    }

    /**
     * @brief Exports user data for backup or transfer
     * @public
     * @param {Object} options - Export options
     * @param {boolean} options.includeSensitive - Whether to include sensitive data
     * @returns {string} JSON string of user data
     */
    exportUserData(options = {}) {
        const { includeSensitive = false } = options;
        const exportData = includeSensitive ? this.userData : this.filterSensitiveData(this.userData);
        
        return JSON.stringify(exportData, null, 2);
    }

    /**
     * @brief Imports user data from backup
     * @public
     * @param {string} jsonData - JSON string of user data to import
     * @param {boolean} confirm - Safety confirmation flag
     * @returns {Object} Imported user data
     * @throws {Error} When import fails or confirmation is missing
     */
    importUserData(jsonData, confirm = false) {
        if (!confirm) {
            throw new Error('UserModel: Import operation requires confirmation.');
        }

        if (!jsonData || typeof jsonData !== 'string') {
            throw new Error('UserModel: Import data must be a valid JSON string.');
        }

        try {
            const importedData = JSON.parse(jsonData);
            this.validateUserDataUpdates(importedData);
            
            return this.updateUserData(importedData, { validate: false });
        } catch (error) {
            console.error('UserModel: Failed to import user data:', error);
            throw new Error(`UserModel: Import failed - ${error.message}`);
        }
    }

    /**
     * @brief Updates configuration options
     * @public
     * @param {Object} newConfiguration - New configuration options
     */
    updateConfiguration(newConfiguration) {
        this.configuration = {
            ...this.configuration,
            ...newConfiguration
        };
        console.debug('UserModel: Configuration updated.', this.configuration);
    }

    /**
     * @brief Destroys the user model and cleans up resources
     * @public
     */
    destroy() {
        if (this.hasUnsavedChanges) {
            this.saveUserData().catch(console.error);
        }
        
        this.clearCache();
        this.changeHistory = [];
        console.info('UserModel: User model destroyed and resources cleaned up.');
    }
}

export default UserModel;