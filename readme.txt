激活虚拟环境
 venv\Scripts\activate

初始化数据库 
flask --app transport init-db 

启动
flask --app transport --debug run
flask --app transport run

生产环境启动
python main.py

生产环境部署
https://blog.csdn.net/shanmu0737/article/details/123741409

激活虚拟环境：
source mysite_env/bin/activate

启动uwsgi
uwsgi --ini /var/www/aimng/uwsgi.ini

启动gunicorn
gunicorn -w 2 -b 0.0.0.0:5000 main:app