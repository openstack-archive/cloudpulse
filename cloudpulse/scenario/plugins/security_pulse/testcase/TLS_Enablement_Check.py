import os
import ConfigParser
import pwd
import stat
from stat import *

class tls_enable_check(object):
	def __init__(self):
		pass

	def read_tls_config(self,config):
		try :
			config.get("ldap","use_tls")
		except ConfigParser.NoOptionError :
			print "Fail - use_tls option is not enabled"
			return
		else :
			use_tls = config.get("ldap","use_tls")
			if use_tls == 'false':
				print "Fail - use_tls option is enabled with 'false' value"
				return
			elif use_tls == 'true':
				ca_dir = None
				try:
					ca_dir = config.get("ldap","tls_cacertdir")
				except ConfigParser.NoOptionError:
					try:
						tls_ca_file = config.get("ldap","tls_cacertfile")
						ca_dir = tls_ca_file[:tls_ca_file.rindex('/')]
					except ConfigParser.NoOptionError:
						print "Fail - Both 'tls_ca_dir' and 'tls_ca_file' are not defined"	
						return
				if not ca_dir:
					print "Fail - Both 'tls_ca_dir' and 'tls_ca_file' are not defined"	
					return
				else:
					for dirName, subdirList, fileList in os.walk(ca_dir):
						os.chdir(dirName)
						for f1 in fileList:
							st = os.stat(f1)
							user = pwd.getpwuid(st[ST_UID])[0]
							group = pwd.getpwuid(st[ST_GID])[0]
							mode = oct(stat.S_IMODE(st[stat.ST_MODE]))
							if user != 'keystone' or group != 'keystone':
								print "Fail - Certificate file directory user/group permission are user=%s, group=%s " % (user,group)
								return
				print "Success - TLS is enabled and the Certificate file permissions are 'keystone'"
				return

if __name__ == '__main__':
	tls_enable_check_obj = tls_enable_check()
	config = ConfigParser.ConfigParser()
	config.read("/etc/keystone/keystone.conf")
	tls_enable_check_obj.read_tls_config(config)
