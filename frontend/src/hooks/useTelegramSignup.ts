import { useMutation } from "@tanstack/react-query";
import axiosInstance from "@/lib/axios";
import { setCookie } from "@/lib/cookies";

type TelegramSignupPayload = {
  telegram_id: string;
  name: string;
  username: string;
  photo_url: string;
  position: string;
  company: string;
  city: string;
  bio: string;
  fields: string[];
};

export function useTelegramSignup() {
  return useMutation({
    mutationFn: async (payload: TelegramSignupPayload) => {
      const response = await axiosInstance.post(
        "/api/v1/telegram-mock-login/",
        payload
      );

      const accessToken = response?.data?.access_token;
      if (accessToken) {
        setCookie("access_token", accessToken, { expires: 30 });
      }

      return response.data;
    },
  });
}
