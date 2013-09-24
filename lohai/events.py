import weakref


class Event(object):
    def __init__(self, event_name):
        self.event_name = event_name
        self.callbacks = []

    def register(self, callback):
        self.callbacks.append(weakref.ref(callback))

    def unregister(self, to_remove):
        for cb_ref in self.callbacks[:]:
            callback = cb_ref()
            if callback is not None and callback == to_remove:
                self.callbacks.remove(cb_ref)
                break

    def notify(self, *args, **kwargs):
        for cb_ref in self.callbacks[:]:
            # dereference weakref
            callback = cb_ref()
            if callback is None:
                # remove any callbacks which have been gc'd
                self.callbacks.remove(cb_ref)

            callback(*args, **kwargs)

    def clear(self):
        self.callbacks = []
