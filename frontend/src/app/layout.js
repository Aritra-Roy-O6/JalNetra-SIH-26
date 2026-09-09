import "./globals.css";
import { ResolvedLocationProvider } from "@/lib/location-context";
import PhoneAuthProvider from "@/components/PhoneAuthProvider";

export const metadata = {
  title: "JalNetra ORCA",
  description: "Marine ecosystem reasoning dashboard",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col"><PhoneAuthProvider><ResolvedLocationProvider>{children}</ResolvedLocationProvider></PhoneAuthProvider></body>
    </html>
  );
}
