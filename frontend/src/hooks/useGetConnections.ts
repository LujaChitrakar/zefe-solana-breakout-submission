import { useQuery } from "@tanstack/react-query";
import axiosInstance from "@/lib/axios";

export interface ConnectedUser {
  id: number;
  name: string;
  username: string;
  photo_url: string;
  telegram_account: string;
  telegram_id: number;
  position: string;
  city?: string;
  bio: string | null;
  user_fields?: { id: number; name: string }[];
  chain_ecosystem?: string;
}

export interface Connection {
  id: number;
  connection_date: string;
  user: ConnectedUser;
  note: string;
  request_direction: "sent" | "received";
}

interface ConnectionResponse {
  connections: Connection[];
  filter_options: {
    positions: string[];
    cities: string[];
    chains: string[];
    fields: string[];
  };
}

export const useConnections = () => {
  return useQuery<ConnectionResponse>({
    queryKey: ["connections"],
    queryFn: async () => {
      const res = await axiosInstance.get("/api/v1/networking/connections");
      const connections: Connection[] = res.data.data.data;

      const positions = Array.from(
        new Set(connections.map((c) => c.user.position).filter(Boolean))
      );

      const cities = Array.from(
        new Set(
          connections
            .map((c) => c.user.city)
            .filter((c): c is string => Boolean(c))
        )
      );

      const chains = Array.from(
        new Set(
          connections
            .map((c) => c.user.chain_ecosystem)
            .filter((c): c is string => Boolean(c))
        )
      );

      const fields = Array.from(
        new Set(
          connections.flatMap(
            (c) => c.user.user_fields?.map((f) => f.name) || []
          )
        )
      );

      return {
        connections,
        filter_options: {
          positions,
          cities,
          chains,
          fields,
        },
      };
    },

    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: true,
  });
};
