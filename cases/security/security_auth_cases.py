"""
Security Authentication Cases for CBR MCP Server

This module contains case-based reasoning examples for secure authentication
implementations, including JWT session management and CSRF protection for Next.js applications.
"""

SECURITY_AUTH_CASES = [
  {
    "problem": "Implement secure session management with JWT tokens and refresh token rotation for Firebase Auth.",
    "solution": """
// lib/secure-session.ts
import { SignJWT, jwtVerify, JWTPayload } from 'jose';
import { cookies } from 'next/headers';
import { getAuth } from 'firebase-admin/auth';
import { getFirestore } from 'firebase-admin/firestore';
import crypto from 'crypto';

interface SessionToken {
  userId: string;
  email: string;
  role: string;
  sessionId: string;
  exp: number;
  iat: number;
  fingerprint?: string;
}

interface RefreshToken {
  tokenId: string;
  userId: string;
  expiresAt: Date;
  createdAt: Date;
  family: string;  // Token family for rotation tracking
  used: boolean;
  revokedAt?: Date;
  userAgent?: string;
  ipAddress?: string;
}

export class SecureSessionManager {
  private readonly accessTokenSecret: Uint8Array;
  private readonly refreshTokenSecret: Uint8Array;
  private readonly db = getFirestore();
  private readonly auth = getAuth();

  // Token expiration times
  private readonly ACCESS_TOKEN_EXPIRY = '15m';  // 15 minutes
  private readonly REFRESH_TOKEN_EXPIRY = 7 * 24 * 60 * 60 * 1000;  // 7 days
  private readonly REFRESH_TOKEN_REUSE_WINDOW = 2 * 60 * 1000;  // 2 minutes grace period

  constructor() {
    // Use strong secrets from environment variables
    this.accessTokenSecret = new TextEncoder().encode(
      process.env.JWT_ACCESS_SECRET || crypto.randomBytes(32).toString('hex')
    );
    this.refreshTokenSecret = new TextEncoder().encode(
      process.env.JWT_REFRESH_SECRET || crypto.randomBytes(32).toString('hex')
    );

    // Warn if using default secrets in production
    if (process.env.NODE_ENV === 'production' && !process.env.JWT_ACCESS_SECRET) {
      console.error('WARNING: Using default JWT secret in production!');
    }
  }

  // Generate device fingerprint for additional security
  private generateFingerprint(req: any): string {
    const userAgent = req.headers['user-agent'] || '';
    const acceptLanguage = req.headers['accept-language'] || '';
    const acceptEncoding = req.headers['accept-encoding'] || '';

    const fingerprint = `${userAgent}|${acceptLanguage}|${acceptEncoding}`;
    return crypto.createHash('sha256').update(fingerprint).digest('hex');
  }

  // Create secure session with access and refresh tokens
  async createSession(
    userId: string,
    req: any,
    res: any
  ): Promise<{ accessToken: string; refreshToken: string }> {
    try {
      // Get user details from Firebase
      const user = await this.auth.getUser(userId);
      const customClaims = user.customClaims || {};

      // Generate unique session ID
      const sessionId = crypto.randomUUID();
      const tokenFamily = crypto.randomUUID();
      const fingerprint = this.generateFingerprint(req);

      // Create access token
      const accessToken = await new SignJWT({
        userId: user.uid,
        email: user.email || '',
        role: customClaims.role || 'user',
        sessionId,
        fingerprint
      })
        .setProtectedHeader({ alg: 'HS256', typ: 'JWT' })
        .setIssuedAt()
        .setExpirationTime(this.ACCESS_TOKEN_EXPIRY)
        .setJti(crypto.randomUUID())
        .sign(this.accessTokenSecret);

      // Create refresh token
      const refreshTokenId = crypto.randomUUID();
      const refreshToken = await new SignJWT({
        tokenId: refreshTokenId,
        userId: user.uid,
        family: tokenFamily
      })
        .setProtectedHeader({ alg: 'HS256', typ: 'JWT' })
        .setIssuedAt()
        .setExpirationTime('7d')
        .setJti(refreshTokenId)
        .sign(this.refreshTokenSecret);

      // Store refresh token in database
      await this.db.collection('refresh_tokens').doc(refreshTokenId).set({
        tokenId: refreshTokenId,
        userId: user.uid,
        family: tokenFamily,
        expiresAt: new Date(Date.now() + this.REFRESH_TOKEN_EXPIRY),
        createdAt: new Date(),
        used: false,
        userAgent: req.headers['user-agent'],
        ipAddress: this.getClientIp(req),
        fingerprint
      });

      // Set secure HTTP-only cookies
      this.setSecureCookies(res, accessToken, refreshToken);

      // Log session creation for audit
      await this.logSessionActivity(user.uid, 'session_created', {
        sessionId,
        ipAddress: this.getClientIp(req)
      });

      return { accessToken, refreshToken };
    } catch (error) {
      console.error('Session creation error:', error);
      throw new Error('Failed to create session');
    }
  }

  // Verify and decode access token
  async verifyAccessToken(token: string, req: any): Promise<SessionToken | null> {
    try {
      const { payload } = await jwtVerify(token, this.accessTokenSecret);

      // Verify fingerprint if present
      if (payload.fingerprint) {
        const currentFingerprint = this.generateFingerprint(req);
        if (payload.fingerprint !== currentFingerprint) {
          console.warn('Fingerprint mismatch detected');
          return null;
        }
      }

      return payload as SessionToken;
    } catch (error) {
      console.error('Access token verification failed:', error);
      return null;
    }
  }

  // Refresh token rotation with reuse detection
  async refreshSession(
    refreshToken: string,
    req: any,
    res: any
  ): Promise<{ accessToken: string; refreshToken: string } | null> {
    try {
      // Verify refresh token
      const { payload } = await jwtVerify(refreshToken, this.refreshTokenSecret);
      const tokenId = payload.tokenId as string;
      const family = payload.family as string;

      // Get token from database
      const tokenDoc = await this.db.collection('refresh_tokens').doc(tokenId).get();

      if (!tokenDoc.exists) {
        console.error('Refresh token not found in database');
        return null;
      }

      const tokenData = tokenDoc.data() as RefreshToken;

      // Check if token has been revoked
      if (tokenData.revokedAt) {
        console.error('Attempted to use revoked refresh token');
        await this.revokeTokenFamily(family);
        return null;
      }

      // Check if token has already been used (possible token theft)
      if (tokenData.used) {
        const usedAt = tokenData.createdAt.getTime();
        const now = Date.now();

        // Allow reuse within grace period (for race conditions)
        if (now - usedAt > this.REFRESH_TOKEN_REUSE_WINDOW) {
          console.error('Refresh token reuse detected - possible theft');
          // Revoke entire token family
          await this.revokeTokenFamily(family);
          return null;
        }
      }

      // Check expiration
      if (tokenData.expiresAt < new Date()) {
        console.error('Refresh token expired');
        return null;
      }

      // Mark old token as used
      await tokenDoc.ref.update({ used: true });

      // Create new session with rotated refresh token
      const user = await this.auth.getUser(tokenData.userId);
      const sessionId = crypto.randomUUID();
      const fingerprint = this.generateFingerprint(req);

      // Create new access token
      const accessToken = await new SignJWT({
        userId: user.uid,
        email: user.email || '',
        role: user.customClaims?.role || 'user',
        sessionId,
        fingerprint
      })
        .setProtectedHeader({ alg: 'HS256', typ: 'JWT' })
        .setIssuedAt()
        .setExpirationTime(this.ACCESS_TOKEN_EXPIRY)
        .setJti(crypto.randomUUID())
        .sign(this.accessTokenSecret);

      // Create new refresh token (rotation)
      const newRefreshTokenId = crypto.randomUUID();
      const newRefreshToken = await new SignJWT({
        tokenId: newRefreshTokenId,
        userId: user.uid,
        family  // Keep same family for tracking
      })
        .setProtectedHeader({ alg: 'HS256', typ: 'JWT' })
        .setIssuedAt()
        .setExpirationTime('7d')
        .setJti(newRefreshTokenId)
        .sign(this.refreshTokenSecret);

      // Store new refresh token
      await this.db.collection('refresh_tokens').doc(newRefreshTokenId).set({
        tokenId: newRefreshTokenId,
        userId: user.uid,
        family,
        expiresAt: new Date(Date.now() + this.REFRESH_TOKEN_EXPIRY),
        createdAt: new Date(),
        used: false,
        userAgent: req.headers['user-agent'],
        ipAddress: this.getClientIp(req),
        fingerprint
      });

      // Set new cookies
      this.setSecureCookies(res, accessToken, newRefreshToken);

      return { accessToken, refreshToken: newRefreshToken };
    } catch (error) {
      console.error('Token refresh error:', error);
      return null;
    }
  }

  // Revoke all tokens in a family (for security breach scenarios)
  private async revokeTokenFamily(family: string): Promise<void> {
    const tokensSnapshot = await this.db
      .collection('refresh_tokens')
      .where('family', '==', family)
      .get();

    const batch = this.db.batch();
    tokensSnapshot.docs.forEach(doc => {
      batch.update(doc.ref, { revokedAt: new Date() });
    });

    await batch.commit();
    console.warn(`Revoked ${tokensSnapshot.size} tokens in family ${family}`);
  }

  // Set secure HTTP-only cookies
  private setSecureCookies(res: any, accessToken: string, refreshToken: string): void {
    const cookieOptions = {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict' as const,
      path: '/'
    };

    res.setHeader('Set-Cookie', [
      `access_token=${accessToken}; Max-Age=${15 * 60}; ${this.serializeCookieOptions(cookieOptions)}`,
      `refresh_token=${refreshToken}; Max-Age=${7 * 24 * 60 * 60}; ${this.serializeCookieOptions(cookieOptions)}`
    ]);
  }

  private serializeCookieOptions(options: any): string {
    const parts = [];
    if (options.httpOnly) parts.push('HttpOnly');
    if (options.secure) parts.push('Secure');
    if (options.sameSite) parts.push(`SameSite=${options.sameSite}`);
    if (options.path) parts.push(`Path=${options.path}`);
    return parts.join('; ');
  }

  private getClientIp(req: any): string {
    const forwarded = req.headers['x-forwarded-for'];
    return typeof forwarded === 'string'
      ? forwarded.split(',')[0].trim()
      : req.socket?.remoteAddress || 'unknown';
  }

  private async logSessionActivity(
    userId: string,
    action: string,
    metadata: any
  ): Promise<void> {
    await this.db.collection('session_logs').add({
      userId,
      action,
      metadata,
      timestamp: new Date()
    });
  }

  // Logout and invalidate session
  async destroySession(refreshToken: string, res: any): Promise<void> {
    try {
      const { payload } = await jwtVerify(refreshToken, this.refreshTokenSecret);
      const family = payload.family as string;

      // Revoke all tokens in the family
      await this.revokeTokenFamily(family);

      // Clear cookies
      res.setHeader('Set-Cookie', [
        'access_token=; Max-Age=0; Path=/',
        'refresh_token=; Max-Age=0; Path=/'
      ]);
    } catch (error) {
      console.error('Session destruction error:', error);
    }
  }
}

export const sessionManager = new SecureSessionManager();
""",
    "category": "security",
    "subcategory": "auth",
    "tags": ["jwt", "authentication", "tokens", "session-management", "refresh-tokens", "firebase", "security"]
  },
  {
    "problem": "Implement secure authentication middleware with CSRF protection for Next.js forms.",
    "solution": """
// lib/csrf-protection.ts
import csrf from 'csrf';
import crypto from 'crypto';
import { NextApiRequest, NextApiResponse } from 'next';
import { getCookie, setCookie } from 'cookies-next';

interface CSRFOptions {
  secret?: string;
  cookieName?: string;
  headerName?: string;
  paramName?: string;
  cookieOptions?: {
    httpOnly?: boolean;
    secure?: boolean;
    sameSite?: 'strict' | 'lax' | 'none';
    maxAge?: number;
    path?: string;
  };
  excludePaths?: string[];
  skipMethods?: string[];
}

class CSRFProtection {
  private tokens: csrf;
  private secret: string;
  private options: Required<CSRFOptions>;

  constructor(options: CSRFOptions = {}) {
    this.tokens = new csrf();
    this.secret = options.secret || process.env.CSRF_SECRET || crypto.randomBytes(32).toString('hex');

    this.options = {
      secret: this.secret,
      cookieName: options.cookieName || 'csrf-secret',
      headerName: options.headerName || 'x-csrf-token',
      paramName: options.paramName || '_csrf',
      cookieOptions: {
        httpOnly: options.cookieOptions?.httpOnly ?? true,
        secure: options.cookieOptions?.secure ?? (process.env.NODE_ENV === 'production'),
        sameSite: options.cookieOptions?.sameSite ?? 'strict',
        maxAge: options.cookieOptions?.maxAge ?? 86400, // 24 hours
        path: options.cookieOptions?.path ?? '/'
      },
      excludePaths: options.excludePaths || ['/api/health', '/api/public'],
      skipMethods: options.skipMethods || ['GET', 'HEAD', 'OPTIONS']
    };
  }

  // Generate CSRF token
  generateToken(req: NextApiRequest, res: NextApiResponse): string {
    // Get or create secret
    let secret = getCookie(this.options.cookieName, { req, res }) as string;

    if (!secret) {
      secret = this.tokens.secretSync();
      setCookie(this.options.cookieName, secret, {
        req,
        res,
        ...this.options.cookieOptions
      });
    }

    // Generate token from secret
    return this.tokens.create(secret);
  }

  // Verify CSRF token
  verifyToken(req: NextApiRequest): boolean {
    // Skip verification for excluded methods
    if (this.options.skipMethods.includes(req.method || 'GET')) {
      return true;
    }

    // Skip verification for excluded paths
    if (this.options.excludePaths.some(path => req.url?.startsWith(path))) {
      return true;
    }

    // Get secret from cookie
    const secret = getCookie(this.options.cookieName, { req }) as string;
    if (!secret) {
      return false;
    }

    // Get token from request
    const token = this.getTokenFromRequest(req);
    if (!token) {
      return false;
    }

    // Verify token
    return this.tokens.verify(secret, token);
  }

  // Get token from request (header, body, or query)
  private getTokenFromRequest(req: NextApiRequest): string | null {
    // Check header
    const headerToken = req.headers[this.options.headerName] as string;
    if (headerToken) {
      return headerToken;
    }

    // Check body
    if (req.body && req.body[this.options.paramName]) {
      return req.body[this.options.paramName];
    }

    // Check query
    if (req.query[this.options.paramName]) {
      return req.query[this.options.paramName] as string;
    }

    return null;
  }

  // Middleware for API routes
  middleware() {
    return async (req: NextApiRequest, res: NextApiResponse, next: () => void) => {
      // Generate token for GET requests
      if (req.method === 'GET') {
        const token = this.generateToken(req, res);
        res.setHeader('X-CSRF-Token', token);
        return next();
      }

      // Verify token for state-changing requests
      if (!this.verifyToken(req)) {
        return res.status(403).json({
          error: 'Invalid CSRF token',
          message: 'The request could not be authenticated. Please refresh and try again.'
        });
      }

      next();
    };
  }
}

// Double Submit Cookie implementation
class DoubleSubmitCSRF {
  private cookieName: string;
  private headerName: string;

  constructor() {
    this.cookieName = '__Host-csrf-token';
    this.headerName = 'x-csrf-token';
  }

  generateToken(): string {
    return crypto.randomBytes(32).toString('base64url');
  }

  setTokenCookie(res: NextApiResponse, token: string): void {
    // Using __Host- prefix for additional security
    res.setHeader('Set-Cookie', [
      `${this.cookieName}=${token}; ` +
      'Secure; HttpOnly; SameSite=Strict; Path=/'
    ]);
  }

  verifyDoubleSubmit(req: NextApiRequest): boolean {
    const cookieToken = this.getTokenFromCookie(req);
    const headerToken = req.headers[this.headerName] as string;

    if (!cookieToken || !headerToken) {
      return false;
    }

    // Constant-time comparison to prevent timing attacks
    return crypto.timingSafeEqual(
      Buffer.from(cookieToken),
      Buffer.from(headerToken)
    );
  }

  private getTokenFromCookie(req: NextApiRequest): string | null {
    const cookies = req.headers.cookie?.split(';') || [];
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === this.cookieName) {
        return value;
      }
    }
    return null;
  }
}

// Synchronizer Token Pattern with session storage
class SynchronizerTokenPattern {
  private sessionStore: Map<string, string>;
  private tokenLifetime: number;

  constructor() {
    this.sessionStore = new Map();
    this.tokenLifetime = 3600000; // 1 hour

    // Clean up expired tokens periodically
    setInterval(() => this.cleanupExpiredTokens(), 3600000);
  }

  generateToken(sessionId: string): string {
    const token = crypto.randomBytes(32).toString('base64url');
    const key = `${sessionId}:${Date.now()}`;
    this.sessionStore.set(key, token);
    return token;
  }

  verifyToken(sessionId: string, token: string): boolean {
    const now = Date.now();

    // Find valid token for session
    for (const [key, storedToken] of this.sessionStore.entries()) {
      const [storedSessionId, timestamp] = key.split(':');

      if (storedSessionId === sessionId) {
        const age = now - parseInt(timestamp);

        if (age < this.tokenLifetime) {
          if (crypto.timingSafeEqual(
            Buffer.from(storedToken),
            Buffer.from(token)
          )) {
            // Token is valid, remove it (one-time use)
            this.sessionStore.delete(key);
            return true;
          }
        }
      }
    }

    return false;
  }

  private cleanupExpiredTokens(): void {
    const now = Date.now();

    for (const [key] of this.sessionStore.entries()) {
      const [, timestamp] = key.split(':');
      const age = now - parseInt(timestamp);

      if (age > this.tokenLifetime) {
        this.sessionStore.delete(key);
      }
    }
  }
}

// Create instances
export const csrfProtection = new CSRFProtection();
export const doubleSubmitCSRF = new DoubleSubmitCSRF();
export const synchronizerToken = new SynchronizerTokenPattern();

// React hook for CSRF token
import { useState, useEffect } from 'react';

export function useCSRFToken(): { token: string | null; loading: boolean } {
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchToken = async () => {
      try {
        const response = await fetch('/api/csrf-token');
        const data = await response.json();
        setToken(data.token);
      } catch (error) {
        console.error('Failed to fetch CSRF token:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchToken();
  }, []);

  return { token, loading };
}

// CSRF token API endpoint
// pages/api/csrf-token.ts
export async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const token = csrfProtection.generateToken(req, res);
  res.status(200).json({ token });
}

// Protected form component
import React from 'react';
import { Form, Button, Alert } from 'react-bootstrap';
import { useCSRFToken } from '@/hooks/useCSRFToken';

export const SecureForm: React.FC = () => {
  const { token, loading } = useCSRFToken();
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!token) {
      setError('Security token not available. Please refresh the page.');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const formData = new FormData(e.target as HTMLFormElement);
      const data = Object.fromEntries(formData.entries());

      const response = await fetch('/api/secure-endpoint', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': token
        },
        body: JSON.stringify(data),
        credentials: 'same-origin'
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Request failed');
      }

      const result = await response.json();
      console.log('Success:', result);
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div>Loading security features...</div>;
  }

  return (
    <Form onSubmit={handleSubmit}>
      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Hidden CSRF token field for traditional form submission */}
      <input type="hidden" name="_csrf" value={token || ''} />

      <Form.Group className="mb-3">
        <Form.Label>Name</Form.Label>
        <Form.Control type="text" name="name" required />
      </Form.Group>

      <Form.Group className="mb-3">
        <Form.Label>Email</Form.Label>
        <Form.Control type="email" name="email" required />
      </Form.Group>

      <Button type="submit" disabled={submitting || !token}>
        {submitting ? 'Submitting...' : 'Submit Securely'}
      </Button>
    </Form>
  );
};

// Usage in API route with all protections
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // Apply CSRF protection
  const isValidCSRF = csrfProtection.verifyToken(req);
  if (!isValidCSRF) {
    return res.status(403).json({ error: 'Invalid CSRF token' });
  }

  // Additional security checks
  const origin = req.headers.origin;
  const allowedOrigins = process.env.ALLOWED_ORIGINS?.split(',') || [];

  if (origin && !allowedOrigins.includes(origin)) {
    return res.status(403).json({ error: 'Origin not allowed' });
  }

  // Check referer
  const referer = req.headers.referer;
  if (!referer || !referer.startsWith(process.env.NEXT_PUBLIC_BASE_URL!)) {
    return res.status(403).json({ error: 'Invalid referer' });
  }

  // Your protected API logic here
  res.status(200).json({ success: true });
}
""",
    "category": "security",
    "subcategory": "auth",
    "tags": ["csrf", "authentication", "middleware", "forms", "security", "nextjs", "tokens"]
  }
]
