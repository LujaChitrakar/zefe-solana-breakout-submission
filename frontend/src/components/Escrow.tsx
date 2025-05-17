import { useState, useEffect } from "react";
import {
  Connection,
  PublicKey,
  Keypair,
  Transaction,
  SystemProgram,
} from "@solana/web3.js";
import { Program, AnchorProvider, web3, utils, BN } from "@coral-xyz/anchor";
import { useWallet } from "@solana/wallet-adapter-react";
import { WalletMultiButton } from "@solana/wallet-adapter-react-ui";
import idl from "../components/zefe.json";
import { buffer } from "stream/consumers";

const LAMPORTS_PER_SOL = 1000000000;
const CONNECTION_COST = 0.003 * LAMPORTS_PER_SOL; // 0.003 SOL in lamports

export default function ConnectionRequestApp() {
  const [receiverAddress, setReceiverAddress] = useState("");
  const [receivedRequest, setReceivedRequests] = useState([]);
  const [requestId, setRequestId] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [connectionRequests, setConnectionRequests] = useState([]);
  const wallet = useWallet();

  // Generate random request ID if not provided
  useEffect(() => {
    if (!requestId) {
      setRequestId(`req_${Math.random().toString(16).substring(2, 15)}`);
    }
  }, [requestId]);

  useEffect(() => {
    if (wallet.connected) {
      fetchReceivedRequests();
    }
  }, [wallet.connected]);

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

  const fetchReceivedRequests = async () => {
    try {
      setLoading(true);
      const provider = getProvider();
      if (!provider) {
        return;
      }

      const program = new Program(idl, provider);
      const connection = provider.connection;
      const accounts = await program.account.escrowAccount.all([
        {
          memcmp: {
            offset: 8, // Adjust based on your account structure
            bytes: wallet.publicKey.toBase58(),
          },
        },
      ]);
      console.log("THIS ARE ACCOUNTS", accounts);

      const requests = accounts.map((acc) => ({
        requestId: acc.account.requestId,
        receiver: acc.account.receiver.toString(),
        sender: acc.account.sender.toString(),
        amount: `${acc.account.amount / LAMPORTS_PER_SOL} SOL`,
        createdAt: new Date(acc.account.createdAt * 1000).toLocaleString(),
        escrowAccount: acc.publicKey.toString(),
      }));

      setReceivedRequests(requests);
    } catch (error) {
      console.error("Error fetching received requests:", error);
    } finally {
      setLoading(false);
    }
  };

  const sendConnectionRequest = async () => {
    try {
      setLoading(true);
      setStatus("Processing...");

      const provider = getProvider();
      if (!provider) {
        setStatus("Please connect your wallet first.");
        setLoading(false);
        return;
      }

      if (!receiverAddress) {
        setStatus("Please enter a receiver address.");
        setLoading(false);
        return;
      }

      // Validate receiver address
      let receiverPubkey;
      try {
        receiverPubkey = new PublicKey(receiverAddress);
      } catch (err) {
        setStatus("Invalid receiver address");
        setLoading(false);
        return;
      }

      const program = new Program(idl, provider);
      console.log(program);

      // Calculate the exact fee amount in lamports
      const lamportsAmount = new BN(CONNECTION_COST);

      // Derive PDA for escrow account
      const [escrowAccount] = await PublicKey.findProgramAddress(
        [
          Buffer.from("escrow"),
          provider.wallet.publicKey.toBuffer(),
          receiverPubkey.toBuffer(),
          Buffer.from(requestId),
        ],
        program.programId
      );

      console.log("Sending connection request...");
      console.log("Sender:", provider.wallet.publicKey.toString());
      console.log("Receiver:", receiverPubkey.toString());
      console.log("Request ID:", requestId);
      console.log("Escrow Account:", escrowAccount.toString());
      console.log("Amount:", lamportsAmount.toString(), "lamports");
      console.log("METHIODS:", program.methods, "");

      // Send the transaction with correct instruction format
      const tx = await program.methods
        .sendConnectionRequest(receiverPubkey, String(requestId))
        .accounts({
          sender: provider.wallet.publicKey,
          escrowAccount: escrowAccount,
          systemProgram: SystemProgram.programId,
        })
        .rpc();

      console.log("Transaction methods:", program.methods);
      console.log("Transaction signature:", tx);
      setStatus(`Connection request sent successfully! Cost: 0.003 SOL`);

      // Add to the list of requests
      setConnectionRequests((prev) => [
        ...prev,
        {
          requestId,
          receiver: receiverAddress,
          amount: "0.003 SOL",
          status: "Pending",
          createdAt: new Date().toLocaleString(),
          txSignature: tx,
        },
      ]);

      await fetchReceivedRequests(); // ⬅️ Add this after request is sent

      // Reset form
      setReceiverAddress("");
      setRequestId(`req_${Math.random().toString(36).substring(2, 15)}`);
    } catch (error) {
      console.error("Error sending connection request:", error);
      setStatus(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const acceptRequest = async (
    escrowAccountPubkey,
    requestId,
    senderPubkey
  ) => {
    try {
      setLoading(true);
      setStatus("Accepting connection request...");

      const provider = getProvider();
      if (!provider) {
        setStatus("Please connect your wallet first.");
        setLoading(false);
        return;
      }

      const program = new Program(idl, provider);
      console.log("This is program", program);

      // Convert senderPubkey string to PublicKey object
      const senderPublicKey = new PublicKey(senderPubkey);

      // Create the seeds correctly
      const [expectedEscrowAccount] = await PublicKey.findProgramAddress(
        [
          Buffer.from("escrow"),
          senderPublicKey.toBuffer(),
          provider.wallet.publicKey.toBuffer(),
          Buffer.from(requestId),
        ],
        program.programId
      );
      const [vault] = await PublicKey.findProgramAddress(
        [
          Buffer.from("vault"),
          senderPublicKey.toBuffer(),
          provider.wallet.publicKey.toBuffer(),
          Buffer.from(requestId),
        ],
        program.programId
      );
      console.log("Sending connection request...");
      console.log("receiver:", provider.wallet.publicKey.toString());
      console.log("Request ID:", requestId);
      console.log("Escrow Account:", expectedEscrowAccount.toString());
      console.log("METHIODS:", program.methods, "");

      console.log("Expected escrow account:", expectedEscrowAccount.toBase58());
      console.log("Actual escrow account:", escrowAccountPubkey);

      if (expectedEscrowAccount.toBase58() !== escrowAccountPubkey) {
        setStatus("Escrow account mismatch!");
        setLoading(false);
        return;
      }
      console.log("THIS IS old address", program.programId);
      console.log("THIS IS NEW address", idl.address);

      const escrowAccount = new PublicKey(escrowAccountPubkey);

      const tx = await program.methods
        .acceptRequest()
        .accounts({
          sender: senderPublicKey,
          escrowAccount: expectedEscrowAccount,
          vault: vault,
          systemProgram: SystemProgram.programId,
        })
        .rpc();

      // Add to the list of requests
      setConnectionRequests((prev) => [
        ...prev,
        {
          requestId,
          receiver: receiverAddress,
          amount: "0.003 SOL",
          status: "Accepted",
          createdAt: new Date().toLocaleString(),
          txSignature: tx,
        },
      ]);

      setStatus("Request accepted and SOL returned to sender!");
      console.log("Transaction:", tx);

      // Refresh list after successful acceptance
      await fetchReceivedRequests();
      setReceivedRequests((prev) =>
        prev.filter((req) => req.requestId !== requestId)
      );
    } catch (error) {
      console.error("Error accepting request:", error);
      setStatus(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const rejectRequest = async (
    escrowAccountPubkey,
    requestId,
    senderPubkey
  ) => {
    try {
      setLoading(true);
      setStatus("Rejecting connection request...");

      const provider = getProvider();
      if (!provider) {
        setStatus("Please connect your wallet first.");
        setLoading(false);
        return;
      }

      const program = new Program(idl, provider);
      console.log("This is program", program);

      // Convert senderPubkey string to PublicKey object
      const senderPublicKey = new PublicKey(senderPubkey);

      // Create the seeds correctly
      const [expectedEscrowAccount] = await PublicKey.findProgramAddress(
        [
          Buffer.from("escrow"),
          senderPublicKey.toBuffer(),
          provider.wallet.publicKey.toBuffer(),
          Buffer.from(requestId),
        ],
        program.programId
      );
      const [vault] = await PublicKey.findProgramAddress(
        [
          Buffer.from("vault"),
          senderPublicKey.toBuffer(),
          provider.wallet.publicKey.toBuffer(),
          Buffer.from(requestId),
        ],
        program.programId
      );
      console.log("Sending connection request...");
      console.log("Sender:", provider.wallet.publicKey.toString());
      console.log("Request ID:", requestId);
      console.log("Escrow Account:", expectedEscrowAccount.toString());
      console.log("METHIODS:", program.methods, "");

      console.log("Expected escrow account:", expectedEscrowAccount.toBase58());
      console.log("Actual escrow account:", escrowAccountPubkey);

      if (expectedEscrowAccount.toBase58() !== escrowAccountPubkey) {
        setStatus("Escrow account mismatch!");
        setLoading(false);
        return;
      }
      console.log("THIS IS old address", program.programId);
      console.log("THIS IS NEW address", idl.address);

      const escrowAccount = new PublicKey(escrowAccountPubkey);

      const tx = await program.methods
        .acceptRequest()
        .accounts({
          sender: senderPublicKey,
          escrowAccount: expectedEscrowAccount,
          vault: vault,
          systemProgram: SystemProgram.programId,
        })
        .rpc();

      // Add to the list of requests
      setConnectionRequests((prev) => [
        ...prev,
        {
          requestId,
          receiver: receiverAddress,
          amount: "0.003 SOL",
          status: "Rejected",
          createdAt: new Date().toLocaleString(),
          txSignature: tx,
        },
      ]);

      setStatus("Request rejected and SOL returned to sender!");
      console.log("Transaction:", tx);

      // Refresh list after successful acceptance
      await fetchReceivedRequests();
      setReceivedRequests((prev) =>
        prev.filter((req) => req.requestId !== requestId)
      );
    } catch (error) {
      console.error("Error rejecting request:", error);
      setStatus(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const markAsSpam = async (sender, requestId, escrowAccountPubkey) => {
    try {
      const provider = getProvider();
      if (!provider) {
        setStatus("Please connect your wallet first.");
        setLoading(false);
        return;
      }

      const senderPublicKey = new PublicKey(sender);
      const program = new Program(idl, provider);

      const [escrowPDA] = await PublicKey.findProgramAddressSync(
        [
          Buffer.from("escrow"),
          senderPublicKey.toBuffer(),
          provider.wallet.publicKey.toBuffer(),
          Buffer.from(requestId),
        ],
        program.programId
      );
      console.log(escrowPDA.toBase58(), escrowAccountPubkey);
      if (escrowPDA.toBase58() !== escrowAccountPubkey) {
        setStatus("Escrow account mismatch!");
        setLoading(false);
        return;
      }

      const tx = await program.methods
        .markAsSpam()
        .accounts({
          receiver: provider.wallet.publicKey,
          escrowAccount: escrowPDA,
        })
        .rpc();

      setConnectionRequests((prev) => [
        ...prev,
        {
          requestId,
          receiver: receiverAddress,
          amount: "0.003 SOL",
          status: "Marked as spam",
          createdAt: new Date().toLocaleString(),
          txSignature: tx,
        },
      ]);
      await fetchReceivedRequests();

      setStatus("Marked as spam!");
      console.log("Transaction:", tx);

      console.log("✅ Marked as spam");
    } catch (err) {
      console.error("❌ Error marking as spam", err);
    }
  };

  const resolveSpam = async (receiver, requestId, escrowAccountPubkey) => {
    try {
      const provider = getProvider();
      if (!provider) {
        setStatus("Please connect your wallet first.");
        setLoading(false);
        return;
      }

      const program = new Program(idl, provider);

      const receiverPubkey = new PublicKey(receiver);
      const [vaultPDA] = web3.PublicKey.findProgramAddressSync(
        [
          Buffer.from("vault"),
          provider.wallet.publicKey.toBuffer(),
          receiverPubkey.toBuffer(),
          Buffer.from(requestId),
        ],
        program.programId
      );

      const [escrowPDA] = web3.PublicKey.findProgramAddressSync(
        [
          Buffer.from("escrow"),
          provider.wallet.publicKey.toBuffer(),
          receiverPubkey.toBuffer(),
          Buffer.from(requestId),
        ],
        program.programId
      );
      console.log(escrowPDA.toBase58(), escrowAccountPubkey);
      if (escrowPDA.toBase58() !== escrowAccountPubkey) {
        setStatus("Escrow account mismatch!");
        setLoading(false);
        return;
      }

      const tx = await program.methods
        .resolveSpam()
        .accounts({
          vault: vaultPDA,
          sender: provider.wallet.publicKey,
          escrowAccount: escrowPDA,
          systemProgram: web3.SystemProgram.programId,
        })
        .rpc();
      setReceivedRequests((prev) =>
        prev.filter((req) => req.requestId !== requestId)
      );
      setStatus("Resolved spam!");
      console.log("Transaction:", tx);
      console.log("✅ Spam resolved and SOL refunded");
    } catch (err) {
      console.error("❌ Error resolving spam", err);
    }
  };

  const claimBackRequest = async (receiver, requestId, escrowAccountPubkey) => {
    try {
      setLoading(true);
      setStatus("Claiming back expired request...");

      const provider = getProvider();
      if (!provider) {
        setStatus("Please connect your wallet first.");
        setLoading(false);
        return;
      }

      const program = new Program(idl, provider);
      const receiverPubkey = new PublicKey(receiver);

      // Derive PDA (must match backend seeds)
      const [expectedEscrowAccount, _bump] = await PublicKey.findProgramAddress(
        [
          Buffer.from("escrow"),
          provider.wallet.publicKey.toBuffer(),
          receiverPubkey.toBuffer(),
          Buffer.from(requestId),
        ],
        program.programId
      );

      const [vault] = await PublicKey.findProgramAddress(
        [
          Buffer.from("vault"),
          provider.wallet.publicKey.toBuffer(),
          receiverPubkey.toBuffer(),
          Buffer.from(requestId),
        ],
        program.programId
      );

      console.log(expectedEscrowAccount.toBase58(), escrowAccountPubkey);
      if (expectedEscrowAccount.toBase58() !== escrowAccountPubkey) {
        setStatus("Escrow account mismatch!");
        setLoading(false);
        return;
      }

      const tx = await program.methods
        .claimBack()
        .accounts({
          sender: provider.wallet.publicKey,
          escrowAccount: expectedEscrowAccount,
          vault: vault,
          systemProgram: web3.SystemProgram.programId,
        })
        .rpc();

      setStatus("Request expired and SOL returned to sender!");
      console.log("✅ Transaction:", tx);

      setReceivedRequests((prev) =>
        prev.filter((req) => req.requestId !== requestId)
      );
    } catch (error) {
      console.error("Error in claimBackRequest:", error);
      setStatus(`❌ Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case "Pending":
        return "bg-yellow-100 text-yellow-800";
      case "Accepted":
        return "bg-green-100 text-green-800";
      case "Rejected":
        return "bg-red-100 text-red-800";
      case "Spam":
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-blue-100 text-blue-800";
    }
  };
  console.log(receivedRequest);
  return (
    <div className="max-w-4xl mx-auto p-6 bg-slate-50 min-h-screen text-black">
      {/* <div className="mb-10 text-center">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          Solana Connection Requests
        </h1>
        <p className="text-gray-600">Send connection requests for 0.003 SOL</p>
      </div>

      <div className="flex justify-end mb-6">
        <WalletMultiButton className="bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded" />
      </div>

      <div className="bg-white p-6 rounded-lg shadow mb-8">
        <h2 className="text-xl font-semibold mb-4">
          Send a New Connection Request
        </h2>

        <div className="mb-4">
          <label className="block text-gray-700 mb-2">Receiver Address</label>
          <input
            type="text"
            className="w-full p-2 border border-gray-300 rounded"
            placeholder="Enter Solana address"
            value={receiverAddress}
            onChange={(e) => setReceiverAddress(e.target.value)}
          />
        </div>

        <div className="mb-4">
          <label className="block text-gray-700 mb-2">Request ID</label>
          <input
            type="text"
            className="w-full p-2 border border-gray-300 rounded bg-gray-100"
            value={requestId}
            readOnly
          />
          <p className="text-xs text-gray-500 mt-1">Auto-generated unique ID</p>
        </div>

        <div className="mb-4">
          <label className="block text-gray-700 mb-2">Cost</label>
          <div className="p-2 bg-gray-100 border border-gray-300 rounded">
            0.003 SOL
          </div>
        </div>

        <button
          className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded w-full disabled:opacity-50 disabled:cursor-not-allowed"
          onClick={sendConnectionRequest}
          disabled={loading || !wallet.connected}
        >
          {loading ? "Processing..." : "Send Connection Request"}
        </button>

        {status && (
          <div
            className={`mt-4 p-3 rounded ${
              status.includes("Error")
                ? "bg-red-100 text-red-700"
                : "bg-green-100 text-green-700"
            }`}
          >
            {status}
          </div>
        )}
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Your Connection Requests</h2>

        <div className="overflow-x-auto">
          <table className="min-w-full bg-white">
            <thead>
              <tr>
                <th className="py-2 px-4 border-b text-left">Request ID</th>
                <th className="py-2 px-4 border-b text-left">Receiver</th>
                <th className="py-2 px-4 border-b text-left">Amount</th>
                <th className="py-2 px-4 border-b text-left">Status</th>
                <th className="py-2 px-4 border-b text-left">Created At</th>
                <th className="py-2 px-4 border-b text-left">Action</th>
              </tr>
            </thead>
            <tbody>
              {receivedRequest.map((request, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="py-2 px-4 border-b">{request.requestId}</td>
                  <td className="py-2 px-4 border-b">{`${request.receiver.substring(
                    0,
                    4
                  )}...${request.receiver.substring(
                    request.receiver.length - 4
                  )}`}</td>
                  <td className="py-2 px-4 border-b">{request.amount}</td>
                  <td className="py-2 px-4 border-b">
                    <span
                      className={`px-2 py-1 ${getStatusBadgeClass(
                        "Pending"
                      )} rounded-full text-xs`}
                    >
                      Pending
                    </span>
                  </td>
                  <td className="py-2 px-4 border-b">{request.createdAt}</td>
                  <td className="py-2 px-4 border-b">
                    <button
                      className="bg-green-600 hover:bg-green-700 text-white font-medium py-1 px-3 rounded text-sm"
                      disabled={loading}
                      onClick={() =>
                        acceptRequest(
                          request.escrowAccount,
                          request.requestId,
                          request.sender
                        )
                      }
                    >
                      Accept
                    </button>
                  </td>
                  <td className="py-2 px-4 border-b">
                    <button
                      className="bg-green-600 hover:bg-green-700 text-white font-medium py-1 px-3 rounded text-sm"
                      disabled={loading}
                      onClick={() =>
                        rejectRequest(
                          request.escrowAccount,
                          request.requestId,
                          request.sender
                        )
                      }
                    >
                      Reject
                    </button>
                  </td>
                  <td>
                    <button
                      className="bg-green-600 hover:bg-green-700 text-white font-medium py-1 px-3 rounded text-sm"
                      disabled={loading}
                      onClick={() =>
                        markAsSpam(
                          request.sender,
                          request.requestId,
                          request.escrowAccount
                        )
                      }
                    >
                      Mark as Spam
                    </button>
                  </td>
                  <td>
                    <button
                      className="bg-green-600 hover:bg-green-700 text-white font-medium py-1 px-3 rounded text-sm"
                      disabled={loading}
                      onClick={() =>
                        resolveSpam(
                          request.receiver,
                          request.requestId,
                          request.escrowAccount
                        )
                      }
                    >
                      Resolve Spam
                    </button>
                  </td>
                  <td>
                    <button
                      className="bg-yellow-500 text-white px-3 py-2 rounded"
                      onClick={() =>
                        claimBackRequest(
                          request.receiver,
                          request.requestId,
                          request.escrowAccount
                        )
                      }
                    >
                      Claim Back
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div> */}
    </div>
  );
}
