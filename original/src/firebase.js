
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.0/firebase-app.js";
import { getFirestore, collection, addDoc, updateDoc, doc } from "https://www.gstatic.com/firebasejs/9.22.0/firebase-firestore.js";

// TODO: User must replace this with their own Firebase Config

const firebaseConfig = {
    apiKey: "AIzaSyCve-vIMHhFc-W15DrFQTZVHQhBfsyxCo8",
    authDomain: "gita-personality-index-survey.firebaseapp.com",
    projectId: "gita-personality-index-survey",
    storageBucket: "gita-personality-index-survey.firebasestorage.app",
    messagingSenderId: "494201601703",
    appId: "1:494201601703:web:1e2b1e51770229f3782582",
    measurementId: "G-E49P0Z35LE"
};


let db;

try {
    const app = initializeApp(firebaseConfig);
    db = getFirestore(app);
    console.log("Firebase initialized successfully");
} catch (e) {
    console.warn("Firebase initialization failed. Make sure to update firebaseConfig in src/firebase.js with your credentials.");
    console.error(e);
}

/**
 * Saves the entire session state to the 'assessments' collection in Firestore.
 * @param {Object} sessionData - The full state object from dataStore
 */
export async function saveSessionData(sessionData) {
    if (!db) {
        console.warn("Cannot save to Firebase: DB not initialized.");
        return;
    }

    try {
        const docRef = await addDoc(collection(db, "assessments"), {
            ...sessionData,
            uploadedAt: new Date().toISOString()
        });
        console.log("Document written with ID: ", docRef.id);
        return docRef.id;
    } catch (e) {
        console.error("Error adding document: ", e);
        throw e;
    }
}

/**
 * Updates an existing session document in Firestore.
 * @param {string} docId - The ID of the document to update
 * @param {Object} data - The data to merge into the document (e.g. { feedback: "..." })
 */
export async function updateSessionData(docId, data) {
    if (!db) {
        console.warn("Cannot update Firebase: DB not initialized.");
        return;
    }

    try {
        const docRef = doc(db, "assessments", docId);
        await updateDoc(docRef, data);
        console.log("Document updated with ID: ", docId);
    } catch (e) {
        console.error("Error updating document: ", e);
        // non-critical, don't throw to avoid user confusion
    }
}
