class Button:
    def __init__(self, color: tuple, position: tuple, bounding_box: tuple, id: int) -> None:
        self.color: tuple = color
        self.position: tuple = position
        self.bounding_box: tuple = bounding_box
        self.id: int = id