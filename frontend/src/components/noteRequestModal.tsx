"use client";

import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { X } from "lucide-react";
import { useWallet } from "@solana/wallet-adapter-react";
import { Connection, PublicKey, SystemProgram } from "@solana/web3.js";
import { AnchorProvider, BN, Program } from "@coral-xyz/anchor";
import idl from "@/components/zefe.json";
import { useSendNetworkingRequest } from "@/hooks/useSendNetworkingRequest";

const LAMPORTS_PER_SOL = 1000000000;
const CONNECTION_COST = 0.003 * LAMPORTS_PER_SOL;
const PROGRAM_ID = new PublicKey(
  "4Ng72C6t9m8RXCBbGMz8ifuQh9S64sDw8h6jaVUSYHit"
);

type Props = {
  onClose: () => void;
  recipientName?: string;
  receiverId: number;
  receiverWallet: string;
};

export default function NoteRequestModal({
  onClose,
  recipientName = "User",
  receiverId,
  receiverWallet,
}: Props) {
  const [noteContent, setNoteContent] = useState(
    `I saw your profile and would love to connect!`
  );
  const [sending, setSending] = useState(false);
  const [requestId, setRequestId] = useState("");
  const wallet = useWallet();
  const sendNote = useSendNetworkingRequest();

  useEffect(() => {
    if (!requestId) {
      setRequestId(`req_${Math.random().toString(36).substring(2, 15)}`);
    }
  }, [requestId]);

  const getProvider = () => {
    if (!wallet.publicKey) return null;

    const connection = new Connection(
      "https://api.devnet.solana.com",
      "confirmed"
    );

    const provider = new AnchorProvider(connection, wallet, {
      commitment: "confirmed",
    });

    return provider;
  };

  const sendConnectionRequest = async () => {
    try {
      setSending(true);
      const provider = getProvider();
      if (!provider) {
        toast.error("Wallet not connected.");
        return;
      }

      if (!receiverWallet) {
        toast.error("Receiver has no wallet address.");
        return;
      }

      let receiverPubkey;
      try {
        receiverPubkey = new PublicKey(receiverWallet);
      } catch (err) {
        toast.error("Invalid receiver wallet address.");
        return;
      }

      const program = new Program(idl, provider);
      const lamportsAmount = new BN(CONNECTION_COST);

      const [escrowAccount] = await PublicKey.findProgramAddress(
        [
          Buffer.from("escrow"),
          provider.wallet.publicKey.toBuffer(),
          receiverPubkey.toBuffer(),
          Buffer.from(requestId),
        ],
        program.programId
      );

      console.log("Sending transaction with data:", {
        sender: provider.wallet.publicKey.toString(),
        receiver: receiverWallet,
        requestId: requestId,
        escrowAccount: escrowAccount.toString(),
      });

      const tx = await program.methods
        .sendConnectionRequest(receiverPubkey, String(requestId))
        .accounts({
          sender: provider.wallet.publicKey,
          escrowAccount: escrowAccount,
          systemProgram: SystemProgram.programId,
        })
        .rpc();

      console.log("Transaction signature:", tx);
      toast.success("0.003 SOL sent successfully!");

      // Include all blockchain data in the API request
      sendNote.mutate(
        {
          receiver: receiverId,
          note_content: noteContent,
          request_id: requestId,
          sender_wallet: provider.wallet.publicKey.toString(),
          receiver_wallet: receiverWallet,
          escrow_account: escrowAccount.toString(),
          tx_signature: tx,
        },
        {
          onSuccess: () => {
            toast.success("Note sent successfully!");
            onClose();
          },
          onError: (error) => {
            console.error("API error:", error);
            toast.error("Failed to send the note. Please try again.");
          },
        }
      );

      // Don't generate new request ID here as it could cause inconsistencies
      // setRequestId(`req_${Math.random().toString(36).substring(2, 15)}`);
    } catch (error) {
      console.error("Error sending connection request:", error);
      toast.error("Transaction failed.");
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl p-6 w-full max-w-md relative shadow-lg space-y-4">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center"
        >
          <X size={14} />
        </button>

        <h2 className="text-lg font-bold text-center">
          Send a note to {recipientName}
        </h2>

        <textarea
          rows={6}
          value={noteContent}
          onChange={(e) => setNoteContent(e.target.value)}
          className="w-full rounded-lg border px-4 py-3 text-sm resize-none text-gray-800 focus:outline-none focus:ring-1 focus:ring-purple-500"
        />

        <p className="text-xs italic text-gray-500 text-center">
          This note costs 0.003 SOL and can only be sent once.
        </p>

        <button
          className="bg-purple-600 w-full text-white font-semibold py-2 rounded-full hover:bg-purple-700 transition"
          onClick={sendConnectionRequest}
          disabled={sending}
        >
          {sending ? "Processing..." : "Send 0.003 SOL to Send Note"}
        </button>
      </div>
    </div>
  );
}
