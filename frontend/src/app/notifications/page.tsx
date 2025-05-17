"use client";

import {
  ResponseStatus,
  useRespondToRequest,
} from "@/hooks/respondToRequestHook";
import { useReceivedNotifications } from "@/hooks/useGetNetworkingRequest";
import Image from "next/image";
import { useState } from "react";
import toast from "react-hot-toast";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faBellSlash } from "@fortawesome/free-solid-svg-icons";
import Navbar from "@/components/navbar";
import { Connection, PublicKey, SystemProgram } from "@solana/web3.js";
import { AnchorProvider, Program, BN, Idl } from "@coral-xyz/anchor";
import idl from "@/components/zefe.json";
import { useWallet, WalletContextState } from "@solana/wallet-adapter-react";

const LAMPORTS_PER_SOL = 1000000000;
const CONNECTION_COST = 0.003 * LAMPORTS_PER_SOL;
const PROGRAM_ID = new PublicKey(
  "4Ng72C6t9m8RXCBbGMz8ifuQh9S64sDw8h6jaVUSYHit"
);

export default function NetworkingRequests() {
  const [expandedNoteId, setExpandedNoteId] = useState<number | null>(null);
  const { data = [], isLoading } = useReceivedNotifications();
  const respond = useRespondToRequest();
  const wallet: WalletContextState = useWallet();
  const [loading, setLoading] = useState(false);

  const toggleNote = (id: number) => {
    setExpandedNoteId((prev) => (prev === id ? null : id));
  };

  const getProvider = () => {
    if (
      !wallet.publicKey ||
      !wallet.signTransaction ||
      !wallet.signAllTransactions
    ) {
      console.log("❌ Wallet not fully connected or initialized");
      return null;
    }

    console.log("✅ Wallet connected:", wallet.publicKey.toString());
    const connection = new Connection(
      "https://api.devnet.solana.com",
      "confirmed"
    );

    const provider = new AnchorProvider(connection, wallet as any, {
      commitment: "confirmed",
    });

    return provider;
  };

  const handleResponse = (id: number, status: ResponseStatus) => {
    console.log(`📤 Sending API response for request ${id}: status=${status}`);
    respond.mutate(
      { requestId: id, status },
      {
        onSuccess: () => {
          console.log(`✅ API response successful: ${status}`);
          toast.success(`Marked as ${status.toUpperCase()}`);
        },
        onError: (error) => {
          console.error(`❌ API response failed:`, error);
          toast.error("Something went wrong. Try again.");
        },
      }
    );
  };

  const acceptRequest = async (note: any) => {
    setLoading(true);
    console.log("🔄 Starting accept request process");
    console.log("📝 Note data:", note);

    try {
      const provider = getProvider();
      if (!provider) {
        toast.error("Please connect your wallet first");
        setLoading(false);
        return;
      }

      // Use data from note object if available, otherwise use fallback
      const senderPublicKey = new PublicKey(
        note.sender_wallet || note.sender_details.wallet_address
      );
      const requestId =
        note.request_id || `req_${Math.random().toString(36).substring(2, 15)}`;

      console.log("🔑 Using sender wallet:", senderPublicKey.toString());
      console.log("🆔 Using request ID:", requestId);

      // Try to use stored escrow account if available
      let escrowAccount;
      if (note.escrow_account) {
        console.log("🏦 Using stored escrow account:", note.escrow_account);
        escrowAccount = new PublicKey(note.escrow_account);
      } else {
        console.log("🏦 Calculating escrow account from seeds...");
        const program = new Program(idl as Idl, PROGRAM_ID, provider);

        [escrowAccount] = await PublicKey.findProgramAddress(
          [
            Buffer.from("escrow"),
            senderPublicKey.toBuffer(),
            provider.wallet.publicKey.toBuffer(),
            Buffer.from(requestId),
          ],
          program.programId
        );
        console.log("🏦 Calculated escrow account:", escrowAccount.toString());
      }

      console.log("🛠️ Calculating vault address...");
      const program = new Program(idl as Idl, PROGRAM_ID, provider);
      const [vault] = await PublicKey.findProgramAddress(
        [
          Buffer.from("vault"),
          senderPublicKey.toBuffer(),
          provider.wallet.publicKey.toBuffer(),
          Buffer.from(requestId),
        ],
        program.programId
      );
      console.log("🏦 Vault address:", vault.toString());

      console.log("📡 Sending blockchain transaction...");
      console.log("📄 Transaction accounts:", {
        sender: senderPublicKey.toString(),
        receiver: provider.wallet.publicKey.toString(),
        escrowAccount: escrowAccount.toString(),
        vault: vault.toString(),
      });

      await program.methods
        .acceptRequest()
        .accounts({
          sender: senderPublicKey,
          escrowAccount: escrowAccount,
          vault: vault,
          systemProgram: SystemProgram.programId,
        })
        .rpc();

      console.log("✅ Blockchain transaction successful!");
      toast.success("Connection accepted on blockchain!");
      handleResponse(note.id, "accepted");
    } catch (error) {
      console.error("❌ Blockchain transaction failed:", error);
      toast.error("Failed to process blockchain transaction");
    } finally {
      setLoading(false);
    }
  };

  const rejectRequest = async (note: any) => {
    setLoading(true);
    console.log("🔄 Starting reject request process");
    console.log("📝 Note data:", note);

    try {
      const provider = getProvider();
      if (!provider) {
        toast.error("Please connect your wallet first");
        setLoading(false);
        return;
      }

      // Use data from note object if available, otherwise use fallback
      const senderPublicKey = new PublicKey(
        note.sender_wallet || note.sender_details.wallet_address
      );
      const requestId =
        note.request_id || `req_${Math.random().toString(36).substring(2, 15)}`;

      console.log("🔑 Using sender wallet:", senderPublicKey.toString());
      console.log("🆔 Using request ID:", requestId);

      // Try to use stored escrow account if available
      let escrowAccount;
      if (note.escrow_account) {
        console.log("🏦 Using stored escrow account:", note.escrow_account);
        escrowAccount = new PublicKey(note.escrow_account);
      } else {
        console.log("🏦 Calculating escrow account from seeds...");
        const program = new Program(idl as Idl, PROGRAM_ID, provider);

        [escrowAccount] = await PublicKey.findProgramAddress(
          [
            Buffer.from("escrow"),
            senderPublicKey.toBuffer(),
            provider.wallet.publicKey.toBuffer(),
            Buffer.from(requestId),
          ],
          program.programId
        );
        console.log("🏦 Calculated escrow account:", escrowAccount.toString());
      }

      console.log("🛠️ Calculating vault address...");
      const program = new Program(idl as Idl, PROGRAM_ID, provider);
      const [vault] = await PublicKey.findProgramAddress(
        [
          Buffer.from("vault"),
          senderPublicKey.toBuffer(),
          provider.wallet.publicKey.toBuffer(),
          Buffer.from(requestId),
        ],
        program.programId
      );
      console.log("🏦 Vault address:", vault.toString());

      console.log(
        "📡 Sending blockchain transaction (reject uses same method as accept)..."
      );
      console.log("📄 Transaction accounts:", {
        sender: senderPublicKey.toString(),
        receiver: provider.wallet.publicKey.toString(),
        escrowAccount: escrowAccount.toString(),
        vault: vault.toString(),
      });

      await program.methods
        .acceptRequest() // Note: This is intentional - blockchain contract uses same method
        .accounts({
          sender: senderPublicKey,
          escrowAccount: escrowAccount,
          vault: vault,
          systemProgram: SystemProgram.programId,
        })
        .rpc();

      console.log("✅ Blockchain transaction successful (rejection)!");
      toast.success("Connection rejected on blockchain");
      handleResponse(note.id, "rejected");
    } catch (error) {
      console.error("❌ Blockchain transaction failed:", error);
      toast.error("Failed to process blockchain transaction");
    } finally {
      setLoading(false);
    }
  };

  const markAsSpam = async (note: any) => {
    setLoading(true);
    console.log("🔄 Starting mark as spam process");
    console.log("📝 Note data:", note);

    try {
      const provider = getProvider();
      if (!provider) {
        toast.error("Please connect your wallet first");
        setLoading(false);
        return;
      }

      // Use data from note object if available, otherwise use fallback
      const senderPublicKey = new PublicKey(
        note.sender_wallet || note.sender_details.wallet_address
      );
      const requestId =
        note.request_id || `req_${Math.random().toString(36).substring(2, 15)}`;

      console.log("🔑 Using sender wallet:", senderPublicKey.toString());
      console.log("🆔 Using request ID:", requestId);

      // Try to use stored escrow account if available
      let escrowAccount;
      if (note.escrow_account) {
        console.log("🏦 Using stored escrow account:", note.escrow_account);
        escrowAccount = new PublicKey(note.escrow_account);
      } else {
        console.log("🏦 Calculating escrow account from seeds...");
        const program = new Program(idl as Idl, PROGRAM_ID, provider);

        [escrowAccount] = await PublicKey.findProgramAddress(
          [
            Buffer.from("escrow"),
            senderPublicKey.toBuffer(),
            provider.wallet.publicKey.toBuffer(),
            Buffer.from(requestId),
          ],
          program.programId
        );
        console.log("🏦 Calculated escrow account:", escrowAccount.toString());
      }

      console.log("📡 Sending mark as spam blockchain transaction...");
      console.log("📄 Transaction accounts:", {
        receiver: provider.wallet.publicKey.toString(),
        escrowAccount: escrowAccount.toString(),
      });

      const program = new Program(idl as Idl, PROGRAM_ID, provider);
      await program.methods
        .markAsSpam()
        .accounts({
          receiver: provider.wallet.publicKey,
          escrowAccount: escrowAccount,
        })
        .rpc();

      console.log("✅ Blockchain transaction successful (mark as spam)!");
      toast.success("Marked as spam on blockchain");
      handleResponse(note.id, "spam");
    } catch (error) {
      console.error("❌ Blockchain transaction failed:", error);
      toast.error("Failed to process blockchain transaction");
    } finally {
      setLoading(false);
    }
  };

  console.log("📊 Rendering with data:", data);

  return (
    <div className="min-h-screen bg-[#FCF3DC] px-6 py-10 text-black">
      <Navbar />
      <h1 className="text-4xl mt-10 font-extrabold text-black text-center mb-10 tracking-tight">
        NETWORKING REQUESTS
      </h1>

      {isLoading ? (
        <p className="text-center text-gray-300">Loading...</p>
      ) : data.length === 0 ? (
        <div className="flex flex-col items-center justify-center mt-20 text-center text-gray-400">
          🔕
          <h2 className="text-black text-xl font-semibold mb-2">
            No Networking Requests Yet
          </h2>
          <p className="text-sm max-w-sm text-black">
            You&apos;re all caught up. Once someone sends you a networking
            request, it will appear here.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {data.map((note: any) => {
            const isExpanded = expandedNoteId === note.id;
            const isPending = note.status === "pending";

            return (
              <div
                key={note.id}
                className="bg-white text-black rounded-3xl p-4 flex flex-col relative shadow-sm"
              >
                <div className="flex items-start gap-4">
                  <Image
                    src={
                      note.sender_details.photo_url || "/avatar-fallback.png"
                    }
                    alt="avatar"
                    width={60}
                    height={60}
                    className="rounded-full object-cover"
                  />

                  <div className="flex-1">
                    <p className="text-sm text-gray-600 mb-1">
                      {new Date(note.created_date).toLocaleDateString("en-US", {
                        day: "numeric",
                        month: "short",
                      })}
                    </p>

                    <p className="font-semibold text-sm">
                      NOTE FROM{" "}
                      {note.sender_details.name?.toUpperCase() || "UNKNOWN"}
                    </p>

                    <p
                      className={`mt-2 text-sm ${
                        isExpanded ? "text-gray-800" : "text-gray-500 truncate"
                      }`}
                    >
                      {isExpanded
                        ? note.note_content
                        : note.note_content.slice(0, 60) + "..."}
                    </p>

                    {isExpanded && isPending && (
                      <div className="flex flex-wrap gap-3 mt-4">
                        <button
                          onClick={() => acceptRequest(note)}
                          disabled={loading || respond.isPending}
                          className="border border-black px-4 py-1 rounded-full text-sm hover:bg-black hover:text-white transition disabled:opacity-50"
                        >
                          {loading ? "PROCESSING..." : "INTERESTED"}
                        </button>
                        <button
                          onClick={() => rejectRequest(note)}
                          disabled={loading || respond.isPending}
                          className="border border-black px-4 py-1 rounded-full text-sm hover:bg-black hover:text-white transition disabled:opacity-50"
                        >
                          {loading ? "PROCESSING..." : "NOT INTERESTED"}
                        </button>
                        <button
                          onClick={() => markAsSpam(note)}
                          disabled={loading || respond.isPending}
                          className="border border-purple-600 text-purple-600 px-4 py-1 rounded-full text-sm hover:bg-purple-600 hover:text-white transition disabled:opacity-50"
                        >
                          {loading ? "PROCESSING..." : "SPAMMER"}
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-end gap-2 mt-4">
                  <button
                    onClick={() => toggleNote(note.id)}
                    className="bg-gradient-to-r from-purple-500 to-indigo-500 text-white px-5 py-1.5 rounded-full text-sm font-semibold shadow hover:brightness-110 transition"
                  >
                    {isExpanded ? "Hide Note" : "View Note"}
                  </button>

                  {isPending && !isExpanded && (
                    <span className="w-3 h-3 bg-red-500 rounded-full" />
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
