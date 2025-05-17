// lib/auth.ts
import { setCookie, getCookie, deleteCookie } from "./cookies";

export const saveAuth = (tokens: {
  accessToken: string;
  refreshToken: string;
  user: any;
}) => {
  // lib/auth.ts
  setCookie("access_token", tokens.accessToken, { expires: 30 });
  setCookie("refresh_token", tokens.refreshToken, { expires: 30 });
  setCookie("user", JSON.stringify(tokens.user), { expires: 30 });
};

export const clearAuth = () => {
  deleteCookie("access_token");
  deleteCookie("refresh_token");
  deleteCookie("user");
};

export const getAuthUser = (): any | null => {
  const user = getCookie("user");
  return user ? JSON.parse(user) : null;
};
