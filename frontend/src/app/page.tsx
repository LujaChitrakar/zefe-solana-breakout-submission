"use client";

import Image from "next/image";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import FilterSection from "@/components/filter-section";
import Footer from "@/components/footer";
import ProfileCard from "@/components/ui/profile-card";
import Navbar from "@/components/navbar";
import { useGetAttendees } from "@/hooks/useGetAttendees";
import TelegramLogin from "@/components/telegramLogin";
import { getAuthUser } from "@/lib/auth";
// import ConnectionRequestApp from "@/components/Escrow";
import { ContextProvider } from "@/contexts/ContextProvider";
require("@solana/wallet-adapter-react-ui/styles.css");

export default function Home() {
  const [selectedFilters, setSelectedFilters] = useState({
    position: "",
    user_fields: "",
    chain: "",
    city: "",
  });
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userData, setUserData] = useState<any>(null);

  const { data, isLoading } = useGetAttendees(selectedFilters);
  const attendees = data?.users ?? [];
  console.log("Attendee data:", data?.users);

  const handleLoginSuccess = (userData: any) => {
    console.log("Login successful", userData);
    setIsLoggedIn(true);
    setUserData(userData);

    // Optionally handle new user onboarding without redirect
    if (userData.is_new_user) {
      console.log("New user detected, showing onboarding UI");
      // You can trigger a modal or update UI here for onboarding
    }
  };

  const derivedFilterOptions = {
    positions: Array.from(
      new Set(
        attendees
          .map((u) => u.user_profile?.position)
          .filter((v): v is string => !!v?.trim())
      )
    ),
    user_fields: Array.from(
      new Set(
        attendees
          .flatMap((u) => u.user_profile.user_fields?.map((f) => f.name) ?? [])
          .filter((v): v is string => !!v?.trim())
      )
    ),
    chains: Array.from(
      new Set(
        attendees
          .map((u) => u.user_profile?.chain_ecosystem)
          .filter((v): v is string => !!v?.trim())
      )
    ),
    cities: Array.from(
      new Set(
        attendees
          .map((u) => u.user_profile?.city)
          .filter((v): v is string => !!v?.trim())
      )
    ),
  };

  return (
    <>
      <div className="min-h-screen flex flex-col bg-[#FCF3DC]">
        <Navbar />

        <main className="flex-1">
          <section className="container mx-auto px-4 py-12 text-center">
            <div className="max-w-3xl mx-auto space-y-6">
              <div className="font-horizon">
                <div className="flex flex-col items-center space-y-2">
                  <h1
                    className=" text-[50px] font-bold text-black"
                    style={{ fontFamily: "Horizon, sans-serif" }}
                  >
                    Connect early
                  </h1>

                  <h2
                    style={{ fontFamily: "Horizon, sans-serif" }}
                    className="text-[50px] font-bold text-black"
                  >
                    Find the right people
                  </h2>
                  <h3
                    className="text-[50px] font-bold text-black"
                    style={{ fontFamily: "Horizon, sans-serif" }}
                  >
                    Build Connection
                  </h3>
                </div>
              </div>

              <div className="text-lg text-gray-700 font-medium">
                Start pre-networking
              </div>

              {isLoggedIn && userData ? (
                <div className="text-lg text-gray-700 font-medium">
                  Welcome, {userData.name}!{" "}
                  {userData.is_new_user && (
                    <span>
                      Let&apos;s get started with{" "}
                      <button
                        onClick={() => console.log("Start onboarding")}
                        className="text-blue-600 hover:underline"
                      >
                        onboarding
                      </button>
                      .
                    </span>
                  )}
                </div>
              ) : (
                <TelegramLogin
                  buttonText="SIGN UP"
                  onLoginSuccess={handleLoginSuccess}
                  buttonClassName="rounded-full bg-blue-600 hover:bg-blue-700 px-6"
                />
              )}

              <div className="mt-10">
                <p className="text-sm text-gray-700 mb-4">
                  {data?.total_users}+ Attendees Already Networking
                </p>
                <div className="flex justify-center -space-x-2">
                  {[...Array(9)].map((_, i) => (
                    <div
                      key={i}
                      className="w-8 h-8 rounded-full border-2 border-white overflow-hidden"
                    >
                      <div className="w-full h-full bg-red-500 flex items-center justify-center">
                        <Image
                          src="https://github.com/AsianChand.png"
                          alt="Attendee"
                          width={32}
                          height={32}
                          className="object-cover"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </section>

          <h2
            style={{ fontFamily: "Horizon, sans-serif" }}
            className="text-[20px] font-medium text-center text-gray-900 "
          >
            ZEFE PRE event Networking test run
          </h2>

          <section className="container mx-auto px-4 py-6">
            <h2 className="text-2xl font-bold mb-6 text-center text-gray-900">
              Filter attendees by
            </h2>

            <FilterSection
              selectedFilters={selectedFilters}
              setSelectedFilters={setSelectedFilters}
              filterOptions={derivedFilterOptions}
            />

            <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 bg-[#1C1C1C] p-4 rounded-lg">
              {isLoading ? (
                <p className="text-white">Loading attendees...</p>
              ) : attendees.length === 0 ? (
                <p className="text-white">No attendees found.</p>
              ) : (
                attendees
                  .filter((user) =>
                    selectedFilters.user_fields
                      ? user.user_profile?.user_fields?.some(
                          (f) =>
                            f.name?.toLowerCase() ===
                            selectedFilters.user_fields.toLowerCase()
                        )
                      : true
                  )
                  .map((user) => <ProfileCard key={user.id} data={user} />)
              )}
            </div>
          </section>
        </main>

        <Footer />
      </div>
      <div>
        {/* <ContextProvider>
          <ConnectionRequestApp />
        </ContextProvider> */}
      </div>
    </>
  );
}
