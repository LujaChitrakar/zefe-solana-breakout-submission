"use client";

import Image from "next/image";
import { Button } from "@/components/ui/button";
import NoteRequestModal from "../noteRequestModal";
import { useState } from "react";
import { useWallet } from "@solana/wallet-adapter-react";
import { useWalletModal } from "@solana/wallet-adapter-react-ui";

export default function ProfileCard({ data }: { data: any }) {
  const [showNoteModal, setShowNoteModal] = useState(false);

  const { publicKey, connected } = useWallet();
  const { setVisible } = useWalletModal();

  const handleMessageClick = () => {
    if (!connected) {
      setVisible(true); // Trigger wallet modal
    } else {
      setShowNoteModal(true); // Show note box if wallet connected
    }
  };

  return (
    <div className="bg-gray-50 rounded-2xl p-6 flex flex-col items-center shadow-md max-w-xs text-center hover:shadow-lg transition">
      <div className="w-20 h-20 rounded-full overflow-hidden bg-red-500 mb-3 flex items-center justify-center">
        <Image
          src={
            data?.photo_url ||
            "https://static.vecteezy.com/system/resources/thumbnails/009/292/244/small/default-avatar-icon-of-social-media-user-vector.jpg"
          }
          alt="Profile"
          width={80}
          height={80}
          className="object-cover"
        />
      </div>

      <h3 className="font-bold text-gray-900 text-lg">{data?.name}</h3>
      <p className="text-sm text-gray-600 mt-1">
        {data?.user_profile?.position} | {data?.user_profile.project_name}
      </p>
      <p className="text-xs text-gray-500 mt-2 leading-snug max-w-[220px]">
        {data?.user_profile?.bio}
      </p>

      <Button
        size="sm"
        onClick={handleMessageClick}
        className="cursor-pointer text-white bg-red-500 hover:bg-red-600 rounded-full px-4 py-1 mt-4 text-xs"
      >
        Message
      </Button>
      {showNoteModal && (
        <NoteRequestModal
          receiverId={data?.id}
          recipientName={data?.name}
          receiverWallet={data?.user_profile?.wallet_address} // ✅ Add this line
          onClose={() => setShowNoteModal(false)}
        />
      )}
    </div>
  );
}
