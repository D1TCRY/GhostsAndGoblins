class GUIComponent(object):
    @property
    def name_id(self):
        raise NotImplementedError
    @name_id.setter
    def name_id(self, value) -> None:
        raise NotImplementedError

    @property
    def fixed(self):
        raise NotImplementedError
    @fixed.setter
    def fixed(self, value) -> None:
        raise NotImplementedError

    def g2d_draw(self, *args) -> None:
        raise NotImplementedError