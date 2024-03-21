import sys
import threading
from collections import deque
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton


class CircularBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)
        self.full = threading.Event()

    def push(self, item):
        self.buffer.append(item)
        if len(self.buffer) == self.capacity:
            self.full.set()

    def pop(self):
        item = self.buffer.popleft()
        self.full.clear()
        return item


class ProducerConsumerWidget(QWidget):
    def __init__(self, buffer_capacity, queue_capacity):
        super().__init__()

        self.buffer_capacity = buffer_capacity
        self.queue_capacity = queue_capacity

        self.buffer = CircularBuffer(buffer_capacity)
        self.producer_queue = deque(maxlen=queue_capacity)
        self.consumer_queue = deque(maxlen=queue_capacity)
        self.nrfull_queue = deque(maxlen=1)
        self.nrempty_queue = deque(maxlen=1)
        self.nrempty_queue.append('E')

        self.producer_button = QPushButton('생산자 버튼')
        self.consumer_button = QPushButton('소비자 버튼')
        self.producer_button.clicked.connect(self.start_producer)
        self.consumer_button.clicked.connect(self.start_consumer)

        self.buffer_label = QLabel('Buffer: ')
        self.queue1_label = QLabel('Producer Queue: ')
        self.queue2_label = QLabel('Consumer Queue: ')
        self.queue3_label = QLabel('nrfull Queue: ')
        self.queue4_label = QLabel('nrempty Queue: ')

        layout = QVBoxLayout()
        layout.addWidget(self.producer_button)
        layout.addWidget(self.consumer_button)
        layout.addWidget(self.buffer_label)
        layout.addWidget(self.queue1_label)
        layout.addWidget(self.queue2_label)
        layout.addWidget(self.queue3_label)
        layout.addWidget(self.queue4_label)

        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_labels)
        self.timer.start(100)

    def start_producer(self):
       
        if not self.buffer.full.is_set():  # 버퍼에 자리가 있으면 
            item = 'P' 
            
            self.buffer.push(item)
            self.update_labels()
            if len(self.buffer.buffer) == 4:
                self.nrfull_queue.append('F')
                if self.nrempty_queue:
                    self.nrempty_queue.pop()
            if len(self.producer_queue) > 0:
                self.producer_queue.pop()
        else:
            if len(self.producer_queue) < self.queue_capacity:
                self.producer_queue.append('P')
            #if self.nrfull_queue:
            #    self.nrfull_queue.append('F')
            
            if self.nrempty_queue:
                self.nrempty_queue.pop()

        print('In버퍼: ', len(self.buffer.buffer))
        

    def start_consumer(self):
        if len(self.buffer.buffer) > 0:  # 버퍼가 1개라도 채워졌을때
            self.buffer.pop()  # 한개 제거
            self.update_labels()
            if len(self.consumer_queue) > 0:
                self.consumer_queue.pop()
        else:
            self.consumer_queue.append('C')

        #if (len(self.consumer_queue) > 0 and len(self.buffer.buffer) > 0):
        #    self.consumer_queue.pop()
        
        print('Out버퍼: ', len(self.buffer.buffer))

        if self.nrfull_queue:
            self.nrfull_queue.pop()

        if len(self.buffer.buffer) == 0 or len(self.buffer.buffer) < 4:
            self.nrempty_queue.append('E')
            #if self.nrfull_queue:
            #    self.nrfull_queue.pop()

    def update_labels(self):
        buffer_text = '버퍼: ' + ''.join(self.buffer.buffer)
        queue1_text = '생산자 큐: ' + ''.join(self.producer_queue)
        queue2_text = '소비자 큐: ' + ''.join(self.consumer_queue)
        queue3_text = 'nrfull: ' + ''.join(self.nrfull_queue)
        queue4_text = 'nrempty: ' + ''.join(self.nrempty_queue)

        self.buffer_label.setText(buffer_text)
        self.queue1_label.setText(queue1_text)
        self.queue2_label.setText(queue2_text)
        self.queue3_label.setText(queue3_text)
        self.queue4_label.setText(queue4_text)

    def paintEvent(self, event):
        painter = QPainter(self)

        #버퍼 그리기
        buffer_rect = self.buffer_label.geometry()
        buffer_rect.adjust(0, 25, 0, 0)
        painter.fillRect(buffer_rect, QColor(255, 255, 255))  

        for i in range(self.buffer_capacity):
            rect = buffer_rect.adjusted(i * 20, 0, i * 20, 0)
            color = QColor(0, 0, 0) if i < len(self.buffer.buffer) else QColor(200, 200, 200)
            painter.fillRect(rect, color)

        # 생산자 큐 그리기
        queue1_rect = self.queue1_label.geometry()
        queue1_rect.adjust(0, 25, 0, 0)
        painter.fillRect(queue1_rect, QColor(255, 255, 255))  

        for i in range(self.queue_capacity):
            rect = queue1_rect.adjusted(i * 20, 0, i * 20, 0)
            color = QColor(255, 0, 0) if i < len(self.producer_queue) else QColor(200, 200, 200)
            painter.fillRect(rect, color)

        # 소비자 큐 그리기
        queue2_rect = self.queue2_label.geometry()
        queue2_rect.adjust(0, 25, 0, 0)
        painter.fillRect(queue2_rect, QColor(255, 255, 255))  

        for i in range(self.queue_capacity):
            rect = queue2_rect.adjusted(i * 20, 0, i * 20, 0)
            color = QColor(0, 255, 0) if i < len(self.consumer_queue) else QColor(200, 200, 200)
            painter.fillRect(rect, color)

        # nrfull 큐 그리기
        queue3_rect = self.queue3_label.geometry()
        queue3_rect.adjust(0, 25, 0, 0)
        painter.fillRect(queue3_rect, QColor(255, 255, 255))  

        if self.nrfull_queue:
            rect = queue3_rect.adjusted(0, 0, 0, 0)
            color = QColor(0, 0, 255)
            painter.fillRect(rect, color)

        # nrempty 큐 그리기
        queue4_rect = self.queue4_label.geometry()
        queue4_rect.adjust(0, 25, 0, 0)
        painter.fillRect(queue4_rect, QColor(255, 255, 255)) 

        if self.nrempty_queue:
            rect = queue4_rect.adjusted(0, 0, 0, 0)
            color = QColor(255, 255, 0)
            painter.fillRect(rect, color)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    buffer_capacity = 4
    queue_capacity = 10

    window = QWidget()
    layout = QHBoxLayout()
    layout.addWidget(ProducerConsumerWidget(buffer_capacity, queue_capacity))
    window.setLayout(layout)

    window.setWindowTitle('2020136149 김태섭')
    window.resize(700,700)
    window.show()

    sys.exit(app.exec_())
