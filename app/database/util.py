class EntryTypes:

    def __init__(self, labels):
        self.labels = labels

    def get_label(self, title):
        title = title.replace('_', '').lower().rstrip().lstrip()

        for label in self.labels.keys():
            if title in self.labels[label]:
                return label

        return None
