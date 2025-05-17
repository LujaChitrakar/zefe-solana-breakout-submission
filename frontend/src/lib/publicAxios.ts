// lib/publicAxios.ts
import axios from "axios";

const API_URL = "https://api.zefe.xyz";
const publicAxios = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export default publicAxios;
