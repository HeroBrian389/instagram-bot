from functionality import export
import os

filename = 'following_all.csv'

os.system(f'rm {filename}')

e = export(filename)

e.dump_all('following_users')

os.system(f'open {filename} -a Microsoft\ Excel')