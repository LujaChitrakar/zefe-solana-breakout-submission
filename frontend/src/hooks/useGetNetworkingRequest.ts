import { useQuery } from "@tanstack/react-query";
import axiosInstance from "@/lib/axios";

export interface NetworkingNotification {
  id: number;
  note_content: string;
  status: "pending" | "accepted" | "rejected" | "spam";
  created_date: string;

  // Blockchain fields
  request_id: string;
  sender_wallet: string;
  receiver_wallet: string;
  escrow_account: string;
  tx_signature?: string;

  sender_details: {
    id: number;
    name: string;
    username: string;
    photo_url: string;
    wallet_address?: string;
  };
}

export const useReceivedNotifications = () => {
  return useQuery<NetworkingNotification[]>({
    queryKey: ["networking", "received"],
    queryFn: async () => {
      console.log("🔄 Fetching received networking requests...");
      const res = await axiosInstance.get(
        "/api/v1/networking/received-requests/"
      );

      const notifications = res.data.data;
      console.log("📦 Received notifications with blockchain data:", notifications);

      // Debug data structure
      if (notifications && notifications.length > 0) {
        console.log("🔍 First notification sample:", {
          id: notifications[0].id,
          request_id: notifications[0].request_id || "⚠️ MISSING",
          sender_wallet: notifications[0].sender_wallet || "⚠️ MISSING",
          escrow_account: notifications[0].escrow_account || "⚠️ MISSING"
        });
      } else {
        console.log("📭 No notifications received");
      }

      return notifications;
    },
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: true,
  });
};