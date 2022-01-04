from argparse import ArgumentParser, _SubParsersAction

SubParserAction = _SubParsersAction

class BaseCLICommand:

    def register(parser: SubParserAction, parent: ArgumentParser):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError