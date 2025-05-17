"use client";

import { useState, useCallback, useEffect, useMemo } from "react";
import { LoginButton } from "@telegram-auth/react";
import {
  Dialog,
  DialogContent,
  DialogTrigger,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import axios from "axios";
import { setCookie, getCookie, deleteCookie } from "@/lib/cookies";
import { clearAuth, getAuthUser, saveAuth } from "@/lib/auth";

interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  auth_date: number;
  hash: string;
}

interface User {
  id: number;
  name: string;
  username: string;
  telegram_id: string;
  photo_url?: string;
  is_new_user?: boolean;
}

interface ApiResponse {
  status: string;
  message: string;
  data?: {
    status: string;
    data: {
      access_token: string;
      refresh_token: string;
      user: User;
    };
  };
}

const TelegramLogin = ({
  onLoginSuccess,
  buttonText = "Sign up with Telegram",
  buttonClassName = "rounded-full bg-blue-600 hover:bg-blue-700 px-6",
  icon,
}: {
  onLoginSuccess?: (userData: User) => void;
  buttonText?: string;
  buttonClassName?: string;
  icon?: React.ReactNode;
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [showTelegramHelp, setShowTelegramHelp] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const apiUrl = useMemo(() => {
    const base =
      process.env.NEXT_PUBLIC_API_BASE_URL ||
      (typeof window !== "undefined" && window.location.hostname === "localhost"
        ? "http://localhost:8000"
        : "https://api.zefe.xyz");

    return base.replace(/\/+$/, "");
  }, []);

  const refreshToken = async (): Promise<boolean> => {
    try {
      const refreshTokenValue = getCookie("refresh_token");
      if (!refreshTokenValue) return false;

      const response = await axios.post(`${apiUrl}/api/v1/token/refresh/`, {
        refresh: refreshTokenValue,
      });

      if (response.data?.access) {
        setCookie("access_token", response.data.access);
        return true;
      }
      return false;
    } catch (error) {
      console.error("Token refresh failed:", error);
      return false;
    }
  };

  useEffect(() => {
    const checkSession = async () => {
      const accessToken = getCookie("access_token");
      const refreshTokenStr = getCookie("refresh_token");

      if (!accessToken || !refreshTokenStr || !getCookie("user")) {
        return;
      }

      try {
        const profileResponse = await axios.get(
          `${apiUrl}/api/v1/web/profile/`,
          {
            headers: { Authorization: `Bearer ${accessToken}` },
          }
        );

        if (profileResponse.status === 200) {
          setIsLoggedIn(true);
          onLoginSuccess?.(getAuthUser());
          return;
        }
      } catch {
        const refreshed = await refreshToken();
        if (refreshed) {
          const newAccessToken = getCookie("access_token");
          try {
            const retryResponse = await axios.get(
              `${apiUrl}/api/v1/web/profile/`,
              {
                headers: { Authorization: `Bearer ${newAccessToken}` },
              }
            );

            if (retryResponse.status === 200) {
              setIsLoggedIn(true);
              onLoginSuccess?.(getAuthUser());
              return;
            }
          } catch {}
        }
      }

      clearAuth();
    };

    checkSession();
  }, [apiUrl, onLoginSuccess]);

  const handleTelegramAuth = useCallback(
    async (user: TelegramUser) => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await axios.post<ApiResponse>(
          `${apiUrl}/api/v1/auth/web/telegram-login/`,
          user,
          {
            headers: { "Content-Type": "application/json" },
            timeout: 15000,
          }
        );

        const result = response.data;

        if (
          result?.status === "SUCCESS" &&
          result?.data?.status === "SUCCESS" &&
          result?.data?.data
        ) {
          const {
            access_token,
            refresh_token,
            user: userData,
          } = result.data.data;

          const fullUser = {
            ...userData,
            is_new_user: userData.is_new_user ?? true,
          };

          saveAuth({
            accessToken: access_token,
            refreshToken: refresh_token,
            user: fullUser,
          });

          setIsLoggedIn(true);
          setIsDialogOpen(false);
          window.dispatchEvent(new Event("auth-changed"));
          onLoginSuccess?.(fullUser);
        } else {
          setError(result?.message || "Unexpected server response.");
        }
      } catch (err: any) {
        if (err.response?.data?.message) {
          setError(`API Error: ${err.response.data.message}`);
        } else if (err.request) {
          setError("No response from server. Check your internet connection.");
        } else {
          setError(`Error: ${err.message}`);
        }
      } finally {
        setIsLoading(false);
      }
    },
    [apiUrl, onLoginSuccess]
  );

  const handleTelegramHelp = () => {
    setShowTelegramHelp((prev) => !prev);
  };

  const handleLogout = () => {
    clearAuth();
    window.dispatchEvent(new Event("auth-changed"));
    setIsLoggedIn(false);
  };

  if (isLoggedIn) {
    return (
      <div className="flex items-center space-x-2">
        <Button className={buttonClassName}>Home</Button>
        <Button variant="outline" onClick={handleLogout} size="sm">
          Logout
        </Button>
      </div>
    );
  }

  return (
    <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
      <DialogTrigger asChild>
        <Button className={buttonClassName} disabled={isLoading}>
          {isLoading ? "..." : icon || buttonText}
        </Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-md">
        <DialogTitle>Sign up with Telegram</DialogTitle>
        <DialogDescription>
          Use your Telegram account to sign in and connect with others.
        </DialogDescription>

        <div className="p-4 text-center">
          {error && <div className="text-red-600 text-sm mb-4">{error}</div>}

          <div className="flex flex-col items-center justify-center">
            <LoginButton
              botUsername="zefexyz_bot"
              onAuthCallback={(user) => handleTelegramAuth(user)}
              buttonSize="large"
              cornerRadius={8}
              showAvatar={true}
            />

            <button
              onClick={handleTelegramHelp}
              className="text-sm text-blue-600 hover:underline mt-4"
            >
              {showTelegramHelp
                ? "Hide help"
                : "Not receiving Telegram message?"}
            </button>

            {showTelegramHelp && (
              <div className="mt-4 text-sm bg-blue-50 p-3 rounded-md text-left">
                <h4 className="font-medium mb-2">Troubleshooting Tips:</h4>
                <ul className="list-disc pl-5 space-y-1">
                  <li>Ensure Telegram is open</li>
                  <li>Message @zefexyz_bot directly</li>
                  <li>Check your phone number format</li>
                  <li>Try Telegram Web (web.telegram.org)</li>
                  <li>Clear cookies/cache and retry</li>
                  <li>Ensure internet connection is stable</li>
                </ul>
                <p className="mt-2">
                  <a
                    href="https://t.me/zefexyz_bot"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    Open @zefexyz_bot in Telegram
                  </a>
                </p>
              </div>
            )}
          </div>
        </div>

        <DialogFooter className="flex flex-col sm:flex-row sm:justify-between">
          <Button
            variant="outline"
            onClick={() => setIsDialogOpen(false)}
            className="mb-2 sm:mb-0"
          >
            Cancel
          </Button>
          <div className="text-xs text-gray-500">
            Having issues? Try refreshing or contact support.
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default TelegramLogin;
