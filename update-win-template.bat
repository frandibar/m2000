echo Actualizacion de m2000
echo Borrando archivo de configuracion para recrear DB...
del "%HOMEPATH%\.m2000.cfg"

echo Instalando m2000...
easy_install m2000-__VERSION__-py2.7.egg

echo Creando acceso directo...
xxmklink "%HOMEPATH%\Escritorio\m2000.lnk" %HOMEDRIVE%\Python27\python.exe %HOMEDRIVE%\Python27\Lib\site-packages\m2000-__VERSION__-py2.7.egg\main.py %HOMEDRIVE%\Python27\Lib\site-packages\m2000-__VERSION__-py2.7.egg\ "Mujeres 2000 - Sistema de Gestion de Creditos" 1 %HOMEDRIVE%\Python27\Lib\site-packages\m2000-__VERSION__-py2.7.egg\m2000\art\win.ico /q
xxmklink "%HOMEPATH%\Desktop\m2000.lnk"    %HOMEDRIVE%\Python27\python.exe %HOMEDRIVE%\Python27\Lib\site-packages\m2000-__VERSION__-py2.7.egg\main.py %HOMEDRIVE%\Python27\Lib\site-packages\m2000-__VERSION__-py2.7.egg\ "Mujeres 2000 - Sistema de Gestion de Creditos" 1 %HOMEDRIVE%\Python27\Lib\site-packages\m2000-__VERSION__-py2.7.egg\m2000\art\win.ico /q

echo Aplicando parche a version 11.12.30 de camelot.
copy base.py %HOMEDRIVE%\Python27\Lib\site-packages\Camelot-11.12.30-py2.7.egg\camelot\admin\action\