// hooks/useRespondToRequest.ts
import { useMutation, useQueryClient } from "@tanstack/react-query";
import axiosInstance from "@/lib/axios";

export type ResponseStatus = "accepted" | "rejected" | "spam";

interface RespondPayload {
  requestId: number;
  status: ResponseStatus;
}

export const useRespondToRequest = () => {
  const queryClient = useQueryClient();

  return useMutation<any, Error, RespondPayload>({
    mutationFn: async ({ requestId, status }) => {
      const res = await axiosInstance.post(
        `/api/v1/networking/respond/${requestId}/`,
        { status }
      );
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["networking", "received"] });
    },
  });
};
