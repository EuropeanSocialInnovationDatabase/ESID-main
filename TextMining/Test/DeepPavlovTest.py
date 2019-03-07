from deeppavlov.skills.pattern_matching_skill import PatternMatchingSkill
from deeppavlov.agents.default_agent.default_agent import DefaultAgent
from deeppavlov.agents.processors.highest_confidence_selector import HighestConfidenceSelector
from deeppavlov import build_model, configs

hello = PatternMatchingSkill(responses=['Hello world!'], patterns=["hi", "hello", "good day"])
bye = PatternMatchingSkill(['Goodbye world!', 'See you around'],
                           patterns=["bye", "chao", "see you"])
fallback = PatternMatchingSkill(["I don't understand, sorry", 'I can say "Hello world!"'])

agent = DefaultAgent([hello, bye, fallback], skills_selector=HighestConfidenceSelector())

print(agent(['god day', 'Bye', 'Or not']))

snips_model = build_model(configs.classifiers.intents_snips , download=True)
print(snips_model(["Hello! What are you doing?"]))