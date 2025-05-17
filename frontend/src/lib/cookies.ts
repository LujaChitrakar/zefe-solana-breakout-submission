// lib/cookies.ts
import Cookies from "js-cookie";

type CookieKey = "access_token" | (string & {});

type SerializeOptions = {
  expires?: number | Date;
  path?: string;
  domain?: string;
  secure?: boolean;
  sameSite?: "lax" | "strict" | "none";
};

export const setCookie = (
  key: CookieKey,
  value: string,
  options?: SerializeOptions
) => {
  Cookies.set(key, value, options);
};

export const getCookie = (key: CookieKey): string | undefined => {
  return Cookies.get(key);
};

export const hasCookie = (key: CookieKey): boolean => {
  return !!Cookies.get(key);
};

export const deleteCookie = (key: CookieKey) => {
  Cookies.remove(key);
};
