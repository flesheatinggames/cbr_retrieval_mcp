"""
Web Development Forms Validation Cases for CBR MCP Server

This module contains case-based reasoning examples for various form validation
approaches in web development, including client-side validation, server-side
validation, and type-safe schema validation using Zod.
"""

WEBDEV_FORMS_VALIDATION_CASES = [
{
 "problem": "A Bootstrap-styled form with client-side validation feedback in React.",
 "solution": """
import { useState } from 'react';
import { Form, Button, Col, Row, Alert } from 'react-bootstrap';

interface FormData {
firstName: string;
lastName: string;
email: string;
city: string;
state: string;
zip: string;
terms: boolean;
}

const ValidatedForm = () => {
const [validated, setValidated] = useState(false);
const [formData, setFormData] = useState<FormData>({
 firstName: '',
 lastName: '',
 email: '',
 city: '',
 state: '',
 zip: '',
 terms: false
});
const [submitSuccess, setSubmitSuccess] = useState(false);

const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
 const { name, value, type, checked } = e.target;
 setFormData(prev => ({
 ...prev,
 [name]: type === 'checkbox' ? checked : value
 }));
};

const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
 event.preventDefault();
 event.stopPropagation();

 const form = event.currentTarget;

 if (form.checkValidity() === false) {
 setValidated(true);
 return;
 }

 setValidated(true);

 try {
 console.log('Submitting:', formData);
 await new Promise(resolve => setTimeout(resolve, 1000));
 setSubmitSuccess(true);

 setTimeout(() => {
 setFormData({
 firstName: '',
 lastName: '',
 email: '',
 city: '',
 state: '',
 zip: '',
 terms: false
 });
 setValidated(false);
 setSubmitSuccess(false);
 }, 3000);
 } catch (error) {
 console.error('Form submission error:', error);
 }
};

return (
 <>
 {submitSuccess && (
 <Alert variant="success" dismissible onClose={() => setSubmitSuccess(false)}>
 Form submitted successfully!
 </Alert>
 )}

 <Form noValidate validated={validated} onSubmit={handleSubmit}>
 <Row className="mb-3">
 <Form.Group as={Col} md="4" controlId="validationCustom01">
  <Form.Label>First name</Form.Label>
  <Form.Control
  required
  type="text"
  name="firstName"
  placeholder="First name"
  value={formData.firstName}
  onChange={handleInputChange}
  />
  <Form.Control.Feedback type="valid">
  Looks good!
  </Form.Control.Feedback>
  <Form.Control.Feedback type="invalid">
  Please provide a valid first name.
  </Form.Control.Feedback>
 </Form.Group>

 <Form.Group as={Col} md="4" controlId="validationCustom02">
  <Form.Label>Last name</Form.Label>
  <Form.Control
  required
  type="text"
  name="lastName"
  placeholder="Last name"
  value={formData.lastName}
  onChange={handleInputChange}
  />
  <Form.Control.Feedback type="valid">
  Looks good!
  </Form.Control.Feedback>
  <Form.Control.Feedback type="invalid">
  Please provide a valid last name.
  </Form.Control.Feedback>
 </Form.Group>
 </Row>

 <Form.Group className="mb-3">
 <Form.Check
  required
  type="checkbox"
  name="terms"
  label="Agree to terms and conditions"
  checked={formData.terms}
  onChange={handleInputChange}
  feedback="You must agree before submitting."
  feedbackType="invalid"
 />
 </Form.Group>

 <Button type="submit">Submit form</Button>
 </Form>
 </>
);
};

export default ValidatedForm;
""",
 "category": "webdev",
 "subcategory": "forms-validation",
 "tags": ["forms", "validation", "client-side", "react", "bootstrap", "html5"]
},
{
 "problem": "Implement secure API key management and environment variable validation for production deployments.",
 "solution": """
// lib/config-validator.ts
import { z } from 'zod';
import crypto from 'crypto';

// Define environment schema
const envSchema = z.object({
// Node environment
NODE_ENV: z.enum(['development', 'test', 'production']),

// Server config
PORT: z.string().regex(/^\\d+$/).transform(Number).optional().default('3000'),
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
SMTP_PORT: z.string().regex(/^\\d+$/).transform(Number).optional(),
SMTP_USER: z.string().optional(),
SMTP_PASSWORD: z.string().optional(),

// API Keys (encrypted)
ENCRYPTED_API_KEYS: z.string().optional(),

// Security settings
ALLOWED_ORIGINS: z.string().transform((val) => val.split(',')),
RATE_LIMIT_MAX_REQUESTS: z.string().regex(/^\\d+$/).transform(Number).optional().default('100'),
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
 throw new Error('Custom validation failed:\\n' + errors.join('\\n'));
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
""",
 "category": "webdev",
 "subcategory": "forms-validation",
 "tags": ["validation", "zod", "schemas", "type-safe", "typescript", "environment", "configuration"]
},
{
 "problem": "Add server-side validation to the user registration endpoint for password strength.",
 "solution": """
<sequential-thinking>
This is a classic TDD case for modifying an existing endpoint.

1.  **Write Failing Tests:** Add new tests to the registration endpoint test suite that assert a 400 Bad Request is returned for weak passwords.
 -   Agent: tdd-test-engineer
 -   Verification: karen (verify the new tests fail as expected)
2.  **Implement Validation:** Add the password validation logic to the registration endpoint handler.
 -   Agent: rust-developer
 -   Verification: karen (verify all tests, including the new ones, now pass)
3.  **Security Audit:** Since this touches authentication, a security review is required.
 -   Agent: security-auditor (blocking)

This results in 5 delegation steps.
</sequential-thinking>
<TodoWrite>
[
{
 "content": "Delegate to tdd-test-engineer to write failing tests for password strength validation",
 "status": "pending",
 "activeForm": "Delegating to tdd-test-engineer to write failing tests"
},
{
 "content": "Delegate to karen to verify the new password tests fail correctly",
 "status": "pending",
 "activeForm": "Delegating to karen to verify failing tests"
},
{
 "content": "Delegate to rust-developer to implement the password strength validation logic",
 "status": "pending",
 "activeForm": "Delegating to rust-developer to implement validation"
},
{
 "content": "Delegate to karen to verify the validation implementation passes all tests",
 "status": "pending",
 "activeForm": "Delegating to karen to verify implementation"
},
{
 "content": "Delegate to security-auditor to audit the new password validation logic",
 "status": "pending",
 "activeForm": "Delegating to security-auditor for audit"
}
]
</TodoWrite>

## Plan for Password Validation

1.  **Write Failing Tests:** Delegate to **tdd-test-engineer** to add tests for the new validation rules.
2.  **Verify Failing Tests:** Delegate to **karen** to confirm the tests fail as expected.
3.  **Implement Validation:** Delegate to **rust-developer** to add the server-side logic.
4.  **Verify Implementation:** Delegate to **karen** to confirm all tests now pass.
5.  **Security Audit:** Delegate to **security-auditor** for a final security review.

Do you approve this plan?
""",
 "category": "webdev",
 "subcategory": "forms-validation",
 "tags": ["validation", "server-side", "backend", "api", "password", "security", "express"]
}
]
