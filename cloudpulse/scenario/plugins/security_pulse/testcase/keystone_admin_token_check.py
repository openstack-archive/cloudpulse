import os
import ConfigParser

class keystone_admin_token_check(object):
	def __init__(self):
		pass

	def keystone_admin_token_test(self):
		ks_conf_file = "/etc/keystone/keystone.conf"
		result = []
		config = ConfigParser.ConfigParser()
		if os.path.exists(ks_conf_file):
			try:
				config.read(ks_conf_file)
			except Exception:
				result.append("admin_token - keystone.conf not found - Fail")
			else:
				try :
					config.get("DEFAULT","admin_token")
				except ConfigParser.NoOptionError,e:
					result.append("admin_token - Not defined - Pass")
				else:
					result.append("admin_token - Defined - Fail")
		else:
			result.append("admin_token - keystone.conf not found - Fail")

		ks_paste_conf_file = "/etc/keystone/keystone-paste.ini"
		if os.path.exists(ks_paste_conf_file):
			try:
				config.read(ks_paste_conf_file)
			except Exception:
				result.append("admin_auth_token - keystone-paste.ini not found - Pass")
			else:
				try :
					config.get("filter:admin_token_auth","paste.filter_factory")
				except (ConfigParser.NoOptionError,ConfigParser.NoSectionError) as e:
					result.append("admin_auth_token - Not defined - Pass")
				else:
					option = config.get("filter:admin_token_auth","paste.filter_factory")
					if "AdminTokenAuthMiddleware" in option:
						result.append("admin_auth_token - Defined - Fail")
					else:
						result.append("admin_auth_token - Not Defined - Pass")
		else:
			result.append("admin_auth_token - keystone-paste.ini not found - Pass")
		print result

if __name__ == '__main__':
	keystone_admin_token_check_obj = keystone_admin_token_check()
	keystone_admin_token_check_obj.keystone_admin_token_test()
