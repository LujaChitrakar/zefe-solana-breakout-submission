use anchor_lang::prelude::*;
pub mod error;
pub mod instructions;
pub mod states;
pub use error::ErrorCode;
pub use instructions::*;
pub use states::*;

declare_id!("4Ng72C6t9m8RXCBbGMz8ifuQh9S64sDw8h6jaVUSYHit");

#[program]
pub mod zefe {
    use super::*;
    use anchor_lang::system_program::{transfer, Transfer};

    pub fn send_connection_request(
        ctx: Context<SendConnection>,
        receiver: Pubkey,
        request_id: String,
    ) -> Result<()> {
        msg!("Processing connection request.");

        let escrow_account = &mut ctx.accounts.escrow_account;
        let amount = 3_000_000;

        escrow_account.sender = ctx.accounts.sender.key();
        escrow_account.receiver = receiver;
        escrow_account.request_id = request_id;
        escrow_account.amount = amount;
        escrow_account.created_at = Clock::get()?.unix_timestamp;
        escrow_account.marked_as_spam = false;
        escrow_account.spam_resolution_time = 0;
        escrow_account.status = RequestStatus::Pending;
        escrow_account.bump = ctx.bumps.escrow_account;

        let cpi_ctx = CpiContext::new(
            ctx.accounts.system_program.to_account_info(),
            Transfer {
                from: ctx.accounts.sender.to_account_info(),
                to: ctx.accounts.vault.to_account_info(),
            },
        );
        transfer(cpi_ctx, amount)?;

        msg!("Transferred {} lamports to vault", amount);
        Ok(())
    }

    pub fn accept_request(ctx: Context<AcceptRequest>) -> Result<()> {
        msg!(
            "Processing accept request for escrow: {}",
            ctx.accounts.escrow_account.key()
        );

        let escrow_account = &mut ctx.accounts.escrow_account;
        let sender = &ctx.accounts.sender;

        // Ensure request is still pending
        require!(
            escrow_account.status == RequestStatus::Pending,
            ErrorCode::InvalidRequestStatus
        );

        escrow_account.status = RequestStatus::Accepted;

        let amount = escrow_account.amount;

        // Return SOL from vault to sender
        if amount > 0 {
            // let seeds: &[&[u8]] = &[
            //     b"vault",
            //     escrow_account.sender.as_ref(),
            //     escrow_account.receiver.as_ref(),
            //     escrow_account.request_id.as_bytes(),
            //     &[ctx.bumps.vault],
            // ];

            // let signer: &[&[&[u8]]] = &[seeds];

            // let cpi_ctx = CpiContext::new_with_signer(
            //     ctx.accounts.system_program.to_account_info(),
            //     Transfer {
            //         from: ctx.accounts.vault.to_account_info(),
            //         to: sender.to_account_info(),
            //     },
            //     signer,
            // );

            // transfer(cpi_ctx, amount)?;
            **ctx.accounts.vault.try_borrow_mut_lamports()? -= amount;
            **ctx.accounts.sender.try_borrow_mut_lamports()? += amount;

            escrow_account.amount = 0;

            msg!("Successfully returned {} lamports to sender", amount);
        } else {
            msg!("No funds to return (amount is 0)");
        }

        msg!("Connection request accepted and funds returned");
        Ok(())
    }

    pub fn reject_request(ctx: Context<RejectRequest>) -> Result<()> {
        msg!(
            "Processing reject request for escrow: {}",
            ctx.accounts.escrow_account.key()
        );

        let escrow_account = &mut ctx.accounts.escrow_account;
        let sender = &ctx.accounts.sender;

        // Ensure request is still pending
        require!(
            escrow_account.status == RequestStatus::Pending,
            ErrorCode::InvalidRequestStatus
        );

        escrow_account.status = RequestStatus::Rejected;

        let amount = escrow_account.amount;

        // Return SOL from vault to sender
        if amount > 0 {
            // let seeds: &[&[u8]] = &[
            //     b"vault",
            //     escrow_account.sender.as_ref(),
            //     escrow_account.receiver.as_ref(),
            //     escrow_account.request_id.as_bytes(),
            //     &[ctx.bumps.vault],
            // ];

            // let signer: &[&[&[u8]]] = &[seeds];

            // let cpi_ctx = CpiContext::new_with_signer(
            //     ctx.accounts.system_program.to_account_info(),
            //     Transfer {
            //         from: ctx.accounts.vault.to_account_info(),
            //         to: sender.to_account_info(),
            //     },
            //     signer,
            // );

            // transfer(cpi_ctx, amount)?;
            **ctx.accounts.vault.try_borrow_mut_lamports()? -= amount;
            **ctx.accounts.sender.try_borrow_mut_lamports()? += amount;

            escrow_account.amount = 0;

            msg!("Successfully returned {} lamports to sender", amount);
        } else {
            msg!("No funds to return (amount is 0)");
        }

        msg!("Connection request accepted and funds returned");
        Ok(())
    }

    pub fn mark_as_spam(ctx: Context<MarkAsSpam>) -> Result<()> {
        let escrow_account = &mut ctx.accounts.escrow_account;
        let clock = Clock::get()?;

        // Only the receiver can mark as spam
        require_keys_eq!(ctx.accounts.receiver.key(), escrow_account.receiver);

        // Only mark if still pending
        require!(
            escrow_account.status == RequestStatus::Pending,
            ErrorCode::InvalidRequestStatus
        );
        escrow_account.status = RequestStatus::SpamConfirmed;

        escrow_account.marked_as_spam = true;
        escrow_account.spam_resolution_time = clock.unix_timestamp + 3 * 24 * 60 * 60; // 3 days (in seconds)

        msg!(
            "Request marked as spam. Funds will be returnable after {}",
            escrow_account.spam_resolution_time
        );
        Ok(())
    }

    pub fn resolve_spam(ctx: Context<ResolveSpam>) -> Result<()> {
        let escrow_account = &mut ctx.accounts.escrow_account;
        let clock = Clock::get()?;
        let current_time = clock.unix_timestamp;

        require!(escrow_account.marked_as_spam, ErrorCode::NotMarkedAsSpam);
        require!(
            current_time >= escrow_account.spam_resolution_time,
            ErrorCode::ResolutiontTimeNotReached
        );

        let amount = escrow_account.amount;

        // Transfer funds from vault to sender
        let seeds: &[&[u8]] = &[
            b"vault",
            escrow_account.sender.as_ref(),
            escrow_account.receiver.as_ref(),
            escrow_account.request_id.as_bytes(),
            &[ctx.bumps.vault],
        ];
        let signer: &[&[&[u8]]] = &[seeds];
        let cpi_ctx = CpiContext::new_with_signer(
            ctx.accounts.system_program.to_account_info(),
            Transfer {
                from: ctx.accounts.vault.to_account_info(),
                to: ctx.accounts.sender.to_account_info(),
            },
            signer,
        );

        transfer(cpi_ctx, amount)?;

        escrow_account.amount = 0;
        escrow_account.status = RequestStatus::SpamResolved;

        msg!("Spam request resolved and funds returned to sender.");
        Ok(())
    }

    pub fn claim_back(ctx: Context<ClaimBack>) -> Result<()> {
        let escrow_account = &mut ctx.accounts.escrow_account;
        let clock = Clock::get()?;

        // 3 days in seconds
        let three_days = 3 * 24 * 60 * 60;

        require!(
            escrow_account.status == RequestStatus::Pending,
            ErrorCode::InvalidRequestStatus
        );
        require!(
            clock.unix_timestamp > escrow_account.created_at + three_days,
            ErrorCode::RequestNotExpired
        );

        let seeds: &[&[u8]] = &[
            b"vault",
            escrow_account.sender.as_ref(),
            escrow_account.receiver.as_ref(),
            escrow_account.request_id.as_bytes(),
            &[ctx.bumps.vault],
        ];
        let signer: &[&[&[u8]]] = &[seeds];

        // Transfer lamports from vault to sender
        let amount = escrow_account.amount;

        let cpi_ctx = CpiContext::new_with_signer(
            ctx.accounts.system_program.to_account_info(),
            Transfer {
                from: ctx.accounts.vault.to_account_info(),
                to: ctx.accounts.sender.to_account_info(),
            },
            signer,
        );

        transfer(cpi_ctx, amount)?;

        // Mark as expired
        escrow_account.status = RequestStatus::Expired;

        Ok(())
    }
}
