use anchor_lang::prelude::*;

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq, Eq, InitSpace)]
pub enum RequestStatus {
    Pending,
    Accepted,
    Rejected,
    SpamConfirmed,
    SpamResolved,
    NotSpam,
    Expired,
}
