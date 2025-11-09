class GUIComponent(object):
    @property
    def name_id(self):
        raise NotImplementedError
    @name_id.setter
    def name_id(self, value) -> None:
        raise NotImplementedError

    @property
    def g2d(self):
        raise NotImplementedError
    @g2d.setter
    def g2d(self, value) -> None:
        raise NotImplementedError

    def g2d_draw(self, *args) -> None:
        raise NotImplementedError