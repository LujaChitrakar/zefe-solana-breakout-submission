// hooks/useAuth.ts
"use client";

import { useEffect, useState } from "react";
import { getCookie } from "@/lib/cookies";

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  const checkAuth = () => {
    const token = getCookie("access_token");
    setIsAuthenticated(!!token);
  };

  useEffect(() => {
    checkAuth();

    window.addEventListener("auth-changed", checkAuth);
    return () => window.removeEventListener("auth-changed", checkAuth);
  }, []);

  return { isAuthenticated };
}
