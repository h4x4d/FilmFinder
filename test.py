from autocorrect import Speller
from spellchecker import SpellChecker
import datetime

a = datetime.datetime.now()
"""spell = Speller(lang='ru')
for i in range(1000):
    print(spell('мошина'))"""

spell = SpellChecker(language='ru')
for i in range(1000):
    print(spell.correction('мошина'))

print((datetime.datetime.now() - a).microseconds)


# 176850
# 327984
