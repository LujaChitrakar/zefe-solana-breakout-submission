use anchor_lang::prelude::*;

use crate::EscrowAccount;

#[derive(Accounts)]
pub struct MarkAsSpam<'info> {
    #[account(mut)]
    pub receiver: Signer<'info>,

    #[account(mut, has_one = receiver)]
    pub escrow_account: Account<'info, EscrowAccount>,
}
