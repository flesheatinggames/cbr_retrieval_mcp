"""
Web Development Deployment Cases for CBR MCP Server

This module contains deployment-related case examples for web development,
including Vercel deployment configuration and environment variable management
for production deployments.

Examples:
- Vercel deployment configuration (vercel.json, build settings, routing)
- Environment variable validation and API key management for production
"""

WEBDEV_DEPLOYMENT_CASES = [
    {
        "problem": "Configure Vercel deployment with custom build settings, environment variables, and routing rules for a Next.js application.",
        "solution": """
// vercel.json - Vercel deployment configuration
{
  "version": 2,
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "regions": ["iad1"],

  "build": {
    "env": {
      "NEXT_PUBLIC_API_URL": "@api-url",
      "NEXT_PUBLIC_ANALYTICS_ID": "@analytics-id"
    }
  },

  "env": {
    "DATABASE_URL": "@database-url",
    "REDIS_URL": "@redis-url",
    "JWT_SECRET": "@jwt-secret",
    "STRIPE_SECRET_KEY": "@stripe-secret",
    "SENDGRID_API_KEY": "@sendgrid-key"
  },

  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "s-maxage=0" },
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-XSS-Protection", "value": "1; mode=block" }
      ]
    },
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-DNS-Prefetch-Control", "value": "on" },
        { "key": "Strict-Transport-Security", "value": "max-age=31536000; includeSubDomains" }
      ]
    }
  ],

  "rewrites": [
    { "source": "/api/:path*", "destination": "/api/:path*" },
    { "source": "/admin/:path*", "destination": "/admin/:path*" }
  ],

  "redirects": [
    {
      "source": "/old-blog/:slug",
      "destination": "/blog/:slug",
      "permanent": true
    }
  ],

  "functions": {
    "api/**/*.ts": {
      "memory": 1024,
      "maxDuration": 10
    }
  },

  "crons": [
    {
      "path": "/api/cron/cleanup",
      "schedule": "0 0 * * *"
    },
    {
      "path": "/api/cron/backup",
      "schedule": "0 2 * * *"
    }
  ]
}

// next.config.js - Next.js build configuration
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,

  // Output configuration
  output: 'standalone',

  // Image optimization
  images: {
    domains: ['firebasestorage.googleapis.com', 'cdn.yourdomain.com'],
    formats: ['image/avif', 'image/webp'],
  },

  // Environment variables available to the browser
  env: {
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL,
  },

  // Security headers
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
          },
        ],
      },
    ];
  },

  // Redirects
  async redirects() {
    return [
      {
        source: '/home',
        destination: '/',
        permanent: true,
      },
    ];
  },

  // Build optimization
  webpack: (config, { dev, isServer }) => {
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          default: false,
          vendors: false,
          commons: {
            name: 'commons',
            chunks: 'all',
            minChunks: 2,
          },
        },
      };
    }
    return config;
  },
};

module.exports = nextConfig;

// .env.production.example - Production environment template
NODE_ENV=production
NEXT_PUBLIC_APP_URL=https://yourdomain.com
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@host:5432/database

# Redis
REDIS_URL=redis://default:password@host:6379

# Authentication
JWT_SECRET=your-secret-key-min-32-chars
SESSION_SECRET=your-session-secret

# Firebase
FIREBASE_PROJECT_ID=your-project
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk@project.iam.gserviceaccount.com

# API Keys (stored as Vercel secrets)
STRIPE_SECRET_KEY=sk_live_...
SENDGRID_API_KEY=SG....

# Feature Flags
ENABLE_ANALYTICS=true
ENABLE_SENTRY=true

# Deployment script
#!/bin/bash
# deploy.sh - Automated deployment to Vercel

echo "🚀 Starting deployment to Vercel..."

# Check if logged in to Vercel
if ! vercel whoami &> /dev/null; then
    echo "❌ Not logged in to Vercel. Run 'vercel login' first."
    exit 1
fi

# Run tests
echo "🧪 Running tests..."
npm run test || { echo "❌ Tests failed"; exit 1; }

# Build locally to verify
echo "🔨 Building locally..."
npm run build || { echo "❌ Build failed"; exit 1; }

# Deploy to preview
echo "📦 Deploying to preview..."
vercel --prod=false

# If production deployment requested
if [ "$1" = "--production" ]; then
    echo "🌐 Deploying to production..."
    vercel --prod
fi

echo "✅ Deployment complete!"
""",
        "category": "webdev",
        "subcategory": "deployment",
        "tags": ["vercel", "deployment", "nextjs", "production", "config", "build", "environment", "ci-cd", "hosting"]
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

// .env.example file generator
export function generateEnvExample(): void {
  const examples: { [key: string]: string } = {
    NODE_ENV: 'development',
    PORT: '3000',
    HOST: 'localhost',

    // Firebase Admin
    FIREBASE_PROJECT_ID: 'your-project-id',
    FIREBASE_CLIENT_EMAIL: 'firebase-adminsdk@your-project.iam.gserviceaccount.com',
    FIREBASE_PRIVATE_KEY: '-----BEGIN PRIVATE KEY-----\\nYOUR_PRIVATE_KEY\\n-----END PRIVATE KEY-----',

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
    .join('\\n');

  console.log('# Environment Variables Example\\n');
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
        "category": "webdev",
        "subcategory": "deployment",
        "tags": ["environment", "env", "config", "validation", "production", "api-keys", "secrets", "zod", "typescript", "deployment"]
    }
]
