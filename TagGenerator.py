from rake_nltk import Rake
import spacy
import re

# !pip install -U pip setuptools wheel
# !pip install -U spacy
# !python -m spacy download xx_ent_wiki_sm

nlp = spacy.load("xx_ent_wiki_sm")

stopwords_sk = ["pre","a","aby","aj","ak","akej","akejže","ako","akom","akomže","akou","akouže","akože","aká","akáže","aké","akého","akéhože","akému","akémuže","akéže","akú","akúže","aký","akých","akýchže","akým","akými","akýmiže","akýmže","akýže","ale","alebo","ani","asi","avšak","až","ba","bez","bezo","bol","bola","boli","bolo","bude","budem","budeme","budete","budeš","budú","buď","by","byť","cez","cezo","dnes","do","ešte","ho","hoci","i","iba","ich","im","inej","inom","iná","iné","iného","inému","iní","inú","iný","iných","iným","inými","ja","je","jeho","jej","jemu","ju","k","kam","kamže","každou","každá","každé","každého","každému","každí","každú","každý","každých","každým","každými","kde","kej","kejže","keď","keďže","kie","kieho","kiehože","kiemu","kiemuže","kieže","koho","kom","komu","kou","kouže","kto","ktorej","ktorou","ktorá","ktoré","ktorí","ktorú","ktorý","ktorých","ktorým","ktorými","ku","ká","káže","ké","kéže","kú","kúže","ký","kýho","kýhože","kým","kýmu","kýmuže","kýže","lebo","leda","ledaže","len","ma","majú","mal","mala","mali","mať","medzi","mi","mne","mnou","moja","moje","mojej","mojich","mojim","mojimi","mojou","moju","možno","mu","musia","musieť","musí","musím","musíme","musíte","musíš","my","má","mám","máme","máte","máš","môcť","môj","môjho","môže","môžem","môžeme","môžete","môžeš","môžu","mňa","na","nad","nado","najmä","nami","naša","naše","našej","naši","našich","našim","našimi","našou","ne","nech","neho","nej","nejakej","nejakom","nejakou","nejaká","nejaké","nejakého","nejakému","nejakú","nejaký","nejakých","nejakým","nejakými","nemu","než","nich","nie","niektorej","niektorom","niektorou","niektorá","niektoré","niektorého","niektorému","niektorú","niektorý","niektorých","niektorým","niektorými","nielen","niečo","nim","nimi","nič","ničoho","ničom","ničomu","ničím","no","nám","nás","náš","nášho","ním","o","od","odo","on","ona","oni","ono","ony","oň","oňho","po","pod","podo","podľa","pokiaľ","popod","popri","potom","poza","pre","pred","predo","preto","pretože","prečo","pri","práve","s","sa","seba","sebe","sebou","sem","si","sme","so","som","ste","svoj","svoja","svoje","svojho","svojich","svojim","svojimi","svojou","svoju","svojím","sú","ta","tak","takej","takejto","taká","takáto","také","takého","takéhoto","takému","takémuto","takéto","takí","takú","takúto","taký","takýto","takže","tam","teba","tebe","tebou","teda","tej","tejto","ten","tento","ti","tie","tieto","tiež","to","toho","tohoto","tohto","tom","tomto","tomu","tomuto","toto","tou","touto","tu","tvoj","tvoja","tvoje","tvojej","tvojho","tvoji","tvojich","tvojim","tvojimi","tvojím","ty","tá","táto","tí","títo","tú","túto","tých","tým","tými","týmto","u","už","v","vami","vaša","vaše","vašej","vaši","vašich","vašim","vaším","veď","viac","vo","vy","vám","vás","váš","vášho","však","všetci","všetka","všetko","všetky","všetok","z","za","začo","začože","zo","áno","čej","či","čia","čie","čieho","čiemu","čiu","čo","čoho","čom","čomu","čou","čože","čí","čím","čími","ďalšia","ďalšie","ďalšieho","ďalšiemu","ďalšiu","ďalšom","ďalšou","ďalší","ďalších","ďalším","ďalšími","ňom","ňou","ňu","že"]
#source of stopwords: https://github.com/stopwords-iso/stopwords-sk/blob/master/stopwords-sk.json
punctuation = [".", ",", "!", "?", "„", "“", "\"", "'", ":", ";", "/", ",“", ".“", "-", "–", "“,", "*", "-*"]

class TagGenerator:
    
    def RakeGenerator(self):
        """
        This method generates tags with RAKE algorithms, and appends the top 2%+1 words into self.tags
        """
        rake = Rake(stopwords=stopwords_sk,punctuations=punctuation)
        rake.extract_keywords_from_text(self.text)
        words_unsorted = dict(rake.get_word_degrees()) #parse to dict
        words_sorted_len = sorted(words_unsorted.items(), key=lambda i: len(i[0])) #order by length

        for key, itup in enumerate(words_sorted_len): #remove duplicates
            if key+1 < len(words_sorted_len):
                for jtup in words_sorted_len[key+1:]:
                    if itup[0] in jtup[0] or itup[0] == jtup[0]:
                        words_sorted_len.remove(jtup)

        for word in words_sorted_len: #remove none charachter findings
            if re.search(r"^[^\w\s]{1,}$", word[0]) != None:
                words_sorted_len.remove(word)

        words_sorted_imp = sorted(words_sorted_len, key=lambda i: i[1], reverse=True) #order by accuracy
        words_sorted_imp = list(filter(lambda i: len(i[0])>3, words_sorted_imp)) #remove too short results
        result_tuple = words_sorted_imp[:int(len(words_sorted_imp)*0.02)+1] #select top 2%+1 of findings
        results = [i[0] for i in result_tuple] #get only keys (names)

        for r in results: #append results, that not in self.tags
            if r not in self.tags:
                self.tags.append(r)

    def NerOrg(self, org_raw : list):
        """
        Gets organizations
        """
        org0 = list(set(org_raw)) #filter out duplicates
        org1 = list(set([re.sub(r"[^\w\s].*", "", i) for i in org0])) #filter out punctuation and duplicates
        org2 = [i for i in org1 if re.search(r".{0,}[A-Z].{0,}", i)!=None] #search for capital letter

        for o in org2: #append org entities to self.tags
            if o not in self.tags:
                self.tags.append(o)

    def NerPer(self, per_raw):
        """
        Gets people
        """
        per0 = list(set(per_raw))
        per1 = [i for i in per0 if re.search(r"^[A-Z].*", i)!=None] #filter on entities whose name starts with capital letter

        per2 = list(set([re.sub(r"[^\w\s].*", "", i) for i in per1])) #filter out punctuation and duplicates
        per2_1 = sorted(per2, key=lambda i: len(i)) #sort it ascending by name length

        per3 = sorted(per2, key=lambda i: len(i), reverse=True) #sor it descending by name length

        for k, v in enumerate(per3): #remove shorter versions
            if k+1<len(per3):
                for w in per2_1:
                    if w in v:
                        per3.remove(w)
        #lemmatization would be good, but a slovak lemmatizator is needed

        for p in per3:
            if p not in self.tags:
                self.tags.append(p)

    def NerLoc(self, loc_raw):
        """
        Gets locations
        """
        loc0 = list(set(loc_raw)) #filter out duplicates
        loc1 = [i for i in loc0 if re.search(r"^[A-Z].*", i)!=None] #filter on entities whose name starts with capital letter
        loc2 = sorted(loc1, key=lambda i: len(i)) #sort ascending by name length

        for k, v in enumerate(loc2): #filter on shorter versions
            if k+1<len(loc2):
                for w in loc2[k+1:]:
                    if v in w:
                        loc2.remove(w)
        loc3 = list(set([re.sub(r"[^\w\s].*", "", i) for i in loc2])) #filter out punctuation and duplicates
        loc4 = [i for i in loc3 if re.search(r"[a-z][A-Z]", i) ==None] #filter out parsing errors if there is

        loc5 = []

        for k, v in enumerate(loc4): #filter similar between two entity
            if k+1<len(loc4):
                foundSimilar = False
                for w in loc4[k+1:]:
                    if v[:-2] == w[:-2]:
                        loc5.append(min(v, w))
                        foundSimilar = True

                if foundSimilar == False:
                    loc5.append(v)
            else:
                if v not in loc5:
                    loc5.append(v)

        for l in loc5: #append locations to self.tags, that not in it
            if l not in self.tags:
                self.tags.append(l)
    
    def NerGenerator(self):
        """
        Generates tags with Named-Entity Recognition, and appends it to self.tags
        """
        for w in stopwords_sk: #add stopwords to nlp
            nlp.Defaults.stop_words.add(w)

        doc = nlp(self.text) #assign doc var
        per_raw = []
        loc_raw = []
        org_raw = []

        for entity in doc.ents: #getting different kind of entities
            if entity.label_ == 'PER':
                per_raw.append(entity.text)
            elif entity.label_ == "LOC":
                loc_raw.append(entity.text)
            elif entity.label_ == "ORG":
                org_raw.append(entity.text)

        #call functions
        self.NerOrg(org_raw)
        self.NerPer(per_raw)
        self.NerLoc(loc_raw)

    def __init__(self, text : str, tags : list):
        self.text = text
        self.tags = tags

        self.RakeGenerator()
        self.NerGenerator()

if __name__ == "__main__":
    nlp = spacy.load("xx_ent_wiki_sm")
    text = "Spojené arabské emiráty sa spájajú s krásnymi plážami, bohatou históriou či futuristickými veľkomestami v podobe Dubaja alebo Abu Dhabi. Avšak, Emiráty nie sú len o týchto dvoch, krajinu tvorí dokopy sedem emirátov, ktoré vytvárajú jedinečný charakter tejto arabskej krajiny.To, že obľuba Emirátov rastie a sú jednou z najlepších exotických destinácií, dokazujú aj dáta cestovnej kancelárie Pelikán – podľa nich v tomto roku rastie záujem o Emiráty o 40 percent v porovnaní s celým minulým rokom, ktorý bol pre ne rekordným.Záujmu dopomáhajú aj nízkonákladové spojenia maďarských aerolínií Wizz Air. Tie sa začínajú na cenovke od necelých 150 eur spiatočne s odletom z Budapešti. K dispozícii sú aj odlety z Viedne, Bratislavy, Katovíc či Krakova. Pre malých i veľkých: DubajMultikultúrny, progresívny, extravagantný a luxusný. Taký je Dubaj, druhý najväčší z emirátov, ktorý azda netreba nikomu predstavovať. Podľa najnovšieho prieskumu mu navyše patrí hneď druhá priečka medzi najlepšími destináciami na svete vhodnými pre rodiny. Prvenstvo zostalo v Emirátoch - v Abu Dhabi.Dubaj je mestom neobmedzených možností - ráno si možno zaplávať v mori a poobede už napríklad lyžovať na krytom svahu. Dominantou mesta je naďalej Burj Khalifa, ktorá cestovateľov sprevádza takmer na každom rohu. Najvyššia budova sveta stojí hneď vedľa spolu s najväčšou tancujúcou fontánou na svete.Samozrejmosťou je aj katalóg tých najlepších hotelov sveta. Za návštevu stojí i Old Dubai, v ktorom doteraz fungujú trhy so zlatom, textilom či korením, alebo niektorý z ostatných svetových rekordov destinácie - napríklad najväčšie vyhliadkové koleso Ain Dubai.Pre náročných dovolenkárov: Abu DhabiAbu Dhabi je najväčším emirátom a povinnou zastávkou pre tých, ktorí obdivujú púšte, oázy, divokú prírodu, panenské pobrežia i moderné veľkomestá. Obľúbeným miestom s krásnymi výhľadmi na okolitú prírodu je najvyšší bod emirátu – vrch Jebel Hafeet. Pozornosti milovníkov prírody by nemala uniknúť ani dychberúca oáza v Al Ain.Abu Dhabi je podobne ako neďaleký Dubaj futuristickým mestom s veľkolepými stavbami, krásnymi plážami a bohatým kultúrnym dedičstvom.Abu Dhabi je domovom Sheikh Zayed Grand Mosque najväčšej mešity Emirátov, rovnako neprehliadnuteľným je i prezidentský palác Qasr Al Watan. Bohatú históriu mesta možno obdivovať v Qasr Al Hosn - najstaršej stavbe v Abu Dhabi.Za návštevu stojí ostrov Yas Island, ktorý je svetoznámym centrom zábavy vhodným pre rodiny s deťmi. Na ostrove sa nachádza aj okruh Yas Marina Circuit, ktorý je každoročne dejiskom posledných pretekov v kalendári Formuly 1.Pre umelecké duše: ŠardžáŠardžá nemá núdzu o krásne mešity, historické centrá, múzeá či umelecké galérie. Emirát je centrom arabskej kultúry, pričom bohaté kultúrne dedičstvo jej rovnomenného najväčšieho mesta neušlo pozornosti UNESCA, ktoré mestu Šardžá udelilo titul hlavného mesta arabského sveta.Jedným z najatraktívnejších miest je centrálny trh Souk al-Markazi, kde možno vo viac ako 600 obchodíkoch nájsť tie najlepšie lokálne výrobky od výmyslu sveta a zažiť orient na vlastnej koži. Za históriou sa treba vydať do komplexu Sharjah Heritage Area, ktoré návštevníkov presunie do vyše sto rokov starej podoby mesta. Tretí najväčší emirát okrem kultúrnych pamiatok skrýva aj prírodné. Ostrov Al Noor je obľúbeným miestom pre prechádzku medzi tropickými rastlinami, navyše ostrov ponúka nádherný výhľad na panorámu mesta.Ťahákom emirátu je aj najväčšie safari mimo afrického kontinentu. V Sharjah Safari parku možno stretnúť žirafy, levy či nosorožce a ďalších 120 druhov zvierat. Deň plný zážitkov je najlepšie ukončiť na promenáde Al Majaz ponúkajúcej širokú škálu atrakcií pre malých i veľkých dovolenkárov. Pre milovníkov prírody: AdžmánNajmenší zo siedmich emirátov je zo západu ohraničený Perzským zálivom a z východu pohorím Hajar. Vďaka tomu sa môže pochváliť rozmanitou scenériou, ktorej dominujú slnkom zaliate pláže, atraktívne mestá a majestátne vrchy. Pohorie Hajar ponúka nádherné túry pre začiatočníkov i skúsených milovníkov náročnej turistiky. Odmenou za výstup sú bezkonkurenčné výhľady na okolité skaly i horské dedinky. Vzrušujúcim únikom do prírody je aj návšteva prírodnej rezervácie Al Zorah, ktorá je domovom pre takmer 60 druhov vtákov. Na svoje si neprídu len ornitológovia, ale aj dobrodruhovia, na ktorých tu čaká nemálo príležitostí na potápanie, plachtenie či kajaking. Samotné mesto Adžmán láka na luxusné hotelové rezorty vhodné pre rodiny s deťmi a promenády s množstvom reštaurácií. Za návštevu stojí miestne múzeum nachádzajúce sa v pevnosti z 18. storočia či prístav s tradičnými dhow loďami. Pre nadšencov vodných športov: FudžajraNajvýchodnejší emirát je pokojným, turistami menej prebádaným miestom, ktoré si zachováva svoju príjemnú a autentickú atmosféru. Napriek tomu, že je najhornatejším emirátom, lákadlom je aj pre milovníkov vodných športov, keďže práve Fudžajra ukrýva tie najlepšie lokality pre potápanie, šnorchlovanie či surfovanie.Najznámejšou z nich je ostrov Jazīrat al Ghubbah známy ako Snoopy Island. Koralový ostrovček priťahuje ľudí z celého sveta nielen vďaka tyrkysovej vode a bohatému podmorskému svetu, ale i adrenalínovému skákaniu z útesov či jazde na nafukovacom banáne.Ďalším populárnym miestom je Wadi Wurayah, ktoré sa stalou vôbec prvou chránenou horskou oblasťou v Spojených arabských emirátoch a je domovom jediného vodopádu v Emirátoch či niekoľkých prírodných bazénov. Pre odvážlivcov aj milovníkov relaxu: Ras Al KhaimahČoraz obľúbenejšou destináciou krajiny je emirát Ras Al Khaimah. Ten si pre dovolenkárov prichystal nádherné pláže, majestátne hory, pútavú históriu i adrenalínové dobrodružstvá. Emirát je však výbornou destináciou na relax na pláži, keďže práve tu vznikajú nové hotely známych značiek.Pri návšteve nemožno vynechať výlet do pohoria Hajar, nad ktorým sa týči Jebel Jais - najvyšší vrchol pohoria, ktorý je tiež domovom najdlhšej lanovej dráhy (zipline) sveta. Za zmienku stojí aj perlová farma Suwaidi Pearls, Národné múzeum Ras Al-Khaimah či pevnosť Dhayah.Známou atrakciou je dedina Jazirat Al Hamra známa ako mesto duchov. Jej ruiny vraj obývajú džinovia, ktorí spôsobujú zmätok a sú príčinou paranormálnych javov. Najsevernejší emirát je tiež obľúbeným miestom pre dovolenkové ničnerobenie. Biele piesočnaté pobrežie a luxusné rezorty sú tak ďalším dôvodom pre výber dovolenky v Ras Al Khaimah.Pre zvedavcov i rybárov: Umm Al QuwainHoci je Umm Al Quwain najmenej obývaným emirátom, v rebríčku nepreskúmaných lokalít mu patrí prvá priečka. Bohatá história emirátu siaha až do doby kamennej, dnes možno dávnu minulosť Umm Al Quwain spoznávať vďaka jednému z najvýznamnejších archeologických nálezísk Emirátov – Ed-Dur. Okrem historikov láka aj rodiny s deťmi, a to najmä kvôli akvaparku Dreamland – najväčšiemu vodnému parku v Spojených arabských emirátoch. Vodné dobrodružstvo priťahuje množstvo ďalších návštevníkov z celého sveta. V tomto prípade však nejde o akvaparky, ale o rybárčenie, keďže vody Umm Al Quwain sú tým najlepším miestom pre hlbokomorský rybolov. Napriek tomu, že v tomto emiráte dovolenkári nenájdu moderné mrakodrapy či luxusné rezorty, Umm Al Quwain zostáva nepreskúmaným klenotom a hodnoverným obrazom okúzľujúceho arabského sveta."

    print(TagGenerator(text=text, tags=[]).tags)