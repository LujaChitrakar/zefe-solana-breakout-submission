"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { VerticalSelector } from "./verticles-selector";
import { useGetUserProfile } from "@/hooks/useGetUserProfile";
import { useUpdateUserProfile } from "@/hooks/useUpdateProfile";
import toast from "react-hot-toast";
import { useGetChains } from "@/hooks/useGetChains";
import { ChainSelector } from "./ChainSelector";
import { useGetPositions } from "@/hooks/useGetPositions";
import { WalletMultiButton } from "@solana/wallet-adapter-react-ui";
import { useWallet } from "@solana/wallet-adapter-react";

type ProfileFormState = {
  fullName: string;
  username: string;
  city: string;
  bio: string;
  position: string;
  projectName: string;
  chainEcosystem: string[];
  twitter: string;
  linkedin: string;
  email: string;
  wallet: string;
};

export default function ProfileDialogContent({
  onClose,
}: {
  onClose: () => void;
}) {
  const { data: positionsData = [] } = useGetPositions();
  const positionOptions = positionsData.map((p: any) => p.label);

  const { data, isLoading } = useGetUserProfile();
  const updateProfile = useUpdateUserProfile();
  const { data: chainData } = useGetChains();
  const [chainOptions, setChainOptions] = useState<
    { value: string; label: string }[]
  >([]);

  const [selectedVerticals, setSelectedVerticals] = useState<string[]>([]);

  const [profile, setProfile] = useState<ProfileFormState>({
    fullName: "",
    username: "",
    city: "",
    bio: "",
    position: "",
    projectName: "",
    chainEcosystem: [],
    twitter: "",
    linkedin: "",
    email: "",
    wallet: "",
  });
  const { publicKey } = useWallet();

  useEffect(() => {
    console.log("Twitter from profileData:", data?.profile?.twitter_account);
  }, [data]);

  useEffect(() => {
    if (Array.isArray(chainData)) {
      setChainOptions(chainData); // <-- NOT .map(...).filter(...)
    }
  }, [chainData]);

  console.log("Raw chainData:", chainData);
  console.log("Options:", chainOptions);

  // Load user profile
  useEffect(() => {
    if (!data || !data.user || !data.profile || !chainData) return;

    const user = data.user;
    const profileData = data.profile;
    let chainList: string[] = [];

    try {
      const raw = profileData.chain_ecosystem;

      if (Array.isArray(raw)) {
        chainList = raw;
      } else if (typeof raw === "string") {
        const parsed = JSON.parse(raw.replace(/'/g, '"'));
        if (Array.isArray(parsed)) chainList = parsed;
      }
    } catch (e) {
      console.warn("Failed to parse chain_ecosystem:", e);
    }

    const selectedVerticalsList = (data.fields ?? []).map((f: any) => f.name);

    setSelectedVerticals(selectedVerticalsList);

    setProfile({
      fullName: user.name ?? "",
      username: user.username ?? "",
      city: profileData.city ?? "",
      bio: profileData.bio ?? "",
      position: profileData.position ?? "",
      projectName: profileData.project_name ?? "",
      chainEcosystem: chainList,
      twitter: profileData.twitter_account ?? "",
      linkedin: profileData.linkedin_url ?? "",
      email: profileData.email ?? "",
      wallet: profileData.wallet_address ?? "",
    });
  }, [data, chainData]);

  useEffect(() => {
    if (publicKey) {
      setProfile((prev) => ({
        ...prev,
        wallet: publicKey.toBase58(),
      }));
    }
  }, [publicKey]);

  const handleChange = (field: keyof ProfileFormState, value: any) => {
    setProfile((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = () => {
    const payload = {
      name: profile.fullName,
      username: profile.username,
      position: profile.position,
      project_name: profile.projectName,
      city: profile.city,
      bio: profile.bio,
      twitter_account: profile.twitter,
      linkedin_url: profile.linkedin,
      email: profile.email,
      wallet_address: profile.wallet,
      verticals: selectedVerticals,
      chain_ecosystem: profile.chainEcosystem,
    };

    toast.promise(updateProfile.mutateAsync(payload), {
      loading: "Saving profile...",
      success: () => {
        onClose();
        return "Profile updated successfully!";
      },
      error: "Failed to update profile. Please try again.",
    });
  };

  if (isLoading) return <p>Loading user profile...</p>;
  console.log("Chains:", profile.chainEcosystem);
  console.log("Twitter:", profile.twitter);
  console.log("Options:", chainOptions);

  return (
    <div className="flex flex-col md:flex-row gap-10">
      <div className="flex flex-col w-full md:w-1/2 space-y-8">
        <div className="flex flex-col items-center">
          <div className="rounded-xl overflow-hidden w-48 h-48 bg-red-500 mb-3">
            <Image
              src={data?.user?.photo_url || "https://i.pravatar.cc/300"}
              alt="Avatar"
              width={192}
              height={192}
              className="object-cover w-full h-full"
            />
          </div>
          <p className="text-sm text-gray-500">Change image</p>
        </div>

        <Section title="PERSONAL">
          <div className="flex flex-col space-y-4 text-sm">
            <EditableField
              label="Full Name"
              value={profile.fullName}
              onChange={(val) => handleChange("fullName", val)}
            />
            <EditableField
              label="Telegram Username"
              value={profile.username}
              disabled
              onChange={(val) => handleChange("username", val)}
            />
            <EditableField
              label="City"
              value={profile.city}
              onChange={(val) => handleChange("city", val)}
            />
            <EditableField
              label="Bio"
              value={profile.bio}
              onChange={(val) => handleChange("bio", val)}
              multiline
            />
          </div>
        </Section>
      </div>

      <div className="flex flex-col w-full md:w-1/2 space-y-8">
        <Section title="PROJECTS">
          <InfoGrid>
            <div className="col-span-2">
              <EditableField
                label="Your position"
                value={profile.position}
                onChange={(val) => handleChange("position", val)}
                options={positionOptions}
              />
            </div>
            <div className="col-span-2">
              <EditableField
                label="Project name"
                value={profile.projectName}
                onChange={(val) => handleChange("projectName", val)}
              />
            </div>
            <div className="col-span-2">
              <p className="text-xs text-gray-500 mb-1">Chain Ecosystem</p>
              <ChainSelector
                selected={profile.chainEcosystem}
                onChange={(val) => handleChange("chainEcosystem", val)}
                options={chainOptions}
              />
            </div>
            <div className="col-span-2">
              <VerticalSelector
                onChange={setSelectedVerticals}
                selected={selectedVerticals}
              />
            </div>
          </InfoGrid>
        </Section>

        <Section title="SOCIALS">
          <div className="flex flex-col space-y-4 text-sm">
            <EditableField
              label="X (Twitter) username"
              value={profile.twitter}
              onChange={(val) => handleChange("twitter", val)}
            />
            <EditableField
              label="LinkedIn URL"
              value={profile.linkedin}
              onChange={(val) => handleChange("linkedin", val)}
            />
            <EditableField
              label="Email address"
              value={profile.email}
              onChange={(val) => handleChange("email", val)}
            />

            {publicKey && (
              <EditableField
                label="Wallet"
                value={profile.wallet}
                onChange={() => {}}
                disabled
              />
            )}
          </div>
        </Section>

        <div className="pt-4 text-right">
          <Button
            className="bg-green-600 hover:bg-green-700"
            onClick={handleSave}
          >
            Save
          </Button>
        </div>
      </div>
    </div>
  );
}

// Layout Components
function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <h2 className="text-lg font-semibold text-black mb-4">{title}</h2>
      {children}
    </div>
  );
}

function InfoGrid({ children }: { children: React.ReactNode }) {
  return <div className="grid grid-cols-2 gap-4 text-sm">{children}</div>;
}

// Reusable Field Component
function EditableField({
  label,
  value,
  onChange,
  multiline = false,
  disabled = false,
  options,
}: {
  label: string;
  value: string | string[];
  onChange: (val: string | string[]) => void;
  multiline?: boolean;
  disabled?: boolean;
  options?: string[];
}) {
  return (
    <div className={`${multiline ? "sm:col-span-2" : ""}`}>
      <p className="text-xs text-gray-500 mb-1">{label}</p>

      {Array.isArray(value) && options ? (
        <select
          multiple
          value={value}
          onChange={(e) => {
            const selected = Array.from(e.target.selectedOptions).map(
              (opt) => opt.value
            );
            onChange(selected);
          }}
          className="w-full rounded-md border px-3 py-2 text-sm text-gray-800 bg-gray-100 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          {options.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      ) : options ? (
        <select
          value={value as string}
          disabled={disabled}
          onChange={(e) => onChange(e.target.value)}
          className="w-full rounded-md border px-3 py-2 text-sm text-gray-800 bg-gray-100 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="">Select one</option>
          {options.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      ) : multiline ? (
        <textarea
          disabled={disabled}
          value={value as string}
          onChange={(e) => onChange(e.target.value)}
          rows={3}
          className="w-full rounded-md border px-3 py-2 text-sm text-gray-800 bg-gray-100 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      ) : (
        <input
          type="text"
          disabled={disabled}
          value={value as string}
          onChange={(e) => onChange(e.target.value)}
          className="w-full rounded-md border px-3 py-2 text-sm text-gray-800 bg-gray-100 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      )}
    </div>
  );
}
