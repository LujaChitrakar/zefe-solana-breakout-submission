use anchor_lang::prelude::*;

use super::RequestStatus;

#[account]
pub struct EscrowAccount {
    pub sender: Pubkey,            //user who sent the request
    pub receiver: Pubkey,          //user who received the request
    pub request_id: String,        //Unique identifier of request
    pub amount: u64,               //Amount in lamports
    pub created_at: i64,           //Timestamp
    pub marked_as_spam: bool,      //Marked as spam or no
    pub spam_resolution_time: i64, //Time until spam resolved(time finish)
    pub status: RequestStatus,     //Current status of request
    pub bump: u8,                  //pda bump
}
