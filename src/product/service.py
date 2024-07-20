class PaymentService:
    @staticmethod
    def confirm_payment(payment_key: str, amount: int) -> bool:
        if payment_key and amount:
            return True
        return False


payment_service = PaymentService()
