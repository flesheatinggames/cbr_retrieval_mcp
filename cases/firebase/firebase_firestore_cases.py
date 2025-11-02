"""
Firebase Firestore Cases for CBR MCP Server

This module contains case-based reasoning examples for Firebase Firestore
database operations including CRUD operations, real-time updates, and
document management.
"""

FIREBASE_FIRESTORE_CASES = [
    {
        "problem": """
A function to add a new document to a 'users' collection in Firestore.
""",
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
""",
        "category": 'firebase',
        "subcategory": 'firestore',
        "tags": ['firebase', 'firestore', 'create', 'add', 'document', 'database', 'crud']
    },
    {
        "problem": """
A React hook to fetch a single document from Firestore by its ID.
""",
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
""",
        "category": 'firebase',
        "subcategory": 'firestore',
        "tags": ['firebase', 'firestore', 'read', 'fetch', 'document', 'database', 'query']
    },
    {
        "problem": """
A React hook to listen for real-time updates on a Firestore collection.
""",
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
""",
        "category": 'firebase',
        "subcategory": 'firestore',
        "tags": ['firebase', 'firestore', 'read', 'collection', 'query', 'database', 'react']
    },
    {
        "problem": """
A function to update an existing document in Firestore.
""",
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
""",
        "category": 'firebase',
        "subcategory": 'firestore',
        "tags": ['firebase', 'firestore', 'update', 'modify', 'document', 'database', 'crud']
    },
    {
        "problem": """
Secure Firebase Storage uploads with file validation, size limits, and malware scanning simulation.
""",
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
""",
        "category": 'firebase',
        "subcategory": 'firestore',
        "tags": ['api', 'async', 'auth', 'authentication', 'event', 'firebase', 'firestore']
    }
]
