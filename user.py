import json

class User():
	version = 0.1

	def __init__(self, id, data):
		self.id = id
		self.data = data
		print("class user instance create id %d" % self.id)
	
	def get_data(self):
		return self.data
		
	def set_data(self, data):
		self.data = data
		
	def get_id(self):
		return self.id
		
	def set_id(self, id):
		self.id = id
		
	def get_type(self):
		return self.data["type"]
	
	def set_type(self, type):
		self.data["type"] = type
	
	def get_public(self):
		return self.data["public"]
		
	def set_public(self, public_attr):
		self.data["public"] = public_attr 
		
	def get_private(self):
		return self.data["private"]
		
	def set_private(self, private_attr):
		self.data["private"] = private_attr
		
	def get_hosts(self):
		return self.data["hosts"]
		
	def set_hosts(self, hosts):
		self.data["hosts"] = hosts
		
	def get_host_by_seq(self, seq):
		return self.data["hosts"][seq]
	
	def set_host_by_seq(self, seq, host):
		self.data["hosts"].insert(seq, host)
		
MAX_USER_NUM = 10000
class Userlist():
	data = []
	users = [None] * MAX_USER_NUM

	def __init__(self, nm = "Userlist"):
		self.name = nm
		print("class %s instance create instance" % self.name)
			
	def get_data(self):
		return self.data
		
	def add_user(self, id, data):
		self.users.insert(id, User(id, data))
		
	def del_user(self, id):
		del self.users[id]
		
	def get_user(self, id):
		return self.users[id]
		
	def set_user(self, id, data):
		self.users[id] = User(id, data)
	
	def load_users_from_file(self):
		with open("user.json", 'r') as f:
			self.data = json.load(f)
		i = 0
		for udata in self.data:
			self.add_user(i, udata)
			i += 1
	
	def save_users_to_file(self):
		for user in users:
			self.data[user.get_id()] = user.get_data
		with open("user_w.json", 'w') as f:
			f.write(json.dumps(data))
