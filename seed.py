import os
import django

# Asegura la configuración de Django (cambia config.settings.production por la que uses)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings.local')
django.setup()

from tournament.models import Team, Player
datos = {
    "Dep. La Araucana": ["Esteban Paredes", "Cristián Álvarez", "Gonzalo Jara", "Matías Rodríguez", "Arturo Sanhueza", "Jaime Valdés", "Walter Montillo", "Gustavo Canales", "Diego Rivarola", "Marcelo Díaz"],
    "Tercer Tiempo F7": ["Claudio Bravo", "Mauricio Isla", "Gary Medel", "Enzo Roco", "Eugenio Mena", "Charles Aránguiz", "Marcelo Díaz", "Jorge Valdivia", "Eduardo Vargas", "Alexis Sánchez"],
    "Real Matadero FC": ["Johnny Herrera", "Osvaldo González", "José Rojas", "Albert Acevedo", "Roberto Cereceda", "Guillermo Marino", "Ezequiel Miralles", "Lucas Barrios", "Humberto Suazo", "Esteban Paredes"],
    "Cancha 3 FC": ["Miguel Pinto", "Yerson Opazo", "Julio Barroso", "Lucas Domínguez", "Juan Cornejo", "César Fuentes", "Esteban Pavez", "Bryan Carrasco", "Octavio Rivero", "Gastón Lezcano"],
    "Los Amigos de Putagán": ["Nicolás Peric", "Boris Rieloff", "Ismael Fuentes", "Sebastián Toro", "Fernando Cordero", "Milovan Mirosevic", "Darío Botinelli", "Lucas Wilchez", "Roberto Gutiérrez", "Carlos Muñoz"],
    "Machicura Mágico": ["Gabriel Arias", "Oscar Opazo", "Valber Huerta", "Benjamín Kuscevic", "Thomas Galdames", "Claudio Baeza", "Pablo Galdames", "Diego Valdés", "Jean Meneses", "Felipe Mora"],
    "Rayo Bucalemu": ["Brayan Cortés", "Paulo Díaz", "Francisco Sierralta", "Guillermo Maripán", "Gabriel Suazo", "Erick Pulgar", "Marcelino Núñez", "Víctor Dávila", "Ben Brereton", "Carlos Palacios"],
    "Costa Maule F7": ["Mauricio Viana", "Paulo Magalhaes", "Leandro Delgado", "Lucas Ascanio", "Matías Campos Toro", "Lorenzo Reyes", "Bryan Rabello", "Ángelo Henríquez", "Felipe Flores", "Junior Fernandes"],
    "La Isla Colbún": ["Sebastián Varas", "Franz Schultz", "Diego Rosende", "Hans Martínez", "Alfonso Parot", "Fernando Manríquez", "César Valenzuela", "Marcos Bolados", "Tobías Figueroa", "Ronnie Fernández"],
    "Defensor Central": ["Cristopher Toselli", "Stefano Magnasco", "Enzo Roco", "Marko Biskupovic", "Raimundo Rebolledo", "Ignacio Saavedra", "Diego Rojas", "Jeisson Vargas", "Nicolás Castillo", "David Llanos"],
    "Los Pichangas": ["Nery Veloso", "Juan Abarca", "Eric Godoy", "Alejandro Contreras", "Nelson Rebolledo", "Alejandro Camargo", "Bryan Carvallo", "Joe Abrigo", "Cecilio Waterman", "Gonzalo Sosa"],
    "Callejeros F7": ["Ignacio González", "Yonathan Andía", "Jonathan Villagra", "Nicolás Díaz", "Alex Ibacache", "Tomás Alarcón", "Pablo Aránguiz", "Williams Alarcón", "Alexander Aravena", "Bastián Yáñez"]
}

for nombre_equipo, jugadores in datos.items():
    equipo, _ = Team.objects.get_or_create(name=nombre_equipo)
    for i, nombre_jugador in enumerate(jugadores, start=1):
        Player.objects.get_or_create(
            team=equipo,
            name=nombre_jugador.split()[0],
            last_name=nombre_jugador.split()[1] if len(nombre_jugador.split()) > 1 else "Apellido",
            number=i,
            defaults={'is_goalkeeper': (i == 1)}
        )

print("¡Proceso finalizado con éxito!")