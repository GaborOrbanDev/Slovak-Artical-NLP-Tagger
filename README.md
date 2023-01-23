# Szlovák nyelvű újságcikk tagger

Az alábbi program egy szlovák ügyfelemnek készült, aki 3 weboldalról akart cikkeket letölteni, és az újságcikkekhez taggeket generálni. A crawler statikus és dinamikus weboldalakat is szemléz. Két algoritmust használtam a tagek generálásához:
- RAKE : Rapid Automatic Keyword Extraction algoritmus
- NER : Named Entity Recognition algoritmus (ehhez egy többnyelvű spacy pipelinet használtam).

Az ügyfelem kérése az volt, hogy egy csv-ben adja vissza a program a keresések eredményét.
