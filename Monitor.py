import multiprocessing
import threading

import numpy as np
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import tkinter as tk

matplotlib.use('TkAgg')


def plotting(result_queue, text_queue, array_len: int, threshold: float):
    fig, ax = plt.subplots(1, 1, figsize=(7, 3))

    stable_x_axis = np.arange(0, array_len, 1, dtype=np.int64)
    initial_array = np.zeros(shape=(array_len,), dtype=np.float64)

    ax.axhline(y=threshold, color='grey', linestyle='--', linewidth=2, zorder=2, label='Threshold')
    ln, = ax.plot(stable_x_axis, initial_array, linestyle='-', linewidth=1, color='k', zorder=3, label='Maximum NCC')
    ax.set_yticks(np.arange(0, 0.5, 0.1))
    ax.set_xlim(0, initial_array.shape[0] - 1)
    ax.set_ylim(0, 0.4)
    ax.grid()
    ax.legend(loc='upper right')

    def init():
        return ln,

    def run(frame):
        while not result_queue.empty():
            updated_array = result_queue.get()
            if updated_array is None:
                plt.close(fig)
                return ln,

            ln.set_data(stable_x_axis, updated_array)
        return ln,

    ani = FuncAnimation(fig, run, frames=None, init_func=init, blit=True, cache_frame_data=False)

    def update_text(tb, tq):
        while True:
            message = tq.get()
            if message is None:
                break
            tb.insert(tk.END, message + "\n")
            tb.see(tk.END)  # 确保文本框滚动到底部

            # buffer size = 5
            lines = int(tb.index('end-1c').split('.')[0])
            if lines > 5:
                tb.delete('1.0', '2.0')

    # 绘制
    root = tk.Tk()
    root.title("Monitor")
    root.attributes('-topmost', True)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    textbox = tk.Text(root, height=5)
    textbox.pack(fill=tk.BOTH, expand=True)

    text_thread = threading.Thread(target=update_text, args=(textbox, text_queue,), daemon=True)
    text_thread.start()

    root.mainloop()
    # plt.show()


class WaveMonitor:
    def __init__(self, array_len: int, threshold: float):
        # 启动线程
        manager = multiprocessing.Manager()
        self.array_queue = manager.Queue()
        self.message_queue = manager.Queue()

        self.process = multiprocessing.Process(target=plotting, args=(self.array_queue, self.message_queue,
                                                                      array_len, threshold, ))

        self.process.start()

    def update_array(self, updated_array: np.ndarray):
        self.array_queue.put(updated_array)

    def update_message(self, updated_text: str):
        self.message_queue.put(updated_text)

    def close(self):
        self.array_queue.put(None)
        self.message_queue.put(None)
        self.process.join()
