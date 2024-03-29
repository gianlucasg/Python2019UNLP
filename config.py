from pattern.web import Wiktionary,DOM,plaintext,SEARCH
from pattern.es import parse
import PySimpleGUI as sg
import json
def seleccionarColor():
	""" Modulo para realizar la seleccion de un color para el tipo de palabra deseadaself.
	  	Este modulo es llamado por uno de los tres botones de palabras que se encuentran en la configuracion."""
	color=''
	col=[[sg.Text('Seleccionar un color')],[sg.Button('Rojo',size=(7,1),button_color=('white','red')),sg.Button('Azul',size=(7,1),button_color=('white','blue'))],
	[sg.Button('Amarillo',size=(7,1),button_color=('white','yellow')),sg.Button('Verde',size=(7,1),button_color=('white','green'))],[sg.Button('Naranja',size=(7,1),button_color=('white','orange')),
	sg.Button('Violeta',size=(7,1),button_color=('white','purple'))]]

	windows=sg.Window('Colores',col)
	while True:
		event,values=windows.Read()
		if event is None:
			if color == '':
				sg.Popup('Seleccione un color por favor')
				break
		if event == 'Rojo':
			color= 'red'
			break
		if event == 'Azul':
			color= 'blue'
			break
		if event == 'Amarillo':
			color= 'yellow'
			break
		if event == 'Verde':
			color= 'green'
			break
		if event == 'Naranja':
			color= 'orange'
			break
		if event == 'Violeta':
			color= 'purple'
			break
	windows.Close()
	return color

def regError():
	""" Modulo el cual realiza el cambio de la tipografia del archivo que contiene los datos
	que generaron un conflicto entre patter y wikcionario """
	try:
		with open('Informe de error.json', 'r') as archivo:
			erro=json.load(archivo)
		fuente=sg.PopupGetText('Ingrese nombre de la fuente a utilizar')
		try:
			lay=[[sg.Text(erro, font=(fuente, 11))]]
		except:
			sg.PopupText('No se encontró la fuente ingresada, se utilizará Arial')
			lay=[[sg.Text(erro, font=('Arial', 11))]]
		win=sg.Window('Prueba',lay)
		event,values=win.Read();
		while True:
			if event==None:
				break
	except:
		sg.Popup('No se encuentran reportes de error')

def infoError(palabra,tipop,tipo):
	"""Modulo el cual crea y guarda o simplemente guarda si ya existe un archivo con las palabras que generaron
	un conflictio entre pattern y wikcionario"""
	error=('Error de pattern: la palabra: '+palabra+' se detecta como '+tipop+' mientras que en wiktionary es: '+tipo+'\n')
	try:
		with open('Informe de error.json', 'r') as archivo:
			erro=json.load(archivo)
		error=error+erro
	except:
		sg.Popup('No se encontraron informes de error previos, creando informe de error')
	with open('Informe de error.json', 'w') as outFile:
		json.dump(error,outFile)
	outFile.close()

def IngresarEliminarPal(lista,cant,wincon):
	"""Modulo el cual realiza el ingreso de palabras como tambien la eliminacion de las mismas"""
	pal=[[sg.Input(key='palabra'),sg.Button('Ingresar')],
	[sg.Table(values=lista,headings=['Palabra','Tipo'],key='tabla',def_col_width=16,auto_size_columns=False)],
	[sg.Input(key='elim'),sg.Button('Eliminar')],
	[sg.Button('Aceptar')]]
	winpal=sg.Window('Ingresar Palabras',pal)
	while True:
		event,values=winpal.Read()
		if event=='Aceptar' or event is None:
			break
		if event=='Eliminar':
			for i in lista:
				if values['elim'] in i:
					tipo=i[1]
					lista.remove(i)
			winpal.FindElement('tabla').Update(values=lista)
			if tipo=='sustantivo':
				cant['sus']=cant['sus']-1
				wincon.FindElement('cantsus').Update(value='/'+str(cant['sus']))
			else:
				if tipo=='adjetivo':
					cant['adj']=cant['adj']-1
					wincon.FindElement('cantadj').Update(value='/'+str(cant['adj']))
				else:
					if tipo=='verbo':
						cant['verb']=cant['verb']-1
						wincon.FindElement('cantverb').Update(value='/'+str(cant['verb']))

		if event=='Ingresar':
			engine=Wiktionary(language='es')
			if values['palabra']=='':
				sg.Popup('No se ingresó una palabra')
			else:
				palabra=values['palabra']
				result=engine.search(palabra)
				jeh=parse(palabra)
				if ('NN'in jeh or 'NNS' in jeh or 'NNP' in jeh or 'NNPS' in jeh):
					tipop='sustantivo'
				else:
					if ('JJ' in jeh or 'JJR' in jeh or 'JJS' in jeh):
						tipop='adjetivo'
					else:
						if('VB' in jeh):
							tipop='verbo'
						else:
							sg.Popup('La palabra no se reconoce como adjetivo, sustantivo o verbo en el modulo pattern')
							tipop='sad'
				if (not result==None):
					flag=True
					for i in range(len(result.sections)):
						if ('Etimología' in str(result.sections[i]) and flag):
							busqueda=result.sections[i+1].string
							flag=False
					if ('Sustantivo' in busqueda or 'sustantivo' in busqueda):
						tipo='sustantivo'
					else:
						if ('Adjetivo' in busqueda or 'adjetivo' in busqueda or 'adjetiva' in busqueda):
							tipo='adjetivo'
						else:
							if ('Verbo' in busqueda or 'verbal' in busqueda):
								tipo='verbo'
							else:
								tipo='malo'
					escribir= False
					definicion=''
					if not tipo=='malo':
						for i in busqueda:
							if escribir==True:
								if i=='2':break
								definicion=definicion+i
							else:
								if i=='1':
									escribir=True
					if not tipo==tipop:
						infoError(palabra,tipop,tipo)
					if tipo=='malo':
						tipo=tipop
						sg.Popup('La palabra no se reconoce como verbo, adjetivo o sustantivo en wiktionary')
				else:
					if (not tipop=='sad'):
						definicion=sg.PopupGetText('La palabra no se encontró en wiktionary pero si en pattern, por favor, ingrese una definición:','Error')
						tipo=tipop
				if (not tipo=='malo' and not tipo=='sad'):
					lista.append([palabra,tipo,definicion])
					if tipo=='sustantivo':
						cant['sus']=cant['sus']+1
						wincon.FindElement('cantsus').Update(value='/'+str(cant['sus']))
					else:
						if tipo=='adjetivo':
							cant['adj']=cant['adj']+1
							wincon.FindElement('cantadj').Update(value='/'+str(cant['adj']))
						else:
							if tipo=='verbo':
								cant['verb']=cant['verb']+1
								wincon.FindElement('cantverb').Update(value='/'+str(cant['verb']))
					winpal.FindElement('tabla').Update(values=lista)
			difinicion=''
			palabra=''
			tipo=''
	winpal.Close()

def config(lista,cant,vert,caps,ayuda):
	"""Modulo el cual realiza todo el entorno grafico para la configuracion del juego"""
	num={}
	color={'sustantivo':('Red'),'adjetivo':('Green'),'verbo':('Purple')}
	vert=True
	caps=True
	ayuda=False
	con=[[sg.Text('Orientación:')],
		[sg.Button('Vertical',key='Vertical'),sg.Button('Horizontal',key='Horizontal',button_color=('Black','LightGrey'))],
		[sg.Text('Ayuda:')],
		[sg.Button('Activada',key='act',button_color=('Black','LightGrey')),sg.Button('Desactivada',key='des')],
		[sg.Button('Ingresar palabras')],[sg.Text('Selecionar colores:')],
		[sg.Button('Colores Verbos',key='colverb'),sg.Button('Colores Sustantivos',key='colsus'),sg.Button('Colores Adjetivos',key='coladj')],
		[sg.Text('Verbos'),sg.Input(key='verb',size=(2,3),default_text='0'),sg.Text('/'+str(cant['verb']),key='cantverb')],
		[sg.Text('Adjetivos'),sg.Input(key='adj',size=(2,3),default_text='0'),sg.Text('/'+str(cant['adj']),key='cantadj')],
		[sg.Text('Sustantivos'),sg.Input(key='sus',size=(2,3),default_text='0'),sg.Text('/'+str(cant['sus']),key='cantsus')],
		[sg.Button('Verificar palabras')],
		[sg.Button('Mayúsculas',key='caps'),sg.Button('Minúsculas',key='min',button_color=('Black','LightGrey'))],
		[sg.Button('Registro de errores')],
		[sg.Button('Salir'),sg.Button('Aceptar',key='Aceptar',disabled=True)]]
	wincon=sg.Window('Configuración',con)
	while True:
		event,values=wincon.Read()
		if event=='Salir' or event is None or event=='Aceptar':
			break
		if event=='Registro de errores':
			regError()
		if event=='Horizontal':
			wincon.FindElement("Horizontal").Update(button_color=('White','DarkBlue'))
			wincon.FindElement("Vertical").Update(button_color=('Black','LightGrey'))
			vert=False
		if event=='Vertical':
			wincon.FindElement("Vertical").Update(button_color=('White','DarkBlue'))
			wincon.FindElement("Horizontal").Update(button_color=('Black','LightGrey'))
			vert=True
		if event=='act':
			wincon.FindElement("act").Update(button_color=('White','DarkBlue'))
			wincon.FindElement("des").Update(button_color=('Black','LightGrey'))
			ayuda=True
		if event=='des':
			wincon.FindElement("des").Update(button_color=('White','DarkBlue'))
			wincon.FindElement("act").Update(button_color=('Black','LightGrey'))
			ayuda=False
		if event=='caps':
			wincon.FindElement("caps").Update(button_color=('White','DarkBlue'))
			wincon.FindElement("min").Update(button_color=('Black','LightGrey'))
			caps=True
		if event=='min':
			wincon.FindElement("min").Update(button_color=('White','DarkBlue'))
			wincon.FindElement("caps").Update(button_color=('Black','LightGrey'))
			caps=False
		if event == 'colverb':
			color['verbo']=seleccionarColor()
		if event == 'colsus':
			color['sustantivo']=seleccionarColor()
		if event == 'coladj':
			color['adjetivo']=seleccionarColor()
		if event=='Ingresar palabras':
			IngresarEliminarPal(lista,cant,wincon)
		if event=='Verificar palabras':
			if (int(values['verb'])>cant['verb'] or int(values['adj'])>cant['adj'] or int(values['sus'])>cant['sus']):
				sg.Popup('No hay palabras suficientes ingresadas')
				if(int(values['verb'])>cant['verb']):
					values['verb']=cant['verb']
					wincon.FindElement('verb').Update(values['verb'])
				if(int(values['adj'])>cant['adj']):
					values['adj']=cant['adj']
					wincon.FindElement('adj').Update(values['adj'])
				if(int(values['sus'])>cant['sus']):
					values['sus']=cant['sus']
					wincon.FindElement('sus').Update(values['sus'])
				wincon.FindElement('Aceptar').Update(disabled=True)
			else:
				wincon.FindElement('Aceptar').Update(disabled=False)
				num=[int(values['sus']),int(values['adj']),int(values['verb'])]
	wincon.Close()
	dic={'palabras':lista,'cant':num,'vert':vert,'caps':caps,'ayuda':ayuda,'color':color}
	return dic
