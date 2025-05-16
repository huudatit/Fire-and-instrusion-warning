// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyAx-vnxqQAWUXlr3YrP8ZDmV3acf1NZ1wY",
  authDomain: "detectionfireandalert.firebaseapp.com",
  projectId: "detectionfireandalert",
  storageBucket: "detectionfireandalert.firebasestorage.app",
  messagingSenderId: "195128054718",
  appId: "1:195128054718:web:c7691f3a37091cb5159fef",
  measurementId: "G-L81MKFRL39",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const auth = getAuth(app);
const db = getFirestore(app);

export { app, auth, db };
