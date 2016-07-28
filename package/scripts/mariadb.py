import os
from time import sleep
from resource_management import *

class MariadbMaster(Script):
    mariadb_packages=['MariaDB-server','MariaDB-client','galera']
    
    def install(self, env):
        #delete mysql-server
        Execute('rpm -e mysql-server', ignore_failures=True)
        
        import params
        self.install_packages(env)
        print 'install mariadb'
        if self.mariadb_packages is not None and len(self.mariadb_packages):
            for pack in self.mariadb_packages:
                Package(pack)
                
        #configure cluster
        Execute('service mysql start')
        sleep(10)
        
        Execute("/usr/bin/mysqladmin -u root password 'dbpass'",ignore_failures=True)
        
        #init db
        Execute('find '+params.service_packagedir+' -iname "*.sh" | xargs chmod +x')
        service_packagedir = params.service_packagedir
        
        cmd = format("{service_packagedir}/scripts/init_db.sh")
        Execute('echo "Running ' + cmd + '" as root')
        Execute(cmd,ignore_failures=True)  
        
        Execute('service mysql stop')
        sleep(5)
        
        env.set_params(params)       
        File("/etc/my.cnf.d/server.cnf",
             content=Template("server.cnf.j2"),
             mode=0644
            )        

    def configure(self, env):       
        print 'configure mariadb'
        

    def start(self, env):
        import params
        if params.mariadb_current_host == params.mariadb_hosts[0]:
            Execute('/etc/init.d/mysql start --wsrep-new-cluster')
        else:
            sleep(10)
            Execute('service mysql start')


    def stop(self, env):
        Execute('service mysql stop')

    def restart(self, env):
        print("restart")
        self.stop(env)
        self.start(env)

    def status(self, env):
       Execute('service mysql status')

if __name__ == "__main__":
    MariadbMaster().execute()
