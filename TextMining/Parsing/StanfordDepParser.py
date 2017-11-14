from nltk.parse.stanford import StanfordDependencyParser
class DepParser:
    def __init__(self):
        self.path_to_jar = '../Resources/stanford-corenlp-full-2017-06-09/stanford-corenlp-3.8.0.jar'
        self.path_to_models_jar = '../Resources/stanford-corenlp-full-2017-06-09/stanford-corenlp-3.8.0-models.jar'
        self.dependency_parser = StanfordDependencyParser(path_to_jar=self.path_to_jar, path_to_models_jar=self.path_to_models_jar)
    def parse(self,text):
        result = self.dependency_parser.raw_parse(text)
        dep = result.next()
        return dep

dp = DepParser()
dep = dp.parse('I saw a boy who has a ball')
print list(dep.triples())