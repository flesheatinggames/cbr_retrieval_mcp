"""
Firebase Authentication Cases for CBR MCP Server

This module contains case-based reasoning examples for Firebase Authentication
implementations including user sign-up, sign-in, session management, and
authentication state handling.
"""

FIREBASE_AUTH_CASES = [
    {
        "problem": """
A React component for user sign-up with Firebase Authentication.
""",
        "solution": """
import React, { useState } from 'react';
import { getAuth, createUserWithEmailAndPassword, updateProfile } from 'firebase/auth';
import { Form, Button, Alert, Spinner } from 'react-bootstrap';

interface SignUpFormData {
  email: string;
  password: string;
  confirmPassword: string;
  displayName: string;
}

interface ValidationErrors {
  email?: string;
  password?: string;
  confirmPassword?: string;
  displayName?: string;
}

const SignUpForm: React.FC = () => {
  const [formData, setFormData] = useState<SignUpFormData>({
    email: '',
    password: '',
    confirmPassword: '',
    displayName: ''
  });
  const [errors, setErrors] = useState<ValidationErrors>({});
  const [apiError, setApiError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const validateForm = (): boolean => {
    const newErrors: ValidationErrors = {};

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    if (formData.displayName.trim().length < 2) {
      newErrors.displayName = 'Display name must be at least 2 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name as keyof ValidationErrors]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setApiError(null);
    setIsLoading(true);

    try {
      const auth = getAuth();
      const userCredential = await createUserWithEmailAndPassword(
        auth,
        formData.email,
        formData.password
      );

      await updateProfile(userCredential.user, {
        displayName: formData.displayName
      });

      setIsSuccess(true);
      console.log('User signed up successfully!');
    } catch (error: any) {
      switch (error.code) {
        case 'auth/email-already-in-use':
          setApiError('This email is already registered.');
          break;
        case 'auth/weak-password':
          setApiError('Password is too weak.');
          break;
        case 'auth/invalid-email':
          setApiError('Invalid email address.');
          break;
        default:
          setApiError('An error occurred. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Form onSubmit={handleSignUp} noValidate>
      {apiError && <Alert variant="danger">{apiError}</Alert>}
      {isSuccess && <Alert variant="success">Account created successfully!</Alert>}

      <Form.Group className="mb-3">
        <Form.Label>Display Name</Form.Label>
        <Form.Control
          type="text"
          name="displayName"
          value={formData.displayName}
          onChange={handleInputChange}
          isInvalid={!!errors.displayName}
          required
        />
        <Form.Control.Feedback type="invalid">
          {errors.displayName}
        </Form.Control.Feedback>
      </Form.Group>

      <Form.Group className="mb-3">
        <Form.Label>Email</Form.Label>
        <Form.Control
          type="email"
          name="email"
          value={formData.email}
          onChange={handleInputChange}
          isInvalid={!!errors.email}
          required
        />
        <Form.Control.Feedback type="invalid">
          {errors.email}
        </Form.Control.Feedback>
      </Form.Group>

      <Form.Group className="mb-3">
        <Form.Label>Password</Form.Label>
        <Form.Control
          type="password"
          name="password"
          value={formData.password}
          onChange={handleInputChange}
          isInvalid={!!errors.password}
          required
        />
        <Form.Control.Feedback type="invalid">
          {errors.password}
        </Form.Control.Feedback>
      </Form.Group>

      <Form.Group className="mb-3">
        <Form.Label>Confirm Password</Form.Label>
        <Form.Control
          type="password"
          name="confirmPassword"
          value={formData.confirmPassword}
          onChange={handleInputChange}
          isInvalid={!!errors.confirmPassword}
          required
        />
        <Form.Control.Feedback type="invalid">
          {errors.confirmPassword}
        </Form.Control.Feedback>
      </Form.Group>

      <Button type="submit" disabled={isLoading} className="w-100">
        {isLoading ? (
          <>
            <Spinner size="sm" className="me-2" />
            Signing Up...
          </>
        ) : (
          'Sign Up'
        )}
      </Button>
    </Form>
  );
};

export default SignUpForm;
""",
        "category": 'firebase',
        "subcategory": 'auth',
        "tags": ['firebase', 'authentication', 'react', 'signup', 'user', 'form-validation', 'email-validation']
    },
    {
        "problem": """
A React hook to get the current Firebase authentication user state in real-time.
""",
        "solution": """
import { useState, useEffect } from 'react';
import { getAuth, onAuthStateChanged, User } from 'firebase/auth';

export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const auth = getAuth();
    const unsubscribe = onAuthStateChanged(
      auth,
      (user) => {
        setUser(user);
        setLoading(false);
      },
      (error) => {
        console.error('Auth state change error:', error);
        setError(error);
        setLoading(false);
      }
    );

    return () => unsubscribe();
  }, []);

  return { user, loading, error };
};
""",
        "category": 'firebase',
        "subcategory": 'auth',
        "tags": ['firebase', 'authentication', 'react', 'hook', 'auth-state', 'session', 'user']
    },
    {
        "problem": """
A function to sign in a user with Google using Firebase Authentication popup.
""",
        "solution": """
import { getAuth, signInWithPopup, GoogleAuthProvider } from 'firebase/auth';

const signInWithGoogle = async () => {
  const auth = getAuth();
  const provider = new GoogleAuthProvider();

  // Add additional scopes if needed
  provider.addScope('https://www.googleapis.com/auth/userinfo.profile');
  provider.addScope('https://www.googleapis.com/auth/userinfo.email');

  try {
    const result = await signInWithPopup(auth, provider);
    const user = result.user;

    // Optional: Get Google access token for additional API calls
    const credential = GoogleAuthProvider.credentialFromResult(result);
    const token = credential?.accessToken;

    return { user, token };
  } catch (error: any) {
    console.error("Error during Google sign-in:", error);

    // Handle specific errors
    if (error.code === 'auth/popup-closed-by-user') {
      throw new Error('Sign-in popup was closed');
    } else if (error.code === 'auth/account-exists-with-different-credential') {
      throw new Error('An account already exists with a different sign-in method');
    }

    throw error;
  }
};

export default signInWithGoogle;
""",
        "category": 'firebase',
        "subcategory": 'auth',
        "tags": ['firebase', 'authentication', 'google', 'signin', 'oauth', 'popup', 'user']
    },
    {
        "problem": """
A function to sign out the current user from Firebase.
""",
        "solution": """
import { getAuth, signOut } from 'firebase/auth';

const handleSignOut = async () => {
  const auth = getAuth();
  try {
    await signOut(auth);

    // Clear any local storage or session data
    localStorage.removeItem('userPreferences');
    sessionStorage.clear();

    console.log("User signed out successfully.");
    return { success: true };
  } catch (error) {
    console.error("Error signing out:", error);
    return { success: false, error };
  }
};

export default handleSignOut;
""",
        "category": 'firebase',
        "subcategory": 'auth',
        "tags": ['authentication', 'firebase', 'signout', 'session', 'user']
    },
    {
        "problem": """
Implement secure session management with JWT tokens and refresh token rotation for Firebase Auth.
""",
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
        "category": 'firebase',
        "subcategory": 'auth',
        "tags": ['firebase', 'authentication', 'security', 'session', 'jwt', 'token', 'refresh-token']
    }
]
