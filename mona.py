# coding: utf-8
import codecs
import datetime
import json
import os
import socket
import sys
import threading
import time
import tkinter as tk
import tkinter.messagebox
import tkinter.scrolledtext as st
import xml.etree.ElementTree as ET

def connect():
	global flag_socket
	s.connect(('monachat.dyndns.org',9095))
	flag_socket=True

	chatlog.writeLog(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	s.sendall('MojaChat\0'.encode())
	read=s.recv(1024)
	if read:
		readHandler(read.decode())
	td_sock.start()
	td_ping.start()


def login():
	connect()
	s.sendall('<ENTER room="/MONA8094" name="monapy" attrib="no"/>\0'.encode())

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
		#COUNT - ROOM
		#ROOM - USER
		#UINFO
		#EXIT
		#ENTER
		#COM
		#SET
		#CONNECT
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
			chatlog.writeLog('----------------------\n')
			for e in msg_root:
				if e.tag=='USER':
					roominfo.data['user'][e.get('id')]=e.attrib
					#save trip
					if not e.get('ihash') in trip: trip[e.get('ihash')]=[e.get('name')]
					trip[e.get('ihash')]=list(set(trip[e.get('ihash')]+[e.get('name')]))
		elif msg_root.tag=='UINFO':
			roominfo.data['user'][msg_root.get('id')]=msg_root.attrib
		elif msg_root.tag=='EXIT':
			chat={}
			chat['time']=datetime.datetime.now()
			chat.update(msg_root.attrib)
			if chat['id'] in roominfo.data['user']:
				chat.update(roominfo.data['user'][chat['id']])
				chatlog.writeLog('[{time:%H:%M:%S}]<<({id}){name}◇{ihash}\n'.format(**chat))
			else:
				chatlog.writeLog('<<({id})\n'.format(**chat))

			roominfo.data['user'].pop(msg_root.get('id'),None)
		elif msg_root.tag=='ENTER':
			#自分が入室するとき
			if msg_root.get('id')==login_id:
				chatlog.writeLog('---- Room{0} ----\n'.format(roominfo.data['enter']))
			roominfo.data['user'][msg_root.get('id')]={'name':'','ihash':''}
			roominfo.data['user'][msg_root.get('id')].update(msg_root.attrib)

			chat={}
			chat['time']=datetime.datetime.now()
			chat.update(msg_root.attrib)
			if chat['id'] in roominfo.data['user']:
				chat.update(roominfo.data['user'][chat['id']])
				chatlog.writeLog('[{time:%H:%M:%S}]>>({id}){name}◇{ihash}\n'.format(**chat))
			else:
				chatlog.writeLog('>>({id})\n'.format(**chat))
			try:
				if not msg_root.get('ihash') in trip: trip[msg_root.get('ihash')]=[]
				trip[msg_root.get('ihash')]=list(set(trip[msg_root.get('ihash')]+[msg_root.get('name')]))
			except:pass
		elif msg_root.tag=='COM':
			com={}
			com['time']=datetime.datetime.now()
			com.update(msg_root.attrib)
			com.update(roominfo.data['user'][com['id']])
			if 'style' in com:
				if com['style']=='2':
					com['cmt']='.｡o('+com['cmt']+')'
				elif com['style']=='3':
					com['cmt']='<<'+com['cmt']+'>>'
			chatlog.writeLog('[{time:%H:%M:%S}]{name}◇{ihash}:{cmt}\n'.format(**com))
		elif msg_root.tag=='SET':
			roominfo.data['user'][msg_root.get('id')].update(msg_root.attrib)
			roominfo.refresh()
		elif msg_root.tag=='CONNECT':
			login_id=msg_root.get('id')
			print(login_id)

def writeHandler(write):
	global login_data
	send_msg=None
	if write=='': return
	if write[0]!='/':
		send_msg=ET.tostring(ET.Element('COM',{'cmt':write})).decode()
	else:
		com_list=write.split()
		if com_list[0]=='/room':
			s.sendall('<EXIT />\0'.encode())
			roominfo.data['enter']='/'+com_list[1] if len(com_list)>1 else ''
			room={'room':'/MONA8094'+roominfo.data['enter']}
			room.update(login_data)
			send_msg=ET.tostring(ET.Element('ENTER',room)).decode()

			roominfo.data['user']={}
			roominfo.data['room']={}
		elif com_list[0]=='/set':
			com={}
			for prop in com_list[1:]:
				key,value=prop.split(':')
				com[key]=value
				login_data[key]=value
			send_msg=ET.tostring(ET.Element('SET',com)).decode()
		elif com_list[0]=='/ig':
			pass
		elif com_list[0]=='/enter':
			roominfo.data['enter']='/'+com_list[1] if len(com_list)>1 else ''
			room={'room':'/MONA8094'+roominfo.data['enter']}
			room.update(login_data)
			send_msg=ET.tostring(ET.Element('ENTER',room)).decode()
		elif com_list[0]=='/exit':
			s.sendall('<EXIT />\0'.encode())
			roominfo.data['user']={}
			roominfo.data['room']={}
		elif com_list[0]=='/login':
			login()
		elif com_list[0]=='/quit':
			quit()
		elif com_list[0]=='/connect':
			connect()
		elif com_list[0]=='/config':
			if len(com_list)<2:
				print(config)
			else:
				k,v=com_list[1].split(':')
				if k=='save': config[v]=login_data
				if k=='load': login_data=config[v]; writeHandler('/room {0}'.format(roominfo.data['enter'][1:]))
		elif com_list[0]=='/wclose':
			if com_list[1]=='roominfo': roominfo.frame.pack_forget()
			if com_list[1]=='chatlog': chatlog.frame.pack_forget()
			if com_list[1]=='netlog': netlog.frame.pack_forget()
		elif com_list[0]=='/wopen':
			if com_list[1]=='roominfo': roominfo.frame.pack(fill='both',expand=True)
			if com_list[1]=='chatlog': chatlog.frame.pack(side="left",fill='both',expand=True)
			if com_list[1]=='netlog': netlog.frame.pack(side="left",fill='both',expand=True)
	if send_msg!=None:
		s.sendall((send_msg+'\0').encode())

def readSocket():
	global flag_socket
	while flag_socket:
		read=s.recv(16384)#8192
		if read:
			readHandler(read.decode())
		else:
			time.sleep(0.1)
def writeSocket(text):
	pass

def quit():
	global flag_socket
	if flag_socket:
		flag_socket=False
		#save chatlog
		chatlog.save()
		#save config and trip
		print(config,trip)
		with open('./data/config.json','bw') as f:
			f.write(json.dumps(config,ensure_ascii=False,indent=2,sort_keys=True).encode())
		with open('./data/trip.json','bw') as f:
			f.write(json.dumps(trip,ensure_ascii=False,indent=2).encode())
		td_sock.join(timeout=0.1)
		s.shutdown(socket.SHUT_RDWR)
		s.close()
	root.destroy()

class EntryBox:
	def __init__(self,parent):
		self.entry=tk.Entry(parent,width=200,font='Arial 14')
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
		editmenu.add_command(label="login",command=self.login)

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
	def login(self):
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
		self.text=tk.Text(self.frame,bd=0,width=5,font='Arial 10')
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
		self.text.yview(tk.END)

	def save(self):
		with open('./data/chatlog.txt','a',encoding='utf-8') as f:
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
		self.text=tk.Text(self.frame,bd=0,width=5,font="Arial 10")
		self.text.config(state=tk.DISABLED)
		#scrollbar
		self.scrollbar=tk.Scrollbar(self.frame,command=self.text.yview,cursor="star")
		self.text['yscrollcommand']=self.scrollbar.set
		#place
		self.frame.pack(side="left",fill='both',expand=True)#self.frame.place(x=0,y=0,width=320,height=480)
		self.label.pack()
		self.scrollbar.pack(side="right",fill=tk.Y,)
		self.text.pack(side="left",fill=tk.BOTH,expand=True)
		self.frame.pack_forget()
	def writeLog(self,string):
		self.text.config(state=tk.NORMAL)
		self.text.insert('end',string)
		self.text.config(state=tk.DISABLED)
		self.text.yview(tk.END)
	def save(self):
		with open('./data/netlog.txt','a') as f:
			self.text.config(state=tk.NORMAL)
			f.write(self.text.get('0.0',tk.END))
			self.text.delete('0.0',tk.END)
			self.text.config(state=tk.DISABLED)			

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
		self.text=tk.Text(self.frame,bd=0,width=10,font='Arial 10')
		self.text.insert('end','room info')
		self.text.config(state=tk.DISABLED)
		#scrollbar
		self.scrollbar=tk.Scrollbar(self.frame,command=self.text.yview,cursor='star')
		self.text['yscrollcommand']=self.scrollbar.set
		#place
		self.label.pack(fill='x')
		#self.scrollbar.pack(side='right',fill='y')
		self.text.pack(fill='both',expand=True)
		self.frame.pack(fill='both',expand=True)

	def refresh(self):
		self.text.config(state=tk.NORMAL)
		self.text.delete('0.0',tk.END)
		#write roominfo
		self.text.insert(tk.END,'HERE\nRoom{n}({c})\n'.format(**self.data['here']))
		self.text.insert(tk.END,'ROOM\n')
		for k,v in self.data['room'].items():
			self.text.insert(tk.END,'Room{0}({1})\t'.format(k,v))
		self.text.insert(tk.END,'\nUSER\n')
		for k,v in self.data['user'].items():
			if not 'name' in v: v['name']='hoge'
			if not 'stat' in v: v['stat']='hoge'
			if not 'ihash' in v: v['ihash']='hoge'
			if not 'type' in v: v['type']='hoge'
			self.text.insert(tk.END,'({id}){name}◇{ihash}:{stat}[{type}]\n'.format(**v))
		self.text.config(state=tk.DISABLED)
if __name__ == '__main__':
	#data
	roominfo=RoomInfo()
	login_id=0
	login_data={'type':'kyaku','name':'nanasi','x':'80','y':'275','r':'50','g':'50','b':'100','scl':'100','stat':'monapy'}

	if not os.path.exists('./data'):
		os.makedirs('./data')
	try:
		with open('./data/config.json',encoding='utf-8') as f:
			config=json.loads(f.read(),'utf-8')
	except:
		config={}
	try:
		with open('./data/trip.json',encoding='utf-8') as f:
			trip=json.loads(f.read(),'utf-8')
	except:
		trip={}
	if 'default' in config:
		login_data=config['default']
	#junbi
	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	td_sock=threading.Thread(target=readSocket,daemon=True)
	td_ping=threading.Thread(target=ping,daemon=True)
	flag_socket=False

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
