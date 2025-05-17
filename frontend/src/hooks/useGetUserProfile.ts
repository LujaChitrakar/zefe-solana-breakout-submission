import axiosInstance from "@/lib/axios";
import { useQuery } from "@tanstack/react-query";

export const useGetUserProfile = () => {
  return useQuery({
    queryKey: ["user-profile"],
    queryFn: async () => {
      const response = await axiosInstance.get("/api/v1/web/profile/");
      const raw = response.data.data.data; // <- fix is here

      return {
        user: raw.user,
        profile: raw.profile,
        fields: raw.fields ?? [],
        chains: [], // fallback if no chains
      };
    },
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
};
