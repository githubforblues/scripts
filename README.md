# scripts
存放一些日常运维工作所需的小脚本

### rm_command.py
这是一个用Python实现的rm命令，可以替换系统中的命令使用。
它能够将删除的文件和目录移动到指定的隐藏文件夹中，并且禁止对根目录下的一些关键目录执行删除操作。

### cron-tomcat_log_clean.sh
这是一个非常简单的shell脚本，能够根据文件数量，删除较旧的日志文件和备份文件。可以配合cronjob使用。
