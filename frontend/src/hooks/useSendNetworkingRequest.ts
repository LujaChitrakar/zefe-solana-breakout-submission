import { useMutation } from "@tanstack/react-query";
import axiosInstance from "@/lib/axios";

type SendNetworkingRequestPayload = {
  receiver: number;
  note_content: string;
  request_id: string;
  sender_wallet: string;
  receiver_wallet: string;
  escrow_account: string;
  tx_signature?: string;
};

export const useSendNetworkingRequest = () => {
  return useMutation({
    mutationFn: async (payload: SendNetworkingRequestPayload) => {
      console.log("📤 Sending networking request with payload:", payload);
      const response = await axiosInstance.post(
        "/api/v1/networking/send-request/",
        payload
      );
      console.log("✅ Response received:", response.data);
      return response.data;
    },
  });
};