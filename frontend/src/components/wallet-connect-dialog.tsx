// components/ui/wallet-connect-dialog.tsx
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogTrigger,
  DialogOverlay,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ChevronDown } from "lucide-react";
import Image from "next/image";
import { useState } from "react";

export function WalletConnectDialog({
  trigger,
  onPaymentSuccess,
}: {
  trigger: React.ReactNode;
  onPaymentSuccess: () => void;
}) {
  const [open, setOpen] = useState(false);

  const handleWalletSelect = () => {
    onPaymentSuccess();
    setOpen(false);
  };
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>

      <DialogOverlay className="fixed inset-0 bg-black/50 backdrop-blur-sm" />
      <DialogContent className="bg-[#1a1a1a] text-white p-6 rounded-2xl max-w-sm w-full">
        <DialogTitle className="text-center text-sm font-medium mb-4">
          Log in or Sign up
        </DialogTitle>

        <div className="space-y-3">
          <WalletOption icon="" onClick={handleWalletSelect} label="Metamask" />
          <WalletOption
            icon=""
            onClick={handleWalletSelect}
            label="Rabby Wallet"
          />
          <WalletOption
            icon=""
            onClick={handleWalletSelect}
            label="Coinbase Wallet"
          />
          <WalletOption
            icon=""
            label="Other wallets"
            rightIcon={<ChevronDown size={16} />}
            onClick={handleWalletSelect}
          />
        </div>
      </DialogContent>
    </Dialog>
  );
}

function WalletOption({
  icon,
  label,
  rightIcon,
  onClick,
}: {
  icon: string;
  label: string;
  rightIcon?: React.ReactNode;
  onClick?: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="flex items-center justify-between w-full px-4 py-2 bg-[#2b2b2b] rounded-lg hover:bg-[#333] transition"
    >
      <div className="flex items-center gap-3">
        {icon ? (
          <Image src={icon} alt={label} width={24} height={24} />
        ) : (
          <div className="w-6 h-6 rounded border border-white opacity-60" />
        )}
        <span className="text-sm font-medium">{label}</span>
      </div>
      {rightIcon}
    </button>
  );
}
