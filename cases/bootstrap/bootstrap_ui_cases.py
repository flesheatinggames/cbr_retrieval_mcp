"""
Bootstrap UI Cases for CBR MCP Server

This module contains case-based reasoning examples for Bootstrap UI component
implementations using react-bootstrap, including navigation bars, modals, forms
with validation, and responsive grid layouts.
"""

BOOTSTRAP_UI_CASES = [
    {
        "problem": """
A responsive navigation bar in a React component using react-bootstrap.
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
        "category": 'bootstrap',
        "subcategory": 'ui',
        "tags": ['bootstrap', 'react-bootstrap', 'navbar', 'navigation', 'responsive', 'ui', 'component']
    },
    {
        "problem": """
A React component that displays a Bootstrap modal dialog.
""",
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
        "category": 'bootstrap',
        "subcategory": 'ui',
        "tags": ['bootstrap', 'react-bootstrap', 'modal', 'dialog', 'ui', 'component', 'overlay']
    },
    {
        "problem": """
A Bootstrap-styled form with validation feedback in React.
""",
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
        "category": 'bootstrap',
        "subcategory": 'ui',
        "tags": ['bootstrap', 'react-bootstrap', 'form', 'validation', 'feedback', 'ui', 'component']
    },
    {
        "problem": """
A React component that displays data in a responsive Bootstrap grid.
""",
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
        "category": 'bootstrap',
        "subcategory": 'ui',
        "tags": ['bootstrap', 'ui', 'react-bootstrap', 'grid', 'card', 'layout', 'responsive']
    }
]
