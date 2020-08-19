import sys
import time

class ProgressBar:
    """
    Progress bar for loops that take a while. Includes linear time estimate and a framerate limit to minimize performance impact.
    Printing other things while it's running will mess with it.
    Has a count function for list comprehension progress bars which returns its argument.

    EXAMPLE:
    progressBar = ProgressBar(len(data))
    data_squared = [None] * len(data)
    for i in range(len(data)):
        data_squared[i] = data[i] ** 2
        progressBar.set_progress(i)

    OR:
    progressBar = ProgressBar(len(data))
    data_squared = [progressBar.count(d) ** 2 for d in data]
    """
    def __init__(self, total, autocomplete = True, framerate = 30, bar_length = 30):
        """
        Initialize a progress bar with the completion point and optional framerate and bar length settings.
        The autocomplete setting automatically prints a new line once progress
        equals total, finalizing that bar. If you repeatedly
        ProgressBar.set_progress(total), this will print a bar every time
        without framerate limit.
        """
        self.total = total
        self.autocomplete = autocomplete
        self.frametime = 1/framerate
        self.last_frame = time.time() - 2 * self.frametime
        self.start_time = time.time()
        self.bar_length = bar_length
        self.partial_blocks = [" ", u"\u258f", u"\u258e", u"\u258d", u"\u258c", u"\u258b", u"\u258a", u"\u2589", u"\u2588"]
        self.progress = 0
        self.update()

    def update(self):
        """
        This function will redraw the progress bar at progress/total completion. It is framerate limited and intended
        to be called on every iteration of a loop with minimal performance cost. It will make a time prediction based on time
        since the object was initialized or reset was last called.
        There should never be a reason to call this function externally.
        Progress values greater than total will be treated as equal to it and
        a note added.
        """
        cur_time = time.time()
        if cur_time - self.last_frame >= self.frametime or self.progress == self.total:
            over_total = self.progress > self.total
            if over_total:
                self.progress = self.total
            self.last_frame = cur_time

            completion = self.progress/self.total
            blocks, center = divmod(completion * self.bar_length, 1)
            blocks = int(blocks)
            center_char = self.partial_blocks[int(round(center * 8))]
            if blocks == self.bar_length:
                center_char = ''
            bar = "[" + blocks * u"\u2588" + center_char + (self.bar_length - blocks - 1) * " " + "]"

            if isinstance(self.total, int) and isinstance(self.progress, int):
                completion_str = "{:d}/{:d} - {:.2f}%".format(self.progress, self.total, 100 * completion)
            else:
                completion_str = "{:.2f}/{:.2f} - {:.2f}%".format(self.progress, self.total, 100 * completion)

            elapsed = cur_time - self.start_time
            time_est = (1 - completion) * elapsed/max(completion, 0.001)

            frame = "{} : {} | Elapsed: {:.2f}s | Remaining (est): {:.2f}s".format(bar, completion_str, elapsed, time_est)
            if over_total:
                frame += " | Progress exceeds total"
            print("\r%s" % frame, end = '')
            sys.stdout.flush()
            if self.autocomplete and self.progress == self.total and not over_total:
                self.last_frame = time.time() - 2 * self.frametime
                self.start_time = time.time()
                self.progress = 0
                print()

    def reset(self, new = False):
        """
        Resets the progress bar to intialization state (primarily for time estimate purposes)
        If new is set to true, it will create a new bar, leaving whatever was left
        of the old bar intact. By default, the reset bar will override the old.
        """
        self.last_frame = time.time() - 2 * self.frametime
        self.start_time = time.time()
        self.progress = 0
        if new:
            print()
        self.update()

    def options(self, total = None, autocomplete = None, framerate = None, bar_length = None):
        """
        Change the settings of the progress bar. This can be done without affecting progress.
        Intended to be used with named parameters
        """
        if total:
            self.total = total
        if autocomplete:
            self.autocomplete = autocomplete
        if framerate:
            self.framerate = framerate
        if bar_length:
            self.bar_length = bar_length
        self.update()

    def set_progress(self, progress):
        """
        Set the progress of the progress bar and update it.
        """
        self.progress = progress
        self.update()

    def count(self, x = None):
        """
        This function returns its only argument, allowing it to be used to
        create a progress bar on list comprehension. May cause slowdown, but
        because the updates are framerate limited, it should be minor.
        E.g.
        bound = 10 ** 6
        progressBar = ProgressBar(bound)
        list1 = [progressBar.count(x) ** 2 for x in range(bound)]

        Can also be used to create a progress bar for a loop without an index
        variable with no argument.
        """
        self.progress += 1
        self.update()
        return x
