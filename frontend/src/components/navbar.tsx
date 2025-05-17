"use client";

import Link from "next/link";
import { Bell, User, Users } from "lucide-react";
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogTitle,
} from "@/components/ui/dialog";
import ProfileDialogContent from "@/components/profile-dailog";
import { useEffect, useState } from "react";
import { useNotificationCount } from "@/hooks/useNotificationCount";
import { useAuth } from "@/hooks/useAuth";
import TelegramLogin from "@/components/telegramLogin";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { WalletMultiButton } from "@solana/wallet-adapter-react-ui";
import dynamic from "next/dynamic";

export default function Navbar() {
  const [isProfileDialogOpen, setIsProfileDialogOpen] = useState(false);

  const router = useRouter();
  const { isAuthenticated } = useAuth();

  const WalletButtonClientOnly = dynamic(
    () => import("./WalletButtonClientOnly"),
    { ssr: false }
  );

  const handlenotificationpage = () => {
    window.location.href = "/notifications";
  };

  const handleconnectionspage = () => {
    window.location.href = "/connections";
  };

  const { data: notificationData } = useNotificationCount();
  const [pendingNotifications, setPendingNotifications] = useState(0);

  useEffect(() => {
    if (
      notificationData &&
      notificationData.data?.data?.unread_count !== undefined
    ) {
      setPendingNotifications(notificationData.data.data.unread_count);
    }
  }, [notificationData]);

  const handleLoginSuccess = (userData: any) => {
    if (userData.is_new_user !== undefined) {
      // router.push(userData.is_new_user ? "/onboarding" : "/dashboard");
    } else {
      // router.push("/dashboard");
    }
  };

  return (
    <header className="border-b py-4 bg-[#FCF3DC]">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between">
          {/* Left: Logo */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-2">
              <Image
                src="/logo.png"
                alt="zefe Logo"
                width={68}
                height={48}
                priority
              />
              {/* <span className="font-bold text-lg text-blue-600">Zefe</span> */}
            </Link>
          </div>

          {/* Right: Icons & Actions */}
          <div className="flex items-center space-x-2">
            {isAuthenticated && (
              <>
                <button
                  onClick={handleconnectionspage}
                  className="w-8 h-8 rounded-full bg-red-500 text-white flex items-center justify-center"
                >
                  <Users size={16} />
                </button>
                <button
                  onClick={handlenotificationpage}
                  className="w-8 h-8 rounded-full bg-red-500 text-white flex items-center justify-center relative"
                >
                  <Bell size={16} />
                  {pendingNotifications > 0 && (
                    <span className="absolute -top-2 -right-2 bg-gradient-to-r from-green-500 to-green-800 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center shadow-md animate-pulse">
                      {pendingNotifications > 9 ? "9+" : pendingNotifications}
                    </span>
                  )}
                </button>
              </>
            )}

            {/* Profile or Telegram login */}
            {isAuthenticated ? (
              <Dialog
                open={isProfileDialogOpen}
                onOpenChange={setIsProfileDialogOpen}
              >
                <DialogTrigger asChild>
                  <button className="w-8 h-8 rounded-full bg-red-500 text-white flex items-center justify-center">
                    <User size={16} />
                  </button>
                </DialogTrigger>
                <DialogContent className="max-w-7xl p-6 rounded-2xl bg-white shadow-xl">
                  <DialogTitle className="sr-only">Profile</DialogTitle>
                  <ProfileDialogContent
                    onClose={() => setIsProfileDialogOpen(false)}
                  />
                </DialogContent>
              </Dialog>
            ) : (
              <TelegramLogin
                buttonText=""
                onLoginSuccess={handleLoginSuccess}
                buttonClassName="w-8 h-8 rounded-full bg-red-500 text-white flex items-center justify-center"
                icon={<User size={16} />}
              />
            )}
            <WalletButtonClientOnly />
          </div>
        </div>
      </div>
    </header>
  );
}
