# Created by @akusio_RR
# MIT License

import ui
import keyboard
import clipboard
import os
from functools import cmp_to_key

FILENAME = "history.txt"

def get_last_word(text:str):
	
	separators = [' ', '.', '\t', '(', '\n', ':', '[', '{', ';', ',', '!', '?', '=', '@', '+', '/', '<', ']', '}', ')', '>', '&', '~']
	
	for i in separators:
		ret = text.rfind(i)
		
		if ret != -1:
			return text[ret+1:]
		
	return None





def save_history(arr, path):
	
	a = open(path, 'w')
	
	ret =	[]
	
	for i in arr:
		ret.append(i + '\n')
	
	a.writelines(ret)
	
	a.close()
	


	
def load_history(path):
	
	a = open(path, 'r')
	
	b = a.readlines()
	
	a.close()
	
	ret = []
	
	for i in b:
		ret.append(CandidateString(i.replace('\n', '')))
		
	return ret




class CandidateString(str):
	def __new__(cls, val):
		self = super().__new__(cls, val)
		self.priority = 0
		return self




class CandidateView(ui.View):
	def __init__(self, *args, **kargs):
		super().__init__(self, *args, **kargs)
		
		self.scroll_view = ui.ScrollView()
		self.edit_button = ui.Button()
		self.paste_button = ui.Button()
		self.all_candidate = []
		self.current_str = ''
		self.is_editing = False
		self.min_priority = -1
		self.file_name = FILENAME
		
		self.scroll_view.border_width = 0
		self.scroll_view.frame = (30+2 ,0 ,self.width, self.height)
		self.scroll_view.width = 6
		self.scroll_view.content_size = (100, 30)
		self.scroll_view.always_bounce_vertical = False
		self.scroll_view.shows_horizontal_scroll_indicator = False
		self.scroll_view.tint_color = '#ffffff'
		self.scroll_view.flex = 'WH'
		self.add_subview(self.scroll_view)
		
		self.edit_button.frame = (40,0,30,30)
		self.edit_button.flex = 'L'
		self.edit_button.image = ui.Image('typb:Edit')
		self.edit_button.action = self.edit_button_action
		self.edit_button.background_color = None
		self.edit_button.border_color = '#ff5858'
		self.edit_button.border_width = 2
		self.edit_button.corner_radius = 5
		self.add_subview(self.edit_button)
		
		self.paste_button.frame = (0,0,30,30)
		self.paste_button.flex = 'R'
		self.paste_button.image = ui.Image('iob:clipboard_24')
		self.paste_button.background_color = None
		self.paste_button.border_color = '#40a8ff'
		self.paste_button.border_width = 2
		self.paste_button.corner_radius = 5
		self.paste_button.action = self.paste_button_action
		self.add_subview(self.paste_button)
		
		self.is_suspend_switch = ui.Switch()
		self.is_suspend_switch.frame = (0, 32, 50, 50)
		self.add_subview(self.is_suspend_switch)
		
		self.tint_color = '#dcdcdc'
		self.background_color = '#3c3a39'
		
		self.all_candidate = load_history(FILENAME)
		
		
		
	def kb_should_insert(self, text=''):
		#self.insert_pair(text)
		self.update_current_str(text)
		return True
		
		
		
	def kb_should_delete(self):
		#self.delete_pair()
		self.update_current_str('')
		return True
		
		
	def kb_text_changed(self):
		self.candidate()
		
		
	def insert_pair(self, text):
		#self.label.text = text
		pair = ['\'', '[', '"', '(', '{']
		insert = ['\'', ']', '"', ')', '}']
		for i in range(len(pair)):
			if text == pair[i]:
				keyboard.insert_text(insert[i])
				keyboard.move_cursor(-1)
	
	
	def delete_pair(self):
		pair = ['\'', '[', '"', '(', '{']
		dlt  = ['\'', ']', '"', ')', '}']
		text = keyboard.get_input_context()
		
		if(text[1] is None) or (text[0] is None):
			return
			
		if len(text[1]) == 0:
			return 
		
		for i in range(len(pair)):
			if text[1][0] == dlt[i] and text[0][-1] == pair[i]:
				keyboard.move_cursor(1)
				keyboard.backspace(1)
	
	
	def cmp_cstring(self, a, b):
		
		if not a.startswith(self.current_str) and b.startswith(self.current_str.lower()):
			return 1
		
		elif a.startswith(self.current_str) and not b.startswith(self.current_str.lower()):
			return -1
			
		elif a.priority > b.priority:
			return 1
			
		elif a.priority < b.priority:
			return -1
			
		else:
			return 0
	
	
	def update_autocomplete(self, arr):
		testlist = arr
		#testlist.sort(key=lambda x:x.priority)
		testlist.sort(key=cmp_to_key(self.cmp_cstring))
		
		for i in self.scroll_view.subviews:
			self.remove_subview(i)
		
		x = 0
		for i in testlist:
			button = ui.Button()
			button.title = i
			button.font = ('Menlo', 13)
			button.border_width = 0
			button.corner_radius = 5
			button.background_color = '#7f7f7f'
			button.size_to_fit()
			button.x = x
			button.y = 1
			button.width += 4
			button.action = self.button_action
			
			self.scroll_view.add_subview(button)
			x += button.width + 4
		
		self.scroll_view.content_size = (x + 10, 30)
		pass
		
	
	def update_current_str(self, text):
		
		separators = [' ', '.', '\t', '(', '\n', ':', '[', '{', ';', ',', '!', '?', '=', '@', '+', '/', '<', ']', '}', ')', '>', '&', '~']
		
		if text == '':
			
			self.current_str = self.current_str[:-1]
		
		elif text in separators:
			
			self.add_candidate(self.current_str)
			self.current_str = ''
			
		else:
			
			self.current_str += text
			
	
	def candidate(self):
		
		if self.current_str == '':
			return
		
		ret = []
		
		for i in self.all_candidate:
			
			lc = self.current_str.lower()
			ilc = i.lower()
			
			#if ilc.startswith(lc):
			if lc in ilc:
				
				ret.append(i)
				
		self.update_autocomplete(ret)
	
	
	def add_candidate(self, text):
		
		if self.is_suspend_switch.value:
			return
		
		text = CandidateString(text)
		if text not in self.all_candidate and len(text) > 3 and not text.startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '"', '\'', '-')):
			
			self.all_candidate.append(text)
			save_history(self.all_candidate, FILENAME)
			
	
	def button_action(self, sender):
		
		if self.is_editing:
			
			self.all_candidate.remove(sender.title)
			self.edit_button_action(None)
			self.update_autocomplete([])
			self.current_str = ''
			save_history(self.all_candidate, FILENAME)
			
		else:
		
			keyboard.backspace(len(self.current_str))
			keyboard.insert_text(sender.title)
			
			for i in self.all_candidate:
				if i == sender.title:
					i.priority = self.min_priority
					self.min_priority -= 1
					break
			
			self.current_str = ''


	def edit_button_action(self, sender):
		
		if self.is_editing:
			
			self.edit_button.background_color = None
			self.edit_button.border_color = '#ff5858'
			self.edit_button.border_width = 2
			self.edit_button.corner_radius = 5
			
			for i in self.scroll_view.subviews:
				i.background_color = '#7f7f7f'
			
			self.is_editing = False
		
		else:
			
			self.edit_button.background_color = '#ff5858'
			
			for i in self.scroll_view.subviews:
				i.background_color = '#ff5858'
			
			self.is_editing = True
			
		
	def paste_button_action(self, sender):
		keyboard.insert_text(clipboard.get())


def main():
	if not os.access(FILENAME, os.F_OK):
		open(FILENAME, 'wb').close()
		
	v = CandidateView()
	
	if keyboard.is_keyboard():
		v.name = 'CandidateView'
		keyboard.set_view(v, '')
		
	else:
		v.name = 'Keyboard Preview'
		v.frame = (0, 0, 320, 220)
		v.present('sheet')
		

if __name__ == '__main__':
	main()
