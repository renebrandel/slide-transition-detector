import progressbar as pb

class ProgressController(object):
    def __init__(self, title, total):
        self.widgets = [title, pb.Percentage(), ' - ', pb.Bar(), ' ']
        self.total = total
        self.progress = None

    def start(self):
        print
        self.progress = pb.ProgressBar(widgets=self.widgets,maxval=self.total).start()

    def update(self, i):
        assert self.progress is not None
        self.progress.update(i)

    def finish(self):
        assert self.progress is not None
        self.progress.finish()
        print