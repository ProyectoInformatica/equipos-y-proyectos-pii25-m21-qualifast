# Estados iniciales
puerta_abierta = False
sensor_encendido = False
prisioneros_dentro = 0

# Rol del usuario (puede ser: "comisario", "policia", "visitante")
rol = input("Ingrese su rol (comisario/policia/visitante): ").lower()

if rol == "comisario":
    accion = input("¿Qué desea hacer? (abrir_puerta / cerrar_puerta / prender_sensor / apagar_sensor): ").lower()

    if accion == "abrir_puerta":
        if puerta_abierta:
            print("La puerta ya está abierta.")
        else:
            puerta_abierta = True
            print("Puerta abierta correctamente.")

    elif accion == "cerrar_puerta":
        if not puerta_abierta:
            print("La puerta ya está cerrada.")
        else:
            puerta_abierta = False
            print("Puerta cerrada correctamente.")

    elif accion == "prender_sensor":
        if sensor_encendido:
            print("El sensor ya está encendido.")
        else:
            sensor_encendido = True
            print("Sensor encendido correctamente.")

    elif accion == "apagar_sensor":
        if not sensor_encendido:
            print("El sensor ya está apagado.")
        else:
            sensor_encendido = False
            print("Sensor apagado correctamente.")

    else:
        print("Acción no válida para comisario.")

elif rol == "policia":
    accion = input("¿Qué desea hacer? (ingresar_prisionero / sacar_prisionero): ").lower()

    if accion == "ingresar_prisionero":
        prisioneros_dentro += 1
        print(f"Se ingresó un prisionero. Total ahora: {prisioneros_dentro}")

    elif accion == "sacar_prisionero":
        if prisioneros_dentro > 0:
            prisioneros_dentro -= 1
            print(f"Se sacó un prisionero. Total ahora: {prisioneros_dentro}")
        else:
            print("No hay prisioneros para sacar.")
    else:
        print("Acción no válida para policía.")

elif rol == "visitante":
    print("No tiene permisos para realizar ninguna acción.")

else:
    print("Rol no reconocido.")
