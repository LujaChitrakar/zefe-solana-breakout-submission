import axiosInstance from "@/lib/axios";
import { useQuery } from "@tanstack/react-query";

// Create a hook to fetch notification count
export const useNotificationCount = () => {
    return useQuery({
        queryKey: ["notification-count"],
        queryFn: async () => {
            const response = await axiosInstance.get("/api/v1/notifications/count");
            return response.data;
        },
        refetchInterval: 60000,
        refetchOnWindowFocus: true,
    });
};