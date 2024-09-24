import xml.etree.ElementTree as ET
from graphviz import Digraph

class Nodo:
    def __init__(self, matriz):
        self.matriz = matriz
        self.siguiente = None

class ListaCircular:
    def __init__(self):
        self.primero = None

   
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