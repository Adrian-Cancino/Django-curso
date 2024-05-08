from decimal import Decimal
from django.conf import settings
from mitienda.models import Product

class Cart:
    def __init__(self, request):
        #Iniciamos el caro
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        # Añadimos productos o los actualizamos
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)}
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # marcamos la sesión como "modificada" para estar seguros de que se guarda
        self.session.modified = True

    def remove(self, product):
        # removemos un producto del carrito
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        # Iterar sobre los items en el carro y obtener los productos de la base de datos
        product_ids = self.cart.keys()
        # obtener los objetos de productos y añadirlos al carrito
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        # Contar los items del carro
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_total_price(self):
        # Costo total del carrito
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
    
    def clear(self):
        # remover el carro de la sesión
        del self.session[settings.CART_SESSION_ID]
        self.save()
