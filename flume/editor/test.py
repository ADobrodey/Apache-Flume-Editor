from PyQt5.QtCore import QObject, pyqtSignal

class Foo(QObject):

    # Define a new signal called 'trigger' that has no arguments.
    trigger = pyqtSignal(int)

    def connect_and_emit_trigger(self):
        # Connect the trigger signal to a slot.
        self.trigger.connect(self.handle_trigger)

        # Emit the signal.
        self.trigger.emit(2)

    def handle_trigger(self, res):
        # Show that the slot has been called.

        print ("trigger signal received", res)

if __name__ == '__main__':

    foo = Foo()
    foo.connect_and_emit_trigger()