#  Zefe – Telegram Mini App for Pre-Event Networking for Solana Breakout Hackathon

PreConnect is a **Telegram Mini App** designed to help event attendees **connect and engage with each other before the actual event** starts. It combines the power of **Web2 (Next.js & Django)** and **Web3 (Solana blockchain via Anchor)** to provide a decentralized, trust-minimized experience for sending connection requests using SOL escrow.

##  Key Features

- 💬 **Connection Request with Personal Note**  
  Users can send a brief note about themselves along with a 0.003 SOL connection request.

-  **Decentralized Escrow System**  
  The SOL is securely held in an **Anchor-powered escrow vault** on the Solana blockchain.

-  **3 Request Actions for Receiver**  
  The receiver of a request has three options:
  - ✅ Accept: Connection is made, and SOL is returned to the sender.
  - ❌ Reject: Request is declined, and SOL is returned to the sender.
  - 🚩 Spam: SOL is held in escrow for 3 days. After the period, the sender can reclaim it.

- ⏱️ **Auto Recovery**  
  If the receiver ignores the request or marks it as spam, the sender can **claim back their SOL after 3 days**.

##  Tech Stack

- **Frontend**: [Next.js](https://nextjs.org/) with Tailwind CSS for sleek UI and seamless Telegram integration.
- **Backend API**: [Django](https://www.djangoproject.com/) handles Telegram authentication and user metadata.
- **Blockchain Layer**: [Solana](https://solana.com/) with [Anchor](https://www.anchor-lang.com/) for escrow logic and programmatic SOL flow.

## 🛠️ How It Works

1. **User connects Telegram account** inside the mini app.
2. **User sends a connection request** with a message and 0.003 SOL.
3. **Escrow program locks the SOL** until the receiver interacts.
4. **Receiver decides**:
   - Accept/Reject: SOL is instantly returned to sender.
   - Spam/Ignore: SOL is locked for 3 days, then claimable by sender.
5. **Sender claims funds** back if no action is taken after timeout.



