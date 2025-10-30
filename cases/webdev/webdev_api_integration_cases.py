"""
Web Development API Integration Cases for CBR MCP Server

This module contains cases demonstrating API integration patterns including
fetch operations, async/await patterns, error handling, and REST API interactions.
"""

WEBDEV_API_INTEGRATION_CASES = [
{
 "problem": "A reusable async function to fetch data from a REST API with proper headers and response handling.",
 "solution": """
// api/client.ts
interface FetchOptions {
method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
headers?: Record<string, string>;
body?: any;
params?: Record<string, string>;
}

interface ApiResponse<T = any> {
data?: T;
error?: string;
status: number;
}

export async function fetchAPI<T = any>(
endpoint: string,
options: FetchOptions = {}
): Promise<ApiResponse<T>> {
const {
 method = 'GET',
 headers = {},
 body,
 params
} = options;

// Build URL with query parameters
let url = endpoint;
if (params) {
 const queryString = new URLSearchParams(params).toString();
 url += `?${queryString}`;
}

// Build request configuration
const config: RequestInit = {
 method,
 headers: {
 'Content-Type': 'application/json',
 ...headers
 },
 credentials: 'include'
};

// Add body for non-GET requests
if (body && method !== 'GET') {
 config.body = JSON.stringify(body);
}

try {
 const response = await fetch(url, config);

 // Parse JSON response
 let data: T | undefined;
 const contentType = response.headers.get('content-type');

 if (contentType && contentType.includes('application/json')) {
 data = await response.json();
 }

 // Handle HTTP errors
 if (!response.ok) {
 return {
 error: data?.message || response.statusText || 'Request failed',
 status: response.status
 };
 }

 return {
 data,
 status: response.status
 };

} catch (error: any) {
 return {
 error: error.message || 'Network error occurred',
 status: 0
 };
}
}

// Usage examples

// GET request
async function getUsers() {
const response = await fetchAPI<User[]>('/api/users');

if (response.error) {
 console.error('Failed to fetch users:', response.error);
 return [];
}

return response.data || [];
}

// POST request
async function createUser(userData: CreateUserData) {
const response = await fetchAPI<User>('/api/users', {
 method: 'POST',
 body: userData
});

if (response.error) {
 throw new Error(response.error);
}

return response.data;
}

// GET with query parameters
async function searchUsers(query: string) {
const response = await fetchAPI<User[]>('/api/users/search', {
 params: { q: query, limit: '10' }
});

return response.data || [];
}

// Custom headers (e.g., authentication)
async function fetchProtectedData(token: string) {
const response = await fetchAPI('/api/protected', {
 headers: {
 'Authorization': `Bearer ${token}`
 }
});

return response.data;
}

// DELETE request
async function deleteUser(userId: string) {
const response = await fetchAPI(`/api/users/${userId}`, {
 method: 'DELETE'
});

if (response.error) {
 throw new Error(response.error);
}

return response.status === 204;
}
""",
 "category": "webdev",
 "subcategory": "api-integration",
 "tags": ["api", "fetch", "async", "rest", "http", "request", "response", "typescript", "async-await"]
},
{
 "problem": "Implement robust error handling for API calls with retry logic, timeout handling, and user-friendly error messages.",
 "solution": """
// api/errorHandling.ts
interface RetryOptions {
maxRetries?: number;
retryDelay?: number;
retryOn?: number[];
timeout?: number;
}

class APIError extends Error {
constructor(
 message: string,
 public status: number,
 public code?: string
) {
 super(message);
 this.name = 'APIError';
}
}

// Sleep utility for retry delays
function sleep(ms: number): Promise<void> {
return new Promise(resolve => setTimeout(resolve, ms));
}

// Fetch with timeout
async function fetchWithTimeout(
url: string,
options: RequestInit = {},
timeout: number = 10000
): Promise<Response> {
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), timeout);

try {
 const response = await fetch(url, {
 ...options,
 signal: controller.signal
 });
 clearTimeout(timeoutId);
 return response;
} catch (error: any) {
 clearTimeout(timeoutId);
 if (error.name === 'AbortError') {
 throw new APIError('Request timeout', 408, 'TIMEOUT');
 }
 throw error;
}
}

// Fetch with retry logic
export async function fetchWithRetry<T = any>(
url: string,
options: RequestInit = {},
retryOptions: RetryOptions = {}
): Promise<T> {
const {
 maxRetries = 3,
 retryDelay = 1000,
 retryOn = [408, 429, 500, 502, 503, 504],
 timeout = 10000
} = retryOptions;

let lastError: Error | APIError;
let attempt = 0;

while (attempt <= maxRetries) {
 try {
 const response = await fetchWithTimeout(url, options, timeout);

 // Parse response
 let data: any;
 const contentType = response.headers.get('content-type');

 if (contentType?.includes('application/json')) {
 data = await response.json();
 } else {
 data = await response.text();
 }

 // Handle HTTP errors
 if (!response.ok) {
 const errorMessage = data?.message || response.statusText;
 const error = new APIError(errorMessage, response.status, data?.code);

 // Retry on specific status codes
 if (attempt < maxRetries && retryOn.includes(response.status)) {
 attempt++;
 await sleep(retryDelay * attempt);
 continue;
 }

 throw error;
 }

 return data;

 } catch (error: any) {
 lastError = error;

 // Don't retry on client errors (except timeout)
 if (error.status && error.status >= 400 && error.status < 500 && error.code !== 'TIMEOUT') {
 throw error;
 }

 // Retry on network errors and server errors
 if (attempt < maxRetries) {
 attempt++;
 await sleep(retryDelay * attempt);
 continue;
 }

 throw error;
 }
}

throw lastError!;
}

// User-friendly error handler
export function handleAPIError(error: unknown): string {
if (error instanceof APIError) {
 switch (error.status) {
 case 400:
 return 'Invalid request. Please check your input and try again.';
 case 401:
 return 'You are not authenticated. Please sign in.';
 case 403:
 return 'You do not have permission to perform this action.';
 case 404:
 return 'The requested resource was not found.';
 case 408:
 return 'Request timeout. Please check your connection and try again.';
 case 429:
 return 'Too many requests. Please wait a moment and try again.';
 case 500:
 return 'Server error. Please try again later.';
 case 503:
 return 'Service temporarily unavailable. Please try again later.';
 default:
 return error.message || 'An unexpected error occurred.';
 }
}

if (error instanceof Error) {
 if (error.message.includes('network') || error.message.includes('fetch')) {
 return 'Network error. Please check your internet connection.';
 }
 return error.message;
}

return 'An unexpected error occurred. Please try again.';
}

// React hook for API calls with error handling
import { useState, useCallback } from 'react';

interface UseAPIOptions<T> {
onSuccess?: (data: T) => void;
onError?: (error: string) => void;
retryOptions?: RetryOptions;
}

export function useAPI<T = any>(options: UseAPIOptions<T> = {}) {
const [data, setData] = useState<T | null>(null);
const [error, setError] = useState<string | null>(null);
const [loading, setLoading] = useState(false);

const execute = useCallback(async (url: string, fetchOptions: RequestInit = {}) => {
 setLoading(true);
 setError(null);

 try {
 const result = await fetchWithRetry<T>(url, fetchOptions, options.retryOptions);
 setData(result);
 options.onSuccess?.(result);
 return result;
 } catch (err) {
 const errorMessage = handleAPIError(err);
 setError(errorMessage);
 options.onError?.(errorMessage);
 throw err;
 } finally {
 setLoading(false);
 }
}, [options]);

const reset = useCallback(() => {
 setData(null);
 setError(null);
 setLoading(false);
}, []);

return {
 data,
 error,
 loading,
 execute,
 reset
};
}

// Usage example
function UserListComponent() {
const { data: users, error, loading, execute } = useAPI<User[]>({
 onSuccess: (users) => console.log(`Loaded ${users.length} users`),
 onError: (error) => console.error('Failed to load users:', error),
 retryOptions: {
 maxRetries: 3,
 retryDelay: 1000
 }
});

useEffect(() => {
 execute('/api/users');
}, [execute]);

if (loading) return <div>Loading users...</div>;
if (error) return <div className="error">{error}</div>;
if (!users) return null;

return (
 <ul>
 {users.map(user => (
 <li key={user.id}>{user.name}</li>
 ))}
 </ul>
);
}
""",
 "category": "webdev",
 "subcategory": "api-integration",
 "tags": ["error-handling", "api", "retry", "async", "fetch", "timeout", "rest", "http", "typescript", "hooks"]
}
]
