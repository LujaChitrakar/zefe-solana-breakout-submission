use crate::EscrowAccount;
use anchor_lang::prelude::*;

#[derive(Accounts)]
pub struct RejectRequest<'info> {
    #[account(mut)]
    pub sender: SystemAccount<'info>,

    #[account(
        mut,
        seeds = [b"escrow", escrow_account.sender.as_ref(), escrow_account.receiver.as_ref(), escrow_account.request_id.as_bytes()],
        bump,
    )]
    pub escrow_account: Account<'info, EscrowAccount>,

    /// CHECK: This is a system-owned account used only to receive lamports. No data is read or written.
    #[account(
        mut,
        seeds = [b"vault", escrow_account.sender.as_ref(), escrow_account.receiver.as_ref(), escrow_account.request_id.as_bytes()],
        bump,
    )]
    pub vault: AccountInfo<'info>,

    pub system_program: Program<'info, System>,
}
