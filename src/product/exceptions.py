class OrderInvalidProductException(Exception):
    message = "Invalid product ID"


class OrderNotFoundException(Exception):
    message = "Order not found"


class OrderPaymentConfirmFailedException(Exception):
    message = "Payment confirmation failed"
