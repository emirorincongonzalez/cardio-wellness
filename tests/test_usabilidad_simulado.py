#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SIMULADOR DE TESTS DE USABILIDAD - CARDIO-WELLNESS
Simula 5 usuarios con diferentes perfiles probando la app
"""

import random
from datetime import datetime
from typing import Dict, List


class UsuarioSimulado:
    """Representa un usuario simulado con perfil específico"""
    
    def __init__(self, id: int, perfil: str):
        self.id = id
        self.perfil = perfil
        self.edad = self._generar_edad(perfil)
        self.experiencia = self._generar_experiencia(perfil)
        self.tareas = {}
        self.satisfaccion = 0
        self.nps = 0
        self.comentarios = []
    
    def _generar_edad(self, perfil: str) -> int:
        edades = {
            'joven_tech': random.randint(18, 25),
            'adulto_promedio': random.randint(30, 45),
            'senior_basico': random.randint(55, 65),
            'millennial_activo': random.randint(28, 38),
            'principiante_total': random.randint(40, 60),
        }
        return edades.get(perfil, 30)
    
    def _generar_experiencia(self, perfil: str) -> str:
        experiencias = {
            'joven_tech': 'Alta',
            'adulto_promedio': 'Media',
            'senior_basico': 'Baja',
            'millennial_activo': 'Media-Alta',
            'principiante_total': 'Baja',
        }
        return experiencias.get(perfil, 'Media')
    
    def simular_tarea(self, tarea: str, dificultad: float) -> Dict:
        """
        Simula la ejecución de una tarea
        
        Args:
            tarea: Nombre de la tarea
            dificultad: 0-1 (0=fácil, 1=difícil)
        
        Returns:
            Dict con resultado de la tarea
        """
        # Probabilidad de éxito basada en experiencia y dificultad
        factor_experiencia = {
            'Alta': 0.95,
            'Media-Alta': 0.90,
            'Media': 0.85,
            'Baja': 0.75,
        }.get(self.experiencia, 0.85)
        
        probabilidad_exito = factor_experiencia * (1 - dificultad * 0.5)
        exito = random.random() < probabilidad_exito
        
        # Tiempo basado en dificultad y experiencia
        tiempo_base = {
            'Alta': 30,
            'Media-Alta': 45,
            'Media': 60,
            'Baja': 90,
        }.get(self.experiencia, 60)
        
        tiempo = tiempo_base * (1 + dificultad)
        if not exito:
            tiempo *= 2  # Tarda más si falla
        
        # Errores basados en dificultad
        errores = int(dificultad * random.randint(0, 3)) if not exito else random.randint(0, 1)
        
        resultado = {
            'exitoso': exito,
            'tiempo_segundos': round(tiempo, 1),
            'errores': errores,
        }
        
        self.tareas[tarea] = resultado
        return resultado
    
    def simular_satisfaccion(self) -> int:
        """Genera satisfacción basada en el éxito de las tareas"""
        if not self.tareas:
            return 0
        
        exitosas = sum(1 for t in self.tareas.values() if t['exitoso'])
        total = len(self.tareas)
        tasa_exito = exitosas / total if total > 0 else 0
        
        # Satisfacción basada en tasa de éxito
        satisfaccion = int(tasa_exito * 5)
        if satisfaccion == 0 and tasa_exito > 0:
            satisfaccion = 1
        
        self.satisfaccion = satisfaccion
        return satisfaccion
    
    def simular_nps(self) -> int:
        """Genera NPS (0-10) basado en satisfacción"""
        if self.satisfaccion == 0:
            self.simular_satisfaccion()
        
        # NPS correlacionado con satisfacción
        nps_base = {
            5: random.randint(9, 10),
            4: random.randint(7, 9),
            3: random.randint(5, 7),
            2: random.randint(3, 5),
            1: random.randint(0, 3),
        }.get(self.satisfaccion, 5)
        
        self.nps = nps_base
        return nps_base
    
    def generar_comentarios(self) -> List[str]:
        """Genera comentarios basados en los resultados"""
        comentarios = []
        
        if not self.tareas:
            return comentarios
        
        # Comentario general
        if self.satisfaccion >= 4:
            comentarios.append("La app es intuitiva y fácil de usar")
        elif self.satisfaccion == 3:
            comentarios.append("La app funciona pero podría mejorar")
        else:
            comentarios.append("Tuve dificultades con varias funciones")
        
        # Comentario específico por tarea fallida
        for tarea, resultado in self.tareas.items():
            if not resultado['exitoso']:
                if tarea == 'Registro':
                    comentarios.append("El registro fue confuso, no entendí los campos")
                elif tarea == 'Login':
                    comentarios.append("No encontraba dónde poner mi contraseña")
                elif tarea == 'Ver Rutina':
                    comentarios.append("Los ejercicios no se veían claramente")
                elif tarea == 'Registrar Sesión':
                    comentarios.append("Registrar mi entrenamiento fue complicado")
                elif tarea == 'Ver Progreso':
                    comentarios.append("Las gráficas de progreso no son claras")
        
        self.comentarios = comentarios
        return comentarios
    
    def to_dict(self) -> Dict:
        """Convierte a diccionario"""
        return {
            'id': self.id,
            'perfil': self.perfil,
            'edad': self.edad,
            'experiencia_tecnologica': self.experiencia,
            'tareas': self.tareas,
            'satisfaccion': self.satisfaccion,
            'nps': self.nps,
            'comentarios': self.comentarios,
        }


class SimuladorUsabilidad:
    """Simula tests de usabilidad con múltiples usuarios"""
    
    def __init__(self):
        self.usuarios = []
        self.tareas = {
            'Registro': 0.3,  # Dificultad 0-1
            'Login': 0.2,
            'Ver Rutina': 0.4,
            'Registrar Sesión': 0.6,
            'Ver Progreso': 0.5,
        }
    
    def crear_usuarios(self):
        """Crea 5 usuarios con perfiles diversos"""
        perfiles = [
            'joven_tech',
            'adulto_promedio',
            'senior_basico',
            'millennial_activo',
            'principiante_total',
        ]
        
        for i, perfil in enumerate(perfiles, 1):
            usuario = UsuarioSimulado(i, perfil)
            self.usuarios.append(usuario)
            print(f"✅ Usuario {i} creado: {perfil} ({usuario.edad} años, exp: {usuario.experiencia})")
    
    def ejecutar_tests(self):
        """Ejecuta todas las tareas para todos los usuarios"""
        print("\n" + "=" * 80)
        print("EJECUTANDO TESTS DE USABILIDAD")
        print("=" * 80 + "\n")
        
        for usuario in self.usuarios:
            print(f"Usuario {usuario.id} ({usuario.perfil}):")
            print("-" * 60)
            
            for tarea, dificultad in self.tareas.items():
                resultado = usuario.simular_tarea(tarea, dificultad)
                estado = "✅" if resultado['exitoso'] else "❌"
                print(f"  {estado} {tarea}: {resultado['tiempo_segundos']}s, {resultado['errores']} errores")
            
            usuario.simular_satisfaccion()
            usuario.simular_nps()
            usuario.generar_comentarios()
            
            print(f"  ⭐ Satisfacción: {usuario.satisfaccion}/5")
            print(f"  📊 NPS: {usuario.nps}/10")
            print()
    
    def generar_reporte(self, archivo: str = 'reporte_usabilidad_simulado.txt'):
        """Genera reporte completo"""
        if not self.usuarios:
            print("❌ No hay usuarios para generar reporte")
            return
        
        total_usuarios = len(self.usuarios)
        
        # Calcular métricas
        exito_por_tarea = {}
        tiempo_por_tarea = {}
        
        for tarea in self.tareas.keys():
            exitosos = sum(1 for u in self.usuarios if u.tareas.get(tarea, {}).get('exitoso', False))
            tiempos = [u.tareas[tarea]['tiempo_segundos'] for u in self.usuarios if tarea in u.tareas]
            
            exito_por_tarea[tarea] = {
                'exitosos': exitosos,
                'total': total_usuarios,
                'porcentaje': (exitosos / total_usuarios * 100),
            }
            
            tiempo_por_tarea[tarea] = {
                'promedio': sum(tiempos) / len(tiempos) if tiempos else 0,
                'min': min(tiempos) if tiempos else 0,
                'max': max(tiempos) if tiempos else 0,
            }
        
        satisfacciones = [u.satisfaccion for u in self.usuarios if u.satisfaccion > 0]
        nps_scores = [u.nps for u in self.usuarios if u.nps > 0]
        
        satisfaccion_promedio = sum(satisfacciones) / len(satisfacciones) if satisfacciones else 0
        nps_promedio = sum(nps_scores) / len(nps_scores) if nps_scores else 0
        
        # Generar reporte
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("REPORTE DE USABILIDAD - CARDIO-WELLNESS (SIMULADO)\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Total de participantes: {total_usuarios}\n\n")
            
            f.write("PERFILES DE USUARIOS:\n")
            f.write("-" * 80 + "\n")
            for u in self.usuarios:
                f.write(f"  {u.id}. {u.perfil:25} ({u.edad} años, {u.experiencia})\n")
            f.write("\n")
            
            f.write("TASA DE ÉXITO POR TAREA:\n")
            f.write("-" * 80 + "\n")
            for tarea, datos in exito_por_tarea.items():
                f.write(f"{tarea:25} {datos['exitosos']:2}/{datos['total']:2} ({datos['porcentaje']:5.1f}%)\n")
            f.write("\n")
            
            f.write("TIEMPO PROMEDIO POR TAREA (segundos):\n")
            f.write("-" * 80 + "\n")
            for tarea, datos in tiempo_por_tarea.items():
                f.write(f"{tarea:25} Prom: {datos['promedio']:6.1f}s  (Min: {datos['min']:3.0f}s, Max: {datos['max']:3.0f}s)\n")
            f.write("\n")
            
            f.write(f"Satisfacción promedio: {satisfaccion_promedio:.2f}/5.0\n")
            f.write(f"NPS promedio: {nps_promedio:.1f}/10\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("COMENTARIOS POR USUARIO:\n")
            f.write("-" * 80 + "\n")
            for u in self.usuarios:
                f.write(f"\nUsuario {u.id} ({u.perfil}):\n")
                for comentario in u.comentarios:
                    f.write(f"  - {comentario}\n")
            f.write("\n")
            
            f.write("=" * 80 + "\n")
            f.write("RECOMENDACIONES:\n")
            f.write("-" * 80 + "\n")
            
            # Generar recomendaciones automáticas
            for tarea, datos in exito_por_tarea.items():
                if datos['porcentaje'] < 80:
                    f.write(f"⚠️  {tarea}: Solo {datos['porcentaje']:.0f}% éxito - Revisar UX\n")
            
            for tarea, datos in tiempo_por_tarea.items():
                if datos['promedio'] > 120:
                    f.write(f"⚠️  {tarea}: Promedio {datos['promedio']:.0f}s - Simplificar flujo\n")
            
            if satisfaccion_promedio < 4:
                f.write(f"⚠️  Satisfacción baja ({satisfaccion_promedio:.1f}/5) - Mejorar experiencia general\n")
            
            if nps_promedio < 7:
                f.write(f"⚠️  NPS bajo ({nps_promedio:.1f}/10) - Usuarios no recomendarían\n")
            
            f.write("\n" + "=" * 80 + "\n")
        
        print(f"\n📄 Reporte guardado en: {archivo}")
        
        # Mostrar resumen
        print("\n" + "=" * 80)
        print("RESUMEN DE USABILIDAD:")
        print(f"  Participantes: {total_usuarios}")
        print(f"  Satisfacción: {satisfaccion_promedio:.2f}/5.0")
        print(f"  NPS: {nps_promedio:.1f}/10")
        print("=" * 80)


def main():
    print("=" * 80)
    print("SIMULADOR DE TESTS DE USABILIDAD - CARDIO-WELLNESS")
    print("=" * 80)
    print()
    
    simulador = SimuladorUsabilidad()
    
    # Crear usuarios
    print("[1/3] Creando usuarios simulados...")
    simulador.crear_usuarios()
    
    # Ejecutar tests
    print("\n[2/3] Ejecutando tests de usabilidad...")
    simulador.ejecutar_tests()
    
    # Generar reporte
    print("\n[3/3] Generando reporte...")
    simulador.generar_reporte()
    
    print("\n✅ Tests de usabilidad completados")


if __name__ == '__main__':
    main()