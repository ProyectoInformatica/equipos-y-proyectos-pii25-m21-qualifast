# Login muy sencillo con reintento ilimitado

# Contraseñas (muy simples)
PASSWORD_COMISARIO = "1234"
PASSWORD_POLICIA = "1234"

while True:
    rol = input("Ingrese su rol (comisario/policia/visitante) o 'salir' para terminar: ").strip().lower()

    if rol == "salir":
        print("Saliendo...")
        break

    if rol == "visitante":
        print("Visitante: no tiene acceso para iniciar sesión.")
        # vuelve a pedir rol (bucle continúa)
        continue

    if rol == "comisario" or rol == "policia":
        contraseña = input("Ingrese la contraseña: ").strip()

        if rol == "comisario":
            if contraseña == PASSWORD_COMISARIO:
                print("Inicio de sesión correcto. Bienvenido, Comisario.")
                # Aquí podrías romper el bucle para continuar con la app
                break
            else:
                print("Contraseña incorrecta para Comisario. Intente nuevamente.")
                # el bucle se repite y vuelve a pedir rol/contraseña

        elif rol == "policia":
            if contraseña == PASSWORD_POLICIA:
                print("Inicio de sesión correcto. Bienvenido, Policía.")
                break
            else:
                print("Contraseña incorrecta para Policía. Intente nuevamente.")
                # vuelve a pedir

    else:
        print("Rol no reconocido. Por favor escriba 'comisario', 'policia' o 'visitante'.")
