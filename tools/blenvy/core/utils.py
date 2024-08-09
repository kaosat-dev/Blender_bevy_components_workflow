import sys
import inspect
import bpy

def full_stack_lines(tb=None):
    text = []
    try:
        if tb is None:
            tb = sys.exc_info()[2]

        text.append('Traceback (most recent call last):')
        for item in reversed(inspect.getouterframes(tb.tb_frame)[1:]):
            text.append('   File "{1}", line {2}, in {3}\n'.format(*item))
            for line in item[4]:
                text.append('       ' + line.lstrip())
        for item in inspect.getinnerframes(tb):
            text.append('   File "{1}", line {2}, in {3}\n'.format(*item))
            for line in item[4]:
                text.append('       ' + line.lstrip())
    except: pass
    return text

def exception_traceback(error):
    traceback_formated = [str(error)]
    traceback_formated += full_stack_lines()
    return traceback_formated

def show_message_box(title = "Message Box", icon = 'INFO', lines=""):
    myLines=lines
    def draw(self, context):
        for n in myLines:
            self.layout.label(text=n)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
