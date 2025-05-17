import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import "@fontsource/orbitron";
import Providers from "./providers";
import { Toaster } from "react-hot-toast";
import { SolanaWalletWrapper } from "@/components/SolanaWalletWrapper"; // ✅ Adjust path as needed

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "zefe",
  description: "Zefe Pre Event Networking App",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <SolanaWalletWrapper>
          <Providers>
            <Toaster position="top-right" />
            {children}
          </Providers>
        </SolanaWalletWrapper>
      </body>
    </html>
  );
}
