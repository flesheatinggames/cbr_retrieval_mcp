"""
Next.js API Cases for CBR MCP Server

Contains cases for Next.js API routes, server actions, and edge functions.
"""

NEXTJS_API_CASES = [
    {
        "problem": """
A Next.js API route that handles a POST request.
""",
        "solution": r"""
// pages/api/contact.js (Pages Router)
import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  // Set CORS headers if needed
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Handle preflight request
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method === 'POST') {
    try {
      const { name, email, message } = req.body;

      // Validate input
      if (!name || !email || !message) {
        return res.status(400).json({
          error: 'Missing required fields',
          fields: {
            name: !name ? 'Name is required' : null,
            email: !email ? 'Email is required' : null,
            message: !message ? 'Message is required' : null,
          }
        });
      }

      // Validate email format
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        return res.status(400).json({
          error: 'Invalid email format'
        });
      }

      // Process the form data (e.g., send email, save to DB)
      console.log('Contact form submission:', { name, email, message });

      // Here you would typically:
      // - Save to database
      // - Send email notification
      // - Integrate with CRM

      res.status(200).json({
        status: 'success',
        message: 'Form submitted successfully'
      });
    } catch (error) {
      console.error('Contact form error:', error);
      res.status(500).json({
        error: 'Internal server error'
      });
    }
  } else {
    res.setHeader('Allow', ['POST', 'OPTIONS']);
    res.status(405).json({
      error: `Method ${req.method} not allowed`
    });
  }
}
""",
        "category": "nextjs",
        "subcategory": "api",
        "tags": ["nextjs", "api", "api-routes", "post", "request", "response"],
    },
    {
        "problem": """
A Next.js API route to add a document to Firestore using the Firebase Admin SDK.
""",
        "solution": r"""
import type { NextApiRequest, NextApiResponse } from 'next';
import { adminDb } from '../../../lib/firebase-admin';
import * as yup from 'yup';

const postSchema = yup.object({
  title: yup.string().required().min(3).max(200),
  content: yup.string().required().min(10).max(10000),
  tags: yup.array().of(yup.string()).max(5),
  published: yup.boolean().default(false),
  category: yup.string().oneOf(['tech', 'lifestyle', 'business', 'other']).required()
});

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', ['POST']);
    return res.status(405).json({ error: `Method ${req.method} not allowed` });
  }

  try {
    // Validate request body
    let validatedData;
    try {
      validatedData = await postSchema.validate(req.body);
    } catch (validationError: any) {
      return res.status(400).json({
        error: 'Validation failed',
        details: validationError.errors
      });
    }

    // Check for duplicate title
    const existingPost = await adminDb
      .collection('posts')
      .where('title', '==', validatedData.title)
      .limit(1)
      .get();

    if (!existingPost.empty) {
      return res.status(409).json({
        error: 'A post with this title already exists'
      });
    }

    // Create post document
    const postData = {
      ...validatedData,
      createdAt: adminDb.FieldValue.serverTimestamp(),
      updatedAt: adminDb.FieldValue.serverTimestamp(),
      views: 0,
      likes: 0
    };

    const docRef = await adminDb.collection('posts').add(postData);

    res.status(201).json({
      success: true,
      id: docRef.id,
      message: 'Post created successfully'
    });
  } catch (error) {
    console.error('Error creating post:', error);
    res.status(500).json({
      error: 'Failed to create post'
    });
  }
}
""",
        "category": "nextjs",
        "subcategory": "api",
        "tags": ["nextjs", "api", "firestore", "firebase", "admin-sdk"],
    },
    {
        "problem": """
Implement rate limiting and DDoS protection for Next.js API routes with Redis.
""",
        "solution": r"""
// lib/rate-limiter.ts
import { NextApiRequest, NextApiResponse } from 'next';
import { Redis } from 'ioredis';
import crypto from 'crypto';

// Initialize Redis client (use environment variable for production)
const redis = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: parseInt(process.env.REDIS_PORT || '6379'),
  password: process.env.REDIS_PASSWORD,
  maxRetriesPerRequest: 3,
  retryStrategy: (times) => Math.min(times * 50, 2000)
});

interface RateLimitConfig {
  windowMs?: number;  // Time window in milliseconds
  maxRequests?: number;  // Max requests per window
  skipSuccessfulRequests?: boolean;  // Don't count successful requests
  skipFailedRequests?: boolean;  // Don't count failed requests
  keyGenerator?: (req: NextApiRequest) => string;  // Custom key generator
  handler?: (req: NextApiRequest, res: NextApiResponse) => void;  // Custom rejection handler
  skip?: (req: NextApiRequest) => boolean;  // Skip certain requests
  blockDuration?: number;  // How long to block after limit exceeded (ms)
}

class RateLimiter {
  private config: Required<RateLimitConfig>;

  constructor(config: RateLimitConfig = {}) {
    this.config = {
      windowMs: config.windowMs || 60 * 1000, // 1 minute default
      maxRequests: config.maxRequests || 100, // 100 requests per minute default
      skipSuccessfulRequests: config.skipSuccessfulRequests || false,
      skipFailedRequests: config.skipFailedRequests || false,
      keyGenerator: config.keyGenerator || this.defaultKeyGenerator,
      handler: config.handler || this.defaultHandler,
      skip: config.skip || (() => false),
      blockDuration: config.blockDuration || 60 * 60 * 1000 // 1 hour block default
    };
  }

  private defaultKeyGenerator(req: NextApiRequest): string {
    // Generate key based on IP address and optionally user ID
    const ip = this.getClientIp(req);
    const userId = (req as any).userId || 'anonymous';
    const endpoint = req.url?.split('?')[0] || 'unknown';

    return `rate_limit:${endpoint}:${ip}:${userId}`;
  }

  private getClientIp(req: NextApiRequest): string {
    // Get real IP address considering proxies
    const forwarded = req.headers['x-forwarded-for'];
    const ip = typeof forwarded === 'string'
      ? forwarded.split(',')[0].trim()
      : req.socket.remoteAddress || 'unknown';

    // Hash IP for privacy
    return crypto.createHash('sha256').update(ip).digest('hex').substring(0, 16);
  }

  private defaultHandler(req: NextApiRequest, res: NextApiResponse): void {
    res.status(429).json({
      error: 'Too Many Requests',
      message: 'You have exceeded the rate limit. Please try again later.',
      retryAfter: this.config.windowMs / 1000 // in seconds
    });
  }

  async middleware(
    req: NextApiRequest,
    res: NextApiResponse,
    next: () => void
  ): Promise<void> {
    // Skip if configured
    if (this.config.skip(req)) {
      return next();
    }

    const key = this.config.keyGenerator(req);
    const blockKey = `${key}:blocked`;

    try {
      // Check if IP is blocked
      const isBlocked = await redis.get(blockKey);
      if (isBlocked) {
        const ttl = await redis.ttl(blockKey);
        res.setHeader('Retry-After', String(ttl));
        res.setHeader('X-RateLimit-Limit', String(this.config.maxRequests));
        res.setHeader('X-RateLimit-Remaining', '0');
        res.setHeader('X-RateLimit-Reset', new Date(Date.now() + ttl * 1000).toISOString());

        return this.config.handler(req, res);
      }

      // Get current request count
      const current = await redis.incr(key);

      // Set expiry on first request
      if (current === 1) {
        await redis.pexpire(key, this.config.windowMs);
      }

      // Get remaining TTL
      const ttl = await redis.pttl(key);
      const resetTime = Date.now() + (ttl > 0 ? ttl : this.config.windowMs);

      // Set rate limit headers
      res.setHeader('X-RateLimit-Limit', String(this.config.maxRequests));
      res.setHeader('X-RateLimit-Remaining', String(Math.max(0, this.config.maxRequests - current)));
      res.setHeader('X-RateLimit-Reset', new Date(resetTime).toISOString());

      // Check if limit exceeded
      if (current > this.config.maxRequests) {
        // Block the user for specified duration
        await redis.setex(blockKey, this.config.blockDuration / 1000, '1');

        res.setHeader('Retry-After', String(this.config.blockDuration / 1000));
        return this.config.handler(req, res);
      }

      // Continue to next middleware
      next();
    } catch (error) {
      console.error('Rate limiter error:', error);
      // Fail open - allow request if Redis is down
      next();
    }
  }
}

// Create different rate limiters for different endpoints
export const apiRateLimiter = new RateLimiter({
  windowMs: 60 * 1000, // 1 minute
  maxRequests: 100 // 100 requests per minute
});

export const authRateLimiter = new RateLimiter({
  windowMs: 15 * 60 * 1000, // 15 minutes
  maxRequests: 5, // 5 attempts per 15 minutes
  blockDuration: 24 * 60 * 60 * 1000 // Block for 24 hours after limit exceeded
});

export const uploadRateLimiter = new RateLimiter({
  windowMs: 60 * 60 * 1000, // 1 hour
  maxRequests: 20 // 20 uploads per hour
});

// DDoS protection with distributed rate limiting
export class DDoSProtection {
  private static instance: DDoSProtection;
  private blacklist: Set<string> = new Set();
  private suspiciousActivity: Map<string, number> = new Map();

  private constructor() {
    // Clean up old entries every hour
    setInterval(() => {
      this.suspiciousActivity.clear();
    }, 60 * 60 * 1000);
  }

  static getInstance(): DDoSProtection {
    if (!DDoSProtection.instance) {
      DDoSProtection.instance = new DDoSProtection();
    }
    return DDoSProtection.instance;
  }

  async checkRequest(req: NextApiRequest): Promise<boolean> {
    const ip = this.getClientIp(req);

    // Check blacklist
    if (this.blacklist.has(ip)) {
      return false;
    }

    // Check for suspicious patterns
    const suspicious = await this.detectSuspiciousActivity(req);
    if (suspicious) {
      const count = (this.suspiciousActivity.get(ip) || 0) + 1;
      this.suspiciousActivity.set(ip, count);

      // Auto-blacklist after 10 suspicious activities
      if (count >= 10) {
        this.blacklist.add(ip);
        console.warn(`IP ${ip} blacklisted for suspicious activity`);
        return false;
      }
    }

    return true;
  }

  private async detectSuspiciousActivity(req: NextApiRequest): Promise<boolean> {
    // Check for common attack patterns
    const url = req.url || '';
    const userAgent = req.headers['user-agent'] || '';

    const suspiciousPatterns = [
      /\.\.\//, // Directory traversal
      /<script/i, // XSS attempt
      /union.*select/i, // SQL injection
      /eval\(/i, // Code injection
      /base64_decode/i, // Encoded payload
      //, // Null byte injection
      /%00/, // Null byte (URL encoded)
      /\.env/, // Environment file access
      /\/etc\/passwd/, // System file access
    ];

    for (const pattern of suspiciousPatterns) {
      if (pattern.test(url) || pattern.test(userAgent)) {
        return true;
      }
    }

    // Check for bot patterns
    const botPatterns = [
      /bot/i,
      /crawler/i,
      /spider/i,
      /scraper/i,
      /curl/i,
      /wget/i,
      /python/i,
      /java/i,
    ];

    const isBot = botPatterns.some(pattern => pattern.test(userAgent));
    const hasNoReferer = !req.headers.referer && req.method === 'POST';
    const hasWeirdHeaders = !userAgent || userAgent.length < 10;

    return isBot || hasNoReferer || hasWeirdHeaders;
  }

  private getClientIp(req: NextApiRequest): string {
    const forwarded = req.headers['x-forwarded-for'];
    return typeof forwarded === 'string'
      ? forwarded.split(',')[0].trim()
      : req.socket.remoteAddress || 'unknown';
  }
}

// Usage in API route
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // DDoS protection
  const ddosProtection = DDoSProtection.getInstance();
  const isAllowed = await ddosProtection.checkRequest(req);

  if (!isAllowed) {
    return res.status(403).json({ error: 'Forbidden' });
  }

  // Apply rate limiting
  await new Promise<void>((resolve) => {
    apiRateLimiter.middleware(req, res, resolve);
  });

  // Your API logic here
  res.status(200).json({ message: 'Success' });
}
""",
        "category": "nextjs",
        "subcategory": "api",
        "tags": ["nextjs", "api", "rate-limiting", "security", "redis", "ddos"],
    },
    {
        "problem": """
A custom _app.js file in Next.js with a global layout component.
""",
        "solution": r"""
// pages/_app.tsx (Pages Router)
import type { AppProps } from 'next/app';
import Layout from '../components/Layout';
import { AuthProvider } from '../contexts/AuthContext';
import { ThemeProvider } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import '../styles/globals.css';

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <ThemeProvider
      breakpoints={['xxxl', 'xxl', 'xl', 'lg', 'md', 'sm', 'xs', 'xxs']}
      minBreakpoint="xxs"
    >
      <AuthProvider>
        <Layout>
          <Component {...pageProps} />
        </Layout>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default MyApp;

// components/Layout.tsx
import React from 'react';
import Head from 'next/head';
import Navigation from './Navigation';
import Footer from './Footer';
import { Container } from 'react-bootstrap';

interface LayoutProps {
  children: React.ReactNode;
  title?: string;
  description?: string;
}

const Layout: React.FC<LayoutProps> = ({
  children,
  title = 'My App',
  description = 'A Next.js application'
}) => {
  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="description" content={description} />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="d-flex flex-column min-vh-100">
        <Navigation />
        <main className="flex-grow-1">
          {children}
        </main>
        <Footer />
      </div>
    </>
  );
};

export default Layout;
""",
        "category": "nextjs",
        "subcategory": "api",
        "tags": ["api", "auth", "bootstrap", "components", "css", "next.js", "nextjs"],
    },
    {
        "problem": """
A Next.js page that is server-side rendered (SSR) and fetches data from Firebase Admin SDK.
""",
        "solution": r"""
import { GetServerSideProps } from 'next';
import { adminDb } from '../lib/firebase-admin';
import { Container, Card, Badge } from 'react-bootstrap';
import Head from 'next/head';

interface Post {
  id: string;
  title: string;
  content: string;
  authorName: string;
  createdAt: string;
  tags: string[];
  views: number;
}

interface PostPageProps {
  post: Post | null;
  error?: string;
}

export const getServerSideProps: GetServerSideProps<PostPageProps> = async (context) => {
  const { id } = context.params as { id: string };

  try {
    const docRef = adminDb.collection('posts').doc(id);
    const docSnap = await docRef.get();

    if (!docSnap.exists) {
      return {
        notFound: true
      };
    }

    const postData = docSnap.data();

    // Increment view counter
    await docRef.update({
      views: adminDb.FieldValue.increment(1)
    });

    // Serialize Firestore timestamps for client
    const post: Post = {
      id: docSnap.id,
      title: postData?.title || '',
      content: postData?.content || '',
      authorName: postData?.authorName || 'Anonymous',
      tags: postData?.tags || [],
      views: postData?.views || 0,
      createdAt: postData?.createdAt?.toDate().toISOString() || new Date().toISOString(),
    };

    return {
      props: {
        post
      },
    };
  } catch (error) {
    console.error('Error fetching post:', error);
    return {
      props: {
        post: null,
        error: 'Failed to load post'
      }
    };
  }
};

function PostPage({ post, error }: PostPageProps) {
  if (error) {
    return (
      <Container className="py-5">
        <div className="alert alert-danger">{error}</div>
      </Container>
    );
  }

  if (!post) {
    return (
      <Container className="py-5">
        <div>Post not found</div>
      </Container>
    );
  }

  return (
    <>
      <Head>
        <title>{post.title} | My Blog</title>
        <meta name="description" content={post.content.substring(0, 160)} />
      </Head>

      <Container className="py-5">
        <Card>
          <Card.Body>
            <h1>{post.title}</h1>

            <div className="mb-3">
              {post.tags.map((tag) => (
                <Badge key={tag} bg="secondary" className="me-2">
                  {tag}
                </Badge>
              ))}
            </div>

            <div className="text-muted mb-4">
              <small>
                By {post.authorName} •
                {new Date(post.createdAt).toLocaleDateString()} •
                {post.views} views
              </small>
            </div>

            <div className="post-content">
              {post.content}
            </div>
          </Card.Body>
        </Card>
      </Container>
    </>
  );
}

export default PostPage;
""",
        "category": "nextjs",
        "subcategory": "api",
        "tags": [
            "nextjs",
            "api",
            "async",
            "auth",
            "bootstrap",
            "firebase",
            "firestore",
        ],
    },
]
