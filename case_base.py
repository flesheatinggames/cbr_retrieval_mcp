"""
Case-Based Reasoning Dataset for Next.js/Firebase/Bootstrap Projects
Enhanced with production-ready code examples, TypeScript support, and best practices
"""

CASE_BASE = [
    # ============================================
    # FIREBASE AUTHENTICATION
    # ============================================
    {
        "problem": "A React component for user sign-up with Firebase Authentication.",
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
"""
    },
    {
        "problem": "A React hook to get the current Firebase authentication user state in real-time.",
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
"""
    },
    {
        "problem": "A function to sign in a user with Google using Firebase Authentication popup.",
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
"""
    },
    {
        "problem": "A function to sign out the current user from Firebase.",
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
"""
    },
    # ============================================
    # FIRESTORE CRUD OPERATIONS
    # ============================================
    {
        "problem": "A function to add a new document to a 'users' collection in Firestore.",
        "solution": """
import { getFirestore, collection, addDoc, serverTimestamp, doc, setDoc } from 'firebase/firestore';

interface UserData {
  displayName: string;
  email: string;
  photoURL?: string;
  bio?: string;
  [key: string]: any;
}

// Option 1: Auto-generated ID
const addUserProfile = async (userId: string, userData: UserData) => {
  const db = getFirestore();
  try {
    const docRef = await addDoc(collection(db, 'users'), {
      uid: userId,
      ...userData,
      createdAt: serverTimestamp(),
      updatedAt: serverTimestamp()
    });
    console.log("Document written with ID: ", docRef.id);
    return docRef.id;
  } catch (error) {
    console.error("Error adding document: ", error);
    return null;
  }
};

// Option 2: Use user ID as document ID (recommended for user profiles)
const setUserProfile = async (userId: string, userData: UserData) => {
  const db = getFirestore();
  try {
    await setDoc(doc(db, 'users', userId), {
      ...userData,
      createdAt: serverTimestamp(),
      updatedAt: serverTimestamp()
    }, { merge: true }); // Merge to avoid overwriting existing data
    
    return userId;
  } catch (error) {
    console.error("Error setting document: ", error);
    return null;
  }
};

export { addUserProfile, setUserProfile };
"""
    },
    {
        "problem": "A React hook to fetch a single document from Firestore by its ID.",
        "solution": """
import { useState, useEffect } from 'react';
import { getFirestore, doc, getDoc, onSnapshot } from 'firebase/firestore';

interface UseFirestoreDocumentOptions {
  realtime?: boolean;
}

const useFirestoreDocument = <T = any>(
  collectionPath: string,
  docId: string | null | undefined,
  options: UseFirestoreDocumentOptions = {}
) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const { realtime = false } = options;

  useEffect(() => {
    if (!docId) {
      setLoading(false);
      setData(null);
      return;
    }

    const db = getFirestore();
    const docRef = doc(db, collectionPath, docId);

    if (realtime) {
      // Real-time listener
      const unsubscribe = onSnapshot(
        docRef,
        (docSnap) => {
          if (docSnap.exists()) {
            setData({ id: docSnap.id, ...docSnap.data() } as T);
          } else {
            setData(null);
          }
          setLoading(false);
          setError(null);
        },
        (err) => {
          console.error('Document listener error:', err);
          setError(err);
          setLoading(false);
        }
      );

      return () => unsubscribe();
    } else {
      // One-time fetch
      const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
          const docSnap = await getDoc(docRef);
          if (docSnap.exists()) {
            setData({ id: docSnap.id, ...docSnap.data() } as T);
          } else {
            setData(null);
          }
        } catch (err) {
          setError(err as Error);
        } finally {
          setLoading(false);
        }
      };

      fetchData();
    }
  }, [collectionPath, docId, realtime]);

  return { data, loading, error };
};

export default useFirestoreDocument;
"""
    },
    {
        "problem": "A React hook to listen for real-time updates on a Firestore collection.",
        "solution": """
import { useState, useEffect } from 'react';
import { getFirestore, collection, onSnapshot, query, orderBy, where, limit, QueryConstraint } from 'firebase/firestore';

interface UseFirestoreCollectionOptions {
  orderByField?: string;
  orderDirection?: 'asc' | 'desc';
  limitResults?: number;
  filters?: Array<{
    field: string;
    operator: any;
    value: any;
  }>;
}

const useFirestoreCollection = <T = any>(
  collectionPath: string,
  options: UseFirestoreCollectionOptions = {}
) => {
  const [data, setData] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const db = getFirestore();
    const collectionRef = collection(db, collectionPath);
    
    // Build query constraints
    const constraints: QueryConstraint[] = [];
    
    // Add filters
    if (options.filters) {
      options.filters.forEach(filter => {
        constraints.push(where(filter.field, filter.operator, filter.value));
      });
    }
    
    // Add ordering
    if (options.orderByField) {
      constraints.push(orderBy(options.orderByField, options.orderDirection || 'desc'));
    } else {
      constraints.push(orderBy('createdAt', 'desc'));
    }
    
    // Add limit
    if (options.limitResults) {
      constraints.push(limit(options.limitResults));
    }
    
    const q = query(collectionRef, ...constraints);

    const unsubscribe = onSnapshot(
      q,
      (querySnapshot) => {
        const items: T[] = [];
        querySnapshot.forEach((doc) => {
          items.push({ id: doc.id, ...doc.data() } as T);
        });
        setData(items);
        setLoading(false);
        setError(null);
      },
      (err) => {
        console.error('Collection listener error:', err);
        setError(err);
        setLoading(false);
      }
    );

    return () => unsubscribe();
  }, [collectionPath, JSON.stringify(options)]);

  return { data, loading, error };
};

export default useFirestoreCollection;
"""
    },
    {
        "problem": "A function to update an existing document in Firestore.",
        "solution": """
import { getFirestore, doc, updateDoc, serverTimestamp, writeBatch } from 'firebase/firestore';

interface UpdateData {
  [key: string]: any;
}

const updateUserProfile = async (docId: string, updatedData: UpdateData) => {
  const db = getFirestore();
  const userDocRef = doc(db, 'users', docId);
  
  try {
    // Add updatedAt timestamp
    const dataWithTimestamp = {
      ...updatedData,
      updatedAt: serverTimestamp()
    };
    
    await updateDoc(userDocRef, dataWithTimestamp);
    console.log("Document successfully updated!");
    return { success: true };
  } catch (error) {
    console.error("Error updating document: ", error);
    return { success: false, error };
  }
};

// Batch update multiple documents
const batchUpdateDocuments = async (
  collectionName: string,
  updates: Array<{ id: string; data: UpdateData }>
) => {
  const db = getFirestore();
  const batch = writeBatch(db);
  
  try {
    updates.forEach(({ id, data }) => {
      const docRef = doc(db, collectionName, id);
      batch.update(docRef, {
        ...data,
        updatedAt: serverTimestamp()
      });
    });
    
    await batch.commit();
    return { success: true };
  } catch (error) {
    console.error("Batch update error:", error);
    return { success: false, error };
  }
};

export { updateUserProfile, batchUpdateDocuments };
"""
    },
    # ============================================
    # NEXT.JS SPECIFICS
    # ============================================
    {
        "problem": "A Next.js page component that fetches data at build time using getStaticProps.",
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
"""
    },
    {
        "problem": "A Next.js API route that handles a POST request.",
        "solution": """
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
"""
    },
    {
        "problem": "A custom _app.js file in Next.js with a global layout component.",
        "solution": """
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
"""
    },
    # ============================================
    # BOOTSTRAP COMPONENTS IN REACT
    # ============================================
    {
        "problem": "A responsive navigation bar in a React component using react-bootstrap.",
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
"""
    },
    {
        "problem": "A React component that displays a Bootstrap modal dialog.",
        "solution": """
import { useState } from 'react';
import { Button, Modal, Form } from 'react-bootstrap';

interface ConfirmationModalProps {
  show: boolean;
  handleClose: () => void;
  title: string;
  children: React.ReactNode;
  onConfirm: () => void | Promise<void>;
  confirmText?: string;
  cancelText?: string;
  confirmVariant?: string;
}

const ConfirmationModal: React.FC<ConfirmationModalProps> = ({ 
  show, 
  handleClose, 
  title, 
  children, 
  onConfirm,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  confirmVariant = 'primary'
}) => {
  const [isProcessing, setIsProcessing] = useState(false);
  
  const handleConfirm = async () => {
    setIsProcessing(true);
    try {
      await onConfirm();
      handleClose();
    } catch (error) {
      console.error('Confirmation error:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <Modal 
      show={show} 
      onHide={handleClose} 
      centered
      backdrop={isProcessing ? 'static' : true}
      keyboard={!isProcessing}
    >
      <Modal.Header closeButton={!isProcessing}>
        <Modal.Title>{title}</Modal.Title>
      </Modal.Header>
      <Modal.Body>{children}</Modal.Body>
      <Modal.Footer>
        <Button 
          variant="secondary" 
          onClick={handleClose}
          disabled={isProcessing}
        >
          {cancelText}
        </Button>
        <Button 
          variant={confirmVariant}
          onClick={handleConfirm}
          disabled={isProcessing}
        >
          {isProcessing ? 'Processing...' : confirmText}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ConfirmationModal;
"""
    },
    {
        "problem": "A Bootstrap-styled form with validation feedback in React.",
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
"""
    },
    {
        "problem": "A React component that displays data in a responsive Bootstrap grid.",
        "solution": """
import { Container, Row, Col, Card, Badge, Button } from 'react-bootstrap';

interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  imageUrl: string;
  rating: number;
  inStock: boolean;
  category: string;
}

interface ProductGridProps {
  products: Product[];
  onAddToCart?: (product: Product) => void;
}

const ProductGrid: React.FC<ProductGridProps> = ({ products, onAddToCart }) => {
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  if (products.length === 0) {
    return (
      <Container className="py-5 text-center">
        <h3>No products found</h3>
        <p className="text-muted">Try adjusting your filters or search criteria</p>
      </Container>
    );
  }

  return (
    <Container>
      <Row className="g-4">
        {products.map((product) => (
          <Col key={product.id} xs={12} sm={6} md={4} lg={3}>
            <Card className="h-100 product-card">
              <div className="position-relative">
                <Card.Img 
                  variant="top" 
                  src={product.imageUrl}
                  alt={product.name}
                  style={{ height: '200px', objectFit: 'cover' }}
                />
                {!product.inStock && (
                  <Badge 
                    bg="danger" 
                    className="position-absolute top-0 end-0 m-2"
                  >
                    Out of Stock
                  </Badge>
                )}
                <Badge 
                  bg="secondary" 
                  className="position-absolute top-0 start-0 m-2"
                >
                  {product.category}
                </Badge>
              </div>
              
              <Card.Body className="d-flex flex-column">
                <Card.Title className="h6">{product.name}</Card.Title>
                <Card.Text className="small text-muted flex-grow-1">
                  {product.description.length > 100
                    ? `${product.description.substring(0, 100)}...`
                    : product.description}
                </Card.Text>
                
                <div className="d-flex justify-content-between align-items-center mt-3">
                  <span className="h5 mb-0 text-primary">
                    {formatPrice(product.price)}
                  </span>
                  <Button
                    size="sm"
                    variant={product.inStock ? 'primary' : 'secondary'}
                    disabled={!product.inStock}
                    onClick={() => onAddToCart?.(product)}
                  >
                    {product.inStock ? 'Add to Cart' : 'Unavailable'}
                  </Button>
                </div>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </Container>
  );
};

export default ProductGrid;
"""
    },
    # ============================================
    # COMBINED EXAMPLES
    # ============================================
    {
        "problem": "A Next.js page that is server-side rendered (SSR) and fetches data from Firebase Admin SDK.",
        "solution": """
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
"""
    },
    {
        "problem": "A higher-order component (HOC) in React to protect routes based on Firebase auth state.",
        "solution": """
import { useRouter } from 'next/router';
import { useAuth } from '../hooks/useAuth';
import { Container, Spinner, Alert } from 'react-bootstrap';
import { useEffect, ComponentType, useState } from 'react';

interface WithAuthOptions {
  redirectTo?: string;
  requireEmailVerification?: boolean;
  allowedRoles?: string[];
  LoadingComponent?: ComponentType;
  UnauthorizedComponent?: ComponentType;
}

function withAuth<P extends object>(
  WrappedComponent: ComponentType<P>,
  options: WithAuthOptions = {}
) {
  const {
    redirectTo = '/login',
    requireEmailVerification = false,
    allowedRoles = [],
    LoadingComponent,
    UnauthorizedComponent
  } = options;

  const WithAuthComponent = (props: P) => {
    const router = useRouter();
    const { user, loading } = useAuth();
    const [isAuthorized, setIsAuthorized] = useState(false);

    useEffect(() => {
      const checkAuth = async () => {
        if (loading) return;

        if (!user) {
          const currentPath = router.asPath;
          sessionStorage.setItem('redirectAfterLogin', currentPath);
          router.replace(redirectTo);
          return;
        }

        if (requireEmailVerification && !user.emailVerified) {
          router.replace('/verify-email');
          return;
        }

        if (allowedRoles.length > 0) {
          try {
            const idTokenResult = await user.getIdTokenResult();
            const userRole = idTokenResult.claims.role || 'user';
            
            if (!allowedRoles.includes(userRole)) {
              setIsAuthorized(false);
              return;
            }
          } catch (error) {
            console.error('Error checking user role:', error);
            setIsAuthorized(false);
            return;
          }
        }

        setIsAuthorized(true);
      };

      checkAuth();
    }, [user, loading, router]);

    if (loading) {
      if (LoadingComponent) {
        return <LoadingComponent />;
      }
      return (
        <Container className="d-flex justify-content-center align-items-center" style={{ minHeight: '100vh' }}>
          <Spinner animation="border" />
        </Container>
      );
    }

    if (!user) {
      return null;
    }

    if (requireEmailVerification && !user.emailVerified) {
      return (
        <Container className="py-5">
          <Alert variant="warning">
            Please verify your email address to access this page.
          </Alert>
        </Container>
      );
    }

    if (allowedRoles.length > 0 && !isAuthorized) {
      if (UnauthorizedComponent) {
        return <UnauthorizedComponent />;
      }
      return (
        <Container className="py-5">
          <Alert variant="danger">
            You don't have permission to access this page.
          </Alert>
        </Container>
      );
    }

    return <WrappedComponent {...props} />;
  };

  WithAuthComponent.displayName = `withAuth(${WrappedComponent.displayName || WrappedComponent.name || 'Component'})`;

  return WithAuthComponent;
}

export default withAuth;
"""
    },
    {
        "problem": "A React component that fetches a list of items from Firestore and displays them as Bootstrap Cards.",
        "solution": """
import { Card, Container, Row, Col, Spinner, Alert, Button, Badge } from 'react-bootstrap';
import useFirestoreCollection from '../hooks/useFirestoreCollection';

interface Item {
  id: string;
  name: string;
  description: string;
  category: string;
  status: 'active' | 'inactive' | 'pending';
  createdAt: any;
  imageUrl?: string;
}

const ItemList = () => {
  const { data: items, loading, error } = useFirestoreCollection<Item>('items', {
    orderByField: 'createdAt',
    orderDirection: 'desc',
    filters: [
      { field: 'status', operator: '!=', value: 'inactive' }
    ]
  });

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'secondary';
      case 'pending': return 'warning';
      default: return 'light';
    }
  };

  if (loading) {
    return (
      <Container className="d-flex justify-content-center py-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="py-5">
        <Alert variant="danger">
          Error loading items: {error.message}
        </Alert>
      </Container>
    );
  }

  if (items.length === 0) {
    return (
      <Container className="py-5">
        <Alert variant="info">
          No items found. Create your first item to get started!
        </Alert>
      </Container>
    );
  }

  return (
    <Container className="py-5">
      <h2 className="mb-4">Items ({items.length})</h2>
      
      <Row className="g-4">
        {items.map(item => (
          <Col key={item.id} xs={12} sm={6} lg={4}>
            <Card className="h-100 shadow-sm">
              {item.imageUrl && (
                <Card.Img 
                  variant="top" 
                  src={item.imageUrl} 
                  style={{ height: '200px', objectFit: 'cover' }}
                />
              )}
              <Card.Body>
                <div className="d-flex justify-content-between align-items-start mb-2">
                  <Card.Title className="h5">{item.name}</Card.Title>
                  <Badge bg={getStatusBadgeVariant(item.status)}>
                    {item.status}
                  </Badge>
                </div>
                
                <Card.Text className="text-muted">
                  {item.description}
                </Card.Text>
                
                <div className="d-flex justify-content-between align-items-center">
                  <small className="text-muted">
                    {item.createdAt?.toDate?.()?.toLocaleDateString() || 'N/A'}
                  </small>
                  
                  <div>
                    <Button variant="link" size="sm">View</Button>
                    <Button variant="link" size="sm">Edit</Button>
                    <Button variant="link" size="sm" className="text-danger">Delete</Button>
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </Container>
  );
};

export default ItemList;
"""
    },
    {
        "problem": "A Next.js API route to add a document to Firestore using the Firebase Admin SDK.",
        "solution": """
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
"""
    },
    {
        "problem": "A React component with a button that triggers a Firebase Cloud Function when clicked.",
        "solution": """
import { useState } from 'react';
import { getFunctions, httpsCallable } from 'firebase/functions';
import { Button, Alert, Spinner, Card, Form } from 'react-bootstrap';

interface ProcessDataRequest {
  input: string;
  options?: {
    format: 'json' | 'csv';
    compress: boolean;
  };
}

interface ProcessDataResponse {
  success: boolean;
  processedData: any;
  processingTime: number;
  message?: string;
}

const CloudFunctionButton = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ProcessDataResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [inputData, setInputData] = useState('');

  const callCloudFunction = async () => {
    if (!inputData.trim()) {
      setError('Please enter some data to process');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const functions = getFunctions();
      const processData = httpsCallable<ProcessDataRequest, ProcessDataResponse>(
        functions, 
        'processData'
      );
      
      const response = await processData({
        input: inputData,
        options: {
          format: 'json',
          compress: inputData.length > 1000
        }
      });
      
      setResult(response.data);
      console.log('Function result:', response.data);
      
      if (response.data.success) {
        setInputData('');
      }
    } catch (error: any) {
      console.error('Error calling cloud function:', error);
      setError(error.message || 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <Card.Body>
        <Card.Title>Cloud Function Demo</Card.Title>
        
        <Form>
          <Form.Group className="mb-3">
            <Form.Label>Input Data</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              placeholder="Enter data to process..."
              value={inputData}
              onChange={(e) => setInputData(e.target.value)}
              disabled={loading}
            />
          </Form.Group>
          
          <Button 
            onClick={callCloudFunction}
            disabled={loading || !inputData.trim()}
            variant="primary"
            className="w-100"
          >
            {loading ? (
              <>
                <Spinner size="sm" className="me-2" />
                Processing...
              </>
            ) : (
              'Run Processing Task'
            )}
          </Button>
        </Form>
        
        {error && (
          <Alert variant="danger" className="mt-3" dismissible onClose={() => setError(null)}>
            {error}
          </Alert>
        )}
        
        {result && (
          <Alert variant={result.success ? 'success' : 'warning'} className="mt-3">
            <Alert.Heading>
              {result.success ? 'Success!' : 'Processing Complete'}
            </Alert.Heading>
            {result.message && <p>{result.message}</p>}
            <hr />
            <p className="mb-0">
              Processing Time: {result.processingTime}ms
            </p>
          </Alert>
        )}
      </Card.Body>
    </Card>
  );
};

export default CloudFunctionButton;
"""
    }
]

# Additional Security-Focused Cases for Next.js/Firebase/Bootstrap
# Add these cases to your existing CASE_BASE list

SECURITY_CASES = [
    {
        "problem": "Implement Content Security Policy (CSP) headers and security middleware in Next.js to prevent XSS attacks.",
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
"""
    },
    {
        "problem": "Secure Firebase Storage uploads with file validation, size limits, and malware scanning simulation.",
        "solution": """
import { getStorage, ref, uploadBytesResumable, deleteObject } from 'firebase/storage';
import { getAuth } from 'firebase/auth';
import crypto from 'crypto';

interface FileValidationOptions {
  maxSizeMB?: number;
  allowedTypes?: string[];
  requireAuth?: boolean;
  scanForMalware?: boolean;
}

interface ValidationResult {
  isValid: boolean;
  error?: string;
}

class SecureStorageService {
  private storage = getStorage();
  private auth = getAuth();

  // File validation
  private validateFile(file: File, options: FileValidationOptions): ValidationResult {
    const {
      maxSizeMB = 10,
      allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'],
      requireAuth = true,
      scanForMalware = true
    } = options;

    // Check authentication
    if (requireAuth && !this.auth.currentUser) {
      return { isValid: false, error: 'User must be authenticated to upload files' };
    }

    // Check file size
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      return { isValid: false, error: `File size exceeds ${maxSizeMB}MB limit` };
    }

    // Check file type
    if (!allowedTypes.includes(file.type)) {
      return { isValid: false, error: `File type ${file.type} is not allowed` };
    }

    // Check file extension matches MIME type
    const extension = file.name.split('.').pop()?.toLowerCase();
    const expectedExtensions: { [key: string]: string[] } = {
      'image/jpeg': ['jpg', 'jpeg'],
      'image/png': ['png'],
      'image/gif': ['gif'],
      'application/pdf': ['pdf']
    };

    const validExtensions = expectedExtensions[file.type];
    if (validExtensions && !validExtensions.includes(extension || '')) {
      return { isValid: false, error: 'File extension does not match file type' };
    }

    // Check for suspicious file names
    const suspiciousPatterns = [
      /\.exe$/i,
      /\.dll$/i,
      /\.bat$/i,
      /\.cmd$/i,
      /\.scr$/i,
      /\.vbs$/i,
      /\.js$/i,
      /\.jar$/i,
      /\.zip$/i,
      /\.rar$/i,
      /<script/i,
      /javascript:/i,
      /on\w+=/i
    ];

    for (const pattern of suspiciousPatterns) {
      if (pattern.test(file.name)) {
        return { isValid: false, error: 'Suspicious filename detected' };
      }
    }

    return { isValid: true };
  }

  // Simulate malware scanning (in production, use a real service like VirusTotal API)
  private async scanForMalware(file: File): Promise<boolean> {
    return new Promise((resolve) => {
      // Read first few bytes to check for known malicious signatures
      const reader = new FileReader();
      reader.onloadend = () => {
        const arr = new Uint8Array(reader.result as ArrayBuffer);
        
        // Check for common malicious file signatures
        const signatures = [
          [0x4D, 0x5A], // EXE files
          [0x7F, 0x45, 0x4C, 0x46], // ELF files
          [0x50, 0x4B, 0x03, 0x04], // ZIP files (could contain malware)
        ];

        for (const signature of signatures) {
          if (arr.length >= signature.length) {
            let match = true;
            for (let i = 0; i < signature.length; i++) {
              if (arr[i] !== signature[i]) {
                match = false;
                break;
              }
            }
            if (match) {
              resolve(false); // Potentially malicious
              return;
            }
          }
        }
        
        resolve(true); // Appears safe
      };
      
      // Read first 512 bytes
      reader.readAsArrayBuffer(file.slice(0, 512));
    });
  }

  // Generate secure file path
  private generateSecurePath(userId: string, file: File): string {
    const timestamp = Date.now();
    const randomString = crypto.randomBytes(16).toString('hex');
    const sanitizedFileName = file.name.replace(/[^a-z0-9.-]/gi, '_');
    const extension = sanitizedFileName.split('.').pop();
    
    // Structure: users/{userId}/uploads/{year}/{month}/{timestamp}_{random}.{ext}
    const date = new Date();
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    
    return `users/${userId}/uploads/${year}/${month}/${timestamp}_${randomString}.${extension}`;
  }

  // Secure upload with validation
  async secureUpload(
    file: File,
    options: FileValidationOptions = {},
    onProgress?: (progress: number) => void
  ): Promise<{ url: string; path: string } | { error: string }> {
    try {
      // Validate file
      const validation = this.validateFile(file, options);
      if (!validation.isValid) {
        return { error: validation.error! };
      }

      // Scan for malware if enabled
      if (options.scanForMalware !== false) {
        const isSafe = await this.scanForMalware(file);
        if (!isSafe) {
          console.error('Malware detected in file:', file.name);
          return { error: 'File failed security scan' };
        }
      }

      const user = this.auth.currentUser;
      if (!user) {
        return { error: 'User not authenticated' };
      }

      // Generate secure path
      const path = this.generateSecurePath(user.uid, file);
      const storageRef = ref(this.storage, path);

      // Create metadata with security context
      const metadata = {
        contentType: file.type,
        customMetadata: {
          uploadedBy: user.uid,
          uploadedAt: new Date().toISOString(),
          originalName: file.name,
          fileSize: String(file.size),
          validated: 'true',
          scanned: options.scanForMalware !== false ? 'true' : 'false'
        },
        // Set cache control for security
        cacheControl: 'private, max-age=3600',
        // Add content disposition to prevent XSS via file uploads
        contentDisposition: 'attachment'
      };

      // Upload with resumable upload for reliability
      const uploadTask = uploadBytesResumable(storageRef, file, metadata);

      return new Promise((resolve, reject) => {
        uploadTask.on(
          'state_changed',
          (snapshot) => {
            const progress = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
            onProgress?.(progress);
          },
          (error) => {
            console.error('Upload error:', error);
            reject({ error: 'Upload failed: ' + error.message });
          },
          async () => {
            try {
              const downloadURL = await getDownloadURL(uploadTask.snapshot.ref);
              
              // Log successful upload for audit
              console.log('Secure upload completed:', {
                userId: user.uid,
                path,
                timestamp: new Date().toISOString()
              });
              
              resolve({ url: downloadURL, path });
            } catch (error) {
              reject({ error: 'Failed to get download URL' });
            }
          }
        );
      });
    } catch (error: any) {
      console.error('Secure upload error:', error);
      return { error: error.message || 'Upload failed' };
    }
  }

  // Secure file deletion with ownership check
  async secureDelete(path: string): Promise<boolean> {
    try {
      const user = this.auth.currentUser;
      if (!user) {
        throw new Error('User not authenticated');
      }

      // Verify the file belongs to the current user
      if (!path.startsWith(`users/${user.uid}/`)) {
        throw new Error('Unauthorized: Cannot delete files from other users');
      }

      const storageRef = ref(this.storage, path);
      await deleteObject(storageRef);
      
      console.log('File securely deleted:', {
        userId: user.uid,
        path,
        timestamp: new Date().toISOString()
      });
      
      return true;
    } catch (error: any) {
      console.error('Secure delete error:', error);
      return false;
    }
  }
}

export const secureStorage = new SecureStorageService();
"""
    },
    {
        "problem": "Implement rate limiting and DDoS protection for Next.js API routes with Redis.",
        "solution": """
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
      /\0/, // Null byte injection
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
"""
    },
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
"""
    },
    {
        "problem": "Implement input sanitization and SQL/NoSQL injection prevention for Firestore queries.",
        "solution": """
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
"""
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
"""
    },
    {
        "problem": "Implement secure error handling and logging that doesn't expose sensitive information in production.",
        "solution": """
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
      { pattern: /\b([A-Za-z0-9_\-]{20,})\b/g, replacement: '[REDACTED_TOKEN]' },
      { pattern: /(api[_-]?key|apikey|api_secret)([\"']?\s*[:=]\s*[\"']?)([^\"'\s]+)/gi, replacement: '$1$2[REDACTED_API_KEY]' },
      { pattern: /(bearer|token|jwt)[\s:]+([^\s]+)/gi, replacement: '$1 [REDACTED_TOKEN]' },
      
      // Passwords
      { pattern: /(password|passwd|pwd)([\"']?\s*[:=]\s*[\"']?)([^\"'\s]+)/gi, replacement: '$1$2[REDACTED_PASSWORD]' },
      
      // Credit cards
      { pattern: /\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/g, replacement: '[REDACTED_CARD]' },
      { pattern: /\b\d{3,4}\b/g, replacement: '[CVV]' },
      
      // Social Security Numbers
      { pattern: /\b\d{3}-\d{2}-\d{4}\b/g, replacement: '[REDACTED_SSN]' },
      
      // Email addresses (partial redaction)
      { pattern: /([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g, replacement: (match, user, domain) => {
        const redactedUser = user.substring(0, 2) + '***';
        return `${redactedUser}@${domain}`;
      }},
      
      // Phone numbers
      { pattern: /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g, replacement: '[REDACTED_PHONE]' },
      
      // IP addresses (partial redaction)
      { pattern: /\b(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\b/g, replacement: '$1.$2.XXX.XXX' },
      
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
import { Alert, Container } from 'react-bootstrap';

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
"""
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
"""
    }
]

# ============================================
# CLAUDE ORCHESTRATION EXAMPLES
# ============================================

ORCHESTRATION_EXAMPLES = [
    {
        "problem": "Refactor the PaymentProcessor service to use the new StripeClient instead of the legacy BraintreeClient.",
        "solution": """
<sequential-thinking>
The user wants to refactor a service. This involves changing implementation details while ensuring behavior remains the same. A Test-Driven Development (TDD) approach is safest.

1.  **Write Refactoring Tests:** Ensure existing tests cover all legacy client behavior. Write new tests for the StripeClient if needed.
    -   Agent: tdd-test-engineer
    -   Verification: karen
2.  **Implement Refactor:** Swap the BraintreeClient with the new StripeClient.
    -   Agent: rust-developer
    -   Verification: karen (ensure all tests pass)
3.  **Final Review:** Review the refactored code for quality and correctness.
    -   Agent: code-reviewer (blocking)

This translates to 5 delegation steps.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to tdd-test-engineer to write integration tests for the PaymentProcessor service using the new StripeClient",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer to write refactoring tests"
    },
    {
        "content": "Delegate to karen to verify the new tests for the PaymentProcessor service",
        "status": "pending",
        "activeForm": "Delegating to karen to verify refactoring tests"
    },
    {
        "content": "Delegate to rust-developer to refactor the PaymentProcessor service to use StripeClient",
        "status": "pending",
        "activeForm": "Delegating to rust-developer to implement refactor"
    },
    {
        "content": "Delegate to karen to verify the PaymentProcessor refactor passes all tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify refactor implementation"
    },
    {
        "content": "Delegate to code-reviewer to review the refactored PaymentProcessor service code",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for final review"
    }
]
</TodoWrite>

## Plan for PaymentProcessor Refactor

1.  **Write Tests:** Delegate to **tdd-test-engineer** to create tests ensuring the new `StripeClient` behaves as expected within the `PaymentProcessor`.
2.  **Verify Tests:** Delegate to **karen** to confirm test quality and coverage.
3.  **Implement Refactor:** Delegate to **rust-developer** to perform the refactoring.
4.  **Verify Implementation:** Delegate to **karen** to ensure all existing and new tests pass.
5.  **Code Review:** Delegate to **code-reviewer** for a final quality check.

Do you approve this plan?
"""
    },
    {
        "problem": "Add a last_login_ip field to the User model in the database.",
        "solution": """
<sequential-thinking>
This is a database migration and a code change. It requires updating the database schema, the data access layer, and the application code that uses it.

1.  **Write Migration Tests:** Test that the repository can handle the new `last_login_ip` field.
    -   Agent: tdd-test-engineer
    -   Verification: karen
2.  **Implement Model/Repository Change:** Add the field to the `User` struct and update the repository logic.
    -   Agent: rust-developer
    -   Verification: karen
3.  **Write Migration Script:** Create the database migration script to add the new column.
    -   Agent: aws-devops-engineer (as they handle infrastructure/DB schema)
    -   Verification: karen (verify script syntax and safety)
4.  **Final Review:** Review all code changes.
    -   Agent: code-reviewer

This results in 7 delegation steps.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to tdd-test-engineer to write tests for the UserRepository to handle the last_login_ip field",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer to write repository tests"
    },
    {
        "content": "Delegate to karen to verify the UserRepository tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to rust-developer to add the last_login_ip field to the User model and repository",
        "status": "pending",
        "activeForm": "Delegating to rust-developer to update model"
    },
    {
        "content": "Delegate to karen to verify the User model implementation",
        "status": "pending",
        "activeForm": "Delegating to karen to verify implementation"
    },
    {
        "content": "Delegate to aws-devops-engineer to write a SurrealDB migration script to add the last_login_ip field",
        "status": "pending",
        "activeForm": "Delegating to aws-devops-engineer to write migration"
    },
    {
        "content": "Delegate to karen to verify the database migration script",
        "status": "pending",
        "activeForm": "Delegating to karen to verify migration script"
    },
    {
        "content": "Delegate to code-reviewer to review all changes related to the new field",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for final review"
    }
]
</TodoWrite>

## Plan for Adding `last_login_ip` Field

1.  **Write Repository Tests:** Delegate to **tdd-test-engineer** to test the data access layer.
2.  **Verify Tests:** Delegate to **karen** to verify the tests.
3.  **Update Code:** Delegate to **rust-developer** to update the application code.
4.  **Verify Code:** Delegate to **karen** to verify the code changes.
5.  **Write Migration Script:** Delegate to **aws-devops-engineer** to create the DB migration script.
6.  **Verify Migration Script:** Delegate to **karen** to verify the script.
7.  **Final Code Review:** Delegate to **code-reviewer** for a final review.

Do you approve this plan?
"""
    },
    {
        "problem": "Integrate with the WeatherAPI to fetch the current weather for a user's location.",
        "solution": """
<sequential-thinking>
This involves creating a new client to communicate with an external API.

1.  **Write WeatherAPI Client Tests:** Create tests for a new service that will call the WeatherAPI.
    -   Agent: tdd-test-engineer
    -   Verification: karen
2.  **Implement WeatherAPI Client:** Build the client.
    -   Agent: rust-developer
    -   Verification: karen
3.  **Final Review:** Review the new client code.
    -   Agent: code-reviewer

This is a 5-step delegation process.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to tdd-test-engineer to write tests for a new WeatherAPI client service",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer to write client tests"
    },
    {
        "content": "Delegate to karen to verify the WeatherAPI client tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to rust-developer to implement the WeatherAPI client",
        "status": "pending",
        "activeForm": "Delegating to rust-developer to implement client"
    },
    {
        "content": "Delegate to karen to verify the WeatherAPI client implementation",
        "status": "pending",
        "activeForm": "Delegating to karen to verify implementation"
    },
    {
        "content": "Delegate to code-reviewer to review the new WeatherAPI client",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for final review"
    }
]
</TodoWrite>

## Plan for WeatherAPI Integration

1.  **Write Client Tests:** Delegate to **tdd-test-engineer** to create tests for the new API client.
2.  **Verify Tests:** Delegate to **karen** to verify the tests.
3.  **Implement Client:** Delegate to **rust-developer** to build the client.
4.  **Verify Implementation:** Delegate to **karen** to verify the implementation.
5.  **Final Code Review:** Delegate to **code-reviewer** for a final review.

Do you approve this plan?
"""
    },
    {
        "problem": "The /api/v1/analytics/report endpoint is too slow. Find the bottleneck and optimize it.",
        "solution": """
<sequential-thinking>
The user is reporting a performance issue with an unknown cause. The first step is investigation.

1.  **Debug Performance:** Use the `debug-specialist` to analyze the endpoint, find the performance bottleneck (e.g., N+1 query, slow computation), and recommend a fix.
    -   Agent: debug-specialist

The fix will require a new plan after the investigation is complete.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to debug-specialist to investigate and identify the performance bottleneck in the /api/v1/analytics/report endpoint",
        "status": "pending",
        "activeForm": "Delegating to debug-specialist to investigate performance"
    }
]
</TodoWrite>

## Plan for Performance Investigation

1.  **Investigate Bottleneck:** I will delegate to the **debug-specialist** to analyze the slow endpoint and provide a root cause analysis with a recommended solution.

Once the analysis is complete, I will formulate a new plan to implement the fix.

Do you approve this investigation plan?
"""
    },
    {
        "problem": "Add internationalization support for French to the <UserProfile> component.",
        "solution": """
<sequential-thinking>
This is an internationalization (i18n) task, which requires a specialist.

1.  **Create Translation Files:** Add the necessary French (fr) translation files for all text in the `<UserProfile>` component.
    -   Agent: i18n-specialist
    -   Verification: karen (verify files exist and have correct keys)
2.  **Implement i18n in Component:** Refactor the `<UserProfile>` component to use the i18n library to display the translated text.
    -   Agent: ui-developer
    -   Verification: karen (verify component renders correctly with French text)
3.  **Final Review:**
    -   Agent: code-reviewer

This is a 5-step delegation process.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to i18n-specialist to create French translation files for the UserProfile component",
        "status": "pending",
        "activeForm": "Delegating to i18n-specialist to add translations"
    },
    {
        "content": "Delegate to karen to verify the French translation files are correctly structured",
        "status": "pending",
        "activeForm": "Delegating to karen to verify translation files"
    },
    {
        "content": "Delegate to ui-developer to refactor the UserProfile component to use the i18n library",
        "status": "pending",
        "activeForm": "Delegating to ui-developer to implement i18n"
    },
    {
        "content": "Delegate to karen to verify the UserProfile component correctly displays French translations",
        "status": "pending",
        "activeForm": "Delegating to karen to verify i18n implementation"
    },
    {
        "content": "Delegate to code-reviewer to review all i18n changes",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for final review"
    }
]
</TodoWrite>

## Plan for Internationalization

1.  **Create Translations:** Delegate to **i18n-specialist** to add French translation files.
2.  **Verify Translations:** Delegate to **karen** to check the new files.
3.  **Implement in Component:** Delegate to **ui-developer** to update the component to use the translations.
4.  **Verify Implementation:** Delegate to **karen** to confirm the component renders correctly.
5.  **Final Code Review:** Delegate to **code-reviewer** for a final review.

Do you approve this plan?
"""
    },
    {
        "problem": "Implement a feature flag for the new 'AI Summary' feature.",
        "solution": """
<sequential-thinking>
This involves both backend logic to check the flag and potentially frontend work to show/hide the feature. I'll focus on the backend implementation first.

1.  **TDD for Flag Logic:** Write tests for the service that will check if the 'AI Summary' feature flag is enabled.
    -   Agent: tdd-test-engineer
    -   Verification: karen
2.  **Implement Flag Check:** Implement the logic.
    -   Agent: rust-developer
    -   Verification: karen
3.  **Code Review:**
    -   Agent: code-reviewer

This breaks down into 5 steps.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to tdd-test-engineer to write tests for the feature flag checking logic for 'AI Summary'",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer to write tests"
    },
    {
        "content": "Delegate to karen to verify the feature flag tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to rust-developer to implement the feature flag check for 'AI Summary'",
        "status": "pending",
        "activeForm": "Delegating to rust-developer to implement logic"
    },
    {
        "content": "Delegate to karen to verify the feature flag implementation passes tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify implementation"
    },
    {
        "content": "Delegate to code-reviewer to review the feature flag implementation",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for review"
    }
]
</TodoWrite>

## Plan for Feature Flag Implementation

1.  **Write Tests:** Delegate to **tdd-test-engineer** to create tests for the flag logic.
2.  **Verify Tests:** Delegate to **karen** to verify the tests.
3.  **Implement Logic:** Delegate to **rust-developer** to add the feature flag check.
4.  **Verify Implementation:** Delegate to **karen** to verify the implementation.
5.  **Final Code Review:** Delegate to **code-reviewer** for a final review.

Do you approve this plan?
"""
    },
    {
        "problem": "Scaffold a new microservice for handling user notifications.",
        "solution": """
<sequential-thinking>
Scaffolding a new service from a template is a DevOps task.

1.  **Scaffold Service:** Use the company's microservice template to create the basic project structure for the `notifications-service`.
    -   Agent: aws-devops-engineer
    -   Verification: karen (verify the project builds and default tests pass)

This is a 2-step process.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to aws-devops-engineer to scaffold the new notifications-service from the standard template",
        "status": "pending",
        "activeForm": "Delegating to aws-devops-engineer to scaffold service"
    },
    {
        "content": "Delegate to karen to verify the new service builds and passes initial checks",
        "status": "pending",
        "activeForm": "Delegating to karen to verify scaffolding"
    }
]
</TodoWrite>

## Plan for New Microservice

1.  **Scaffold Service:** Delegate to **aws-devops-engineer** to create the new service from the project template.
2.  **Verify:** Delegate to **karen** to ensure the newly created service is valid and buildable.

Do you approve this plan?
"""
    },
    {
        "problem": "Update the Dockerfile and CI/CD pipeline to use the new base image rust:1.79-slim.",
        "solution": """
<sequential-thinking>
This is a pure DevOps and infrastructure change.

1.  **Update Files:** Modify the `Dockerfile` and `.github/workflows/ci.yml` to use the new base image.
    -   Agent: aws-devops-engineer
    -   Verification: karen (verify the CI pipeline completes successfully with the new image)

This is a simple 2-step delegation.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to aws-devops-engineer to update Dockerfile and CI pipeline to use rust:1.79-slim",
        "status": "pending",
        "activeForm": "Delegating to aws-devops-engineer to update files"
    },
    {
        "content": "Delegate to karen to verify that the CI pipeline passes with the new base image",
        "status": "pending",
        "activeForm": "Delegating to karen to verify pipeline"
    }
]
</TodoWrite>

## Plan for CI/CD Update

1.  **Update Infrastructure Files:** Delegate to **aws-devops-engineer** to update the necessary configuration files.
2.  **Verify Changes:** Delegate to **karen** to trigger and verify the CI pipeline to confirm the change is working.

Do you approve this plan?
"""
    },
    {
        "problem": "Remove the deprecated LegacyReporting module and all its usages.",
        "solution": """
<sequential-thinking>
Removing code requires careful testing to ensure no regressions are introduced.

1.  **Write Tests:** Write characterization tests around the code that uses the `LegacyReporting` module to lock down its current behavior.
    -   Agent: tdd-test-engineer
    -   Verification: karen
2.  **Remove Module:** Delete the `LegacyReporting` module and refactor the code that used it.
    -   Agent: rust-developer
    -   Verification: karen (ensure all tests still pass)
3.  **Final Review:**
    -   Agent: code-reviewer

This breaks down into 5 steps.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to tdd-test-engineer to write characterization tests for code using LegacyReporting",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer to write tests"
    },
    {
        "content": "Delegate to karen to verify the new characterization tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to rust-developer to remove the LegacyReporting module and refactor its usages",
        "status": "pending",
        "activeForm": "Delegating to rust-developer to remove module"
    },
    {
        "content": "Delegate to karen to verify that all tests pass after removing the module",
        "status": "pending",
        "activeForm": "Delegating to karen to verify removal"
    },
    {
        "content": "Delegate to code-reviewer to review the removal of the LegacyReporting module",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for review"
    }
]
</TodoWrite>

## Plan for Deprecation Removal

1.  **Write Tests:** Delegate to **tdd-test-engineer** to write tests to prevent regressions.
2.  **Verify Tests:** Delegate to **karen** to verify the tests.
3.  **Remove Code:** Delegate to **rust-developer** to perform the code removal and refactoring.
4.  **Verify Removal:** Delegate to **karen** to run all tests and confirm success.
5.  **Final Code Review:** Delegate to **code-reviewer** for a final review.

Do you approve this plan?
"""
    },
    {
        "problem": "Fix the accessibility issues on the login form. It is missing labels and has poor color contrast.",
        "solution": """
<sequential-thinking>
This is a UI and accessibility (a11y) task.

1.  **Fix A11y Issues:** Update the login form component to add proper `aria-labels` and adjust the CSS to meet WCAG color contrast standards.
    -   Agent: ui-developer
    -   Verification: karen (run an automated accessibility checker like Axe and verify the specific issues are resolved)
2.  **Final Review:**
    -   Agent: code-reviewer

This is a 3-step plan.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to ui-developer to fix accessibility issues on the login form",
        "status": "pending",
        "activeForm": "Delegating to ui-developer to fix a11y issues"
    },
    {
        "content": "Delegate to karen to verify the accessibility fixes using an automated checker",
        "status": "pending",
        "activeForm": "Delegating to karen to verify a11y fixes"
    },
    {
        "content": "Delegate to code-reviewer to review the accessibility improvements",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for review"
    }
]
</TodoWrite>

## Plan for Accessibility Fixes

1.  **Implement Fixes:** Delegate to **ui-developer** to update the login form's code and styles.
2.  **Verify Fixes:** Delegate to **karen** to run accessibility checks and confirm the issues are resolved.
3.  **Code Review:** Delegate to **code-reviewer** for a final review.

Do you approve this plan?
"""
    },
    {
        "problem": "Add structured logging to the authentication service.",
        "solution": """
<sequential-thinking>
This involves adding logging statements at key points in the authentication flow.

1.  **TDD for Logging:** Write tests that mock the logger and assert that it's called with the correct structured data on login success and failure.
    -   Agent: tdd-test-engineer
    -   Verification: karen
2.  **Implement Logging:** Add the logging statements to the authentication service code.
    -   Agent: rust-developer
    -   Verification: karen
3.  **Code Review:**
    -   Agent: code-reviewer

This is a 5-step plan.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to tdd-test-engineer to write tests for structured logging in the authentication service",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer to write logging tests"
    },
    {
        "content": "Delegate to karen to verify the logging tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to rust-developer to implement structured logging in the authentication service",
        "status": "pending",
        "activeForm": "Delegating to rust-developer to implement logging"
    },
    {
        "content": "Delegate to karen to verify the logging implementation passes all tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify implementation"
    },
    {
        "content": "Delegate to code-reviewer to review the new logging implementation",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for review"
    }
]
</TodoWrite>

## Plan for Structured Logging

1.  **Write Tests:** Delegate to **tdd-test-engineer** to create tests that verify logging output.
2.  **Verify Tests:** Delegate to **karen** to verify the tests.
3.  **Implement Logging:** Delegate to **rust-developer** to add the logging code.
4.  **Verify Implementation:** Delegate to **karen** to confirm tests pass.
5.  **Final Code Review:** Delegate to **code-reviewer** for a final review.

Do you approve this plan?
"""
    },
    {
        "problem": "Create a nightly cron job that cleans up expired user sessions from the database.",
        "solution": """
<sequential-thinking>
This requires two distinct parts: the cleanup logic and the scheduling mechanism.

1.  **TDD for Cleanup Logic:** Write tests for the function that will delete expired sessions.
    -   Agent: tdd-test-engineer
    -   Verification: karen
2.  **Implement Cleanup Logic:** Write the session cleanup function.
    -   Agent: rust-developer
    -   Verification: karen
3.  **Schedule Cron Job:** Create the infrastructure configuration (e.g., a Kubernetes CronJob YAML or an AWS Lambda scheduled event) to run the cleanup logic nightly.
    -   Agent: aws-devops-engineer
    -   Verification: karen (verify the job is scheduled in the target environment)
4.  **Code Review:** Review the cleanup logic code.
    -   Agent: code-reviewer

Total of 7 steps.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to tdd-test-engineer to write tests for the expired session cleanup logic",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer to write cleanup tests"
    },
    {
        "content": "Delegate to karen to verify the cleanup logic tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to rust-developer to implement the expired session cleanup logic",
        "status": "pending",
        "activeForm": "Delegating to rust-developer to implement cleanup logic"
    },
    {
        "content": "Delegate to karen to verify the cleanup logic implementation",
        "status": "pending",
        "activeForm": "Delegating to karen to verify implementation"
    },
    {
        "content": "Delegate to aws-devops-engineer to create and schedule the nightly cron job",
        "status": "pending",
        "activeForm": "Delegating to aws-devops-engineer to schedule job"
    },
    {
        "content": "Delegate to karen to verify the cron job is scheduled correctly",
        "status": "pending",
        "activeForm": "Delegating to karen to verify scheduling"
    },
    {
        "content": "Delegate to code-reviewer to review the session cleanup code",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for review"
    }
]
</TodoWrite>

## Plan for Session Cleanup Cron Job

1.  **Write Logic Tests:** Delegate to **tdd-test-engineer** for the cleanup logic.
2.  **Verify Logic Tests:** Delegate to **karen**.
3.  **Implement Logic:** Delegate to **rust-developer** to write the cleanup function.
4.  **Verify Logic:** Delegate to **karen**.
5.  **Schedule Job:** Delegate to **aws-devops-engineer** to set up the cron job infrastructure.
6.  **Verify Schedule:** Delegate to **karen**.
7.  **Code Review:** Delegate to **code-reviewer**.

Do you approve this plan?
"""
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
"""
    },
    {
        "problem": "Implement a Redis caching layer for the get_product_list function.",
        "solution": """
<sequential-thinking>
This involves modifying an existing function to add caching logic.

1.  **TDD for Caching:** Write tests for the `get_product_list` function that cover cache hit and cache miss scenarios.
    -   Agent: tdd-test-engineer
    -   Verification: karen
2.  **Implement Caching:** Modify the function to include logic to check Redis for cached data before hitting the database.
    -   Agent: rust-developer
    -   Verification: karen
3.  **Code Review:**
    -   Agent: code-reviewer

This is a 5-step process.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to tdd-test-engineer to write tests for Redis caching in get_product_list",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer to write caching tests"
    },
    {
        "content": "Delegate to karen to verify the caching tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to rust-developer to implement the Redis caching layer for get_product_list",
        "status": "pending",
        "activeForm": "Delegating to rust-developer to implement caching"
    },
    {
        "content": "Delegate to karen to verify the caching implementation passes all tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify implementation"
    },
    {
        "content": "Delegate to code-reviewer to review the new caching implementation",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for review"
    }
]
</TodoWrite>

## Plan for Caching Layer

1.  **Write Tests:** Delegate to **tdd-test-engineer** to test cache hit/miss scenarios.
2.  **Verify Tests:** Delegate to **karen** to verify the tests.
3.  **Implement Caching:** Delegate to **rust-developer** to add the Redis logic.
4.  **Verify Implementation:** Delegate to **karen** to verify the implementation.
5.  **Final Code Review:** Delegate to **code-reviewer** for a final review.

Do you approve this plan?
"""
    },
    {
        "problem": "The security audit found we need to add HTTP Security Headers like CSP and HSTS.",
        "solution": """
<sequential-thinking>
This is a security hardening task that involves middleware changes.

1.  **Implement Security Headers:** Add middleware to the web server that injects Content-Security-Policy (CSP), Strict-Transport-Security (HSTS), and other recommended security headers into all responses.
    -   Agent: 31337 (security specialist)
    -   Verification: karen (verify headers are present in server responses)
2.  **Security Audit:** Have the changes formally audited.
    -   Agent: security-auditor (blocking authority)

This is a 3-step plan.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to 31337 to implement middleware for adding HTTP security headers",
        "status": "pending",
        "activeForm": "Delegating to 31337 to implement headers"
    },
    {
        "content": "Delegate to karen to verify the security headers are present on HTTP responses",
        "status": "pending",
        "activeForm": "Delegating to karen to verify headers"
    },
    {
        "content": "Delegate to security-auditor to re-audit the application for HTTP security headers",
        "status": "pending",
        "activeForm": "Delegating to security-auditor for re-audit"
    }
]
</TodoWrite>

## Plan for HTTP Security Headers

1.  **Implement Headers:** Delegate to **31337** to add the required middleware.
2.  **Verify Implementation:** Delegate to **karen** to check that responses now include the correct headers.
3.  **Security Audit:** Delegate to **security-auditor** for a final verification of the security posture.

Do you approve this plan?
"""
    },
    {
        "problem": "Create a new GET endpoint /api/v1/health that returns a 200 OK.",
        "solution": """
<sequential-thinking>
This is a very simple, standard backend task. The full TDD workflow should still be followed for consistency.

1.  **Write Tests:** Create a test file for the health endpoint that asserts a 200 status code and expected JSON body.
    -   Agent: tdd-test-engineer
    -   Verification: karen
2.  **Implement Endpoint:** Create the route and handler for `/api/v1/health`.
    -   Agent: rust-developer
    -   Verification: karen
3.  **Final Review:**
    -   Agent: code-reviewer

A 5-step delegation.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to tdd-test-engineer to write tests for the /api/v1/health endpoint",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer to write health tests"
    },
    {
        "content": "Delegate to karen to verify the health endpoint tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to rust-developer to implement the /api/v1/health endpoint",
        "status": "pending",
        "activeForm": "Delegating to rust-developer to implement endpoint"
    },
    {
        "content": "Delegate to karen to verify the health endpoint implementation",
        "status": "pending",
        "activeForm": "Delegating to karen to verify implementation"
    },
    {
        "content": "Delegate to code-reviewer to review the new health endpoint code",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for review"
    }
]
</TodoWrite>

## Plan for Health Endpoint

1.  **Write Tests:** Delegate to **tdd-test-engineer**.
2.  **Verify Tests:** Delegate to **karen**.
3.  **Implement Endpoint:** Delegate to **rust-developer**.
4.  **Verify Implementation:** Delegate to **karen**.
5.  **Code Review:** Delegate to **code-reviewer**.

Do you approve this plan?
"""
    },
    {
        "problem": "Migrate the state management in the Dashboard page from local state to a global Zustand store.",
        "solution": """
<sequential-thinking>
This is a frontend refactoring task. It should be broken into creating the store and then using the store.

1.  **TDD for Zustand Store:** Write tests for the new global dashboard store, covering its actions and initial state.
    -   Agent: tdd-test-engineer
    -   Verification: karen
2.  **Implement Zustand Store:** Create the Zustand store file.
    -   Agent: ui-developer
    -   Verification: karen
3.  **TDD for Component Refactor:** Write tests for the Dashboard page that mock the new store and assert correct rendering.
    -   Agent: tdd-test-engineer
    -   Verification: karen
4.  **Implement Component Refactor:** Refactor the Dashboard component to use the new store instead of local state.
    -   Agent: ui-developer
    -   Verification: karen
5.  **Code Review:**
    -   Agent: code-reviewer

This is a 9-step plan.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to tdd-test-engineer to write tests for the new Dashboard Zustand store",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer to test store"
    },
    {
        "content": "Delegate to karen to verify the Zustand store tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to ui-developer to implement the Dashboard Zustand store",
        "status": "pending",
        "activeForm": "Delegating to ui-developer to implement store"
    },
    {
        "content": "Delegate to karen to verify the Zustand store implementation",
        "status": "pending",
        "activeForm": "Delegating to karen to verify store"
    },
    {
        "content": "Delegate to tdd-test-engineer to write tests for the refactored Dashboard component",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer to test component"
    },
    {
        "content": "Delegate to karen to verify the refactored component tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to ui-developer to refactor the Dashboard component to use the Zustand store",
        "status": "pending",
        "activeForm": "Delegating to ui-developer to refactor component"
    },
    {
        "content": "Delegate to karen to verify the refactored Dashboard component implementation",
        "status": "pending",
        "activeForm": "Delegating to karen to verify component"
    },
    {
        "content": "Delegate to code-reviewer to review the state management migration",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for review"
    }
]
</TodoWrite>

## Plan for State Management Migration

1.  **Test Store:** Delegate to **tdd-test-engineer** to test the new store.
2.  **Verify Store Tests:** Delegate to **karen**.
3.  **Implement Store:** Delegate to **ui-developer** to create the store.
4.  **Verify Store:** Delegate to **karen**.
5.  **Test Component:** Delegate to **tdd-test-engineer** to test the refactored component.
6.  **Verify Component Tests:** Delegate to **karen**.
7.  **Implement Component Refactor:** Delegate to **ui-developer**.
8.  **Verify Component Refactor:** Delegate to **karen**.
9.  **Code Review:** Delegate to **code-reviewer**.

Do you approve this plan?
"""
    },
    {
        "problem": "Create a reusable React component for a data table with sorting and pagination.",
        "solution": """
<sequential-thinking>
This is a complex UI feature that should be broken down into smaller pieces. Let's start with the core table functionality.

1.  **TDD for DataTable Component:** Write tests for a basic `<DataTable>` component that renders rows and columns.
    -   Agent: tdd-test-engineer
    -   Verification: karen
2.  **Implement DataTable Component:**
    -   Agent: ui-developer
    -   Verification: karen
3.  **TDD for Sorting Logic:** Write tests for the sorting functionality.
    -   Agent: tdd-test-engineer
    -   Verification: karen
4.  **Implement Sorting Logic:** Add sorting to the `<DataTable>`.
    -   Agent: ui-developer
    -   Verification: karen
5.  **TDD for Pagination Logic:** Write tests for the pagination controls.
    -   Agent: tdd-test-engineer
    -   Verification: karen
6.  **Implement Pagination Logic:** Add pagination to the `<DataTable>`.
    -   Agent: ui-developer
    -   Verification: karen
7.  **Documentation:** Document the new component's props and usage.
    -   Agent: documentation-specialist
    -   Verification: karen
8.  **Code Review:**
    -   Agent: code-reviewer

This plan has 15 steps.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to tdd-test-engineer to write tests for the base DataTable component",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer for base table tests"
    },
    {
        "content": "Delegate to karen to verify base DataTable tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to ui-developer to implement the base DataTable component",
        "status": "pending",
        "activeForm": "Delegating to ui-developer for base table implementation"
    },
    {
        "content": "Delegate to karen to verify the base DataTable implementation",
        "status": "pending",
        "activeForm": "Delegating to karen to verify implementation"
    },
    {
        "content": "Delegate to tdd-test-engineer to write tests for sorting functionality",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer for sorting tests"
    },
    {
        "content": "Delegate to karen to verify sorting tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to ui-developer to implement sorting functionality",
        "status": "pending",
        "activeForm": "Delegating to ui-developer for sorting implementation"
    },
    {
        "content": "Delegate to karen to verify the sorting implementation",
        "status": "pending",
        "activeForm": "Delegating to karen to verify implementation"
    },
    {
        "content": "Delegate to tdd-test-engineer to write tests for pagination functionality",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer for pagination tests"
    },
    {
        "content": "Delegate to karen to verify pagination tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to ui-developer to implement pagination functionality",
        "status": "pending",
        "activeForm": "Delegating to ui-developer for pagination implementation"
    },
    {
        "content": "Delegate to karen to verify the pagination implementation",
        "status": "pending",
        "activeForm": "Delegating to karen to verify implementation"
    },
    {
        "content": "Delegate to documentation-specialist to document the new DataTable component",
        "status": "pending",
        "activeForm": "Delegating to documentation-specialist to write docs"
    },
    {
        "content": "Delegate to karen to verify the DataTable documentation",
        "status": "pending",
        "activeForm": "Delegating to karen to verify docs"
    },
    {
        "content": "Delegate to code-reviewer to review the complete DataTable component",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for final review"
    }
]
</TodoWrite>

## Plan for DataTable Component

1.  **Test/Implement Base Table:** A 4-step process for the basic component.
2.  **Test/Implement Sorting:** A 4-step process for adding sorting.
3.  **Test/Implement Pagination:** A 4-step process for adding pagination.
4.  **Document:** A 2-step process to document the component.
5.  **Code Review:** Final review of all new code.

Do you approve this plan?
"""
    },
    {
        "problem": "Add a dark mode toggle to the UI that persists the user's preference.",
        "solution": """
<sequential-thinking>
This is a full-stack feature involving UI, state management, and a backend endpoint.

1.  **Backend - TDD:** Write tests for a new endpoint `/api/user/preferences` that accepts a theme preference.
    -   Agent: tdd-test-engineer
    -   Verification: karen
2.  **Backend - Implement:** Implement the endpoint to save the user's preference to the database.
    -   Agent: rust-developer
    -   Verification: karen
3.  **Frontend - TDD UI:** Write tests for a new `<ThemeToggle>` component.
    -   Agent: tdd-test-engineer
    -   Verification: karen
4.  **Frontend - Implement UI:** Build the `<ThemeToggle>` component.
    -   Agent: ui-developer
    -   Verification: karen
5.  **Frontend - TDD Logic:** Write tests for the client-side logic that calls the backend and applies the theme.
    -   Agent: tdd-test-engineer
    -   Verification: karen
6.  **Frontend - Implement Logic:** Implement the logic to manage the theme state and call the API.
    -   Agent: ui-developer
    -   Verification: karen
7.  **Code Review:**
    -   Agent: code-reviewer

This is a comprehensive 13-step plan.
</sequential-thinking>
<TodoWrite>
[
    { "content": "Delegate to tdd-test-engineer to write tests for the user preferences API endpoint", "status": "pending", "activeForm": "Delegating tests for preferences API" },
    { "content": "Delegate to karen to verify the user preferences API tests", "status": "pending", "activeForm": "Delegating verification of API tests" },
    { "content": "Delegate to rust-developer to implement the user preferences API endpoint", "status": "pending", "activeForm": "Delegating implementation of preferences API" },
    { "content": "Delegate to karen to verify the user preferences API implementation", "status": "pending", "activeForm": "Delegating verification of API implementation" },
    { "content": "Delegate to tdd-test-engineer to write tests for the ThemeToggle UI component", "status": "pending", "activeForm": "Delegating tests for ThemeToggle UI" },
    { "content": "Delegate to karen to verify the ThemeToggle UI tests", "status": "pending", "activeForm": "Delegating verification of UI tests" },
    { "content": "Delegate to ui-developer to implement the ThemeToggle UI component", "status": "pending", "activeForm": "Delegating implementation of ThemeToggle UI" },
    { "content": "Delegate to karen to verify the ThemeToggle UI implementation", "status": "pending", "activeForm": "Delegating verification of UI implementation" },
    { "content": "Delegate to tdd-test-engineer to write tests for the theme management client logic", "status": "pending", "activeForm": "Delegating tests for client logic" },
    { "content": "Delegate to karen to verify the client logic tests", "status": "pending", "activeForm": "Delegating verification of client logic tests" },
    { "content": "Delegate to ui-developer to implement the theme management client logic", "status": "pending", "activeForm": "Delegating implementation of client logic" },
    { "content": "Delegate to karen to verify the client logic implementation", "status": "pending", "activeForm": "Delegating verification of client logic implementation" },
    { "content": "Delegate to code-reviewer to review the entire dark mode feature", "status": "pending", "activeForm": "Delegating final code review" }
]
</TodoWrite>

## Plan for Dark Mode Feature

1.  **Backend API:** Test and implement the endpoint for saving user preferences (4 steps).
2.  **Frontend UI:** Test and implement the `<ThemeToggle>` switch (4 steps).
3.  **Frontend Logic:** Test and implement the client-side logic for theme management (4 steps).
4.  **Code Review:** Perform a final review of all frontend and backend code.

Do you approve this plan?
"""
    },
    {
        "problem": "Analyze the project's requirements from the PRD and create a task breakdown in Task Master.",
        "solution": """
<sequential-thinking>
The user is asking for a planning operation using Task Master based on a Product Requirements Document (PRD). According to the `Task Master Delegation Protocol`, this complex planning work must be delegated to the `product-strategist`.

1.  **Parse PRD and Create Tasks:** Delegate the entire planning process to the `product-strategist`. This agent will read the PRD, understand the requirements, and use the `taskmaster` tool to create a detailed task breakdown with epics and stories.
    -   Agent: product-strategist
    -   Verification: karen (verify that tasks have been created in Task Master and they align with the PRD).

This is a 2-step delegation. I will not use the `taskmaster` tool directly for this planning operation.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to product-strategist to analyze the PRD and create a complete task breakdown in Task Master",
        "status": "pending",
        "activeForm": "Delegating to product-strategist for project planning"
    },
    {
        "content": "Delegate to karen to verify that the task breakdown in Task Master is complete and accurate based on the PRD",
        "status": "pending",
        "activeForm": "Delegating to karen to verify the project plan"
    }
]
</TodoWrite>

## Plan for Project Task Breakdown

1.  **Delegate Planning:** I will delegate the task of analyzing the PRD and creating the project plan in Task Master to the **product-strategist**.
2.  **Verify Plan:** Afterwards, I will ask **karen** to verify the completeness and accuracy of the generated plan.

Do you approve this plan?
"""
    }
]





# To add these to your existing CASE_BASE, simply extend the list:
CASE_BASE.extend(SECURITY_CASES)
CASE_BASE.extend(ORCHESTRATION_EXAMPLES)

# ============================================
# HELPER FUNCTIONS
# ============================================

def save_case_base_to_file(filename="firebase_nextjs_bootstrap_cases.json"):
    """Save the case base to a JSON file for easy loading."""
    import json
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(CASE_BASE, f, indent=2, ensure_ascii=False)
    
    print(f"Case base saved to {filename}")
    print(f"Total cases: {len(CASE_BASE)}")
    return filename

def load_case_base_from_file(filename="firebase_nextjs_bootstrap_cases.json"):
    """Load the case base from a JSON file."""
    import json
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File {filename} not found. Using default case base.")
        return CASE_BASE

def search_cases(query, case_base=None):
    """Search for relevant cases based on a query."""
    if case_base is None:
        case_base = CASE_BASE
    
    query_lower = query.lower()
    results = []
    
    for case in case_base:
        problem_lower = case["problem"].lower()
        solution_lower = case["solution"].lower()
        
        # Calculate relevance score
        score = 0
        query_words = query_lower.split()
        
        for word in query_words:
            if word in problem_lower:
                score += 2  # Higher weight for problem matches
            if word in solution_lower:
                score += 1
        
        if score > 0:
            results.append((score, case))
    
    # Sort by relevance score (descending)
    results.sort(key=lambda x: x[0], reverse=True)
    
    # Return top 5 most relevant cases
    return [case for _, case in results[:5]]

def add_case(problem, solution, case_base=None):
    """Add a new case to the case base."""
    if case_base is None:
        case_base = CASE_BASE
    
    new_case = {
        "problem": problem,
        "solution": solution
    }
    
    case_base.append(new_case)
    print(f"Added new case. Total cases: {len(case_base)}")
    return case_base

def validate_case_base(case_base=None):
    """Validate that all cases have proper structure."""
    if case_base is None:
        case_base = CASE_BASE
    
    issues = []
    
    for i, case in enumerate(case_base):
        if "problem" not in case:
            issues.append(f"Case {i}: Missing 'problem' field")
        if "solution" not in case:
            issues.append(f"Case {i}: Missing 'solution' field")
        if not isinstance(case.get("problem", ""), str):
            issues.append(f"Case {i}: 'problem' must be a string")
        if not isinstance(case.get("solution", ""), str):
            issues.append(f"Case {i}: 'solution' must be a string")
    
    if issues:
        print("Validation issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("Case base validation passed!")
        print(f"Total valid cases: {len(case_base)}")
        return True

def get_case_statistics(case_base=None):
    """Get statistics about the case base."""
    if case_base is None:
        case_base = CASE_BASE
    
    stats = {
        "total_cases": len(case_base),
        "categories": {
            "firebase_auth": 0,
            "firestore": 0,
            "nextjs": 0,
            "bootstrap": 0,
            "combined": 0
        },
        "avg_solution_length": 0
    }
    
    total_length = 0
    
    for case in case_base:
        problem_lower = case["problem"].lower()
        
        if "firebase" and "auth" in problem_lower:
            stats["categories"]["firebase_auth"] += 1
        elif "firestore" in problem_lower:
            stats["categories"]["firestore"] += 1
        elif "next.js" in problem_lower or "nextjs" in problem_lower:
            stats["categories"]["nextjs"] += 1
        elif "bootstrap" in problem_lower:
            stats["categories"]["bootstrap"] += 1
        else:
            stats["categories"]["combined"] += 1
        
        total_length += len(case["solution"])
    
    stats["avg_solution_length"] = total_length // len(case_base) if case_base else 0
    
    print("\nCase Base Statistics:")
    print(f"Total Cases: {stats['total_cases']}")
    print("\nCategories:")
    for category, count in stats["categories"].items():
        print(f"  {category}: {count}")
    print(f"\nAverage Solution Length: {stats['avg_solution_length']} characters")
    
    return stats

# Main execution
if __name__ == "__main__":
    print("=" * 50)
    print("Firebase/Next.js/Bootstrap Case-Based Reasoning Dataset")
    print("=" * 50)
    
    # Validate the case base
    if validate_case_base():
        # Get statistics
        get_case_statistics()
        
        # Save to JSON file
        filename = save_case_base_to_file()
        
        # Example: Search for Firebase authentication cases
        print("\n" + "=" * 50)
        print("Example Search: 'Firebase authentication'")
        print("=" * 50)
        results = search_cases("Firebase authentication")
        for i, case in enumerate(results, 1):
            print(f"\n{i}. {case['problem']}")
            print(f"   Solution length: {len(case['solution'])} characters")