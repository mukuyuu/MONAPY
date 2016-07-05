# coding: utf-8
import codecs
import socket
import sys
import threading
import time
import tkinter as tk
import tkinter.messagebox
import tkinter.scrolledtext as st
import xml.etree.ElementTree as ET

def login():
	global flag_socket
	s.connect(('monachat.dyndns.org',9095))
	flag_socket=True
	td_sock.start()

	s.sendall("MojaChat\0".encode())
	read=s.recv(4096)
	if read:
		f_netlog.write(read)
		readHandler(read.decode())
	chatlog.writeLog('<---- Room{0} ---->\n'.format('/MONA8094'))
	s.sendall('<ENTER room="/MONA8094" name="bot" attrib="no"/>\0'.encode())

	td_ping.start()

def ping():
	while flag_socket:
		time.sleep(15)
		s.sendall('<NOP />\0'.encode())

def readHandler(read):
	global login_id
	msg_list=read.rstrip('\0').split('\0')
	for line in msg_list:
		netlog.writeLog(line+'\n')
	for i in range(len(msg_list)):
		try:
			msg_root=ET.fromstring(msg_list[i])
		except:print('not proper xml:',msg_list[i]);continue
		if msg_root.tag=='COUNT':
			if msg_root.get('c')!=None and int(msg_root.get('c'))>0:
				roominfo.data['here'].update(msg_root.attrib)
			for e in msg_root:
				if e.tag=='ROOM':	
					roominfo.data['room'][e.get('n')]=e.get('c')
					if not int(e.get('c'))>0:
						del roominfo.data['room'][e.get('n')]
			roominfo.refresh()
		elif msg_root.tag=='ROOM':
			chatlog.writeLog('----------------\n')
			for e in msg_root:
				if e.tag=='USER':
					roominfo.data['user'][e.get('id')]=e.attrib
		elif msg_root.tag=='EXIT':
			roominfo.data['user'].pop(msg_root.get('id'),None)
			chatlog.writeLog('<<({id})\n'.format(**msg_root.attrib))
		elif msg_root.tag=='ENTER':
			if msg_root.get('id')==login_id:
				chatlog.writeLog('---- Room{0} ----\n'.format(roominfo.data['enter']))

			roominfo.data['user'][msg_root.get('id')]=msg_root.attrib
			chatlog.writeLog('>>({id})\n'.format(**msg_root.attrib))
		elif msg_root.tag=='COM':
			chatlog.writeLog('({id}):{cmt}\n'.format(**msg_root.attrib))
		elif msg_root.tag=='SET':
			roominfo.data['user'][msg_root.get('id')].update(msg_root.attrib)
			roominfo.refresh()
		elif msg_root.tag=='CONNECT':
			login_id=msg_root.get('id')
			print(login_id)

def writeHandler(write):
	send_msg=None
	if write[0]!='/':
		send_msg=ET.tostring(ET.Element('COM',{'cmt':write})).decode()
	elif write.startswith('/cmt '):
		com=ET.Element('COM',{'cmt':write.lstrip('/cmt ')})
		send_msg=ET.tostring(com).decode()
	elif write.startswith('/enter '):
		s.sendall('<EXIT />\0'.encode())
		roominfo.data['enter']=write[len('/enter '):]
		room={'room':'/MONA8094'+roominfo.data['enter']}
		room.update(login_data)
		send_msg=ET.tostring(ET.Element('ENTER',room)).decode()

		roominfo.data['user']={}
		roominfo.data['room']={}
	elif write.startswith('/set '):
		props=write[len('/set '):].split()
		com={}
		for prop in props:
			key,value=prop.split(':')
			com[key]=value
			login_data[key]=value
		send_msg=ET.tostring(ET.Element('SET',com)).decode()
	elif write.startswith('/connect'):
		login()
	if send_msg!=None:
		s.sendall((send_msg+'\0').encode())

def readSocket():
	global flag_socket
	while flag_socket:
		read=s.recv(8192)
		if read:
			f_netlog.write(read)
			readHandler(read.decode())
		else:
			time.sleep(0.1)
def writeSocket(text):
	pass

def quit():
	global flag_socket
	if flag_socket:
		flag_socket=False
		print('0',flag_socket)
		td_sock.join(timeout=0.1)
		s.shutdown(socket.SHUT_RDWR)
		s.close()
	root.destroy()

class EntryBox:
	def __init__(self,parent):
		self.entry=tk.Entry(parent,width=200,font='Arial 12')
		self.entry.bind("<Return>",self.send)
		self.entry.pack(side="bottom",fill='both')
	def send(self,event):
		text=self.entry.get()
		self.entry.delete(first=0,last=tk.END)
		writeHandler(text)

class Menu:
	def __init__(self,master):
		menu=tk.Menu(master)
		master.config(menu=menu)

		filemenu=tk.Menu(menu)
		filemenu.add_command(label="Save log",command=self.saveLog)
		filemenu.add_separator()
		filemenu.add_command(label="Close",command=quit)

		editmenu=tk.Menu(menu)
		editmenu.add_command(label="connect",command=self.connect)

		viewmenu=tk.Menu(menu)
		viewmenu.add_command(label="view network",command=self.showNetwork)

		helpmenu=tk.Menu(menu)
		helpmenu.add_command(label="help",command=self.help)
		#place
		menu.add_cascade(label="File",menu=filemenu)
		menu.add_cascade(label="Edit",menu=editmenu)
		menu.add_cascade(label="View",menu=viewmenu)
		menu.add_cascade(label="Help",menu=helpmenu)
	def saveLog(self):
		print("save chatlog")
		chatlog.save()
	def connect(self):
		print("Tring to connect")
		login()
	def showNetwork(self):
		print("coming soon...")
	def help(self):
		print("coming soon...")

class ChatLog:
	def __init__(self,parent):
		#frame
		self.frame=tk.Frame(parent)
		self.label=tk.Label(self.frame,text='Chat Log')
		#chatlog
		self.text=tk.Text(self.frame,bd=0,width=5,font='Arial')
		self.text.config(state=tk.DISABLED)
		#scrollbar
		self.scrollbar=tk.Scrollbar(self.frame,command=self.text.yview,cursor='star')
		self.text['yscrollcommand']=self.scrollbar.set
		#place
		self.frame.pack(side='left',fill='both',expand=True)
		self.label.pack()
		self.scrollbar.pack(side='right',fill=tk.Y)
		self.text.pack(side='left',fill=tk.BOTH,expand=True)

	def writeLog(self,string):
		self.text.config(state=tk.NORMAL)
		self.text.insert('end',string)
		self.text.config(state=tk.DISABLED)

	def save(self):
		f=open('chatlog.txt','a')
		self.text.config(state=tk.NORMAL)
		f.write(self.text.get('0.0',tk.END))
		self.text.delete('0.0',tk.END)
		self.text.config(state=tk.DISABLED)

class NetworkLog:
	def __init__(self,parent):
		#frame
		self.frame=tk.Frame(parent)#self.frame=tk.Frame(parent,width=320,height=480)
		self.label=tk.Label(self.frame,text='Network Log')
		#netlog
		self.text=tk.Text(self.frame,bd=0,width=5,font="Arial")
		self.text.config(state=tk.DISABLED)
		#scrollbar
		self.scrollbar=tk.Scrollbar(self.frame,command=self.text.yview,cursor="star")
		self.text['yscrollcommand']=self.scrollbar.set
		#place
		self.frame.pack(side="left",fill='both',expand=True)#self.frame.place(x=0,y=0,width=320,height=480)
		self.label.pack()
		self.scrollbar.pack(side="right",fill=tk.Y,)
		self.text.pack(side="left",fill=tk.BOTH,expand=True)
		#self.frame.pack_forget()
	def writeLog(self,string):
		self.text.config(state=tk.NORMAL)
		self.text.insert('end',string)
		self.text.config(state=tk.DISABLED)
		self.text.yview(tk.END)

class RoomInfo:
	def __init__(self):
		self.data={}
		self.data['enter']=''
		self.data['here']={}
		self.data['room']={}
		self.data['user']={}

	def makeDisp(self,parent):
		#frame
		self.frame=tk.Frame(parent)
		self.label=tk.Label(self.frame,text='Room Info',width=30)
		#roominfo
		self.text=tk.Text(self.frame,bd=0,width=10,font='Arial')
		self.text.insert('end','room info')
		self.text.config(state=tk.DISABLED)
		#place
		self.label.pack(fill='x')
		self.text.pack(fill='both',expand=True)
		self.frame.pack(fill='both',expand=True)
	def refresh(self):
		self.text.config(state=tk.NORMAL)
		self.text.delete('0.0',tk.END)
		for k in ['here','room','user']:
			self.text.insert(tk.END,str(self.data[k])+'\n')
		self.text.config(state=tk.DISABLED)
if __name__ == '__main__':
	#data
	roominfo=RoomInfo()
	login_id=0
	login_data={'type':'kyaku','name':'nanasi','x':'80','y':'275','r':'50','g':'50','b':'100','scl':'100','stat':'monapy'}
	#junbi
	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	td_sock=threading.Thread(target=readSocket,daemon=True)
	td_ping=threading.Thread(target=ping,daemon=True)
	flag_socket=False
	f_netlog=open('netlog.txt','ba')

	#window
	root=tk.Tk()
	root.title('★MONAPY★')
	root.geometry("640x480")
	root.config(bg='#d0d0f3')
	root.protocol("WM_DELETE_WINDOW",quit)
	#widget
	menu=Menu(root)
	entrybox=EntryBox(root)
	fm0=tk.Frame(root)
	chatlog=ChatLog(fm0)
	netlog=NetworkLog(fm0)
	roominfo.makeDisp(fm0)
	#pack#fm1.pack(side='left',fill='both',expand=True)#fm1.place(x=320,y=0,width=320,height=480)
	fm0.pack(fill=tk.BOTH,expand=True)

	root.mainloop()