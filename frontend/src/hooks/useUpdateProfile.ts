import { useMutation } from "@tanstack/react-query";
import axiosInstance from "@/lib/axios";

type UpdateProfilePayload = {
  name: string;
  username: string;
  position: string;
  project_name: string;
  city: string;
  bio: string;
  twitter_account: string;
  linkedin_url: string;
  email: string;
  wallet_address: string;
  verticals: string[];
  chain_ecosystem: string[];
};

export const useUpdateUserProfile = () => {
  return useMutation({
    mutationFn: async (payload: UpdateProfilePayload) => {
      const response = await axiosInstance.put(
        `/api/v1/onboarding?source=web`,
        payload
      );

      return response.data;
    },
  });
};
