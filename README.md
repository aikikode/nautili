Nautili / Кораблики
===================

Donate to support the project / Поддержите проект:  
[![](https://www.paypalobjects.com/en_US/RU/i/btn/btn_donateCC_LG.gif)
](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=996CAQCKW2M7C)  
* * *

Board-style game inspired by the book ['Nautili and tin soldiers'](http://www.livelib.ru/book/1000541123) by Oleg Orlov and Riurik Popov.  
See full game rules description and instructions on map creation on [Wiki](https://github.com/aikikode/nautili/wiki).

По мотивам настольной игры, описанной в книге ["Кораблики и солдатики"](http://www.livelib.ru/book/1000541123) Олегом Орловым и Рюриком Поповым.  
Подробное описание правил игры и как создавать свои карты смотрите в соответствующих разделах [Wiki](https://github.com/aikikode/nautili/wiki).  
  
![](http://i.imgur.com/TvUeenu.png)  
Run / Запуск игры
-----------------

###Install dependencies / Установите необходимые зависимости  
####Linux users / Для Linux:  
```bash
sudo apt-get install python-pygame
sudo apt-get install python-pip
sudo pip install -r requirements.txt
```
####Windows users / Для Windows  
#####x32 system / 32-разрядная система:
* [Python 2.7](https://www.python.org/ftp/python/2.7.6/python-2.7.6.msi)
* [PyGame](http://pygame.org/ftp/pygame-1.9.1.win32-py2.7.msi)
* [PyTMX](https://github.com/bitcraft/PyTMX) - copy pytmx directory into internal nautili directory / скопируйте папку pytmx во внутренюю папку nautili (туда, где находится файл \__init__.py)
* [Pillow](https://pypi.python.org/packages/2.7/P/Pillow/Pillow-2.4.0.win32-py2.7.exe#md5=6c181d7041c147c2293daf59af213c5e)  

#####x86_64 system / 64-разрядная система:  
* [Python 2.7](https://www.python.org/ftp/python/2.7.6/python-2.7.6rc1.amd64.msi)
* [PyGame](http://www.lfd.uci.edu/~gohlke/pythonlibs/sn5ub7d9/pygame-1.9.2a0.win-amd64-py2.7.exe)
* [PyTMX](https://github.com/bitcraft/PyTMX) - copy pytmx directory into internal nautili directory / скопируйте папку pytmx во внутренюю папку nautili (туда, где находится файл \__init__.py)
* [Pillow](https://pypi.python.org/packages/2.7/P/Pillow/Pillow-2.4.0.win-amd64-py2.7.exe)  

###Run the game / Запустите игру  
####Linux users / Для Linux:  
```bash
python ./nautili.pyw
```
####Windows users / Для Windows:  
Double click nautili.pyw and if prompt input path to installed Python 2.7 / Запустите файл nautili.pyw и если понадобится, укажите путь до Python 2.7, который вы устанавливали до этого.
