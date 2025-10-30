"""
React Component Cases for CBR MCP Server

This module contains case-based reasoning examples for React component implementations
including Bootstrap integration, state management, forms, navigation, modals, and
data display patterns.
"""

REACT_COMPONENTS_CASES = [
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
""",
        "category": "react",
        "subcategory": "components",
        "tags": ["react", "component", "bootstrap", "navbar", "navigation", "responsive", "ui"]
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
""",
        "category": "react",
        "subcategory": "components",
        "tags": ["react", "component", "bootstrap", "modal", "dialog", "ui", "useState"]
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
""",
        "category": "react",
        "subcategory": "components",
        "tags": ["react", "component", "bootstrap", "form", "validation", "input", "feedback", "useState"]
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
""",
        "category": "react",
        "subcategory": "components",
        "tags": ["react", "component", "bootstrap", "grid", "layout", "card", "responsive", "display data"]
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
""",
        "category": "react",
        "subcategory": "components",
        "tags": ["react", "component", "bootstrap", "firestore", "list", "display", "fetch", "data", "card"]
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
""",
        "category": "react",
        "subcategory": "components",
        "tags": ["react", "component", "bootstrap", "button", "click", "trigger", "action", "cloud function", "firebase"]
    }
]
