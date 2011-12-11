import subprocess

def execute_mysql_script(filename):
    fd = open(filename)
    cmd = 'mysql -uroot -proot'
    ret = subprocess.call(cmd.split(' '), stdin=fd)
    fd.close()
    return ret

def setup_db():
    execute_mysql_script('tables.sql')
    execute_mysql_script('views.sql')

