import { useState } from "react";
import axiosInstance from "@/lib/axios";

export const useRemoveConnection = () => {
    const [isRemoving, setIsRemoving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const removeConnection = async (connectionId: number) => {
        console.log("[removeConnection] Attempting to remove connection:", connectionId);
        setIsRemoving(true);
        setError(null);

        try {
            console.log("[removeConnection] Sending request to remove connection:", connectionId);

            const response = await axiosInstance.post(
                `/api/v1/networking/connections/${connectionId}/remove/`
            );

            console.log("[removeConnection] Response:", response.data);

            if (response.data?.status === "SUCCESS") {
                console.log("[removeConnection] Connection removed successfully");
                return { success: true };
            } else {
                console.error("[removeConnection] Failed with response:", response.data);
                setError(response.data?.message || "Failed to remove connection");
                return { success: false };
            }
        } catch (err: any) {
            console.error("[removeConnection] Error:", err);
            setError(
                err.response?.data?.message ||
                "An error occurred while removing the connection"
            );
            return { success: false };
        } finally {
            setIsRemoving(false);
        }
    };

    return { removeConnection, isRemoving, error };
};