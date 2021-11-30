
#Para usar este código tenga en cuenta que:

* "Libro1.csv" contiene la información relativa a las materias, prerequisitos y la periodicidad en que estas se dictan.
Para un funcionamiento adecuado del programa recuerde poner en este archivo solo las materias que desea ver. Por ejemplo:
si desea terminar una doble línea de profundización (IA y ciber) ponga allí solo las materias que necesita para cumplir 
estos requerimientos.

Tenga en cuenta que en el campo de frecuencia un 1 significa que la materia es semestral, y un 0 que esta se dicte anualmente
Además en el campo de "starting semester" se añade la próxima vez en que se va a dictar dicha materia, incluyendo dentro de esta definición 
materias que se estén dictando este semestre. 

Finalmente en la columna "dependency" se añade la materia que es prerrequisito inmediatamente anterior de la materia que se desea ver.

* "Libro2.csv" contiene en la columna "completed lecture" las materias que se han terminado exitosamente. 

#Para ejecutar el código: 

python3 schedule5.py

#Salvedades respecto a la herramienta

Para la herramienta será imposible dar una solución si una de las materias que son prerrequisito base (materias obligatorias de MACC que desbloquean 
una o varias electivas de profundización) no está seleccionadas como vistas en "Libro2.csv", por lo tanto esta herramienta se perfila como una generadora de 
todas las rutas posibles y viables bajo ciertas restricciones dadas por el usuario, a partir de las cuales el usuario puede hacer una selección más cómoda 
de qué ruta seguir basado en las materias que habrá visto.

Al final, verá un print de las llaves del diccionario, las llaves de este diccionario son las permutaciones del número de materias que se inscriben por semestre dado, 
modificando el código puede hacer una visualización de estas llaves en la forma en la que guste. 

pd: me dio mucha pereza añadirle funcionalidades extra en la consola, como la de escojer que valores del diccionario ver, dando como base una llave. sorry, not sorry. 



