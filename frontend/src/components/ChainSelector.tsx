"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog";
import { ChevronDown } from "lucide-react";
import toast from "react-hot-toast";
import * as DialogPrimitive from "@radix-ui/react-dialog";

export function ChainSelector({
  selected,
  onChange,
  options,
}: {
  selected: string[];
  onChange: (chains: string[]) => void;
  options: { value: string; label: string }[];
}) {
  const [open, setOpen] = useState(false);

  const toggleChain = (chain: string) => {
    let updated: string[];

    if (selected.includes(chain)) {
      updated = selected.filter((c) => c !== chain);
    } else {
      if (selected.length >= 3) {
        toast.error("You can select up to 3 chains only.");
        return;
      }
      updated = [...selected, chain];
    }

    onChange(updated);
  };

  return (
    <div className="flex flex-wrap items-center gap-2">
      {selected.slice(0, 3).map((chain) => {
        const label =
          options.find((opt) => opt.value === chain)?.label || chain;
        return (
          <span
            key={chain}
            className="bg-gray-200 text-sm px-3 py-1 rounded-full"
          >
            {label}
          </span>
        );
      })}

      {selected.length > 3 && (
        <span className="text-xs text-gray-500">
          +{selected.length - 3} more
        </span>
      )}

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild>
          <button
            type="button"
            className="rounded-full px-2 py-1 text-sm border text-gray-600 hover:bg-gray-100"
          >
            <ChevronDown size={16} />
          </button>
        </DialogTrigger>

        <DialogContent className="max-w-xl rounded-2xl">
          <DialogPrimitive.Title className="sr-only">
            Select Chains
          </DialogPrimitive.Title>
          <div className="mb-4">
            <h2 className="text-lg font-semibold">Select Chains</h2>
            <p className="text-sm text-gray-500">
              You can select up to 3 chains
            </p>
          </div>

          <div className="grid grid-cols-3 gap-3 max-h-[70vh] overflow-y-auto">
            {options.map((chain) => (
              <button
                key={chain.value}
                onClick={() => toggleChain(chain.value)}
                title={chain.label}
                className={`rounded-full px-4 py-2 text-sm text-center border w-full
      ${
        selected.includes(chain.value)
          ? "bg-blue-600 text-white"
          : "bg-gray-100 text-gray-800"
      }
    `}
                style={{
                  whiteSpace: "normal",
                  wordBreak: "break-word",
                }}
              >
                {chain.label}
              </button>
            ))}
          </div>

          <div className="mt-6 text-right">
            <Button onClick={() => setOpen(false)}>Done</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
