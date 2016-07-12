import progressbar as pb


class ProgressController(object):
    """
    Controlls the ProgressBar UI to indicate the progress
    of a process.
    """
    def __init__(self, title, total=100):
        """
        The default initializer.
        :param title: the title of the progress bar
        :param total: the maximum value of the progress
        """
        self.widgets = [title, pb.Percentage(), ' - ', pb.Bar(), ' ']
        self.total = total
        self.progress = None

    def start(self):
        """
        Prints a new line ofter starting to seperate progressbar from
        the rest of the output.
        Then prints the progress bar UI.
        """
        self.progress = pb.ProgressBar(widgets=self.widgets,maxval=self.total).start()

    def update(self, i):
        """
        Updates the progress bar according to the parameter i.
        :param i: The progress of the process
        """
        assert self.progress is not None
        self.progress.update(i)

    def increment(self, step=1):
        assert self.progress is not None
        self.progress.update(self.progress.currval + 1)

    def finish(self):
        """
        Stops updating the progress bar. And show an indication that
        it's finished. Also prints an empty line after the progress bar.
        """
        assert self.progress is not None
        self.progress.finish()
