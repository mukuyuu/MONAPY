# coding: utf-8
from PIL import Image,ImageTk
import time
import tkinter as tk


class Chara:
	canvas=None
	def __init__(self,**set_data):
		data={'name':'hoge','ihash':'hoge','stat':'hoge','type':'hoge','trip':'',
			'x':200,'y':200,'r':250,'g':250,'b':250,'scl':100}
		data.update(set_data)
		self.data=data
		fchar=tk.Frame()
		#img
		try:
			image=Image.open('./character/{0}.png'.format(data['type']))
		except:
			image=Image.open('./character/nochara.png')
		for x in range(image.size[0]):
			for y in range(image.size[1]):
				r,g,b,a=image.getpixel((x,y))
				if a==255:
					image.putpixel((x,y),(int(data['r']*r/255),int(data['g']*g/255),int(data['b']*b/255)))
		self.image=image if data['scl']==100 else image.transpose(Image.FLIP_LEFT_RIGHT)
		self.img=ImageTk.PhotoImage(image)

		self.id=Chara.canvas.create_image(data['x'],data['y'],anchor=tk.CENTER,image=self.img)
		self.textid=Chara.canvas.create_text(data['x'],data['y']+64,anchor=tk.N,text='bot楽しいよ！',justify='center')
		self.setText()
	def setText(self):
		Chara.canvas.itemconfig(self.textid,text='{name}\n◇{ihash}\n{stat}'.format(**self.data))
	def setChara(self,chara='abogado',r=0,g=0,b=0):
		try:
			image=Image.open('./character/{0}.png'.format(data['type']))
		except:
			image=Image.open('./character/nochara.png')
		for x in range(image.size[0]):
			for y in range(image.size[1]):
				r,g,b,a=image.getpixel((x,y))
				if a==255:
					image.putpixel((x,y),(int(data['r']*r/255),int(data['g']*g/255),int(data['b']*b/255)))
		self.image=image if data['scl']==100 else image.transpose(Image.FLIP_LEFT_RIGHT)
		self.img=ImageTk.PhotoImage(image)
	def setXY(self,x,y):
		Chara.canvas.move(self.id,x-self.data['x'],y-self.data['y'])
		Chara.canvas.move(self.textid,x-self.data['x'],y-self.data['y'])
		self.data['x'],self.data['y']=x,y
	def setStat(self,text):
		self.data['stat']=text
		self.setText()
	def exit(self):
		Chara.canvas.delete(self.id)
		Chara.canvas.delete(self.textid)
		self.image=None
		self.img=None
		self.id=None
		self.textid=None
		self.data=None

class MyChara(Chara):
	def __init__(self,**set_data):
		Chara.__init__(self,**set_data)

		Chara.canvas.tag_bind(self.id,'<Button1-Motion>',self.drag)
		Chara.canvas.tag_bind(self.id,'<1>',self.click)
	def click(self,event):
		self.data['scl']=-self.data['scl']
		Chara.canvas.itemconfig(self.id,image=self.img)
		Chara.canvas.itemconfig(self.textid,text='{name}\n◇{ihash}\n{stat}\n{scl}'.format(**self.data))
		#self.img=self.img.transpose(Image.FLIP_LEFT_RIGHT)
	def drag(self,event):
		x,y=event.x,event.y
		Chara.canvas.move(self.id,x-self.data['x'],y-self.data['y'])
		Chara.canvas.move(self.textid,x-self.data['x'],y-self.data['y'])
		self.data['x'],self.data['y']=x,y

class Disp(tk.Frame):
	def __init__(self,master=None):
		tk.Frame.__init__(self,master)
		self.master.title('Room Display')
		self.master.geometry('+20+20')
		self.cvs=tk.Canvas(self,width=480,height=320,bd=2)#,bg='midnightblue'
		self.cvs.pack(fill=tk.BOTH,expand=True)

		Chara.canvas=self.cvs

		self.counter=0
		self.chara_dict={}
	def createChara(self,set_data={}):
		for key in ['x','y','scl','r','g','b']:
			if key in set_data:
				set_data[key]=int(set_data[key])
				if key in ['r','g','b']:
					set_data[key]=int(set_data[key]*2.55)
		self.chara_dict[set_data['id']]=Chara(**set_data)
	def createMyChara(self,set_data={}):
		self.chara_dict[set_data['id']]=MyChara(**set_data)
	def deleteChara(self,userid):
		if userid not in self.chara_dict: return
		self.chara_dict[userid].exit()
		self.chara_dict.pop(userid)
	def handleCom(self,**com_data):
		
		pass
	def handleSet(self,**set_data):
		if 'stat' in set_data:
			self.chara_dict[set_data['id']].setStat(set_data['stat'])
		if 'x' in set_data and 'y' in set_data:
			self.chara_dict[set_data['id']].setXY(int(set_data['x']),int(set_data['y']))
	def refresh(self,**users):
		for i in list(self.chara_dict.keys()):
			self.deleteChara(i)

"""
somewidget.winfo_width()
somewidget.winfo_height()
root.bind('<Configure>',change_size)

"""