class ZephyrAgent:
    def __init__(self):
        self.name = "Zéphyr"

    async def process(self, message: str) -> str:
        return f"Tu as dit : {message}"