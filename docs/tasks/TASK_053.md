add admin command /refund to refund starts by its transaction id (telegram payment charge id)
/refund <transaction_id> and it will be refunded
no need to change anything in db, like subscriptions, just use telegram payment refund api