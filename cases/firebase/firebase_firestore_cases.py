"""
Firebase Firestore Cases for CBR MCP Server

This module contains case-based reasoning examples for Firebase Firestore
database operations including CRUD operations, real-time updates, and
document management.
"""

FIREBASE_FIRESTORE_CASES = [
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
""",
        "category": "firebase",
        "subcategory": "firestore",
        "tags": ["firestore", "create", "add", "document", "database", "crud", "collection", "firebase", "nosql", "document-write"]
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
""",
        "category": "firebase",
        "subcategory": "firestore",
        "tags": ["firestore", "read", "fetch", "document", "database", "query", "firebase", "react", "hook", "realtime"]
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
""",
        "category": "firebase",
        "subcategory": "firestore",
        "tags": ["firestore", "read", "collection", "query", "database", "firebase", "react", "hook", "realtime", "snapshot"]
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
""",
        "category": "firebase",
        "subcategory": "firestore",
        "tags": ["firestore", "update", "modify", "document", "database", "crud", "firebase", "batch", "batch-write", "document-delete"]
    }
]
