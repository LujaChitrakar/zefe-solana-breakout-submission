use anchor_lang::prelude::*;

#[error_code]
pub enum ErrorCode {
    #[msg("Invalid request status")]
    InvalidRequestStatus,
    #[msg("invalid receiver")]
    InvalidReceiver,
    #[msg("Request not marked as spam")]
    NotMarkedAsSpam,
    #[msg("Spam resolution time not reached")]
    ResolutiontTimeNotReached,
    #[msg("Request has not expired yet")]
    RequestNotExpired,
    #[msg("Insufficient funds in escrow account")]
    InsufficientFunds,
    #[msg("The price data in invalid")]
    InvalidPriceData,
}
