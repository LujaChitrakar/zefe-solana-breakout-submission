use anchor_lang::prelude::*;

use crate::EscrowAccount;

#[derive(Accounts)]
pub struct ResolveSpam<'info> {
    /// CHECK: vault is validated by PDA and signer
    #[account(mut, seeds = [b"vault", escrow_account.sender.as_ref(), escrow_account.receiver.as_ref(), escrow_account.request_id.as_bytes()], bump)]
    pub vault: AccountInfo<'info>,

    #[account(mut)]
    pub sender: SystemAccount<'info>,

    #[account(mut, has_one = sender)]
    pub escrow_account: Account<'info, EscrowAccount>,

    pub system_program: Program<'info, System>,
}
