import sympy as sp
import numpy as np
import cmath

class MetodoBairstow:
    def __init__(self):
        self.x = sp.Symbol('x')

    def calcular(self, funcion_str, r0, s0, tolerancia):
        """
        Calcula dos raíces de un polinomio usando el Método de Bairstow.
        """
        try:
            # 1. Extraer los coeficientes del polinomio automáticamente
            f_expr = sp.sympify(funcion_str)
            poly = sp.Poly(f_expr, self.x)
            a = poly.all_coeffs()  # Esto devuelve [a_n, a_{n-1}, ..., a_0]
            a = [float(c) for c in a]
        except Exception as e:
            return {"error": f"Error al interpretar el polinomio: {e}"}

        n = len(a) - 1
        if n < 3:
            return {"error": "El método de Bairstow requiere un polinomio de grado 3 o mayor."}

        # Valores iniciales
        r = float(r0)
        s = float(s0)
        
        iteraciones = []
        i = 1
        
        # 2. Bucle Principal
        while True:
            # Inicializamos los arreglos b y c con ceros
            b = [0.0] * (n + 1)
            c = [0.0] * (n + 1)
            
            # Calcular el arreglo b (Primera división sintética)
            b[0] = a[0]
            b[1] = a[1] + r * b[0]
            for j in range(2, n + 1):
                b[j] = a[j] + r * b[j-1] + s * b[j-2]
                
            # Calcular el arreglo c (Segunda división sintética - derivadas parciales)
            c[0] = b[0]
            c[1] = b[1] + r * c[0]
            for j in range(2, n): 
                c[j] = b[j] + r * c[j-1] + s * c[j-2]
                
            # Extraer las variables para el sistema de ecuaciones 2x2
            c1 = c[n-1]
            c2 = c[n-2]
            c3 = c[n-3]
            
            b0 = b[n]
            b1 = b[n-1]
            
            # Regla de Cramer para resolver el sistema de ecuaciones
            det = c2 * c2 - c1 * c3
            if det == 0:
                return {"error": "El determinante se hizo cero. Cambia los valores iniciales."}
                
            dr = (-b1 * c2 + b0 * c3) / det  # Equivale a tu 'Vr' en Excel
            ds = (-b0 * c2 + b1 * c1) / det  # Equivale a tu 'vs' en Excel
            
            # Nuevas aproximaciones
            r_nuevo = r + dr
            s_nuevo = s + ds
            
            # 3. Cálculo de Error Máximo Relativo Porcentual
            error_r = abs(dr / r_nuevo) * 100 if r_nuevo != 0 else 100.0
            error_s = abs(ds / s_nuevo) * 100 if s_nuevo != 0 else 100.0
            error_max = max(error_r, error_s)
            
            iteraciones.append({
                "Iteración": i,
                "r": r_nuevo,
                "s": s_nuevo,
                "Δr": dr,
                "Δs": ds,
                "Error Máx (%)": error_max
            })
            
            # Condición de parada
            if error_max <= tolerancia:
                break
                
            r = r_nuevo
            s = s_nuevo
            i += 1
            
            if i > 100:
                return {"error": "El método diverge o es muy lento. Se detuvo en la iteración 100."}

        # 4. Calcular las dos raíces con la fórmula cuadrática usando los valores finales
        discriminante = cmath.sqrt(r_nuevo**2 + 4*s_nuevo)
        raiz1 = (r_nuevo + discriminante) / 2
        raiz2 = (r_nuevo - discriminante) / 2
        
        # Limpiar números complejos si en realidad son reales (ej. 1.0 + 0j -> 1.0)
        def limpiar_raiz(num):
            if abs(num.imag) < 1e-10:
                return round(num.real, 6)
            return complex(round(num.real, 6), round(num.imag, 6))

        return {
            "exito": True,
            "raiz1": limpiar_raiz(raiz1),
            "raiz2": limpiar_raiz(raiz2),
            "total_iteraciones": i,
            "tabla_iteraciones": iteraciones
        }