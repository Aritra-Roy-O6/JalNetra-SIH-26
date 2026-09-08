import "./globals.css";
import { ResolvedLocationProvider } from "@/lib/location-context";

export const metadata = {
  title: "JalNetra ORCA",
  description: "Marine ecosystem reasoning dashboard",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col"><ResolvedLocationProvider>{children}</ResolvedLocationProvider></body>
    </html>
  );
}
