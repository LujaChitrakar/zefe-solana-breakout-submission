// components/NoteRequestModal.tsx
import { useSendNetworkingRequest } from "@/hooks/useSendNetworkingRequest";
import { X } from "lucide-react";
import { useState } from "react";
import toast from "react-hot-toast";

type NoteRequestModalProps = {
  onClose: () => void;
  recipientName?: string;
  receiverId: number; // required
};

export default function NoteRequestModal({
  onClose,
  recipientName = "Jon",
  receiverId,
}: NoteRequestModalProps) {
  const [noteContent, setNoteContent] = useState(
    `I saw your profile and would love to connect!`
  );
  const sendRequest = useSendNetworkingRequest();
  const handleSend = () => {
    sendRequest.mutate(
      {
        receiver: receiverId,
        note_content: noteContent,
      },
      {
        onSuccess: () => {
          toast.success("Note sent successfully!");
          onClose();
        },
        onError: () => {
          toast.error("Failed to send the note. Please try again.");
        },
      }
    );
  };
  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl p-6 w-full max-w-md relative shadow-lg text-center space-y-4">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center"
        >
          <X size={14} />
        </button>

        <h2 className="text-lg font-bold">
          NOTE REQUEST TO {recipientName.toUpperCase()}
        </h2>

        <textarea
          rows={7}
          value={noteContent}
          className="w-full rounded-md border px-4 py-3 text-sm resize-none text-gray-800 focus:outline-none focus:ring-1 focus:ring-purple-500"
          onChange={(e) => setNoteContent(e.target.value)}
        />

        <p className="text-xs italic text-gray-500">
          ALERT: You can only send this note request once.
        </p>

        <button
          className="bg-purple-600 text-white font-bold px-6 py-2 rounded-full hover:bg-purple-700 transition"
          onClick={handleSend}
          disabled={sendRequest.isPending}
        >
          {sendRequest.isPending ? "Sending..." : "SEND"}
        </button>
      </div>
    </div>
  );
}
