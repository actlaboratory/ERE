from ._englishToKanaConverter.englishToKanaConverter import EnglishToKanaConverter
import globalPluginHandler
import speech


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    def __init__(self):
        super().__init__()
        processText_original = speech.speech.processText
        c = EnglishToKanaConverter()

        def processText(locale,text,symbolLevel):
            text = processText_original(locale,text,symbolLevel)
            if locale.startswith("ja"):
                text = c.process(text)
            return text
        speech.speech.processText = processText
