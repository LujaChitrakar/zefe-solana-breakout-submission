// hooks/useGetChains.ts
import { useQuery } from "@tanstack/react-query";
import publicAxios from "@/lib/publicAxios";

export const useGetChains = () => {
  return useQuery({
    queryKey: ["available-chains"],
    queryFn: async () => {
      const res = await publicAxios.get("/api/v1/attendees");
      // ✅ Return full chain array (not just values)
      return res.data.data.filter_options.chains ?? [];
    },
  });
};
