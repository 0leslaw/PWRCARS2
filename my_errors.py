class StuckInWallError(Exception):
    def __init__(self):
        super().__init__("Sprite was stuck in wall")
