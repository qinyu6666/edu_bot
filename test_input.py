#linux操作
# import signal
#
# class TimeoutException(Exception):
#     pass
#
# def input_with_timeout(prompt, timeout):
#     def timeout_handler(signum, frame):
#         raise TimeoutException()
#
#     signal.signal(signal.SIGALRM, timeout_handler)
#     signal.alarm(timeout)
#     try:
#         return input(prompt)
#     except TimeoutException:
#         print("\n输入超时！")
#         return None
#     finally:
#         signal.alarm(0)
#
# # 等待用户输入，超时时间为 5 秒
# user_input = input_with_timeout("请输入一些内容（5秒内）：", 5)
# if user_input:
#     print(f"你输入的内容是：{user_input}")


#Windows操作
import threading

# class TimeoutException(Exception):
#     pass

def wait_for_input(prompt, timeout):
    result = [None]  # 使用列表来存储结果，因为非局部变量在嵌套函数中不可变
    event = threading.Event()  # 用于同步线程

    def input_thread():
        try:
            result[0] = input(prompt)
        except EOFError:  # 捕获用户通过 Ctrl+D 发送的 EOF
            result[0] = None
        finally:
            event.set()  # 通知主线程输入已完成

    thread = threading.Thread(target=input_thread)
    thread.start()
    thread.join(timeout)  # 等待线程完成或超时

    # if not event.is_set():  # 如果线程未完成
    #     print("\n输入超时！")
    #     raise TimeoutException()

    return result[0]

try:
    # 等待用户输入，超时时间为 5 秒
    user_input = wait_for_input("请输入一些内容（5秒内）：", 5)
    if user_input:
        print(f"你输入的内容是：{user_input}")
except TimeoutException:
    print("超时未输入内容。")