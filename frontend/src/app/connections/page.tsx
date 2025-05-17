"use client";

import Image from "next/image";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useConnections } from "@/hooks/useGetConnections";
import { useRemoveConnection } from "@/hooks/useRemoveConnection";
import Navbar from "@/components/navbar";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { MoreVertical } from "lucide-react";

const filters = ["ROLE", "VERTICALS", "CHAIN ECOSYSTEM", "CITY"];

const filterKeyMap: Record<
  string,
  "position" | "user_fields" | "chain" | "city"
> = {
  ROLE: "position",
  VERTICALS: "user_fields",
  "CHAIN ECOSYSTEM": "chain",
  CITY: "city",
};

export default function ConnectionPage() {
  const [activeFilter, setActiveFilter] = useState("ROLE");
  const [selectedFilters, setSelectedFilters] = useState({
    position: "",
    user_fields: "",
    chain: "",
    city: "",
  });
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedConnection, setSelectedConnection] = useState<any>(null);

  const { data, isLoading, refetch } = useConnections();
  const { removeConnection, isRemoving } = useRemoveConnection();

  const connections = data?.connections ?? [];
  const filterOptions = data?.filter_options ?? {
    positions: [],
    fields: [],
    chains: [],
    cities: [],
  };

  const getOptionsForActiveFilter = () => {
    const key = filterKeyMap[activeFilter];
    switch (key) {
      case "position":
        return filterOptions.positions;
      case "user_fields":
        return filterOptions.fields;
      case "chain":
        return filterOptions.chains;
      case "city":
        return filterOptions.cities;
      default:
        return [];
    }
  };

  const filteredConnections = connections.filter((conn) => {
    const user = conn.user;
    const { position, user_fields, chain, city } = selectedFilters;

    const matchPosition = position
      ? user.position?.toLowerCase() === position.toLowerCase()
      : true;
    const matchCity = city
      ? user.city?.toLowerCase() === city.toLowerCase()
      : true;
    const matchChain = chain
      ? user.chain_ecosystem?.toLowerCase() === chain.toLowerCase()
      : true;
    const matchField = user_fields
      ? user.user_fields?.some(
          (f) => f.name?.toLowerCase() === user_fields.toLowerCase()
        )
      : true;

    return matchPosition && matchCity && matchChain && matchField;
  });

  const handleRemove = async () => {
    if (!selectedConnection) return;
    const result = await removeConnection(selectedConnection.id);
    if (result.success) {
      setModalOpen(false);
      refetch();
    }
  };

  return (
    <div className="min-h-screen bg-[#FCF3DC] text-black px-4 py-8">
      <Navbar />
      <header className="mb-10 mt-10">
        <div
          style={{ fontFamily: "Horizon, sans-serif" }}
          className="text-sm tracking-wider font-semibold text-black"
        >
          PRE EVENT CONNECTION LIST
        </div>
        <h1 className="text-4xl font-extrabold mt-2">Filter by</h1>
      </header>

      <div className="flex gap-3 flex-wrap mb-6">
        {filters.map((filter) => (
          <button
            key={filter}
            className={`border px-4 py-1 rounded-full text-sm font-semibold transition ${
              activeFilter === filter
                ? "bg-white text-black"
                : "border-black text-black"
            }`}
            onClick={() => setActiveFilter(filter)}
          >
            {filter}
          </button>
        ))}
      </div>

      {getOptionsForActiveFilter().length > 0 && (
        <div className="flex flex-wrap gap-3 mb-10">
          {getOptionsForActiveFilter().map((option) => (
            <button
              key={option}
              className={`px-4 py-1 rounded-full text-sm font-semibold border ${
                selectedFilters[filterKeyMap[activeFilter]] === option
                  ? "bg-red-500 text-black"
                  : "border-black text-black"
              }`}
              onClick={() =>
                setSelectedFilters((prev) => ({
                  ...prev,
                  [filterKeyMap[activeFilter]]:
                    prev[filterKeyMap[activeFilter]] === option ? "" : option,
                }))
              }
            >
              {option}
            </button>
          ))}
        </div>
      )}

      {isLoading ? (
        <p className="text-gray-300">Loading connections...</p>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {filteredConnections.length === 0 ? (
            <p className="text-gray-400 col-span-full">No connections found.</p>
          ) : (
            filteredConnections.map((conn: any, index: number) => (
              <div
                key={index}
                className="bg-white rounded-2xl relative flex flex-col items-center text-center p-4 text-black"
              >
                <div className="absolute top-2 right-2">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" className="h-6 w-6 p-0">
                        <MoreVertical className="w-4 h-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent>
                      <DropdownMenuItem
                        onClick={() => {
                          setSelectedConnection(conn);
                          setModalOpen(true);
                        }}
                      >
                        Remove
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
                <div className="w-16 h-16 mb-3 rounded-full overflow-hidden">
                  <Image
                    src={conn.user.photo_url || "/avatar-fallback.png"}
                    alt={conn.user.name}
                    width={64}
                    height={64}
                    className="object-cover"
                  />
                </div>
                <p className="text-sm font-bold">{conn.user.name}</p>
                <p className="text-xs text-gray-600 mb-3">
                  {conn.user.position}{" "}
                  {conn.user.project_name && `at ${conn.user.project_name}`}
                </p>
                <Button
                  className="text-xs bg-gray-200 hover:bg-gray-300 rounded-full px-4 py-1"
                  variant="outline"
                >
                  MESSAGE IN TELEGRAM
                </Button>
              </div>
            ))
          )}
        </div>
      )}

      <Dialog open={modalOpen} onOpenChange={setModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Remove this connection?</DialogTitle>
          </DialogHeader>
          <div className="flex justify-end gap-3 mt-4">
            <Button variant="outline" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleRemove} disabled={isRemoving}>
              {isRemoving ? "Removing..." : "Confirm"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
