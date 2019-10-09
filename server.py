#  Created by Jaroslaw.Doo
#  my.agreegator+skillbox@gmail.com
#
#  Copyright © 2019
#
#  Сервер для обработки сообщений от клиентов
#
from twisted.internet import reactor
from twisted.internet.protocol import connectionDone, ServerFactory
from twisted.protocols.basic import LineOnlyReceiver


class ConnectionHandler(LineOnlyReceiver):
    factory: 'Server'
    login: str                  #  Тут логин пользователя будет
    login_try_count: int = 3    # Даем три попытки ввести логин

    def SendToAll(self, message, ReallyAll=False):
        for user in self.factory.clients:
            if ReallyAll or (user is not self):  # кроме написавшего
                user.sendLine(message.encode())
        # пополним историю сообщений
        self.factory.message_history.append(message)
        while len(self.factory.message_history) > 10:  # больше 10 последних сообщений не храним
            self.factory.message_history.pop(0)  # удаляем сначала списка

    def connectionLost(self, reason=connectionDone):
        self.factory.clients.remove(self)
        print(f"Disconnected, total connections now: {len(self.factory.clients)}")
        if self.login is None:
            pass  # если кто-то так и не смог авторизоваться, то и нечего сообщать всем что он ушел даже не зайдя в чат
        else:
            self.factory.used_logins.remove(
                self.login.upper())  # вычеркем логин из списка и осовбодим его для нового входа
            message = f"<Server>: User <{self.login}> left this chat, farewell"
            self.SendToAll(message)

    def connectionMade(self):
        self.login = None
        self.login_try_count = 3
        self.factory.clients.append(self)
        conn_amount = len(self.factory.clients)
        print(f"New connection, total connections: {conn_amount}")
        self.sendLine(
            f"<Server>: First of all, please, enter YourLogin  (you have {self.login_try_count} attempts)".encode())

    def lineReceived(self, line: bytes):
        message = line.decode()
        #  проверим сперва авторизован ли пользователь на этом соединении
        if not (self.login is None):
            # пользователь авторизован все Ок, разошлем его сообщение всем другим
            message = f"<{self.login}>: {message}"
            self.SendToAll(message)
        else:
            self.login_try_count -= 1  # уменьшаем число доступных попыток авториации
            login = message.strip(' <>.,:;$!@#$%^&*()_+=-\/"''').replace(' ',
                                                                         '_')  # почистим имя от спец-символов чтобы не выпендривались
            logUp = login.upper()  # приводим к верхнему регистру для сравнения со всеми другими (т.е. различать регистр в логинах не будем)
            if logUp in self.factory.used_logins:
                self.sendLine(f"<Server>: Login {login} already used, try another.".encode())
            else:
                if len(login) >= 2 and (logUp != "SERVER"):  # слишком короткое и служебное имя Server нельзя
                    self.login = login
                    self.factory.used_logins.append(logUp)
                    print(f"New user: {login}")
                    # Вышлем новому пользователю пропущенные им сообщения чата
                    self.factory.send_history(self)
                    # Сообщим всем о входе нового пользователя в чат
                    message = f"<Server>: Welcome, {login}!!!"
                    self.SendToAll(message,
                                   True)  # благодаря второму парметру сам вошедший тоже получит это приветствие
                else:
                    self.sendLine(f"<Server>: Invalid login, try again".encode())

            # Контрольная проверка
            if self.login is None:  # Все еще так и не авторизовался?
                if self.login_try_count > 0:
                    # сможет еще раз попробовать
                    self.sendLine(f"<Server>: You have {self.login_try_count} attempts to enter login.".encode())
                else:
                    # ну все, это была последняя капля
                    self.sendLine("<Server>: Good buy. Try another time.".encode())
                    self.transport.loseConnection()  # Disconnect


# End of class 'ConnectionHandler' description


class Server(ServerFactory):
    protocol = ConnectionHandler
    clients: list
    used_logins: list
    message_history: list

    def __init__(self):
        self.clients = []  # список соединений
        self.used_logins = []  # список использованных логинов
        self.message_history = []  # история сообщений в чате (храним 10 последних только)

    def send_history(self, handle: ConnectionHandler):
        # Вышлем новому пользователю пропущенные им сообщения чата
        for message in self.message_history:
            handle.sendLine(message.encode())

    def startFactory(self):
        print("Server started...")

    def stopFactory(self):
        print("Server stopped.")


# End of class 'Server'  description


reactor.listenTCP(
    7410, Server()
)
reactor.run()
