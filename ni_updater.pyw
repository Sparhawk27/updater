# -*- coding: utf-8 -*-
from Tkinter import *
import tkMessageBox
from functools import partial
from datetime import datetime
import io
import gzip
import zlib
import urllib2
import os
import sys
import hashlib
import traceback
import niel #custom logging module
import logging

class niUpdater:
	def __init__(self, parent):
		self.myParent = parent
		self.topContainer = Frame(parent)
		self.topContainer.pack(side=TOP, expand=1, fill=X, anchor=NW)
		self.midContainer = Frame(parent)
		self.midContainer.pack(side=TOP, expand=1, fill=X, anchor=NW)
		self.btmContainer = Frame(parent)
		self.btmContainer.pack(side=BOTTOM, expand=0, fill=X, anchor=NW)

		#------------------ ENTRY --------------------------------------
		v = StringVar()
		v.set(myloc + "\\ModuleName")
		entry1 = Entry(self.topContainer, textvariable=v)
		entry1.pack(side=LEFT, expand=1, fill=X)
		entry1.configure(state=DISABLED)

		#------------------ BUTTONS ------------------------------------
		button_name = "OK"
		button_name2 = "?"

		# command binding
		var = StringVar()
		self.button1 = Button(self.topContainer, command=lambda: self.buttonPress(var))
		self.button2 = Button(self.topContainer, command=lambda: self.button2Press())

		# event binding -- passing the event as an argument
		self.button1.bind("<Return>",
			lambda
			event :
			self.buttonHandler_a(var)
		)

		self.button2.bind("<Return>",
			lambda
			event :
			self.button2Handler_a()
		)

		self.button1.configure(text=button_name, width=5)
		self.button1.pack(side=LEFT)
		
		self.button2.configure(text=button_name2, width=5)
		self.button2.pack(side=LEFT)
		
		self.button1.focus_force()  # Put keyboard focus on button1

		#------------------ LANGUAGE -----------------------------------
		self.buttonEng = Button(self.midContainer, command=lambda: self.setLanguage("eng",var))
		self.buttonEng.configure(text="Eng", width=5, height = 1)
		self.buttonEng.pack(side=LEFT)

		self.buttonFre = Button(self.midContainer, command=lambda: self.setLanguage("fre",var))
		self.buttonFre.configure(text="Fre", width=5)
		self.buttonFre.pack(side=LEFT)
		
		self.buttonGer = Button(self.midContainer, command=lambda: self.setLanguage("ger",var))
		self.buttonGer.configure(text="Ger", width=5)
		self.buttonGer.pack(side=LEFT)

		self.buttonIta = Button(self.midContainer, command=lambda: self.setLanguage("ita",var))
		self.buttonIta.configure(text="Ita", width=5)
		self.buttonIta.pack(side=LEFT)

		self.buttonNor = Button(self.midContainer, command=lambda: self.setLanguage("nor",var))
		self.buttonNor.configure(text="Nor", width=5)
		self.buttonNor.pack(side=LEFT)

		self.buttonRus = Button(self.midContainer, command=lambda: self.setLanguage("rus",var))
		self.buttonRus.configure(text="Rus", width=5)
		self.buttonRus.pack(side=LEFT)

		self.buttonSpa = Button(self.midContainer, command=lambda: self.setLanguage("spa",var))
		self.buttonSpa.configure(text="Spa", width=5)
		self.buttonSpa.pack(side=LEFT)



		#------------------ LABEL --------------------------------------
		self.label = Label(self.btmContainer,textvariable=var, width=55, anchor=W, justify=LEFT)
		self.label.pack(side=LEFT, expand=1, fill=X)
		var.set("Ready to update... Press OK")

	def downloadFile(self, filename, localfile, var):
		url = webloc + filename.replace('\\','/')
		url = url.replace(' ','%20')
		self.msg_downloading(var, filename)
		response = urllib2.urlopen(url)

		fout = open(localfile, 'wb')
		if url.endswith('.gz'):
			data = zlib.decompress(response.read(), 15+32)
			fout.writelines(bytes(data))
		else:
			fout.writelines(response)
		fout.close()

	def doCompare(self, dir, hashfile, var):
		global dlFailed, curNum
		if dlFailed == True: pass
		if not dir.endswith("\\"):
			dir = dir + "\\"
		while dlFailed == False:
			fileName = hashfile.readline()

			if not fileName:
				break
			fileName = fileName.rstrip('\n')
			if fileName.startswith("V::"): #its the version number - ignore
				pass
			elif fileName.startswith("W::"): #website folder - ignore
				pass
			elif fileName.startswith("X::"): #ignore - exists only for counting reasons
				pass
			elif fileName.startswith("F::"): #its a folder
				curNum += 1
				var.set("(" + str(curNum) + "/" + str(totNum) + ")  " + fileName.replace("F::",""))
				root.update()
				if not os.path.exists(dir + fileName.replace("F::","")):
					os.makedirs(dir + fileName.replace("F::",""))
			else:
				curNum += 1
				var.set("(" + str(curNum) + "/" + str(totNum) + ")  " + fileName)
				root.update()
				webHash = hashfile.readline()
				webHash = webHash.rstrip('\n')
				attempts = 0
				verification = False
				while attempts < 4 and dlFailed==False:
					attempts = attempts + 1
					try:
						localFile = dir + fileName
						if not os.path.exists(localFile): #create file
							newfile = open(localFile, 'w+')
							newfile.close()
						localHash = hashlib.sha1(open(localFile, 'rb').read()).hexdigest()
						if not webHash == localHash:
							try:
								self.msg_downloading(var, localFile)
								self.downloadFile(fileName + ".gz", localFile, var)
								if attempts == 4:
									dlFailed = true
							except:
								if attempts == 4:
									dlFailed = true
									return
								logging.info(datetime.now())
								logging.debug("File: " + fileName)
								logging.error("", exc_info=niel.full_exc_info())
								logging.info("\n")
								self.msg_dlFailed(var, fileName)
						else:
							attempts = 5
					except OSError as exc:
						logging.info(datetime.now())
						logging.debug("File: " + fileName)
						logging.error(str(exc), exc_info=niel.full_exc_info())
						logging.info("\n")
						self.msg_error(var, "File IO Error")
						
				if attempts == 4:
					logging.info(datetime.now())
					logging.debug("File: " + fileName)
					logging.debug("LHash: " + localHash)
					logging.debug("WHash: " + webHash)
					logging.error("", exc_info=niel.full_exc_info())
					logging.info("\n")
					self.msg_error(var, "Hash Code Mismatch")


	def buttonPress(self, var):
		try:
			global webloc, webloc1, myloc, dlFailed,curNum,totNum
			self.button1.configure(state=DISABLED)
			self.msg_ready(var)
			dlFailed = False
			hashfile = myloc + '\\hash.txt'

			if (myloc.upper().endswith("MOUNTBLADE WARBAND\\MODULES")) or (myloc.endswith("MountBlade Warband/Modules/")):
				if not os.path.exists(myloc + "\\NordInvasion"):
					os.makedirs(myloc + "\\NordInvasion")
				path = myloc + "\\NordInvasion\\"
			else:
				self.msg_folder(var)
				return
			
			webloc = webloc1
			curNum = 0
			totNum = 0

			try:
				self.downloadFile("hash.txt", hashfile, var)
			except:
				dlFailed=True

				logging.info(datetime.now())
				logging.debug("Downloading hash file")
				logging.error("", exc_info=niel.full_exc_info())
				logging.info("\n")
				self.msg_dlFailed(var, "Hash File")		
			else:
				global myVersion

				####### readline
				file = open(hashfile,'rt')#, encoding='ansi')
				totNum = sum(1 for line in file)
				totNum -= 2
				totNum = totNum/2
				file.seek(0,0)
				webVersion = int(file.readline().replace("V::","").rstrip('\n')) #get version number
				if not webVersion:
					self.msg_error(var,"Hash file empty!")
				elif myVersion < webVersion:
					tkMessageBox.showwarning("Version Error","Out of Date")
				else:
					webloc = file.readline().replace("W::","").rstrip('\n')
					self.doCompare(path,file,var)
				file.close()
				self.button1.configure(state=NORMAL)
				if dlFailed==False: self.msg_finish(var)
		except:
			logging.info(datetime.now())
			logging.debug("Button1 Press")
			logging.error("", exc_info=niel.full_exc_info())
			logging.info("\n")
			self.msg_error(var, "Fatal Error")

	def buttonHandler_a(self, var):
		self.buttonPress(var)
		

	def buttonHandler_a(self):
		self.buttonPress2()

	#Messages are defined below - Warning: Single Threaded so UI will NOT update when the downloads are running
	def msg_ready(self,var):
		if l=="eng":
			var.set("Ready to update... Press OK")
		elif l=="fre":
			var.set("Mise à jour prête... Appuyez sur OK")
		elif l=="spa":
			var.set("Listo para actualizar... Pulse OK")
		elif l=="ger":
			var.set("Bereit zum updaten... Klick auf OK")
		elif l=="ita":
			var.set("Pronto per l'aggiornamento ... Premere OK")
		elif l=="rus":
			var.set("Готовность к обновлению... Нажмите ОК")
		elif l=="nor":
			var.set("Klar til å oppdatere... Trykk OK")
		root.update()

	def msg_downloading(self,var,f):
		if l=="eng":
			var.set("(" + str(curNum) + "/" + str(totNum) + ")  " + "Downloading: " + f)
		elif l=="fre":
			var.set("(" + str(curNum) + "/" + str(totNum) + ")  " + "En cours de téléchargement: " + f)
		elif l=="spa":
			var.set("(" + str(curNum) + "/" + str(totNum) + ")  " + "Descargar: " + f)
		elif l=="ger":
			var.set("(" + str(curNum) + "/" + str(totNum) + ")  " + "Downloading: " + f)
		elif l=="ita":
			var.set("(" + str(curNum) + "/" + str(totNum) + ")  " + "Scaricando: " + f)
		elif l=="rus":
			var.set("(" + str(curNum) + "/" + str(totNum) + ")  " + "Загрузка файлов: " + f)
		elif l=="nor":
			var.set("(" + str(curNum) + "/" + str(totNum) + ")  " + "Laster ned: " + f)
		root.update()

	def msg_dlFailed(self,var,f):
		if l=="eng":
			var.set("Download Failed: "+f)
			tkMessageBox.showerror("Error", "Downloading update failed.\n\nFailed update: " + f + "\n\nPlease contact a developer on IRC.") 
		elif l=="fre":
			var.set("Échec au téléchargement: "+f)
			tkMessageBox.showerror("Erreur", "Échec au téléchagement de la mise à jour.\n\nÉchec de la mise à jour: " + f + "\n\nS.v.p contacter un développeur sur IRC.") 
		elif l=="spa":
			var.set("Falló la descarga: "+f)
			tkMessageBox.showerror("Error","Descarga de actualización falló. Error de actualización: " +f+ "\n\nPóngase en contacto con un desarrollador en el IRC.")
		elif l=="ger":
			var.set("Downloading Update fehlgeschlagen. Fehlgeschlagenes Update: "+f)
			tkMessageBox.showerror("Error","Downloading Update fehlgeschlagen. Fehlgeschlagenes Update: "+f+"\n\nBitte kontaktieren Sie einen Developer auf IRC.")
		elif l=="ita":
			var.set("Download non riuscito: "+f)
			tkMessageBox.showerror("Errore","Il download dell'aggiornamento non riuscito. Aggiornamento non riuscito: "+f+"\n\nSi prega di contattare uno sviluppatore su IRC.")
		elif l=="rus":
			var.set("Загрузка прервана: "+f)
			tkMessageBox.showerror("Ошибка","Загрузка файлов прервана. Не удалось обновить: "+f)
		elif l=="nor":
			var.set("Nedlastning feilet: "+f)
			tkMessageBox.showerror("Error","Nedlasting av oppdatering feilet. Feilet oppdatering: "+f)
		root.update()

	def msg_error(self,var,error):
		if l=="eng":
			var.set("Error: " + error)
			tkMessageBox.showerror("Error", error + "\n\nPlease contact a developer on IRC.")
		elif l=="fre":
			var.set("Error: " + error)
			tkMessageBox.showerror("Erreur" "S.v.p contacter un développeur sur IRC.")
		elif l=="spa":
			var.set("Error: " + error)
			tkMessageBox.showerror("Error", error + "\n\nPóngase en contacto con un desarrollador en el IRC.")
		elif l=="ger":
			var.set("Error: " + error)
			tkMessageBox.showerror("Error", error + "\n\nBitte kontaktieren Sie einen Developer auf IRC.")
		elif l=="ita":
			var.set("Error: " + error)
			tkMessageBox.showerror("Errore", error + "\n\nSi prega di contattare uno sviluppatore su IRC.")
		elif l=="rus":
			var.set("Error: " + error)
			tkMessageBox.showerror("Ошибка", error + "\n\nContact Dev on IRC")
		elif l=="nor":
			var.set("Error: " + error)
			tkMessageBox.showerror("Error", error + "\n\nContact Dev on IRC")
		root.update()

	def msg_folder(self,var):
		var.set("Error: Wrong Folder")
		tkMessageBox.showerror("Error", "The updater needs to be located in the Mount & Blade Modules folder. \n\nCurrent Directory: "+myloc)
		root.update()


	def msg_running(self,var):
		if l=="eng":
			var.set("Running...")
		elif l=="fre":
			var.set("En marche...")
		elif l=="spa":
			var.set("Corriendo...")
		elif l=="ger":
			var.set("Läuft...")
		elif l=="ita":
			var.set("Esecuzione di...")
		elif l=="rus":
			var.set("Запуск...")
		elif l=="nor":
			var.set("Kjører...")
		root.update()
			
	def msg_finish(self,var):
		var.set("Updated Successfully")
		root.update()

	def button2Press(self):
		if l=="eng":
			tkMessageBox.showinfo("Nord Invasion Updater", "Welcome to the Nord Invasion updater.\n\nPlease place the updater in the Warband modules folder then hit OK. It will connect to the internet and download all required updates.\n\nFor questions contact Naozumi or NI Dev Team.")
		elif l=="fre":
			tkMessageBox.showinfo("Mise à jour de Nord Invasion", "Bienvenue à la mise à jour de Nord Invasion.\n\nS.v.p placer le logiciel de mise à jour dans le répertoire des modules de Warband et appuyer sur OK. Le logiciel se connectera à Internet et téléchargera les mise à jours nécessaire.\n\nPour des questions, contacter Naozumi ou l'équipe de développement de NI.")
		elif l=="spa":
			tkMessageBox.showinfo("Nord invasión de actualización", "Bienvenido a nord invasión actualizador.\n\nPor favor coloque el actualizador en el partida de guerra módulos carpetas entonces presione ok.\n\nSe Va conectará a la Internet Y descargar todas las actualizaciones necesarias.\n\nPara preguntas contacto Naozumi Y  NI Dev Team.")
		elif l=="ger":
			tkMessageBox.showinfo("Nord Invasion Updater","Willkommen beim Nord - Invasion Updater. Bitte platzieren sie den Updater in das Verzeichnis des Warband Modules und bestätigen sie anschließend mit OK.\n\nDie benötigten Dateien werden daraufhin heruntergeladen.\n\nFür Fragen kontaktieren sie bitte Naozumi oder das Dev Team.")
		elif l=="ita":
			tkMessageBox.showinfo("Nord Invasion Updater","Benvenuti al Nord Invasion updater.\n\nSi prega di inserire il programma di aggiornamento nella cartella moduli Warband  poi premere OK.\n\nSi collegherà ad internet e scaricare tutti gli aggiornamenti necessari.\n\nPer domande contattare Naozumi o NI Dev Team")
		elif l=="rus":
			tkMessageBox.showinfo("NordInvasion Updater","Добро пожаловать в NordInvasion updater.\n\nПожалуйста, переместите Updater в папку Warband Modules, затем нажмите Ок.\n\nПроизойдет подключение к интернету и обновление будет закачано.\n\nПо всем вопросам обращайтесь к Naozuni или к NI Dev Team.")
		elif l=="nor":
			tkMessageBox.showinfo("NordInvasion Updater","Velkommen til Nord Invasion Updater.\n\nVennligst plaser oppdatereren i Warband Modules mappen og trykk OK.\n\nDen vil koble til internet og laste ned alle de nødvendige oppdateringene.\n\nNoen spørsmål vennligst kontakt Naozumi eller NI Dev Team.")
		root.update()

	def setLanguage(self, language, var):
		global l
		l=language
		self.msg_ready(var)


logging.basicConfig(filename='ni_updater.log',level=logging.DEBUG)
l        = "eng"
curNum   = 0
totNum   = 0
dlFailed = False
pathname = os.path.dirname(sys.argv[0])
myloc    = os.path.abspath(pathname)
webloc   = ""
#Hostname
webloc1  = "http://www.hostname.com/mod/"
webfolder = ""
#Updater Version Number
myVersion  = 1.3
root     = Tk()
niup     = niUpdater(root)
root.wm_title("Nord Invasion Updater")
root.mainloop()
