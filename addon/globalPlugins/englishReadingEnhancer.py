from ._englishToKanaConverter.englishToKanaConverter import EnglishToKanaConverter
import globalPluginHandler
import speech


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    def __init__(self):
        super().__init__()
        if hasattr(speech, "speech"):
            processText_original = speech.speech.processText
        else:
            processText_original = speech.processText
        c = EnglishToKanaConverter()

        def processText(locale,text,symbolLevel):
            text = processText_original(locale,text,symbolLevel)
            if locale.startswith("ja"):
                text = c.process(text)
            return text
        if hasattr(speech, "speech"):
            speech.speech.processText = processText
        else:
            speech.processText = processText
