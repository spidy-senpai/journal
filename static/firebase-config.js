import { initializeApp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js";
import { getAuth, 
         GoogleAuthProvider } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-firestore.js";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDXZ_Q3UJKepiwSao4IIo5vBNVx80UJNMo",
  authDomain: "moon-69bef.firebaseapp.com",
  projectId: "moon-69bef",
  storageBucket: "moon-69bef.firebasestorage.app",
  messagingSenderId: "489523094617",
  appId: "1:489523094617:web:f641df150b037c7f49bd48",
  measurementId: "G-3BXWF2S80J"
};
  // Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

const db = getFirestore(app);

export { auth, provider, db };