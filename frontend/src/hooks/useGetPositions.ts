// hooks/useGetPositions.ts
import { useQuery } from "@tanstack/react-query";
import publicAxios from "@/lib/publicAxios";

export const useGetPositions = () => {
  return useQuery({
    queryKey: ["available-positions"],
    queryFn: async () => {
      const res = await publicAxios.get("/api/v1/attendees");
      return res.data.data.filter_options.positions ?? [];
    },
  });
};
