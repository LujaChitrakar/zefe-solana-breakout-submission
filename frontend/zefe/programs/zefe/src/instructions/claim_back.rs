use anchor_lang::prelude::*;

use crate::EscrowAccount;

#[derive(Accounts)]
pub struct ClaimBack<'info> {
    #[account(mut, has_one = sender)]
    pub escrow_account: Account<'info, EscrowAccount>,

    /// CHECK: This is a PDA vault owned by the program. Checked via seeds in CPI.
    #[account(mut, seeds = [b"vault", escrow_account.sender.as_ref(), escrow_account.receiver.as_ref(), escrow_account.request_id.as_bytes()], bump)]
    pub vault: AccountInfo<'info>,

    #[account(mut)]
    pub sender: Signer<'info>,

    pub system_program: Program<'info, System>,
}
