import os
import xml.etree.ElementTree as ET
from flask import Flask, request, render_template, redirect, url_for, send_file
import graphviz

class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None

class ListaEnlazada:
    def __init__(self):
        self.cabeza = None

    def insertar(self, dato):
        nuevo_nodo = Nodo(dato)
        nuevo_nodo.siguiente = self.cabeza
        self.cabeza = nuevo_nodo

    def obtener_lista(self):
        lista = []
        actual = self.cabeza
        while actual:
            lista.append(actual.dato)
            actual = actual.siguiente
        return lista

class XMLManager:
    def __init__(self):
        self.archivos = ListaEnlazada()

    def guardar_archivo(self, file):
        carpeta_uploads = 'uploads'
        if not os.path.exists(carpeta_uploads):
            os.makedirs(carpeta_uploads)

        ruta_archivo = os.path.join(carpeta_uploads, file.filename)
        file.save(ruta_archivo)
        self.archivos.insertar(ruta_archivo)
        return ruta_archivo

class Producto:
    def __init__(self, nombre, secuencia):
        self.nombre = nombre
        self.secuencia = secuencia.replace('\n', ' ').replace('\t', ' ').strip().split()

class Maquina:
    def __init__(self, nombre, cantidad_lineas, cantidad_componentes, tiempo_ensamblaje):
        self.nombre = nombre
        self.cantidad_lineas = cantidad_lineas
        self.cantidad_componentes = cantidad_componentes
        self.tiempo_ensamblaje = tiempo_ensamblaje
        self.productos = ListaEnlazada()

    def agregar_producto(self, producto):
        self.productos.insertar(producto)

    def obtener_productos(self):
        return self.productos.obtener_lista()

class MachineManager:
    def __init__(self):
        self.maquinas = ListaEnlazada()

    def cargar_maquinas(self, archivo_xml):
        tree = ET.parse(archivo_xml)
        root = tree.getroot()

        for maquina in root.findall('Maquina'):
            nombre = maquina.find('NombreMaquina').text.strip()
            num_lineas = int(maquina.find('CantidadLineasProduccion').text.strip())
            num_componentes = int(maquina.find('CantidadComponentes').text.strip())
            tiempo_ensamblaje = int(maquina.find('TiempoEnsamblaje').text.strip())

            nueva_maquina = Maquina(nombre, num_lineas, num_componentes, tiempo_ensamblaje)

            for producto in maquina.find('ListadoProductos').findall('Producto'):
                nombre_producto = producto.find('nombre').text.strip()
                secuencia = producto.find('elaboracion').text
                nuevo_producto = Producto(nombre_producto, secuencia)
                nueva_maquina.agregar_producto(nuevo_producto)

            self.maquinas.insertar(nueva_maquina)

    def obtener_maquinas(self):
        return self.maquinas.obtener_lista()

class AssemblySimulator:
    def __init__(self, machine_manager):
        self.machine_manager = machine_manager

    def simular_producto(self, nombre_producto):
        for maquina in self.machine_manager.obtener_maquinas():
            for producto in maquina.obtener_productos():
                if producto.nombre == nombre_producto:
                    return self.simular_maquina_producto(maquina, producto)
        return None

    def simular_maquina_producto(self, maquina, producto):
        tiempo_total = 0
        movimientos = []
        
        for paso in producto.secuencia:
            linea = int(paso[1])
            componente = int(paso[3])
            brazo_movimiento = componente
            tiempo_ensamblaje = maquina.tiempo_ensamblaje

            movimientos.append({
                'linea': linea,
                'componente': componente,
                'tiempo_movimiento': brazo_movimiento,
                'tiempo_ensamblaje': tiempo_ensamblaje
            })

            tiempo_total += brazo_movimiento + tiempo_ensamblaje
        
        return {
            'producto': producto.nombre,
            'maquina': maquina.nombre,
            'movimientos': movimientos,
            'tiempo_total': tiempo_total
        }

class ReportGenerator:
    def __init__(self):
        self.reporte_data = ListaEnlazada()

    def agregar_dato(self, dato):
        self.reporte_data.insertar(dato)

    def generar_reporte(self, simulacion):
        nombre_reporte = f"reporte_{simulacion['producto']}.html"
        ruta_reporte = os.path.join('reports', nombre_reporte)
        
        if not os.path.exists('reports'):
            os.makedirs('reports')

        with open(ruta_reporte, 'w', encoding='utf-8') as f:
            contenido_html = render_template('reporte.html', simulacion=simulacion)
            f.write(contenido_html)
        
        return ruta_reporte

app = Flask(__name__)

machine_manager = MachineManager()
xml_manager = XMLManager()

@app.route('/')
def index():
    maquinas = machine_manager.obtener_maquinas()
    return render_template('index.html', maquinas=maquinas)

@app.route('/cargar_archivo', methods=['POST'])
def cargar_archivo():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    
    ruta_archivo = xml_manager.guardar_archivo(file)
    machine_manager.cargar_maquinas(ruta_archivo)
    return redirect(url_for('index'))

@app.route('/simular/<nombre_producto>')
def simular(nombre_producto):
    simulador = AssemblySimulator(machine_manager)
    resultado_simulacion = simulador.simular_producto(nombre_producto)
    
    if resultado_simulacion is None:
        return "Producto no encontrado", 404

    report_generator = ReportGenerator()
    ruta_reporte = report_generator.generar_reporte(resultado_simulacion)
    
    return redirect(url_for('descargar_reporte', nombre_archivo=os.path.basename(ruta_reporte)))

@app.route('/descargar_reporte/<nombre_archivo>')
def descargar_reporte(nombre_archivo):
    return send_file(os.path.join('reports', nombre_archivo), as_attachment=True)

@app.route('/imprimir_nombre', methods=['POST'])
def imprimir_nombre():
    nombre = "BRAYAN ALEXANDER GUZMAN MARGOS-202105658"
    return render_template('nombre.html', nombre=nombre)

@app.route('/generar_grafico')
def generar_grafico():
    dot = graphviz.Digraph()

    for maquina in machine_manager.obtener_maquinas():
        dot.node(maquina.nombre)
        for producto in maquina.obtener_productos():
            dot.node(producto.nombre)
            dot.edge(maquina.nombre, producto.nombre)

    ruta_grafico = 'static/grafico.png'
    dot.render('static/grafico', format='png', cleanup=True)

    return render_template('grafico.html', ruta_grafico=ruta_grafico)

if __name__ == '__main__':
    app.run(debug=True)


