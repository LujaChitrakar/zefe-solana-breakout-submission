import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogTrigger,
  DialogTitle,
} from "@/components/ui/dialog";
import { ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";

type VerticalSelectorProps = {
  selected: string[];
  onChange: (next: string[]) => void;
};

const VERTICALS = [
  "DEFI",
  "DePIN",
  "RWA",
  "GAMEFI",
  "TOKEN",
  "NFT",
  "AI",
  "EVENT",
  "DAO",
  "COMMUNITY",
  "TOKENIZATION",
  "BLOCKCHAIN",
  "VENTURE CAPITAL",
  "INVESTEMENT",
];

export function VerticalSelector({
  selected,
  onChange,
}: VerticalSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);

  const toggleVertical = (item: string) => {
    if (selected.includes(item)) {
      onChange(selected.filter((v) => v !== item));
    } else if (selected.length < 3) {
      onChange([...selected, item]);
    }
  };

  return (
    <div>
      <p className="text-xs text-gray-500 mb-1">
        Select relevant verticals (only three)
      </p>

      <div className="flex flex-wrap items-center gap-2">
        {selected.slice(0, 5).map((v) => (
          <button
            key={v}
            type="button"
            onClick={() => toggleVertical(v)}
            className="px-3 py-1 bg-red-500 text-white text-xs rounded-full hover:brightness-110 transition cursor-pointer"
            title="Click to remove"
          >
            {v}
          </button>
        ))}

        {selected.length > 5 && (
          <span className="text-xs text-gray-500 italic">
            +{selected.length - 5} more
          </span>
        )}

        <Dialog open={isOpen} onOpenChange={setIsOpen}>
          <DialogTrigger asChild>
            <button
              type="button"
              className="w-6 h-6 flex items-center justify-center bg-gray-200 rounded-full hover:bg-gray-300 transition"
              title="Edit verticals"
            >
              <ChevronDown size={16} />
            </button>
          </DialogTrigger>

          <DialogContent className="max-w-md rounded-xl p-6">
            <DialogTitle className="text-lg font-semibold mb-4">
              Select Verticals
            </DialogTitle>

            <div className="grid grid-cols-2 gap-3">
              {VERTICALS.map((item) => {
                const isSelected = selected.includes(item);
                const disabled = !isSelected && selected.length >= 3;

                return (
                  <button
                    key={item}
                    type="button"
                    onClick={() => toggleVertical(item)}
                    disabled={disabled}
                    className={`border px-3 py-1 text-sm rounded-full transition ${
                      isSelected
                        ? "bg-blue-600 text-white"
                        : "bg-gray-100 text-gray-800 hover:bg-gray-200"
                    } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
                  >
                    {item}
                  </button>
                );
              })}
            </div>

            <div className="mt-6 text-right">
              <Button variant="outline" onClick={() => setIsOpen(false)}>
                Done
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
