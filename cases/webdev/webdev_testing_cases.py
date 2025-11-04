"""
Web Development Testing Cases for CBR MCP Server

This module contains testing examples for web development projects,
including Jest unit testing patterns and React Testing Library component testing.

Cases:
1. Jest unit testing for utility functions with mocking and assertions
2. React Testing Library component testing with user interactions
"""

WEBDEV_TESTING_CASES = [
    {
        "problem": """
Write Jest unit tests for a utility function that validates email addresses and handles edge cases.
""",
        "solution": r"""
// utils/validation.ts
export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validatePassword = (password: string): {
  isValid: boolean;
  errors: string[]
} => {
  const errors: string[] = [];

  if (password.length < 8) {
    errors.push('Password must be at least 8 characters');
  }

  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }

  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  }

  if (!/[0-9]/.test(password)) {
    errors.push('Password must contain at least one number');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
};

// __tests__/validation.test.ts
import { validateEmail, validatePassword } from '../utils/validation';

describe('validateEmail', () => {
  it('should return true for valid email addresses', () => {
    expect(validateEmail('test@example.com')).toBe(true);
    expect(validateEmail('user.name@domain.co.uk')).toBe(true);
    expect(validateEmail('first+last@subdomain.example.org')).toBe(true);
  });

  it('should return false for invalid email addresses', () => {
    expect(validateEmail('invalid')).toBe(false);
    expect(validateEmail('no-at-sign.com')).toBe(false);
    expect(validateEmail('@no-local.com')).toBe(false);
    expect(validateEmail('no-domain@')).toBe(false);
    expect(validateEmail('spaces in@email.com')).toBe(false);
  });

  it('should handle empty strings', () => {
    expect(validateEmail('')).toBe(false);
  });

  it('should handle special characters correctly', () => {
    expect(validateEmail('user+tag@example.com')).toBe(true);
    expect(validateEmail('user_name@example.com')).toBe(true);
  });
});

describe('validatePassword', () => {
  it('should accept valid passwords', () => {
    const result = validatePassword('Password123');
    expect(result.isValid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  it('should reject passwords shorter than 8 characters', () => {
    const result = validatePassword('Pass1');
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Password must be at least 8 characters');
  });

  it('should require at least one uppercase letter', () => {
    const result = validatePassword('password123');
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Password must contain at least one uppercase letter');
  });

  it('should require at least one lowercase letter', () => {
    const result = validatePassword('PASSWORD123');
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Password must contain at least one lowercase letter');
  });

  it('should require at least one number', () => {
    const result = validatePassword('Password');
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Password must contain at least one number');
  });

  it('should return multiple error messages for invalid passwords', () => {
    const result = validatePassword('pass');
    expect(result.isValid).toBe(false);
    expect(result.errors.length).toBeGreaterThan(1);
    expect(result.errors).toContain('Password must be at least 8 characters');
    expect(result.errors).toContain('Password must contain at least one uppercase letter');
    expect(result.errors).toContain('Password must contain at least one number');
  });
});
""",
        "category": "webdev",
        "subcategory": "testing",
        "tags": [
            "jest",
            "unit-tests",
            "testing",
            "validation",
            "mocking",
            "assertions",
            "typescript",
        ],
    },
    {
        "problem": """
Write React Testing Library tests for a login form component with user interactions and async validation.
""",
        "solution": r"""
// components/LoginForm.tsx
import React, { useState } from 'react';
import { Form, Button, Alert } from 'react-bootstrap';

interface LoginFormProps {
  onSubmit: (email: string, password: string) => Promise<void>;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSubmit }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await onSubmit(email, password);
    } catch (err: any) {
      setError(err.message || 'Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Form onSubmit={handleSubmit} data-testid="login-form">
      {error && <Alert variant="danger">{error}</Alert>}

      <Form.Group className="mb-3">
        <Form.Label htmlFor="email">Email</Form.Label>
        <Form.Control
          id="email"
          type="email"
          placeholder="Enter email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          disabled={isLoading}
          required
        />
      </Form.Group>

      <Form.Group className="mb-3">
        <Form.Label htmlFor="password">Password</Form.Label>
        <Form.Control
          id="password"
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          disabled={isLoading}
          required
        />
      </Form.Group>

      <Button variant="primary" type="submit" disabled={isLoading}>
        {isLoading ? 'Logging in...' : 'Login'}
      </Button>
    </Form>
  );
};

// __tests__/LoginForm.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { LoginForm } from '../components/LoginForm';

describe('LoginForm', () => {
  const mockOnSubmit = jest.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  it('should render login form with email and password fields', () => {
    render(<LoginForm onSubmit={mockOnSubmit} />);

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('should update input values when user types', async () => {
    const user = userEvent.setup();
    render(<LoginForm onSubmit={mockOnSubmit} />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);

    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');

    expect(emailInput).toHaveValue('test@example.com');
    expect(passwordInput).toHaveValue('password123');
  });

  it('should call onSubmit with email and password when form is submitted', async () => {
    mockOnSubmit.mockResolvedValue(undefined);
    const user = userEvent.setup();
    render(<LoginForm onSubmit={mockOnSubmit} />);

    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');

    const submitButton = screen.getByRole('button', { name: /login/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith('test@example.com', 'password123');
      expect(mockOnSubmit).toHaveBeenCalledTimes(1);
    });
  });

  it('should show loading state while submitting', async () => {
    mockOnSubmit.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
    const user = userEvent.setup();
    render(<LoginForm onSubmit={mockOnSubmit} />);

    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');

    const submitButton = screen.getByRole('button', { name: /login/i });
    await user.click(submitButton);

    expect(screen.getByRole('button', { name: /logging in/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /logging in/i })).toBeDisabled();

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /^login$/i })).toBeInTheDocument();
    });
  });

  it('should display error message when login fails', async () => {
    const errorMessage = 'Invalid credentials';
    mockOnSubmit.mockRejectedValue(new Error(errorMessage));
    const user = userEvent.setup();
    render(<LoginForm onSubmit={mockOnSubmit} />);

    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'wrongpassword');

    const submitButton = screen.getByRole('button', { name: /login/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  it('should disable form inputs while loading', async () => {
    mockOnSubmit.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
    const user = userEvent.setup();
    render(<LoginForm onSubmit={mockOnSubmit} />);

    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');

    const submitButton = screen.getByRole('button', { name: /login/i });
    await user.click(submitButton);

    expect(screen.getByLabelText(/email/i)).toBeDisabled();
    expect(screen.getByLabelText(/password/i)).toBeDisabled();

    await waitFor(() => {
      expect(screen.getByLabelText(/email/i)).not.toBeDisabled();
      expect(screen.getByLabelText(/password/i)).not.toBeDisabled();
    });
  });

  it('should clear error message on successful submission', async () => {
    mockOnSubmit.mockRejectedValueOnce(new Error('First error'));
    const user = userEvent.setup();
    render(<LoginForm onSubmit={mockOnSubmit} />);

    // First submission with error
    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'wrongpassword');
    await user.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(screen.getByText('First error')).toBeInTheDocument();
    });

    // Second submission succeeds
    mockOnSubmit.mockResolvedValue(undefined);
    await user.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(screen.queryByText('First error')).not.toBeInTheDocument();
    });
  });
});
""",
        "category": "webdev",
        "subcategory": "testing",
        "tags": [
            "testing-library",
            "react",
            "jest",
            "unit-tests",
            "component-testing",
            "user-interaction",
            "async",
        ],
    },
]
