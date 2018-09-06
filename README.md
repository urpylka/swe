# simple-web-engine

Мои сохраненные ссылки: http://telegra.ph/Napisanie-sobstvennoj-CMS-03-14

## Алгоритм

1. Пользователь совершает GET запрос на адрес веб-сервера
2. Модуля ModRewrite (веб. сервера Apache) переадресует запрос на `page.php?link=<ТЕЛО ЗАПРОСА>`
3. Ядро движка `page.php` обрабатывает запрос пользователя на просмотр страницы
4. Если по запросу найдена 1 страница, проверяются права пользователя на её просмотр
5. Если прав хватает, подгружается шаблон для её отображения

## Функции

1. Подмена ардреса (с помощью модуля веб. сервера Apache - ModRewrite).
2. Выдача пользователю тех страниц, на которые у него есть доступ.
3. Редактирование и создание страниц.

## TODO

* Обезличить (удалить все внешние ссылки, изображения)
* Создать скрипт для простого развертывания
* Возможно лучше хранить адрес шаблона а не его имя, тогда вместо свича будет поверка на существование шаблона
* Необходим класс для работы со страницей
* Семантическая проблема движок работает только на новости или вообще на все страницы?
* При уменьшении размера страницы quickmenu вылезает за границы
* Хранить права на использование шаблона и страницы отдельно?
* Qr код внизу справа
* Шаблоны перевести на функции
* Закрыть modules
* Codeinteger
  * https://ru.wikipedia.org/wiki/CodeIgniter
  * https://ru.wikipedia.org/wiki/Model-View-Controller
  * http://codeigniter3.info
  * http://codeigniter3.info/guide/overview/at_a_glance
* Drupal
  * https://habrahabr.ru/post/103600/
  * https://ru.wikipedia.org/wiki/Content_Management_Framework
  * https://ru.wikipedia.org/wiki/Drupal
* Изменение производится на сервере, потом производится рендер в статику (кешируются) - средства сборки
* Умное логирование и сессирование =D тех кто заходит ip, размер экрана, откуда и тд
* min js
* Доделать меню
* Отключение доступа если у тебя говнобраузер
* Редактор страниц (меню админа)
* Свой обработчик ошибок
* Усовершенствовать права доступа
* Апач смотрит конфиги от рута
* Добавить соль в md5
* Добавить защиту от mysql инъекций

# Docker LAMP
Linux + Apache + MariaDB (MySQL) + PHP 7.2 on Docker Compose. Mod_rewrite enabled by default.

## Instructions

Enter the following command to start your containers:

```bash
sudo docker-compose up -d
```

To stop them, use this:

```bash
sudo docker-compose stop
```

To view logs^ use them:

```bash
sudo docker-compose logs -f -t
```

Feel free to make pull requests and help to improve this.

If you are looking for phpMyAdmin, take a look at [this](https://github.com/celsocelante/docker-lamp/issues/2).

