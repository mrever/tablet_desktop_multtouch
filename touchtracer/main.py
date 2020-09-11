__version__ = '1.0'

import kivy
kivy.require('1.0.6')

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Point, GraphicException
from random import random
from math import sqrt
import socket


host = '192.168.1.107' #socket.gethostname()  # as both code is running on same pc
port = 55435  # socket server port number
client_socket = socket.socket()  # instantiate
try:
    client_socket.connect((host, port))  # connect to the server
    # client_socket.close()  # close the connection
except Exception as e:
    msg = str(e)

msg = 'drawing'
def sendmsg(message = {'1':'message1'}):
    # return

    # client_socket.send('fuck '.encode())  # send message
    tosend = ''
    for m in sorted(list(message.keys())):
        tosend += m
        tosend += ' '
        tosend += message[m]
        tosend += ' '
    tosend += '\n'
    client_socket.send(tosend.encode())  # send message

    # for m in sorted(list(message.keys())):
        # client_socket.send((m+' ' + message[m]+' ').encode())  # send message
    # client_socket.send(('\n').encode())  # send message
    data = client_socket.recv(1024).decode()  # receive response

    # print('Received from server: ' + data)  # show in terminal
    # client_socket.close()  # close the connection


def calculate_points(x1, y1, x2, y2, steps=5):
    dx = x2 - x1
    dy = y2 - y1
    dist = sqrt(dx * dx + dy * dy)
    if dist < steps:
        return
    o = []
    m = dist / steps
    for i in range(1, int(m)):
        mi = i / m
        lastx = x1 + dx * mi
        lasty = y1 + dy * mi
        o.extend([lastx, lasty])
    return o


class Touchtracer(FloatLayout):

    def on_touch_down(self, touch):
        message = {'event':'touchdown',
                   'uid':str(touch.uid),
                   'x':str(touch.x),
                   'y':str(touch.y),
                   }
        sendmsg(message)
        win = self.get_parent_window()
        ud = touch.ud
        ud['group'] = g = str(touch.uid)
        pointsize = 5
        ud['color'] = random()

        with self.canvas:
            Color(ud['color'], 1, 1, mode='hsv', group=g)
            ud['lines'] = [
                Rectangle(pos=(touch.x, 0), size=(1, win.height), group=g),
                Rectangle(pos=(0, touch.y), size=(win.width, 1), group=g),
                Point(points=(touch.x, touch.y), source='particle.png',
                      pointsize=pointsize, group=g)]

        ud['label'] = Label(size_hint=(None, None))
        self.update_touch_label(ud['label'], touch)
        self.add_widget(ud['label'])
        touch.grab(self)
        return True

    def on_touch_move(self, touch):
        message = {'event':'touchmove',
                   'uid':str(touch.uid),
                   'x':str(touch.x),
                   'y':str(touch.y),
                   }
        sendmsg(message)
        if touch.grab_current is not self:
            return
        ud = touch.ud
        ud['lines'][0].pos = touch.x, 0
        ud['lines'][1].pos = 0, touch.y

        index = -1

        while True:
            try:
                points = ud['lines'][index].points
                oldx, oldy = points[-2], points[-1]
                break
            except:
                index -= 1

        points = calculate_points(oldx, oldy, touch.x, touch.y)

        if points:
            try:
                lp = ud['lines'][-1].add_point
                for idx in range(0, len(points), 2):
                    lp(points[idx], points[idx + 1])
            except GraphicException:
                pass

        ud['label'].pos = touch.pos
        import time
        t = int(time.time())
        if t not in ud:
            ud[t] = 1
        else:
            ud[t] += 1
        self.update_touch_label(ud['label'], touch)

    def on_touch_up(self, touch):
    # def on_release(self, touch):
        message = {'event':'touchup',
                   'uid':str(touch.uid),
                   'x':str(touch.x),
                   'y':str(touch.y),
                   }
        if touch.grab_current is not self:
            return
        sendmsg(message)
        touch.ungrab(self)
        ud = touch.ud
        self.canvas.remove_group(ud['group'])
        self.remove_widget(ud['label'])

    def update_touch_label(self, label, touch):
        label.text = 'T: %s\nPos: (%d, %d)\nClass: %s' % (
            touch.id, touch.x, touch.y, touch.__class__.__name__)
        # label.text = msg
        label.texture_update()
        label.pos = touch.pos
        label.size = label.texture_size[0] + 20, label.texture_size[1] + 20


class TouchtracerApp(App):
    title = 'Touchtracer'
    icon = 'icon.png'

    def build(self):
        return Touchtracer()

    def on_pause(self):
        return True


if __name__ == '__main__':
    sendmsg()
    tapp = TouchtracerApp()
    tapp.run()

