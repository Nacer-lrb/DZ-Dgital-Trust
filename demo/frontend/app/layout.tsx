import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DZ Sign | Documents et vérification",
  description:
    "Une démonstration locale pour comprendre la signature et la vérification de documents PDF.",
  robots: { index: false, follow: false },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  );
}
