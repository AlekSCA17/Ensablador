import xml.etree.ElementTree as ET
from graphviz import Digraph

class Nodo:
    def __init__(self, matriz):
        self.matriz = matriz
        self.siguiente = None

class ListaCircular:
    def __init__(self):
        self.primero = None

    def agregar(self, matriz):
        nuevo_nodo = Nodo(matriz)
        if self.primero is None:
            self.primero = nuevo_nodo
            self.primero.siguiente = self.primero
        else:
            temp = self.primero
            while temp.siguiente != self.primero:
                temp = temp.siguiente
            temp.siguiente = nuevo_nodo
            nuevo_nodo.siguiente = self.primero

    def buscar(self, nombre):
        temp = self.primero
        if temp is None:
            return None
        while True:
            if temp.matriz.nombre == nombre:
                return temp.matriz
            temp = temp.siguiente
            if temp == self.primero:
                break
        return None