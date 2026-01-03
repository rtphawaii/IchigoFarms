class Cart:
    SESSION_KEY = "cart"

    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.get(self.SESSION_KEY, {"items": {}})

    def add(self, product_id, qty=1):
        pid = str(product_id)
        items = self.cart["items"]
        items[pid] = {"qty": items.get(pid, {"qty": 0})["qty"] + qty}
        self.save()

    def set(self, product_id, qty):
        pid = str(product_id)
        if qty <= 0:
            self.cart["items"].pop(pid, None)
        else:
            self.cart["items"][pid] = {"qty": qty}
        self.save()

    def clear(self):
        self.cart = {"items": {}}
        self.save()

    def save(self):
        self.session[self.SESSION_KEY] = self.cart
        self.session.modified = True
