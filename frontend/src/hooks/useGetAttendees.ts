import { useQuery, UseQueryOptions } from "@tanstack/react-query";
import axiosInstance from "@/lib/axios";
import publicAxios from "@/lib/publicAxios";

export interface Filters {
  position?: string;
  user_fields?: string;
  chain?: string;
  city?: string;
}

interface Attendee {
  id: number;
  name: string;
  photo_url: string;
  user_profile: {
    position: string;
    bio: string;
    project_name: string | null;
    user_fields?: { id: number; name: string }[]; // ✅ ADD THIS
    chain_ecosystem?: string; // ✅ ADD THIS
    city?: string; // ✅ ADD THIS
  };
}

interface AttendeeResponse {
  users: Attendee[];
  total_users: number;
  filter_options: any;
}

export const useGetAttendees = (filters?: Filters) => {
  return useQuery<AttendeeResponse, Error>({
    queryKey: ["attendees", filters],
    queryFn: async () => {
      const params = new URLSearchParams();

      if (filters?.position) {
        params.append("position", filters.position.toUpperCase());
      }
      if (filters?.user_fields) {
        params.append("user_fields", filters.user_fields);
      }
      if (filters?.chain) {
        params.append("chains", filters.chain.toUpperCase());
      }
      if (filters?.city) {
        params.append("city", filters.city.toUpperCase());
      }

      const response = await publicAxios.get(`/api/v1/attendees?${params}&source=WEB`);


      return response.data.data;
    },
  });
};
