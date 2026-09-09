"use client";

import { createContext, useContext, useEffect, useRef, useState, useSyncExternalStore } from "react";
import { RecaptchaVerifier, onAuthStateChanged, signInWithPhoneNumber, signOut as firebaseSignOut } from "firebase/auth";
import { firebaseAuth, firebaseConfigured } from "@/lib/firebase";

const PhoneAuthContext = createContext(null);
const TEST_PHONE = "+911234567890";
const TEST_CODE = "123456";
const testMode = process.env.NEXT_PUBLIC_FIREBASE_AUTH_TEST_MODE === "true";
const DEMO_AUTH_EVENT = "jalnetra-demo-auth-change";

function demoSessionSnapshot() {
  return testMode && sessionStorage.getItem("jalnetra-demo-auth") === TEST_PHONE;
}

function subscribeToDemoSession(listener) {
  window.addEventListener(DEMO_AUTH_EVENT, listener);
  return () => window.removeEventListener(DEMO_AUTH_EVENT, listener);
}

function setDemoSession(active) {
  if (active) sessionStorage.setItem("jalnetra-demo-auth", TEST_PHONE);
  else sessionStorage.removeItem("jalnetra-demo-auth");
  window.dispatchEvent(new Event(DEMO_AUTH_EVENT));
}
const errorMessage = (error) => ({
  "auth/invalid-phone-number": "Enter your number with country code, for example +919876543210.",
  "auth/invalid-app-credential": "Firebase rejected app verification. Confirm localhost is listed in Authorized Domains under Firebase Auth Settings.",
  "auth/captcha-check-failed": "Firebase couldn't complete app verification. Refresh the page and try again.",
  "auth/operation-not-allowed": "Phone sign-in is disabled in Firebase. Enable Phone provider under Firebase Console -> Authentication -> Sign-in method, and restart your Next.js dev server.",
  "auth/too-many-requests": "Too many attempts. Please wait a few minutes and try again.",
  "auth/quota-exceeded": "SMS quota is unavailable. Please try again later.",
}[error?.code] || `We couldn't send the code (${error?.code || "error"}). Please try again.`);

export function usePhoneAuth() {
  return useContext(PhoneAuthContext);
}

export default function PhoneAuthProvider({ children }) {
  const [user, setUser] = useState(() => firebaseAuth ? undefined : null);
  const demoSignedIn = useSyncExternalStore(subscribeToDemoSession, demoSessionSnapshot, () => false);
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [confirmation, setConfirmation] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const verifier = useRef(null);

  useEffect(() => {
    if (!firebaseAuth) return undefined;
    return onAuthStateChanged(firebaseAuth, setUser);
  }, []);

  useEffect(() => () => verifier.current?.clear(), []);

  async function sendCode(event) {
    event.preventDefault();
    setError("");
    if (!/^\+\d{8,15}$/.test(phone.trim())) { setError("Enter your number with country code, for example +919876543210."); return; }
    setBusy(true);
    // ponytail: local demo bypass; replace with Firebase test flow before deployment.
    if (testMode && phone.trim() === TEST_PHONE) { setConfirmation({ demoBypass: true }); setBusy(false); return; }
    try {
      verifier.current ||= new RecaptchaVerifier(firebaseAuth, "phone-recaptcha", { size: "invisible" });
      setConfirmation(await signInWithPhoneNumber(firebaseAuth, phone.trim(), verifier.current));
    } catch (requestError) {
      setError(errorMessage(requestError));
      verifier.current?.clear();
      verifier.current = null;
    } finally { setBusy(false); }
  }

  async function verifyCode(event) {
    event.preventDefault();
    setError("");
    if (!/^\d{6}$/.test(code.trim())) { setError("Enter the six-digit code sent to your phone."); return; }
    setBusy(true);
    if (confirmation.demoBypass) {
      if (code.trim() === TEST_CODE) {
        setDemoSession(true);
      } else setError("That code isn't valid. Check it and try again.");
      setBusy(false);
      return;
    }
    try { await confirmation.confirm(code.trim()); }
    catch (verifyError) { setError(verifyError?.code === "auth/invalid-verification-code" ? "That code isn't valid. Check it and try again." : "We couldn't verify that code. Please try again."); }
    finally { setBusy(false); }
  }

  if (user === undefined && !demoSignedIn) return <div className="auth-loading">Checking secure sign-in…</div>;
  if (user || demoSignedIn) return <PhoneAuthContext.Provider value={{ user: user || { uid: "jalnetra-demo-user", phoneNumber: TEST_PHONE }, signOut: async () => { setDemoSession(false); if (firebaseAuth?.currentUser) await firebaseSignOut(firebaseAuth); } }}>{children}</PhoneAuthContext.Provider>;

  return <main className="auth-shell"><section className="auth-card" aria-labelledby="phone-login-title">
    <div className="brand-mark"><span className="brand-dot" />JalNetra</div>
    <p className="eyebrow">Marine safety, in your language</p>
    <h1 id="phone-login-title">Sign in with your phone</h1>
    <p>We’ll send a one-time code to keep your marine updates personal and secure.</p>
    {!firebaseConfigured ? <p className="auth-error">Firebase settings are missing. Add the existing `NEXT_PUBLIC_FIREBASE_*` values to `.env.local` and restart the app.</p> : confirmation ? <form onSubmit={verifyCode}><label htmlFor="verification-code">Six-digit code</label><input id="verification-code" inputMode="numeric" autoComplete="one-time-code" value={code} onChange={(event) => setCode(event.target.value.replace(/\D/g, "").slice(0, 6))} placeholder="123456" autoFocus /><button type="submit" disabled={busy}>{busy ? "Verifying…" : "Verify and continue"}</button><button type="button" className="auth-link" onClick={() => { setConfirmation(null); setCode(""); setError(""); }}>Use a different number</button></form> : <form onSubmit={sendCode}><label htmlFor="phone-number">Mobile number</label><input id="phone-number" type="tel" inputMode="tel" autoComplete="tel" value={phone} onChange={(event) => setPhone(event.target.value)} placeholder="+919876543210" autoFocus /><button type="submit" disabled={busy}>{busy ? "Sending…" : "Send verification code"}</button></form>}
    {error && <p className="auth-error" role="alert">{error}</p>}<div id="phone-recaptcha" />
  </section></main>;
}
