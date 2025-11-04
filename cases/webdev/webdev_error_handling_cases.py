"""
Web Development Error Handling Cases

This module contains case-based reasoning examples focused on error handling patterns
in web development, including:
- Secure error logging and monitoring (Winston, Sentry)
- React error boundaries for graceful error recovery
- Form validation with comprehensive error states
- User-facing error notifications and alerts
- Error recovery patterns and fallback UI

These cases demonstrate production-ready error handling approaches that prevent
security vulnerabilities while providing good user experience.
"""

WEBDEV_ERROR_HANDLING_CASES = [
    {
        "problem": """
Implement secure error handling and logging that doesn't expose sensitive information in production.
""",
        "solution": r"""
// lib/secure-logger.ts
import winston from 'winston';
import { Sentry } from '@sentry/nextjs';
import crypto from 'crypto';

interface LogContext {
  userId?: string;
  sessionId?: string;
  requestId?: string;
  ip?: string;
  userAgent?: string;
  method?: string;
  path?: string;
  statusCode?: number;
  duration?: number;
  error?: Error;
  metadata?: Record<string, any>;
}

interface SensitiveDataPattern {
  pattern: RegExp;
  replacement: string;
}

class SecureLogger {
  private logger: winston.Logger;
  private isDevelopment: boolean;
  private isProduction: boolean;
  private sensitivePatterns: SensitiveDataPattern[];

  constructor() {
    this.isDevelopment = process.env.NODE_ENV === 'development';
    this.isProduction = process.env.NODE_ENV === 'production';

    // Define sensitive data patterns to redact
    this.sensitivePatterns = [
      // API Keys and tokens
      { pattern: /([A-Za-z0-9_\-]{20,})/g, replacement: '[REDACTED_TOKEN]' },
      { pattern: /(api[_-]?key|apikey|api_secret)(["']?\s*[:=]\s*["']?)([^"'\s]+)/gi, replacement: '$1$2[REDACTED_API_KEY]' },
      { pattern: /(bearer|token|jwt)[\s:]+([^\s]+)/gi, replacement: '$1 [REDACTED_TOKEN]' },

      // Passwords
      { pattern: /(password|passwd|pwd)(["']?\s*[:=]\s*["']?)([^"'\s]+)/gi, replacement: '$1$2[REDACTED_PASSWORD]' },

      // Credit cards
      { pattern: /\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}/g, replacement: '[REDACTED_CARD]' },
      { pattern: /\d{3,4}/g, replacement: '[CVV]' },

      // Social Security Numbers
      { pattern: /\d{3}-\d{2}-\d{4}/g, replacement: '[REDACTED_SSN]' },

      // Email addresses (partial redaction)
      { pattern: /([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g, replacement: (match, user, domain) => {
        const redactedUser = user.substring(0, 2) + '***';
        return `${redactedUser}@${domain}`;
      }},

      // Phone numbers
      { pattern: /\d{3}[-.]?\d{3}[-.]?\d{4}/g, replacement: '[REDACTED_PHONE]' },

      // IP addresses (partial redaction)
      { pattern: /(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})/g, replacement: '$1.$2.XXX.XXX' },

      // Firebase keys
      { pattern: /(AIza[0-9A-Za-z_-]{35})/g, replacement: '[REDACTED_FIREBASE_KEY]' },

      // Private keys
      { pattern: /-----BEGIN[^-]+-----[\s\S]*?-----END[^-]+-----/g, replacement: '[REDACTED_PRIVATE_KEY]' },
    ];

    // Configure Winston logger
    this.logger = winston.createLogger({
      level: this.isDevelopment ? 'debug' : 'info',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json()
      ),
      defaultMeta: {
        service: 'nextjs-app',
        environment: process.env.NODE_ENV
      },
      transports: this.getTransports(),
      exceptionHandlers: [
        new winston.transports.File({ filename: 'logs/exceptions.log' })
      ],
      rejectionHandlers: [
        new winston.transports.File({ filename: 'logs/rejections.log' })
      ]
    });
  }

  private getTransports(): winston.transport[] {
    const transports: winston.transport[] = [];

    // Console transport for development
    if (this.isDevelopment) {
      transports.push(
        new winston.transports.Console({
          format: winston.format.combine(
            winston.format.colorize(),
            winston.format.simple()
          )
        })
      );
    }

    // File transports for production
    if (this.isProduction) {
      // Error logs
      transports.push(
        new winston.transports.File({
          filename: 'logs/error.log',
          level: 'error',
          maxsize: 5242880, // 5MB
          maxFiles: 5
        })
      );

      // Combined logs
      transports.push(
        new winston.transports.File({
          filename: 'logs/combined.log',
          maxsize: 5242880, // 5MB
          maxFiles: 5
        })
      );

      // Security audit logs
      transports.push(
        new winston.transports.File({
          filename: 'logs/security.log',
          level: 'warn',
          maxsize: 5242880, // 5MB
          maxFiles: 10
        })
      );
    }

    return transports;
  }

  // Redact sensitive information from data
  private redactSensitiveData(data: any): any {
    if (typeof data === 'string') {
      let redacted = data;
      for (const { pattern, replacement } of this.sensitivePatterns) {
        redacted = redacted.replace(pattern, replacement as any);
      }
      return redacted;
    }

    if (Array.isArray(data)) {
      return data.map(item => this.redactSensitiveData(item));
    }

    if (typeof data === 'object' && data !== null) {
      const redacted: any = {};
      for (const [key, value] of Object.entries(data)) {
        // Redact sensitive keys entirely
        const sensitiveKeys = [
          'password', 'secret', 'token', 'apikey', 'api_key',
          'authorization', 'cookie', 'session', 'private_key',
          'credit_card', 'ssn', 'social_security'
        ];

        if (sensitiveKeys.some(k => key.toLowerCase().includes(k))) {
          redacted[key] = '[REDACTED]';
        } else {
          redacted[key] = this.redactSensitiveData(value);
        }
      }
      return redacted;
    }

    return data;
  }

  // Generate request ID for tracking
  private generateRequestId(): string {
    return crypto.randomBytes(16).toString('hex');
  }

  // Log with context
  private logWithContext(
    level: string,
    message: string,
    context?: LogContext
  ): void {
    const requestId = context?.requestId || this.generateRequestId();

    const logData = {
      message,
      requestId,
      timestamp: new Date().toISOString(),
      ...this.redactSensitiveData(context || {})
    };

    this.logger.log(level, logData);

    // Send to Sentry in production for errors
    if (this.isProduction && level === 'error' && context?.error) {
      Sentry.captureException(context.error, {
        contexts: {
          request: {
            url: context.path,
            method: context.method,
            headers: {
              'user-agent': context.userAgent
            }
          }
        },
        user: {
          id: context.userId,
          ip_address: context.ip
        },
        tags: {
          requestId,
          sessionId: context.sessionId
        }
      });
    }
  }

  // Public logging methods
  info(message: string, context?: LogContext): void {
    this.logWithContext('info', message, context);
  }

  warn(message: string, context?: LogContext): void {
    this.logWithContext('warn', message, context);
  }

  error(message: string, error: Error, context?: LogContext): void {
    this.logWithContext('error', message, { ...context, error });
  }

  debug(message: string, context?: LogContext): void {
    if (this.isDevelopment) {
      this.logWithContext('debug', message, context);
    }
  }

  // Security-specific logging
  security(event: string, context?: LogContext): void {
    this.logWithContext('warn', `SECURITY: ${event}`, context);
  }

  // Audit logging
  audit(action: string, userId: string, details: any): void {
    this.logWithContext('info', `AUDIT: ${action}`, {
      userId,
      metadata: details,
      timestamp: new Date().toISOString()
    });
  }
}

// Create singleton instance
export const logger = new SecureLogger();

// Error handler middleware
export class ErrorHandler {
  static handle(error: any, req: any, res: any): void {
    const requestId = crypto.randomBytes(8).toString('hex');

    // Log the error
    logger.error('Request error', error, {
      requestId,
      method: req.method,
      path: req.url,
      ip: req.ip,
      userAgent: req.headers['user-agent'],
      statusCode: error.statusCode || 500
    });

    // Prepare error response
    const isDevelopment = process.env.NODE_ENV === 'development';

    let statusCode = 500;
    let message = 'Internal Server Error';
    let details = undefined;

    // Determine status code and message
    if (error.statusCode) {
      statusCode = error.statusCode;
    } else if (error.name === 'ValidationError') {
      statusCode = 400;
      message = 'Validation Error';
    } else if (error.name === 'UnauthorizedError') {
      statusCode = 401;
      message = 'Unauthorized';
    } else if (error.name === 'ForbiddenError') {
      statusCode = 403;
      message = 'Forbidden';
    } else if (error.name === 'NotFoundError') {
      statusCode = 404;
      message = 'Not Found';
    }

    // In development, include error details
    if (isDevelopment) {
      details = {
        error: error.message,
        stack: error.stack,
        ...error
      };
    }

    // Send error response
    res.status(statusCode).json({
      error: {
        message,
        requestId,
        timestamp: new Date().toISOString(),
        ...(details && { details })
      }
    });
  }

  // Async error wrapper
  static asyncHandler(fn: Function) {
    return (req: any, res: any, next: any) => {
      Promise.resolve(fn(req, res, next)).catch((error) => {
        ErrorHandler.handle(error, req, res);
      });
    };
  }
}

// Custom error classes
export class AppError extends Error {
  statusCode: number;
  isOperational: boolean;

  constructor(message: string, statusCode: number = 500) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;
    Error.captureStackTrace(this, this.constructor);
  }
}

export class ValidationError extends AppError {
  constructor(message: string, details?: any) {
    super(message, 400);
    this.name = 'ValidationError';
    if (details) {
      (this as any).details = details;
    }
  }
}

export class AuthenticationError extends AppError {
  constructor(message: string = 'Authentication failed') {
    super(message, 401);
    this.name = 'UnauthorizedError';
  }
}

export class AuthorizationError extends AppError {
  constructor(message: string = 'Access denied') {
    super(message, 403);
    this.name = 'ForbiddenError';
  }
}

export class NotFoundError extends AppError {
  constructor(message: string = 'Resource not found') {
    super(message, 404);
    this.name = 'NotFoundError';
  }
}

// Usage in API routes
import { NextApiRequest, NextApiResponse } from 'next';
import { logger, ErrorHandler, ValidationError } from '@/lib/secure-logger';

export default ErrorHandler.asyncHandler(
  async (req: NextApiRequest, res: NextApiResponse) => {
    const startTime = Date.now();

    try {
      // Log request
      logger.info('API request', {
        method: req.method,
        path: req.url,
        ip: req.headers['x-forwarded-for'] as string || req.socket.remoteAddress,
        userAgent: req.headers['user-agent']
      });

      // Validate input
      if (!req.body.email) {
        throw new ValidationError('Email is required', {
          field: 'email',
          code: 'REQUIRED_FIELD'
        });
      }

      // Your API logic here
      const result = { success: true };

      // Log successful response
      logger.info('API response', {
        method: req.method,
        path: req.url,
        statusCode: 200,
        duration: Date.now() - startTime
      });

      res.status(200).json(result);
    } catch (error) {
      throw error; // Will be caught by asyncHandler
    }
  }
);

// Global error boundary component for React
import React from 'react';
import { Alert, Container, Button } from 'react-bootstrap';

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

export class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  ErrorBoundaryState
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error,
      errorInfo: null
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    // Log error to logger
    logger.error('React error boundary', error, {
      metadata: {
        componentStack: errorInfo.componentStack
      }
    });

    // Report to Sentry
    if (process.env.NODE_ENV === 'production') {
      Sentry.captureException(error, {
        contexts: {
          react: {
            componentStack: errorInfo.componentStack
          }
        }
      });
    }
  }

  render() {
    if (this.state.hasError) {
      const isDevelopment = process.env.NODE_ENV === 'development';

      return (
        <Container className="py-5">
          <Alert variant="danger">
            <Alert.Heading>Oops! Something went wrong</Alert.Heading>
            <p>We're sorry for the inconvenience. The error has been logged and we'll look into it.</p>

            {isDevelopment && this.state.error && (
              <details className="mt-3">
                <summary>Error details (development only)</summary>
                <pre className="mt-2">
                  {this.state.error.toString()}
                  {this.state.errorInfo?.componentStack}
                </pre>
              </details>
            )}

            <hr />
            <div className="d-flex justify-content-end">
              <Button onClick={() => window.location.reload()}>
                Reload Page
              </Button>
            </div>
          </Alert>
        </Container>
      );
    }

    return this.props.children;
  }
}
""",
        "category": "webdev",
        "subcategory": "error-handling",
        "tags": [
            "errors",
            "logging",
            "winston",
            "sentry",
            "boundaries",
            "react",
            "security",
        ],
    },
    {
        "problem": """
Implement React error boundaries for graceful error handling and recovery in component trees.
""",
        "solution": r"""
// components/ErrorBoundary.tsx
import React from 'react';
import { Alert, Container, Button } from 'react-bootstrap';

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

export class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    // Log error to error reporting service
    console.error('ErrorBoundary caught an error:', error, errorInfo);

    // Store error info in state
    this.setState({
      errorInfo
    });

    // Call optional error handler prop
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // In production, you would send this to an error tracking service
    // Example: Sentry.captureException(error, { contexts: { react: { componentStack: errorInfo.componentStack } } });
  }

  handleReset = (): void => {
    // Reset error boundary state
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
  };

  render() {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      const isDevelopment = process.env.NODE_ENV === 'development';

      return (
        <Container className="py-5">
          <Alert variant="danger">
            <Alert.Heading>Oops! Something went wrong</Alert.Heading>
            <p>
              We're sorry for the inconvenience. The error has been logged and we'll look into it.
            </p>

            {isDevelopment && this.state.error && (
              <details className="mt-3">
                <summary>Error details (development only)</summary>
                <pre className="mt-2 p-3 bg-light border rounded">
                  <strong>Error:</strong> {this.state.error.toString()}
                  {this.state.errorInfo?.componentStack && (
                    <>
                      <br /><br />
                      <strong>Component Stack:</strong>
                      {this.state.errorInfo.componentStack}
                    </>
                  )}
                </pre>
              </details>
            )}

            <hr />
            <div className="d-flex justify-content-between">
              <Button
                variant="outline-secondary"
                onClick={this.handleReset}
              >
                Try Again
              </Button>
              <Button
                variant="primary"
                onClick={() => window.location.reload()}
              >
                Reload Page
              </Button>
            </div>
          </Alert>
        </Container>
      );
    }

    return this.props.children;
  }
}

// Specialized error boundaries for different use cases

// Fallback UI component for feature-level errors
export const FeatureErrorFallback: React.FC<{ feature: string; onReset: () => void }> = ({
  feature,
  onReset
}) => (
  <Alert variant="warning" className="m-3">
    <Alert.Heading>Unable to load {feature}</Alert.Heading>
    <p>This feature is temporarily unavailable. Please try again.</p>
    <Button variant="outline-warning" onClick={onReset}>
      Retry
    </Button>
  </Alert>
);

// Usage example - wrap entire app
// pages/_app.tsx
import { ErrorBoundary } from '@/components/ErrorBoundary';
import type { AppProps } from 'next/app';

function MyApp({ Component, pageProps }: AppProps) {
  const handleError = (error: Error, errorInfo: React.ErrorInfo) => {
    // Send to error tracking service
    console.error('Application error:', error, errorInfo);
  };

  return (
    <ErrorBoundary onError={handleError}>
      <Component {...pageProps} />
    </ErrorBoundary>
  );
}

export default MyApp;

// Usage example - wrap specific features
import { ErrorBoundary, FeatureErrorFallback } from '@/components/ErrorBoundary';

const DashboardPage = () => {
  return (
    <div>
      <h1>Dashboard</h1>

      {/* Wrap potentially unstable components */}
      <ErrorBoundary
        fallback={
          <FeatureErrorFallback
            feature="Analytics Widget"
            onReset={() => window.location.reload()}
          />
        }
      >
        <AnalyticsWidget />
      </ErrorBoundary>

      <ErrorBoundary
        fallback={
          <FeatureErrorFallback
            feature="User Activity"
            onReset={() => window.location.reload()}
          />
        }
      >
        <UserActivityFeed />
      </ErrorBoundary>
    </div>
  );
};

// Async component error boundary wrapper
export const AsyncErrorBoundary: React.FC<{
  children: React.ReactNode;
  loadingFallback?: React.ReactNode;
}> = ({ children, loadingFallback }) => {
  return (
    <ErrorBoundary>
      <React.Suspense fallback={loadingFallback || <div>Loading...</div>}>
        {children}
      </React.Suspense>
    </ErrorBoundary>
  );
};
""",
        "category": "webdev",
        "subcategory": "error-handling",
        "tags": [
            "react",
            "error-boundaries",
            "componentdidcatch",
            "error-recovery",
            "fallback",
            "error-ui",
            "errors",
        ],
    },
    {
        "problem": """
Implement user-friendly error notifications and recovery UI with toast messages and fallback states.
""",
        "solution": r"""
// components/ToastNotification.tsx
import React, { createContext, useContext, useState, useCallback } from 'react';
import { Toast, ToastContainer } from 'react-bootstrap';

interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  autohide?: boolean;
  delay?: number;
}

interface ToastContextType {
  showToast: (toast: Omit<ToastMessage, 'id'>) => void;
  showSuccess: (title: string, message: string) => void;
  showError: (title: string, message: string) => void;
  showWarning: (title: string, message: string) => void;
  showInfo: (title: string, message: string) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
};

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const showToast = useCallback((toast: Omit<ToastMessage, 'id'>) => {
    const id = `toast-${Date.now()}-${Math.random()}`;
    const newToast: ToastMessage = {
      ...toast,
      id,
      autohide: toast.autohide ?? true,
      delay: toast.delay ?? 5000
    };
    setToasts((prev) => [...prev, newToast]);
  }, []);

  const showSuccess = useCallback(
    (title: string, message: string) => {
      showToast({ type: 'success', title, message });
    },
    [showToast]
  );

  const showError = useCallback(
    (title: string, message: string) => {
      showToast({ type: 'error', title, message, autohide: false });
    },
    [showToast]
  );

  const showWarning = useCallback(
    (title: string, message: string) => {
      showToast({ type: 'warning', title, message });
    },
    [showToast]
  );

  const showInfo = useCallback(
    (title: string, message: string) => {
      showToast({ type: 'info', title, message });
    },
    [showToast]
  );

  const getVariant = (type: ToastMessage['type']) => {
    switch (type) {
      case 'success':
        return 'success';
      case 'error':
        return 'danger';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      default:
        return 'primary';
    }
  };

  return (
    <ToastContext.Provider
      value={{ showToast, showSuccess, showError, showWarning, showInfo }}
    >
      {children}
      <ToastContainer position="top-end" className="p-3">
        {toasts.map((toast) => (
          <Toast
            key={toast.id}
            bg={getVariant(toast.type)}
            onClose={() => removeToast(toast.id)}
            show={true}
            autohide={toast.autohide}
            delay={toast.delay}
          >
            <Toast.Header>
              <strong className="me-auto">{toast.title}</strong>
            </Toast.Header>
            <Toast.Body className="text-white">{toast.message}</Toast.Body>
          </Toast>
        ))}
      </ToastContainer>
    </ToastContext.Provider>
  );
};

// components/ErrorRecoveryComponent.tsx
import { useState } from 'react';
import { Alert, Button, Spinner } from 'react-bootstrap';
import { useToast } from './ToastNotification';

interface ErrorRecoveryProps {
  operation: () => Promise<void>;
  operationName: string;
  maxRetries?: number;
}

export const ErrorRecoveryComponent: React.FC<ErrorRecoveryProps> = ({
  operation,
  operationName,
  maxRetries = 3
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const { showSuccess, showError, showWarning } = useToast();

  const handleOperation = async () => {
    setIsLoading(true);
    setError(null);

    try {
      await operation();
      showSuccess('Success', `${operationName} completed successfully`);
      setRetryCount(0);
    } catch (err) {
      const error = err as Error;
      setError(error);

      if (retryCount < maxRetries) {
        showWarning(
          'Operation Failed',
          `${operationName} failed. You can try again. (Attempt ${retryCount + 1}/${maxRetries})`
        );
      } else {
        showError(
          'Maximum Retries Reached',
          `${operationName} failed after ${maxRetries} attempts. Please contact support.`
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = async () => {
    if (retryCount < maxRetries) {
      setRetryCount((prev) => prev + 1);
      await handleOperation();
    }
  };

  const handleReset = () => {
    setError(null);
    setRetryCount(0);
  };

  return (
    <div>
      {error && (
        <Alert variant="danger" dismissible onClose={handleReset}>
          <Alert.Heading>Error: {error.message}</Alert.Heading>
          <p>
            {retryCount < maxRetries
              ? `You have ${maxRetries - retryCount} retry attempts remaining.`
              : 'Maximum retry attempts reached. Please contact support if the problem persists.'}
          </p>
          {retryCount < maxRetries && (
            <div className="d-flex gap-2">
              <Button variant="outline-danger" onClick={handleRetry} disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Spinner size="sm" className="me-2" />
                    Retrying...
                  </>
                ) : (
                  `Retry (${retryCount + 1}/${maxRetries})`
                )}
              </Button>
              <Button variant="secondary" onClick={handleReset}>
                Dismiss
              </Button>
            </div>
          )}
        </Alert>
      )}

      {!error && (
        <Button onClick={handleOperation} disabled={isLoading}>
          {isLoading ? (
            <>
              <Spinner size="sm" className="me-2" />
              Processing...
            </>
          ) : (
            operationName
          )}
        </Button>
      )}
    </div>
  );
};

// Usage example in _app.tsx
import { ToastProvider } from '@/components/ToastNotification';
import type { AppProps } from 'next/app';

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <ToastProvider>
      <Component {...pageProps} />
    </ToastProvider>
  );
}

export default MyApp;

// Usage example in a component
import { useToast } from '@/components/ToastNotification';
import { ErrorRecoveryComponent } from '@/components/ErrorRecoveryComponent';

const ExamplePage = () => {
  const { showSuccess, showError } = useToast();

  const handleSaveData = async () => {
    try {
      const response = await fetch('/api/save', {
        method: 'POST',
        body: JSON.stringify({ data: 'example' })
      });

      if (!response.ok) {
        throw new Error('Failed to save data');
      }

      showSuccess('Saved', 'Your data has been saved successfully');
    } catch (error) {
      showError('Save Failed', error.message);
      throw error;
    }
  };

  return (
    <div>
      <h1>Error Recovery Example</h1>
      <ErrorRecoveryComponent
        operation={handleSaveData}
        operationName="Save Data"
        maxRetries={3}
      />
    </div>
  );
};
""",
        "category": "webdev",
        "subcategory": "error-handling",
        "tags": [
            "error-notifications",
            "toast",
            "recovery",
            "user-feedback",
            "error-messages",
            "ui",
            "alerts",
        ],
    },
]
