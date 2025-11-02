"""
Next.js Routing Cases for CBR MCP Server

Contains cases for Next.js 13+ App Router navigation patterns, dynamic routes,
and middleware implementation.
"""

NEXTJS_ROUTING_CASES = [
    {
        "problem": """
A responsive navigation bar in Next.js using react-bootstrap with Next.js Link routing and authentication-aware navigation.
""",
        "solution": """
import { Navbar, Nav, Container, NavDropdown, Button } from 'react-bootstrap';
import Link from 'next/link';
import { useAuth } from '../hooks/useAuth';
import { useRouter } from 'next/router';

const AppNavbar = () => {
  const { user, signOut } = useAuth();
  const router = useRouter();

  const handleSignOut = async () => {
    await signOut();
    router.push('/');
  };

  return (
    <Navbar bg="dark" variant="dark" expand="lg" collapseOnSelect sticky="top">
      <Container>
        <Link href="/" passHref legacyBehavior>
          <Navbar.Brand>
            <img
              src="/logo.svg"
              width="30"
              height="30"
              className="d-inline-block align-top me-2"
              alt="Logo"
            />
            MyApp
          </Navbar.Brand>
        </Link>

        <Navbar.Toggle aria-controls="basic-navbar-nav" />

        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Link href="/" passHref legacyBehavior>
              <Nav.Link active={router.pathname === '/'}>Home</Nav.Link>
            </Link>
            <Link href="/about" passHref legacyBehavior>
              <Nav.Link active={router.pathname === '/about'}>About</Nav.Link>
            </Link>
            <Link href="/contact" passHref legacyBehavior>
              <Nav.Link active={router.pathname === '/contact'}>Contact</Nav.Link>
            </Link>

            {user && (
              <NavDropdown title="Services" id="services-dropdown">
                <Link href="/services/consulting" passHref legacyBehavior>
                  <NavDropdown.Item>Consulting</NavDropdown.Item>
                </Link>
                <Link href="/services/development" passHref legacyBehavior>
                  <NavDropdown.Item>Development</NavDropdown.Item>
                </Link>
                <NavDropdown.Divider />
                <Link href="/services/support" passHref legacyBehavior>
                  <NavDropdown.Item>Support</NavDropdown.Item>
                </Link>
              </NavDropdown>
            )}
          </Nav>

          <Nav>
            {user ? (
              <>
                <Link href="/dashboard" passHref legacyBehavior>
                  <Nav.Link>Dashboard</Nav.Link>
                </Link>
                <NavDropdown title={user.displayName || user.email} id="user-dropdown">
                  <Link href="/profile" passHref legacyBehavior>
                    <NavDropdown.Item>Profile</NavDropdown.Item>
                  </Link>
                  <Link href="/settings" passHref legacyBehavior>
                    <NavDropdown.Item>Settings</NavDropdown.Item>
                  </Link>
                  <NavDropdown.Divider />
                  <NavDropdown.Item onClick={handleSignOut}>
                    Sign Out
                  </NavDropdown.Item>
                </NavDropdown>
              </>
            ) : (
              <>
                <Link href="/login" passHref legacyBehavior>
                  <Nav.Link>Login</Nav.Link>
                </Link>
                <Link href="/signup" passHref>
                  <Button variant="primary" className="ms-2">Sign Up</Button>
                </Link>
              </>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default AppNavbar;
""",
        "category": 'nextjs',
        "subcategory": 'routing',
        "tags": ['nextjs', 'routing', 'navigation', 'link', 'app-router']
    },
    {
        "problem": """
A Next.js page with dynamic route [id] parameter that is server-side rendered (SSR) and fetches data from Firebase Admin SDK.
""",
        "solution": """
import React, { useEffect } from 'react';
import { GetServerSideProps } from 'next';
import Head from 'next/head';
import { Container, Card, Badge, Alert } from 'react-bootstrap';

// Use isomorphic-dompurify for Next.js SSR compatibility (provides DOM implementation in Node.js)
// Requires: isomorphic-dompurify ^2.0.0 (includes DOMPurify 3.2.4+ with CVE-2025-26791 fix)
import DOMPurify from 'isomorphic-dompurify';

import { adminDb } from '../lib/firebase-admin';

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

// Define security hook outside component for stable reference (prevents memory leaks)
const securityHook = (node: any) => {
  if (node.nodeName === 'A') {
    // Enforce noopener noreferrer on external links (prevents reverse tabnapping)
    if (node.getAttribute('target') === '_blank') {
      node.setAttribute('rel', 'noopener noreferrer');
    }
    // Defense-in-depth: Block javascript: protocol (redundant with ALLOWED_URI_REGEXP but safe)
    const href = node.getAttribute('href');
    if (href && href.toLowerCase().startsWith('javascript:')) {
      node.removeAttribute('href');
    }
  }
};

const PostPage: React.FC<PostPageProps> = ({ post, error }) => {
  // Register DOMPurify hook once on component mount with stable reference
  useEffect(() => {
    DOMPurify.addHook('afterSanitizeAttributes', securityHook);

    // Cleanup: Remove hook on component unmount using same reference
    return () => {
      DOMPurify.removeHook('afterSanitizeAttributes', securityHook);
    };
  }, []);

  if (error) {
    return (
      <Container className="mt-5">
        <Alert variant="danger">{error}</Alert>
      </Container>
    );
  }

  if (!post) {
    return null;
  }

  return (
    <>
      <Head>
        <title>{post.title}</title>
        <meta name="description" content={post.content.substring(0, 160)} />
      </Head>

      <Container className="mt-5">
        <Card>
          <Card.Header>
            <h1>{post.title}</h1>
            <div className="d-flex justify-content-between align-items-center">
              <small className="text-muted">
                By {post.authorName} • {new Date(post.createdAt).toLocaleDateString()}
              </small>
              <small className="text-muted">{post.views} views</small>
            </div>
          </Card.Header>
          <Card.Body>
            {/* XSS Prevention: DOMPurify sanitizes user HTML per OWASP A03:2021 (Injection) */}
            <div dangerouslySetInnerHTML={{
              __html: DOMPurify.sanitize(post.content, {
                ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
                ALLOWED_ATTR: ['href', 'target', 'rel'],
                // Allow https://, mailto:, absolute paths (/), relative paths (./), and hash links (#)
                ALLOWED_URI_REGEXP: /^(?:(?:https?|mailto):\/\/|\/(?!\/)[\w\-\/]*|\.\/[\w\-\/]+|\#[\w\-]+)$/i,
                KEEP_CONTENT: false,          // Remove disallowed tags entirely
                RETURN_DOM: false,            // Return string, not DOM object
                RETURN_DOM_FRAGMENT: false,   // Return string, not fragment
                RETURN_DOM_IMPORT: false,     // Don't create importable node
                FORCE_BODY: true,             // Wrap in <body> for consistent parsing
                WHOLE_DOCUMENT: false,        // Sanitize fragment, not full document
                SANITIZE_DOM: true            // Enable DOM sanitization
              })
            }} />
          </Card.Body>
          <Card.Footer>
            {post.tags.map((tag) => (
              <Badge key={tag} bg="secondary" className="me-2">
                {tag}
              </Badge>
            ))}
          </Card.Footer>
        </Card>
      </Container>
    </>
  );
};

export default PostPage;
""",
        "category": 'nextjs',
        "subcategory": 'routing',
        "tags": ['nextjs', 'routing', 'dynamic-routes', 'params', 'slug']
    },
    {
        "problem": """
Implement Content Security Policy (CSP) headers and security middleware in Next.js to prevent XSS attacks.
""",
        "solution": """
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import crypto from 'crypto';

export function middleware(request: NextRequest) {
  const nonce = crypto.randomBytes(16).toString('base64');
  const cspHeader = `
    default-src 'self';
    script-src 'self' 'nonce-${nonce}' 'strict-dynamic' https: 'unsafe-inline' ${
      process.env.NODE_ENV === 'development' ? "'unsafe-eval'" : ''
    };
    style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net;
    img-src 'self' blob: data: https:;
    font-src 'self' https://fonts.gstatic.com;
    object-src 'none';
    base-uri 'self';
    form-action 'self';
    frame-ancestors 'none';
    block-all-mixed-content;
    upgrade-insecure-requests;
    connect-src 'self' https://identitytoolkit.googleapis.com https://firestore.googleapis.com https://firebase.googleapis.com wss://*.firebaseio.com;
  `.replace(/\s{2,}/g, ' ').trim();

  const requestHeaders = new Headers(request.headers);
  requestHeaders.set('x-nonce', nonce);
  requestHeaders.set('Content-Security-Policy', cspHeader);

  const response = NextResponse.next({
    request: {
      headers: requestHeaders,
    },
  });

  // Add security headers
  response.headers.set('Content-Security-Policy', cspHeader);
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set('X-XSS-Protection', '1; mode=block');
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');
  response.headers.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');

  return response;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};

// pages/_document.tsx (for Pages Router) or app/layout.tsx (for App Router)
import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        {/* Additional security meta tags */}
        <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
        <meta name="format-detection" content="telephone=no" />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}

// utils/security.ts
export const sanitizeInput = (input: string): string => {
  // Remove any HTML tags and script injections
  return input
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/<[^>]+>/g, '')
    .trim();
};

export const validateOrigin = (origin: string | null): boolean => {
  const allowedOrigins = process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'];
  return origin ? allowedOrigins.includes(origin) : false;
};
""",
        "category": 'nextjs',
        "subcategory": 'routing',
        "tags": ['nextjs', 'routing', 'middleware', 'edge', 'request']
    },
    {
        "problem": """
A Next.js page component that fetches data at build time using getStaticProps.
""",
        "solution": """
import { GetStaticProps } from 'next';
import { Container, Row, Col, Card } from 'react-bootstrap';

interface Post {
  id: string;
  title: string;
  excerpt: string;
  publishedAt: string;
}

interface BlogProps {
  posts: Post[];
}

export const getStaticProps: GetStaticProps<BlogProps> = async () => {
  try {
    const res = await fetch('https://api.example.com/posts');

    if (!res.ok) {
      throw new Error('Failed to fetch posts');
    }

    const posts = await res.json();

    return {
      props: {
        posts,
      },
      // Re-generate page every 60 seconds
      revalidate: 60,
    };
  } catch (error) {
    console.error('Error fetching posts:', error);
    return {
      props: {
        posts: [],
      },
      revalidate: 60,
    };
  }
};

function Blog({ posts }: BlogProps) {
  if (posts.length === 0) {
    return (
      <Container className="py-5">
        <p>No posts available at the moment.</p>
      </Container>
    );
  }

  return (
    <Container className="py-5">
      <h1 className="mb-4">Blog Posts</h1>
      <Row>
        {posts.map((post) => (
          <Col key={post.id} md={6} lg={4} className="mb-4">
            <Card h-100>
              <Card.Body>
                <Card.Title>{post.title}</Card.Title>
                <Card.Text>{post.excerpt}</Card.Text>
                <small className="text-muted">
                  {new Date(post.publishedAt).toLocaleDateString()}
                </small>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </Container>
  );
}

export default Blog;
""",
        "category": 'nextjs',
        "subcategory": 'routing',
        "tags": ['nextjs', 'routing', 'async', 'bootstrap', 'http', 'json', 'api']
    }
]
