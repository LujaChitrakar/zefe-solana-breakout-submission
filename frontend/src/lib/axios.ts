// lib/axios.ts
import axios from "axios";
import { getCookie } from "@/lib/cookies";

// const API_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.zefe.xyz";
const API_URL = "https://api.zefe.xyz";

console.log("🔧 API Base URL being used:", API_URL);

const axiosInstance = axios.create({
  baseURL: API_URL,
  // baseURL: 'https://api.zefe.xyz',
  headers: {
    "Content-Type": "application/json",
    // 'ngrok-skip-browser-warning': 'true',
  },
});
console.log("🔧 API Base URL:", process.env.NEXT_PUBLIC_API_BASE_URL);

// Automatically attach access token (if exists) to every request
axiosInstance.interceptors.request.use((config) => {
  const token = getCookie("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default axiosInstance;
