import Link from "next/link";

export default function Footer() {
  return (
    <footer className="py-2">
      <div className="container mx-auto px-4">
        <div className="flex justify-center items-center h-full">
          <div className="flex items-center text-center">
            <p className="text-sm text-gray-600">Powered by</p>
            <span className="ml-2 font-bold text-red-500">Zefe</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
