import sympy as sp
import numpy as np

class MetodoBiseccion:
    def __init__(self):
        # Definimos 'x' como un símbolo matemático para que SymPy lo entienda
        self.x = sp.Symbol('x')

    def calcular(self, funcion_str, a, b, tolerancia):
        """
        Calcula la raíz de una ecuación no lineal usando el Método de Bisección.
        Evalúa el error relativo porcentual.
        """
        # 1. Convertir el texto a una función matemática evaluable
        try:
            f_expr = sp.sympify(funcion_str)
            f = sp.lambdify(self.x, f_expr, 'numpy') 
        except Exception as e:
            return {"error": f"Error al interpretar la función matemática: {e}"}

        # 2. Verificar que la raíz exista en el intervalo dado
        if f(a) * f(b) >= 0:
            return {"error": "El intervalo [a, b] no es válido. Asegúrate de que f(a) * f(b) < 0."}

        # 3. Inicializar variables para el bucle
        iteraciones = []
        error_actual = 100.0  # Empezamos con un error alto
        c_anterior = 0
        i = 1

        # 4. Bucle principal
        while True:
            # Calcular el punto medio
            c = (a + b) / 2
            
            # --- NUEVO: CÁLCULO DEL ERROR RELATIVO PORCENTUAL ---
            if i > 1:
                if c != 0: # Protegemos el código contra división por cero
                    error_actual = abs((c - c_anterior) / c) * 100
                else:
                    error_actual = 100.0 # Si c es 0, mantenemos un error alto para continuar iterando

            # Guardar los datos de esta iteración
            iteraciones.append({
                "Iteración": i,
                "a": a,
                "b": b,
                "c": c,
                "f(c)": f(c),
                "Error (%)": error_actual if i > 1 else None # Cambiamos el nombre a "Error (%)"
            })

            # 5. Condición de parada (Tolerancia vs Error Relativo Porcentual)
            if (i > 1 and error_actual <= tolerancia) or f(c) == 0:
                break

            # 6. Evaluar en qué sub-intervalo está la raíz
            if f(a) * f(c) < 0:
                b = c  
            else:
                a = c  

            c_anterior = c
            i += 1

            if i > 200: # Límite de seguridad
                break

        return {
            "exito": True,
            "raiz_aproximada": c,
            "total_iteraciones": len(iteraciones),
            "tabla_iteraciones": iteraciones
        }