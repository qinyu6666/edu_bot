import sys
import select
import time

import msvcrt
import sys
import time

import threading
import sys
import time
import os


import threading
import time
import sys
import os
import time
import platform
import threading
from queue import Queue, Empty

# 全局锁确保同一时间只有一个输入线程
input_lock = threading.Lock()


def wait_for_input(timeout=4, prompt="请输入: "):
    """等待用户输入，超时返回空字符串（安全跨平台解决方案）"""
    with input_lock:  # 确保同一时间只有一个输入线程
        return _wait_for_input_impl(timeout, prompt)


def _wait_for_input_impl(timeout=4, prompt="请输入: "):
    """实际的输入等待实现"""
    print(prompt, end='', flush=True)

    # 用于存储结果的线程安全队列
    result_queue = Queue()
    input_done = threading.Event()

    # 创建并启动输入线程
    thread = threading.Thread(target=_input_worker, args=(result_queue, input_done))
    thread.daemon = True
    thread.start()

    try:
        # 等待结果或超时
        result = result_queue.get(timeout=timeout)
        return result
    except Empty:
        # 超时处理
        input_done.set()
        # 清除输入缓冲区
        _clear_input_buffer()
        print("\n时间到！")
        return ""
    finally:
        # 确保线程退出
        input_done.set()
        thread.join(0.5)  # 等待线程退出


def _input_worker(queue, done_event):
    """输入工作线程"""
    try:
        # 使用平台特定的输入方法
        if platform.system() == 'Windows':
            result = _windows_input(done_event)
        else:
            result = _unix_input(done_event)

        if not done_event.is_set():
            queue.put(result)
    except Exception:
        if not done_event.is_set():
            queue.put("")


def _unix_input(done_event):
    """Unix/Linux/Mac 输入处理"""
    import select
    import termios
    import tty

    # 保存原始终端设置
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        # 设置终端为原始模式
        tty.setraw(fd)
        input_chars = []

        while not done_event.is_set():
            # 检查输入是否就绪
            rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
            if rlist:
                # 读取单个字符
                char = sys.stdin.read(1)

                if char == '\n':  # 回车结束
                    print()  # 换行
                    return ''.join(input_chars)
                elif char == '\x03':  # Ctrl+C
                    raise KeyboardInterrupt
                elif char == '\x7f':  # 退格键
                    if input_chars:
                        input_chars.pop()
                        # 回显处理：退格、空格、再退格
                        sys.stdout.write('\b \b')
                        sys.stdout.flush()
                else:
                    input_chars.append(char)
                    # 回显字符
                    sys.stdout.write(char)
                    sys.stdout.flush()
            else:
                # 轻微延迟避免忙等待
                time.sleep(0.01)

        # 事件被设置，返回空字符串
        return ""
    finally:
        # 恢复终端原始设置
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def _windows_input(done_event):
    """Windows 输入处理"""
    # 尝试导入msvcrt，如果失败则使用备用方法
    try:
        import msvcrt
    except ImportError:
        return _windows_fallback_input(done_event)

    input_chars = []

    while not done_event.is_set():
        if msvcrt.kbhit():  # 检测按键
            char = msvcrt.getwch()

            # 处理特殊按键
            if char == '\r':  # 回车结束
                print()  # 换行
                return ''.join(input_chars)
            elif char == '\x03':  # Ctrl+C
                raise KeyboardInterrupt
            elif char == '\x08':  # 退格键
                if input_chars:
                    input_chars.pop()
                    # 回显处理：退格、空格、再退格
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
            else:
                input_chars.append(char)
                # 回显字符
                sys.stdout.write(char)
                sys.stdout.flush()
        else:
            # 轻微延迟避免忙等待
            time.sleep(0.05)

    # 事件被设置，返回空字符串
    return ""


def _windows_fallback_input(done_event):
    """Windows 备用输入方法（当msvcrt不可用时）"""
    input_chars = []

    while not done_event.is_set():
        # 尝试读取一行
        try:
            # 使用带超时的select
            if _is_input_ready():
                char = sys.stdin.read(1)

                if char == '\n':  # 回车结束
                    return ''.join(input_chars)
                elif char == '\x03':  # Ctrl+C
                    raise KeyboardInterrupt
                elif char == '\x08':  # 退格键
                    if input_chars:
                        input_chars.pop()
                        # 回显处理：退格、空格、再退格
                        sys.stdout.write('\b \b')
                        sys.stdout.flush()
                else:
                    input_chars.append(char)
                    # 回显字符
                    sys.stdout.write(char)
                    sys.stdout.flush()
        except (IOError, ValueError):
            # 非阻塞读取可能失败
            pass

        time.sleep(0.01)

    # 事件被设置，返回空字符串
    return ""


def _is_input_ready():
    """检查输入是否就绪（跨平台兼容方法）"""
    if platform.system() == 'Windows':
        try:
            import msvcrt
            return msvcrt.kbhit()
        except ImportError:
            # 在Windows上使用select作为备选方案
            try:
                import select
                return select.select([sys.stdin], [], [], 0)[0] != []
            except:
                # select在Windows上可能不支持文件描述符
                return False
    else:
        import select
        return select.select([sys.stdin], [], [], 0)[0] != []


def _clear_input_buffer():
    """清除输入缓冲区（跨平台兼容方法）"""
    if platform.system() == 'Windows':
        try:
            import msvcrt
            while msvcrt.kbhit():
                msvcrt.getwch()
        except ImportError:
            # Windows备选清除方法
            try:
                while _is_input_ready():
                    sys.stdin.read(1)
            except:
                pass
    else:
        pass
        # Unix/Linux/Mac清除方法
        # try:
        #     import termios
        #     # 设置非阻塞读取
        #     fd = sys.stdin.fileno()
        #     old_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        #     fcntl.fcntl(fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)
        #
        #     try:
        #         while True:
        #             try:
        #                 char = sys.stdin.read(1)
        #                 if not char:
        #                     break
        #             except (IOError, ValueError):
        #                 break
        #     finally:
        #         # 恢复原始设置
        #         fcntl.fcntl(fd, fcntl.F_SETFL, old_flags)
        # except ImportError:
        #     # 如果fcntl不可用，使用简单清除方法
        #     try:
        #         while _is_input_ready():
        #             sys.stdin.read(1)
        #     except:
        #         pass


# 测试代码


# 调用函数
user_input = wait_for_input(timeout=6, prompt="请输入一些内容：")

# 检查用户输入
if user_input:
    print(f"你输入的内容是：{user_input}")
else:
    print("没有输入内容。")


print('hhhhhhhdnnn')


user_input2 = wait_for_input(timeout=6, prompt="请输入一些内容：")
if user_input2:
    print(f"你输入的内容是：{user_input2}")
else:
    print("没有输入内容。")