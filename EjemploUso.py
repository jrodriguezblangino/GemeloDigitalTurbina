import time
from GemeloTurbina import Turbina, EstadoTurbina

def test_turbina():
    # Crear instancia de la turbina
    turbina = Turbina()


    print("=== Escenario 1: Arranque normal desde panel ===")
    turbina.selectora_local = True  # Modo PANEL
    turbina.sensor_valvula_principal = False  # Válvula principal abierta
    turbina.botones_comando["Arranque"] = True
    turbina.update()
    print(f"Estado actual: {turbina.estado_actual}")
    time.sleep(2)
    
    print("\n=== Escenario 2: Operación en modo automático ===")
    # La turbina ya debería estar en modo automático después del arranque
    if turbina.estado_actual == EstadoTurbina.AUTOMATICO:
        print("Ajustando setpoint automático a 5000 RPM")
        turbina.SPAuto_inversa(5000)
        turbina.control_automatico()
        print(f"Velocidad actual: {turbina.velocidad} RPM")
        print(f"Comando válvula: {turbina.comando_valvula}%")
    
    print("\n=== Escenario 3: Parada controlada ===")
    turbina.botones_comando["ParadaControlada"] = True
    turbina.update()
    print(f"Estado después de parada controlada: {turbina.estado_actual}")
    
    print("\n=== Escenario 4: Intento de arranque con válvula principal cerrada ===")
    turbina.selectora_local = False  
    turbina.sensor_valvula_principal = True  # Válvula principal cerrada
    turbina.botones_comando["Arranque"] = True
    turbina.update()
    print(f"Estado actual: {turbina.estado_actual}")
    
    print("\n=== Escenario 5: Parada de emergencia por sobretemperatura ===")
    EstadoTurbina.AUTOMATICO
    turbina.sensor_valvula_principal = False
    turbina.botones_comando["Arranque"] = True
    turbina.update()
    time.sleep(2)
    # Simulamos sobretemperatura
    print("Simulando condición de sobretemperatura...")
    turbina.temperatura_quemadores = 360
    turbina.update()
    print(f"Estado actual: {turbina.estado_actual}")
    print(f"Freno activado: {turbina.freno}")
    print(f"Válvula de escape: {turbina.valvula_escape}")
    
    print("\n=== Escenario 6: Parada de emergencia por baja presión sostenida ===")
    EstadoTurbina.AUTOMATICO
    turbina.sensor_valvula_principal = False
    turbina.botones_comando["Arranque"] = True
    turbina.update()
    time.sleep(2)
    print("Simulando condición de baja presión...")
    turbina.velocidad = 4500
    turbina.presion_gas = 3.0
    turbina.update()
    time.sleep(31)  # Esperamos más de 30 segundos
    turbina.update()
    print(f"Estado actual: {turbina.estado_actual}")
    
    print("\n=== Escenario 7: Operación en modo manual ===")
    turbina.estado_actual = EstadoTurbina.AUTOMATICO  # Corregir asignación faltante
    turbina.ModoControl = 0  # Modo manual
    turbina.SPManual_inversa(50)  # 50% de apertura
    turbina.control_velocidad()  # Actualizado por nuevo nombre
    print(f"Comando válvula en modo manual: {turbina.comando_valvula}%")
    
    print("\n=== Escenario 8: Parada de emergencia por botón ===")
    turbina.botones_parada_emergencia["Boton1"] = True
    turbina.update()
    print(f"Estado actual: {turbina.estado_actual}")
    print(f"Velocidad: {turbina.velocidad}")
    print(f"Quemador de emergencia: {turbina.quemador_emergencia}")

if __name__ == "__main__":
    test_turbina()