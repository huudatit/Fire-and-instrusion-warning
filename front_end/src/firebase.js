// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth, connectAuthEmulator } from "firebase/auth";
import { getFirestore, connectFirestoreEmulator } from "firebase/firestore";
import { getFunctions, connectFunctionsEmulator } from "firebase/functions";


// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyAx-vnxqQAWUXlr3YrP8ZDmV3acf1NZ1wY",
  authDomain: "detectionfireandalert.firebaseapp.com",
  projectId: "detectionfireandalert",
  storageBucket: "detectionfireandalert.appspot.com",
  messagingSenderId: "195128054718",
  appId: "1:195128054718:web:c7691f3a37091cb5159fef",
  measurementId: "G-L81MKFRL39",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase services
const analytics = getAnalytics(app);
const auth = getAuth(app);
const db = getFirestore(app);
const functions = getFunctions(app);

// Connect to emulators in development environment
if (import.meta.env.DEV || window.location.hostname === "localhost") {
  try {
    // Use emulators if needed
    // connectAuthEmulator(auth, "http://localhost:9099");
    // connectFirestoreEmulator(db, "localhost", 8080);
    // connectFunctionsEmulator(functions, "localhost", 5001);
    console.log("Firebase running in development mode");
  } catch (error) {
    console.error("Error connecting to Firebase emulators:", error);
  }
}

// Enable Firestore persistence for offline capabilities
try {
  db.enablePersistence({ synchronizeTabs: true }).catch((err) => {
    if (err.code === "failed-precondition") {
      // Multiple tabs open, persistence can only be enabled in one tab at a time
      console.warn("Firestore persistence failed: Multiple tabs open");
    } else if (err.code === "unimplemented") {
      // The browser doesn't support persistence
      console.warn("Firestore persistence is not supported in this browser");
    }
  });
} catch (error) {
  console.error("Error enabling Firestore persistence:", error);
}

// Helper function to check if user is authenticated
const isAuthenticated = () => {
  return new Promise((resolve) => {
    const unsubscribe = auth.onAuthStateChanged((user) => {
      unsubscribe();
      resolve(!!user);
    });
  });
};

// Helper function to get current user
const getCurrentUser = () => {
  return new Promise((resolve, reject) => {
    const unsubscribe = auth.onAuthStateChanged((user) => {
      unsubscribe();
      resolve(user);
    }, reject);
  });
};

export { app, auth, db, functions, isAuthenticated, getCurrentUser };
