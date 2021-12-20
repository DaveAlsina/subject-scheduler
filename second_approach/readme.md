
## Ejecución 

Para ejecutar por primera vez y testear rápidamente el programa puede ejecutar:

		python3 build_graph_from_lecture_grid.py
		
Aparecerá un menú de opciones, para probar el programa y que sea rápidamente seleccione 
la opcion -1 de menú. Las soluciones encontradas se guardarán en un csv dentro de la carpeta
**solutions** con un timestamp por nombre de archivo.


### Versiones 

Para satisfacer los requerimientos  de versiones de librerías puede crear un ambiente virtual 
con **virtualenv**:

		python -m venv ./venv
		source ./venv/bin/activate

Después instale los requerimientos:

		pip install -r requirements.txt

Al momento de salir de la carpeta puede ejecutar:

		deactivate

Para desactivar el ambiente virtual.

Un script para automatizar la activación y desactivación de los ambientes virtuales 
que le puede ser de mucha utilidad es: 

		function cd() {
		  if [[ -d ./venv ]] ; then
			deactivate
		  fi

		  builtin cd $1

		  if [[ -d ./venv ]] ; then
			. ./venv/bin/activate
		  fi
		}

_Puede agregarlo a su .bashrc_






