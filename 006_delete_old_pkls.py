from __future__ import print_function
import os
import re

re_pkl_file = re.compile('^large_heat_load_dict_\d{4}_\d+.pkl$')
backup_cmd='rsync -uv ./*.pkl* /eos/user/l/lhcscrub/bckp_hl_dicts'
git_cmd = "git filter-branch --tree-filter 'rm -f %s' HEAD"
latest_pkls = ['large_heat_load_dict_2015_latest.pkl', 'large_heat_load_dict_2016_latest.pkl']

links = [os.path.basename(os.readlink(file_)) for file_ in latest_pkls]

os.chdir(os.path.dirname(os.path.abspath(__file__)))
files = os.listdir('.')

to_delete = []
for file_ in files:
    if re_pkl_file.match(file_) and file_ not in links:
        to_delete.append(file_)

def delete():
    for file_ in to_delete:
        git = git_cmd % file_
        print(git)
        os.system(git)
        os.system('rm %s' % file_)

def backup():
    print('Backup data to eos!')
    print(backup_cmd)
    os.system(backup_cmd)

if __name__ == '__main__':
    print(links)
    print('Delete the following files from here and from git?')
    for _file in sorted(to_delete):
        print(_file)

    backup()
    inp = raw_input('y/n')
    if inp == 'y':
        delete()

