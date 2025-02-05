#GEMELO DIGITAL QUE SIMULA LA CREACION DE UNA TURBINA DE GAS

import time #modulo usado unicamente para aportar experiencia de usuario en la simulacion

###################SE DEFINE EL ESTADO DE LA TURBINA Y LA TURBINA#########################

class EstadoTurbina:
    DETENIDA = "detenida"
    ARRANQUE = "arranque"
    AUTOMATICO = "automático"
    PARADA_CONTROLADA = "parada_controlada"
    EMERGENCIA = "emergencia"

class Turbina:

    # Al ser un gemelo digital, se crean los atributos dentro de la clase, no en el inicio

    def __init__(self):
        # --- Configuración inicial del sistema ---
        self.estado_actual = EstadoTurbina.DETENIDA
        
        # --- Entradas digitales ---
        # True: Modo PANEL, False: Modo LOCAL
        self.selectora_local = False
        self.botones_parada_emergencia = {"Boton1": False, "Boton2": False}
        self.botones_comando = {"Arranque": False, "ParadaControlada": False}
        self.sensores_llama = {"Quemador1": False, "Quemador2": False}
        self.sensor_valvula_principal = False  # True cuando está cerrada
        self.sensor_freno = False  # True cuando está cerrado

        # --- Entradas analógicas ---
        # Rango típico: 0-6000 RPM (4-20mA)
        self.velocidad = 0
        self.presion_gas = 4.0 # bar
        self.temperatura_quemadores = 300 # ºC
        self.ModoControl = 0  # 0 = Manual, 1 = Automático
        self.SPManual = 4  # 4mA = 0% apertura 
        self.SPAuto = 4  # 4mA = 0 RPM

        # --- Salidas de control ---
        self.comando_valvula = 0  # 0-100% apertura
        self.consigna_velocidad = 0  # RPM (4-20mA)

        # Variables internas
        self.tiempo_baja_presion = None
        self.en_arranque = False
        self.tiempo_inicio_secuencia = None

        # Salidas digitales - Se inicializan todas como False, luego se activan según la secuencia
        self.motor_arranque = False
        self.junta_neumatica = False  
        self.chisperos = {"Quemador1": False, "Quemador2": False} 
        self.freno = False 
        self.valvula_escape = False
        self.quemador_emergencia = False
        self.valvula_2vias = False

    # Operaciones para convertir y ajustar los valores de miliamperios y viceversa

    def valor_convertido(self, valor, min_range, max_range):
        """
        Convierte valor de 4-20mA a rango de medición real
        Args:
            valor: señal de entrada en mA (4-20)
            min_range: valor mínimo del rango real
            max_range: valor máximo del rango real
        Returns:
            Valor convertido a unidades de ingeniería
        """
        valor = max(4, min(20, valor))  # Limitar entre 4-20mA
        return min_range + (valor - 4) * (max_range - min_range) / 16

    def conversion_inversa(self, valor, min_range, max_range):
        valor = max(min_range, min(max_range, valor))  # Limitar al rango
        return 4 + (valor - min_range) * 16 / (max_range - min_range)
    
    # Metodos para convertir entradas analógicas a entradas digitales

    def SPManual_porcentaje(self):
        return self.valor_convertido(self.SPManual, 0, 100)  # 0-100%

    def SPManual_inversa(self, percentage):
        self.SPManual = self.conversion_inversa(percentage, 0, 100) # Rango 4-20mA.

    def SPAuto_conversion(self):
        return self.valor_convertido(self.SPAuto, 0, 6000)  # 0-6000 RPM

    def SPAuto_inversa(self, rpm):
        self.SPAuto = self.conversion_inversa(rpm, 0, 6000) # RPM a miliamperios.


    ####################DEFINICION DE LOS METODOS DE LA TURBINA#################################3



    #CHEQUEO DE CUALQUIER ESTADO QUE PUEDA GENERAR UNA EMERGENCIA

    def condiciones_emergencia(self):

        # Si se presiona un botón de parada de emergencia

        if self.botones_parada_emergencia["Boton1"] or self.botones_parada_emergencia["Boton2"]:
            print("Parada de emergencia: botón presionado.")
            self.parada_emergencia()
            return True #si se produce una emergencia, se devuelve True en todos los casos para salir del bucle inmediatamente 

        # Si la velocidad excede 5500 RPM

        if self.velocidad > 5500:
            print("Parada de emergencia: velocidad excede 5500 RPM.")
            self.parada_emergencia()
            return True
        
        # Si la presión de gas es mayor a 5.5 bar

        if self.presion_gas > 5.5:
            print("Parada de emergencia: presión de gas mayor a 5.5 bar.")
            self.parada_emergencia()
            return True
        
        # Si la presión de gas es baja durante 30 segundos y la velocidad es mayor a 4000 RPM

        if self.presion_gas < 3.3 and self.velocidad > 4000:
            if self.tiempo_baja_presion is None:
                self.tiempo_baja_presion = time.time()
            elif time.time() - self.tiempo_baja_presion > 30:
                print("Parada de emergencia: presión baja durante 30 segundos a alta velocidad.")
                self.parada_emergencia()
                return True
            
        #El else es necesario para que el tiempo_baja_presion se reinicie a None si la velocidad es menor a 4000 RPM

        else:
            self.tiempo_baja_presion = None

        # Si la temperatura de los quemadores es mayor a 350 ºC

        if self.temperatura_quemadores > 350:
            print("Parada de emergencia: sobretemperatura.")
            self.parada_emergencia()
            return True
        

    # METODO DE PARADA DE EMERGENCIA 

    def parada_emergencia(self):

        self.estado_actual = EstadoTurbina.EMERGENCIA #Cambia el estado de la turbina a emergencia
        self.comando_valvula = 0 #Comando de apertura de la válvula
        self.freno = True #Activa el freno
        self.valvula_escape = True #Activa la válvula de escape
        self.quemador_emergencia = True #Activa el quemador de emergencia
        self.valvula_2vias = True  # Cierra el paso de gas
        self.velocidad = 0 #Detiene la turbina
        print("Parada de emergencia completada. ")


    # METODO DE SECUENCIA DE ARRANQUE

    def secuencia_arranque(self):
        #Chequeo de que la turbina esté totalmente detenida
        if self.estado_actual != EstadoTurbina.DETENIDA:
            print("Error: La turbina no está totalmente detenida.")
            return False

        if self.velocidad > 0:
            print("Error: La turbina no está completamente detenida.")
            return False

        if self.sensor_valvula_principal:  # True significa cerrada
            print("Error: Válvula principal cerrada. No se puede iniciar el arranque.")
            return False
        
        #ELSE: Se inicia la secuencia de arranque

        self.estado_actual = EstadoTurbina.ARRANQUE
        print("PASO 1: Iniciando secuencia de arranque...")
        
        # Motor auxiliar y junta neumática - Aceleración hasta auto-sustentación
        self.motor_arranque = True
        self.junta_neumatica = True
        while self.velocidad < 478:
            self.velocidad += 50
            print(f"Acelerando con motor auxiliar: {self.velocidad} RPM")
            time.sleep(0.5)
        print(f"Auto sustentación alcanzada: {self.velocidad} RPM")

        # Encendido de quemadores - Control manual inicial
        print("PASO 2: Encendiendo quemadores...")
        self.chisperos["Quemador1"] = True
        self.chisperos["Quemador2"] = True
        time.sleep(2)
    
        self.sensores_llama["Quemador1"] = True
        self.sensores_llama["Quemador2"] = True
        
        # Chequeo de que los sensores de temperatura y presión de gas estén funcionando

        for sensor_estado in self.sensores_llama.values():
            if not sensor_estado:
                print("Error: Uno o ambos quemadores no encendieron.")
                self.parada_emergencia()
                return False

        # Control manual inicial - Apertura de válvula gradualmente
        self.ModoControl = 0
        self.SPManual_inversa(10)  # 10% de apertura
        print("Modo manual activado. Válvula abierta al 10%")

        # Aceleración hasta 2750 RPM
        print("PASO 3: Acelerando hasta 2750 RPM...")
        self.SPManual_inversa(25)  # 25% de apertura
        while self.velocidad < 2750:
            self.velocidad += 100
            print(f"Acelerando: {self.velocidad} RPM")
            time.sleep(0.5)

        # Desacople del motor auxiliar
        self.junta_neumatica = False
        print("Motor auxiliar desacoplado.")
        time.sleep(5)
        self.motor_arranque = False
        print("Motor auxiliar apagado.")

        # Activación del control automático
        print("PASO 4: Activando control automático...")
        self.ModoControl = 1
        self.SPAuto_inversa(4600)
        self.estado_actual = EstadoTurbina.AUTOMATICO
        print("Control automático activado. Consigna: 4600 RPM")
        return True
    
    # METODO DE PARADA CONTROLADA

    def parada_controlada(self):

        # Chequeo de que la turbina esté en automático y que la velocidad sea mayor a 2500 RPM

        if self.estado_actual != EstadoTurbina.AUTOMATICO or self.velocidad < 2500:
            print("No se puede realizar parada controlada: la turbina no está en automático.")
            return False
        
        # Si se presiona el botón de parada de emergencia

        self.estado_actual = EstadoTurbina.PARADA_CONTROLADA
        print("Iniciando parada controlada...")
        
        # Reducción gradual de velocidad

        self.ModoControl = 0
        print("Comenzando la reducción de velocidad...")
        self.SPManual_inversa(10)  # 10% apertura
        print("Apertura de válvula al 10%")
        time.sleep(10)
        self.SPManual_inversa(0)   # Cierre completo
        print("Válvula completamente cerrada.")

        while self.velocidad > 0:
            self.velocidad = max(0, self.velocidad - 100)
            print(f"Desacelerando: {self.velocidad} RPM")
            time.sleep(1)

        # Activación del freno
        self.freno = True
        self.estado_actual = EstadoTurbina.DETENIDA
        print("Parada controlada completada.")
        return True
    

    # METODO DE CONTROL DE LA TURBINA EN AUTOMÁTICO

    def control_velocidad(self):
        """Controla la velocidad mediante PID básico"""
        # Chequeo de que la turbina esté en automático
        if self.ModoControl == 1:
            error = self.SPAuto_conversion() - self.velocidad
            # Control proporcional simple con límites
            ajuste = error * 0.01  # Ganancia
            self.comando_valvula = max(0, min(100, self.comando_valvula + ajuste))
        else:  # Modo Manual
            self.comando_valvula = self.SPManual_porcentaje()

    # MÉTODO DE ACTUALIZACIÓN DE LA TURBINA

    def update(self):
        if self.condiciones_emergencia():
            return  # Si hay emergencia, no se ejecutan más acciones

        # Control basado en la selectora
        if self.selectora_local:  # PANEL
            if self.botones_comando["Arranque"] and self.estado_actual == EstadoTurbina.DETENIDA:
                self.en_arranque = True
            if self.botones_comando["ParadaControlada"] and self.estado_actual == EstadoTurbina.AUTOMATICO:
                self.parada_controlada()
        else:  # LOCAL
            if self.botones_comando["Arranque"] and self.estado_actual == EstadoTurbina.DETENIDA:
                self.en_arranque = True
            if self.botones_comando["ParadaControlada"] and self.estado_actual == EstadoTurbina.AUTOMATICO:
                self.parada_controlada()

        # Ejecución de secuencias según estado
        if self.en_arranque:
            self.secuencia_arranque()
            self.en_arranque = False
        elif self.estado_actual == EstadoTurbina.AUTOMATICO:
            self.control_velocidad()