use crate::EscrowAccount;
use anchor_lang::prelude::*;

#[derive(Accounts)]
#[instruction(receiver: Pubkey, request_id: String)]
pub struct SendConnection<'info> {
    #[account(mut)]
    pub sender: Signer<'info>,

    #[account(
        init,
        payer = sender,
        space =256,
        seeds = [b"escrow", sender.key().as_ref(), receiver.as_ref(), request_id.as_bytes()],
        bump
    )]
    pub escrow_account: Account<'info, EscrowAccount>,

    /// CHECK: This is a system-owned account used only to receive lamports. No data is read or written.
    #[account(
        init,
        payer = sender,
        seeds = [b"vault", sender.key().as_ref(), receiver.as_ref(), request_id.as_bytes()],
        space = 0, // No data needed
        bump,
    )]
    pub vault: AccountInfo<'info>,

    pub system_program: Program<'info, System>,
}
