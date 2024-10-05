class Nodo:
    def __init__(self, dato=None):
        self.dato = dato
        self.siguiente = None

class ListaEnlazada:
    def __init__(self):
        self.cabeza = None

    def insertar(self, dato):
        nuevo_nodo = Nodo(dato)
        if self.cabeza is None:
            self.cabeza = nuevo_nodo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo

    # Hacer la lista iterable
    def __iter__(self):
        self.actual = self.cabeza
        return self

    def __next__(self):
        if self.actual is None:
            raise StopIteration
        else:
            dato = self.actual.dato
            self.actual = self.actual.siguiente
            return dato 

class Pila:
    def __init__(self):
        self.items = []

    def es_vacia(self):
        return len(self.items) == 0

    def apilar(self, item):
        self.items.append(item)

    def desapilar(self):
        if not self.es_vacia():
            return self.items.pop()

    def peek(self):
        if not self.es_vacia():
            return self.items[-1]

    def size(self):
        return len(self.items)

