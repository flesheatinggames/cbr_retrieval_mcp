"""
Security Validation Cases for CBR MCP Server

This module contains cases demonstrating secure validation techniques including:
- Input sanitization and SQL/NoSQL injection prevention
- Secure API key management and environment variable validation
- Production-ready security implementations for Next.js applications
"""

SECURITY_VALIDATION_CASES = [
    {
        "problem": "Implement input sanitization and SQL/NoSQL injection prevention for Firestore queries.",
        "solution": r"""
// lib/input-sanitizer.ts
import DOMPurify from 'isomorphic-dompurify';
import validator from 'validator';

interface SanitizationOptions {
  allowHTML?: boolean;
  maxLength?: number;
  allowedTags?: string[];
  allowedAttributes?: string[];
  stripScripts?: boolean;
  normalizeWhitespace?: boolean;
}

export class InputSanitizer {
  // Sanitize string input
  static sanitizeString(
  input: string,
  options: SanitizationOptions = {}
  ): string {
  const {
    allowHTML = false,
    maxLength = 10000,
    allowedTags = [],
    allowedAttributes = [],
    stripScripts = true,
    normalizeWhitespace = true
  } = options;

  if (typeof input !== 'string') {
    return '';
  }

  let sanitized = input;

  // Trim and limit length
  sanitized = sanitized.trim().substring(0, maxLength);

  // Remove null bytes
  sanitized = sanitized.replace(/\0/g, '');

  // Normalize whitespace
  if (normalizeWhitespace) {
    sanitized = sanitized.replace(/\s+/g, ' ');
  }

  // HTML sanitization
  if (allowHTML) {
    sanitized = DOMPurify.sanitize(sanitized, {
    ALLOWED_TAGS: allowedTags,
    ALLOWED_ATTR: allowedAttributes,
    KEEP_CONTENT: true,
    RETURN_DOM: false,
    RETURN_DOM_FRAGMENT: false,
    RETURN_DOM_IMPORT: false,
    SAFE_FOR_JQUERY: true
    });
  } else {
    // Strip all HTML tags
    sanitized = sanitized.replace(/<[^>]*>/g, '');

    // Escape special characters
    sanitized = validator.escape(sanitized);
  }

  // Remove dangerous patterns
  if (stripScripts) {
    // Remove script tags and event handlers
    sanitized = sanitized.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
    sanitized = sanitized.replace(/on\w+\s*=/gi, '');
    sanitized = sanitized.replace(/javascript:/gi, '');
    sanitized = sanitized.replace(/data:text\/html/gi, '');
  }

  // Remove Firestore/SQL injection patterns
  const dangerousPatterns = [
    /(\$|\.\.\/|\.\.\\)/g,  // Path traversal
    /[';]--/g,  // SQL comments
    /(\bOR\b|\bAND\b)\s*['"]=?['"]/gi,  // SQL injection
    /\bUNION\b.*\bSELECT\b/gi,  // SQL UNION
    /\bDROP\b.*\bTABLE\b/gi,  // SQL DROP
    /\bINSERT\b.*\bINTO\b/gi,  // SQL INSERT
    /\bDELETE\b.*\bFROM\b/gi,  // SQL DELETE
    /\bUPDATE\b.*\bSET\b/gi,  // SQL UPDATE
    /\/\*.*\*\//g,  // Multi-line comments
    /\{.*\$.*\}/g,  // Template literals
  ];

  dangerousPatterns.forEach(pattern => {
    sanitized = sanitized.replace(pattern, '');
  });

  return sanitized;
  }

  // Sanitize email
  static sanitizeEmail(email: string): string | null {
  const normalized = validator.normalizeEmail(email, {
    all_lowercase: true,
    gmail_remove_dots: true,
    gmail_remove_subaddress: false,
    outlookdotcom_remove_subaddress: false,
    yahoo_remove_subaddress: false,
    icloud_remove_subaddress: false
  });

  if (normalized && validator.isEmail(normalized)) {
    return normalized;
  }

  return null;
  }

  // Sanitize URL
  static sanitizeURL(url: string): string | null {
  if (!validator.isURL(url, {
    protocols: ['http', 'https'],
    require_protocol: true,
    require_valid_protocol: true,
    require_host: true,
    require_port: false,
    allow_protocol_relative_urls: false,
    allow_fragments: true,
    allow_query_components: true,
    validate_length: true
  })) {
    return null;
  }

  // Additional checks for dangerous URLs
  const dangerousPatterns = [
    /javascript:/i,
    /data:text\/html/i,
    /vbscript:/i,
    /file:\/\//i,
    /about:blank/i
  ];

  for (const pattern of dangerousPatterns) {
    if (pattern.test(url)) {
    return null;
    }
  }

  return validator.trim(url);
  }

  // Sanitize phone number
  static sanitizePhoneNumber(phone: string, locale = 'en-US'): string | null {
  // Remove all non-numeric characters except + for international
  const cleaned = phone.replace(/[^\d+]/g, '');

  if (validator.isMobilePhone(cleaned, 'any')) {
    return cleaned;
  }

  return null;
  }

  // Sanitize numeric input
  static sanitizeNumber(input: any, options: {
  min?: number;
  max?: number;
  isFloat?: boolean;
  decimals?: number;
  } = {}): number | null {
  const {
    min = -Infinity,
    max = Infinity,
    isFloat = false,
    decimals = 2
  } = options;

  const num = isFloat ? parseFloat(input) : parseInt(input, 10);

  if (isNaN(num)) {
    return null;
  }

  if (num < min || num > max) {
    return null;
  }

  if (isFloat && decimals !== undefined) {
    return Math.round(num * Math.pow(10, decimals)) / Math.pow(10, decimals);
  }

  return num;
  }

  // Sanitize array input
  static sanitizeArray<T>(
  input: any[],
  itemSanitizer: (item: any) => T | null,
  options: {
    maxLength?: number;
    unique?: boolean;
  } = {}
  ): T[] {
  const {
    maxLength = 1000,
    unique = false
  } = options;

  if (!Array.isArray(input)) {
    return [];
  }

  let sanitized = input
    .slice(0, maxLength)
    .map(itemSanitizer)
    .filter(item => item !== null) as T[];

  if (unique) {
    sanitized = [...new Set(sanitized)];
  }

  return sanitized;
  }

  // Sanitize object/JSON input
  static sanitizeObject(
  input: any,
  schema: { [key: string]: (value: any) => any }
  ): { [key: string]: any } {
  if (typeof input !== 'object' || input === null) {
    return {};
  }

  const sanitized: { [key: string]: any } = {};

  for (const [key, sanitizer] of Object.entries(schema)) {
    if (key in input) {
    const value = sanitizer(input[key]);
    if (value !== null && value !== undefined) {
      sanitized[key] = value;
    }
    }
  }

  return sanitized;
  }
}

// Firestore query builder with injection prevention
export class SecureFirestoreQuery {
  private db: any;

  constructor(db: any) {
  this.db = db;
  }

  // Build secure where clause
  buildWhereClause(
  field: string,
  operator: any,
  value: any
  ): any {
  // Validate field name (prevent injection via field names)
  if (!this.isValidFieldName(field)) {
    throw new Error('Invalid field name');
  }

  // Validate operator
  const validOperators = ['==', '!=', '<', '<=', '>', '>=', 'array-contains', 'in', 'array-contains-any'];
  if (!validOperators.includes(operator)) {
    throw new Error('Invalid operator');
  }

  // Sanitize value based on type
  const sanitizedValue = this.sanitizeQueryValue(value);

  return { field, operator, value: sanitizedValue };
  }

  // Validate field name to prevent injection
  private isValidFieldName(field: string): boolean {
  // Field name should only contain alphanumeric, dots, and underscores
  const pattern = /^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$/;

  // Check length
  if (field.length > 100) {
    return false;
  }

  // Check pattern
  if (!pattern.test(field)) {
    return false;
  }

  // Prevent special Firestore fields that could be dangerous
  const dangerousFields = ['__name__', '__proto__', 'constructor', 'prototype'];
  if (dangerousFields.includes(field.toLowerCase())) {
    return false;
  }

  return true;
  }

  // Sanitize query values
  private sanitizeQueryValue(value: any): any {
  if (value === null || value === undefined) {
    return value;
  }

  if (typeof value === 'string') {
    return InputSanitizer.sanitizeString(value, {
    allowHTML: false,
    maxLength: 1000
    });
  }

  if (typeof value === 'number') {
    return InputSanitizer.sanitizeNumber(value, {
    min: -Number.MAX_SAFE_INTEGER,
    max: Number.MAX_SAFE_INTEGER
    });
  }

  if (typeof value === 'boolean') {
    return value;
  }

  if (Array.isArray(value)) {
    return InputSanitizer.sanitizeArray(
    value,
    (item) => this.sanitizeQueryValue(item),
    { maxLength: 100 }
    );
  }

  if (value instanceof Date) {
    return value;
  }

  if (typeof value === 'object') {
    // Don't allow complex objects in queries
    throw new Error('Complex objects not allowed in queries');
  }

  return null;
  }

  // Execute secure query
  async executeQuery(
  collection: string,
  conditions: Array<{ field: string; operator: string; value: any }>,
  options: {
    orderBy?: { field: string; direction: 'asc' | 'desc' };
    limit?: number;
    startAfter?: any;
  } = {}
  ): Promise<any[]> {
  // Validate collection name
  if (!this.isValidFieldName(collection)) {
    throw new Error('Invalid collection name');
  }

  let query = this.db.collection(collection);

  // Apply where conditions
  for (const condition of conditions) {
    const sanitized = this.buildWhereClause(
    condition.field,
    condition.operator,
    condition.value
    );
    query = query.where(sanitized.field, sanitized.operator, sanitized.value);
  }

  // Apply ordering
  if (options.orderBy) {
    if (!this.isValidFieldName(options.orderBy.field)) {
    throw new Error('Invalid orderBy field');
    }
    query = query.orderBy(options.orderBy.field, options.orderBy.direction);
  }

  // Apply pagination
  if (options.limit) {
    const sanitizedLimit = InputSanitizer.sanitizeNumber(options.limit, {
    min: 1,
    max: 1000
    });
    if (sanitizedLimit) {
    query = query.limit(sanitizedLimit);
    }
  }

  if (options.startAfter) {
    query = query.startAfter(options.startAfter);
  }

  const snapshot = await query.get();
  return snapshot.docs.map((doc: any) => ({
    id: doc.id,
    ...doc.data()
  }));
  }
}

// Usage example in API route
export async function handleUserInput(req: any, db: any) {
  const sanitizer = new InputSanitizer();
  const queryBuilder = new SecureFirestoreQuery(db);

  // Sanitize all inputs
  const sanitizedData = InputSanitizer.sanitizeObject(req.body, {
  name: (v) => InputSanitizer.sanitizeString(v, { maxLength: 100 }),
  email: (v) => InputSanitizer.sanitizeEmail(v),
  age: (v) => InputSanitizer.sanitizeNumber(v, { min: 0, max: 150 }),
  website: (v) => InputSanitizer.sanitizeURL(v),
  phone: (v) => InputSanitizer.sanitizePhoneNumber(v),
  bio: (v) => InputSanitizer.sanitizeString(v, {
    maxLength: 500,
    allowHTML: false
  }),
  tags: (v) => InputSanitizer.sanitizeArray(
    v,
    (tag) => InputSanitizer.sanitizeString(tag, { maxLength: 50 }),
    { maxLength: 10, unique: true }
  )
  });

  // Use sanitized data for Firestore operations
  await db.collection('users').add({
  ...sanitizedData,
  createdAt: new Date()
  });

  return sanitizedData;
}
""",
        "category": "security",
        "subcategory": "validation",
        "tags": [
            "validation",
            "sanitization",
            "input",
            "sql-injection",
            "xss",
            "firestore",
            "security",
        ],
    },
    {
        "problem": "Implement secure API key management and environment variable validation for production deployments.",
        "solution": r"""
// lib/config-validator.ts
import { z } from 'zod';
import crypto from 'crypto';

// Define environment schema
const envSchema = z.object({
  // Node environment
  NODE_ENV: z.enum(['development', 'test', 'production']),

  // Server config
  PORT: z.string().regex(/^\d+$/).transform(Number).optional().default('3000'),
  HOST: z.string().optional().default('localhost'),

  // Firebase config
  FIREBASE_PROJECT_ID: z.string().min(1),
  FIREBASE_CLIENT_EMAIL: z.string().email(),
  FIREBASE_PRIVATE_KEY: z.string().min(100),
  FIREBASE_DATABASE_URL: z.string().url().optional(),
  FIREBASE_STORAGE_BUCKET: z.string().optional(),

  // Firebase client config
  NEXT_PUBLIC_FIREBASE_API_KEY: z.string().min(20),
  NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: z.string().min(10),
  NEXT_PUBLIC_FIREBASE_PROJECT_ID: z.string().min(1),
  NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET: z.string().optional(),
  NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID: z.string().optional(),
  NEXT_PUBLIC_FIREBASE_APP_ID: z.string().min(20),
  NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID: z.string().optional(),

  // Security keys
  JWT_ACCESS_SECRET: z.string().min(32),
  JWT_REFRESH_SECRET: z.string().min(32),
  ENCRYPTION_KEY: z.string().length(64),  // 32 bytes in hex

  // Database
  DATABASE_URL: z.string().url().optional(),
  REDIS_URL: z.string().url().optional(),

  // External services
  SMTP_HOST: z.string().optional(),
  SMTP_PORT: z.string().regex(/^\d+$/).transform(Number).optional(),
  SMTP_USER: z.string().optional(),
  SMTP_PASSWORD: z.string().optional(),

  // API Keys (encrypted)
  ENCRYPTED_API_KEYS: z.string().optional(),

  // Security settings
  ALLOWED_ORIGINS: z.string().transform((val) => val.split(',')),
  RATE_LIMIT_MAX_REQUESTS: z.string().regex(/^\d+$/).transform(Number).optional().default('100'),
  SESSION_SECRET: z.string().min(32),
  COOKIE_SECURE: z.string().transform((val) => val === 'true').optional().default('true'),

  // Feature flags
  ENABLE_ANALYTICS: z.string().transform((val) => val === 'true').optional().default('false'),
  ENABLE_SENTRY: z.string().transform((val) => val === 'true').optional().default('false'),
  SENTRY_DSN: z.string().url().optional(),
});

type EnvConfig = z.infer<typeof envSchema>;

// Encrypted API key storage
class SecureApiKeyManager {
  private encryptionKey: Buffer;
  private algorithm = 'aes-256-gcm';

  constructor(encryptionKey: string) {
  this.encryptionKey = Buffer.from(encryptionKey, 'hex');
  }

  // Encrypt API key
  encrypt(apiKey: string): string {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv(this.algorithm, this.encryptionKey, iv);

  let encrypted = cipher.update(apiKey, 'utf8', 'hex');
  encrypted += cipher.final('hex');

  const authTag = cipher.getAuthTag();

  return iv.toString('hex') + ':' + authTag.toString('hex') + ':' + encrypted;
  }

  // Decrypt API key
  decrypt(encryptedData: string): string {
  const parts = encryptedData.split(':');
  const iv = Buffer.from(parts[0], 'hex');
  const authTag = Buffer.from(parts[1], 'hex');
  const encrypted = parts[2];

  const decipher = crypto.createDecipheriv(this.algorithm, this.encryptionKey, iv);
  decipher.setAuthTag(authTag);

  let decrypted = decipher.update(encrypted, 'hex', 'utf8');
  decrypted += decipher.final('utf8');

  return decrypted;
  }

  // Store multiple API keys
  storeApiKeys(keys: { [service: string]: string }): string {
  const encrypted: { [service: string]: string } = {};

  for (const [service, key] of Object.entries(keys)) {
    encrypted[service] = this.encrypt(key);
  }

  return JSON.stringify(encrypted);
  }

  // Retrieve API key
  getApiKey(encryptedKeys: string, service: string): string | null {
  try {
    const keys = JSON.parse(encryptedKeys);
    if (keys[service]) {
    return this.decrypt(keys[service]);
    }
    return null;
  } catch (error) {
    console.error('Failed to retrieve API key:', error);
    return null;
  }
  }
}

// Configuration validator and loader
export class ConfigValidator {
  private static instance: ConfigValidator;
  private config: EnvConfig | null = null;
  private apiKeyManager: SecureApiKeyManager | null = null;
  private validationErrors: string[] = [];

  private constructor() {}

  static getInstance(): ConfigValidator {
  if (!ConfigValidator.instance) {
    ConfigValidator.instance = new ConfigValidator();
  }
  return ConfigValidator.instance;
  }

  // Validate and load configuration
  load(): EnvConfig {
  if (this.config) {
    return this.config;
  }

  try {
    // Parse environment variables
    const parsed = envSchema.parse(process.env);

    // Additional custom validations
    this.validateCustomRules(parsed);

    // Initialize API key manager
    this.apiKeyManager = new SecureApiKeyManager(parsed.ENCRYPTION_KEY);

    // Store config
    this.config = parsed;

    // Log successful validation (without sensitive data)
    console.log('✅ Environment configuration validated successfully');
    console.log('Environment:', parsed.NODE_ENV);
    console.log('Port:', parsed.PORT);
    console.log('Allowed Origins:', parsed.ALLOWED_ORIGINS);

    return this.config;
  } catch (error) {
    if (error instanceof z.ZodError) {
    this.validationErrors = error.errors.map(err =>
      `${err.path.join('.')}: ${err.message}`
    );

    console.error('❌ Environment validation failed:');
    this.validationErrors.forEach(err => console.error(`  - ${err}`));

    // In production, fail fast
    if (process.env.NODE_ENV === 'production') {
      process.exit(1);
    }
    }
    throw error;
  }
  }

  // Custom validation rules
  private validateCustomRules(config: EnvConfig): void {
  const errors: string[] = [];

  // Ensure Firebase private key is properly formatted
  if (!config.FIREBASE_PRIVATE_KEY.includes('BEGIN PRIVATE KEY')) {
    errors.push('FIREBASE_PRIVATE_KEY must be a valid private key');
  }

  // Ensure strong secrets in production
  if (config.NODE_ENV === 'production') {
    if (config.JWT_ACCESS_SECRET.length < 64) {
    errors.push('JWT_ACCESS_SECRET must be at least 64 characters in production');
    }

    if (config.JWT_REFRESH_SECRET === config.JWT_ACCESS_SECRET) {
    errors.push('JWT_REFRESH_SECRET must be different from JWT_ACCESS_SECRET');
    }

    if (!config.COOKIE_SECURE) {
    errors.push('COOKIE_SECURE must be true in production');
    }

    if (config.ALLOWED_ORIGINS.includes('*')) {
    errors.push('ALLOWED_ORIGINS cannot contain wildcard in production');
    }
  }

  // Validate URLs
  if (config.DATABASE_URL && !config.DATABASE_URL.startsWith('postgresql://') &&
    !config.DATABASE_URL.startsWith('mysql://')) {
    errors.push('DATABASE_URL must be a valid database connection string');
  }

  if (errors.length > 0) {
    this.validationErrors.push(...errors);
    throw new Error('Custom validation failed:\n' + errors.join('\n'));
  }
  }

  // Get configuration value
  get<K extends keyof EnvConfig>(key: K): EnvConfig[K] {
  if (!this.config) {
    this.load();
  }
  return this.config![key];
  }

  // Get decrypted API key
  getApiKey(service: string): string | null {
  if (!this.apiKeyManager) {
    return null;
  }

  const encryptedKeys = this.get('ENCRYPTED_API_KEYS');
  if (!encryptedKeys) {
    return null;
  }

  return this.apiKeyManager.getApiKey(encryptedKeys, service);
  }

  // Check if running in production
  isProduction(): boolean {
  return this.get('NODE_ENV') === 'production';
  }

  // Get validation errors
  getValidationErrors(): string[] {
  return this.validationErrors;
  }
}

// Create singleton instance
export const config = ConfigValidator.getInstance();

// .env.example file generator
export function generateEnvExample(): void {
  const examples: { [key: string]: string } = {
  NODE_ENV: 'development',
  PORT: '3000',
  HOST: 'localhost',

  // Firebase Admin
  FIREBASE_PROJECT_ID: 'your-project-id',
  FIREBASE_CLIENT_EMAIL: 'firebase-adminsdk@your-project.iam.gserviceaccount.com',
  FIREBASE_PRIVATE_KEY: '-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----',

  // Firebase Client
  NEXT_PUBLIC_FIREBASE_API_KEY: 'your-api-key',
  NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: 'your-project.firebaseapp.com',
  NEXT_PUBLIC_FIREBASE_PROJECT_ID: 'your-project-id',
  NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET: 'your-project.appspot.com',
  NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID: '123456789',
  NEXT_PUBLIC_FIREBASE_APP_ID: 'your-app-id',

  // Security (generate with: openssl rand -hex 32)
  JWT_ACCESS_SECRET: crypto.randomBytes(32).toString('hex'),
  JWT_REFRESH_SECRET: crypto.randomBytes(32).toString('hex'),
  ENCRYPTION_KEY: crypto.randomBytes(32).toString('hex'),
  SESSION_SECRET: crypto.randomBytes(32).toString('hex'),

  // Allowed origins
  ALLOWED_ORIGINS: 'http://localhost:3000,https://yourdomain.com',

  // Rate limiting
  RATE_LIMIT_MAX_REQUESTS: '100',

  // Features
  ENABLE_ANALYTICS: 'false',
  ENABLE_SENTRY: 'false',
  COOKIE_SECURE: 'true',
  };

  const content = Object.entries(examples)
  .map(([key, value]) => `${key}="${value}"`)
  .join('\n');

  console.log('# Environment Variables Example\n');
  console.log(content);
}

// Usage in your app
// app/layout.tsx or pages/_app.tsx
import { config } from '@/lib/config-validator';

// Load and validate config at startup
try {
  config.load();
} catch (error) {
  console.error('Failed to load configuration:', error);
  // Handle error appropriately
}

// Use throughout your app
const apiKey = config.getApiKey('stripe');
const isProduction = config.isProduction();
const allowedOrigins = config.get('ALLOWED_ORIGINS');
""",
        "category": "security",
        "subcategory": "validation",
        "tags": [
            "validation",
            "environment",
            "api-keys",
            "configuration",
            "security",
            "zod",
            "encryption",
        ],
    },
]
