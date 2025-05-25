article_analysis_prompt_ee = """
Tee põhjalik analüüs esitatud artiklist, järgides järgmisi juhiseid. **Vastus peab olema esitatud eesti keeles.**

**1. Informatsiooni väljavõtmine:**

*   **Poliitilised parteid:** Tuleta meelde ja loetle *ainult* need poliitilised parteid, mis on artiklis mainitud *ja* mis esinevad järgmises nimekirjas. Kasuta *originaalseid partei nimetusi*:
    *   Eesti Keskerakond
    *   Eesti Konservatiivne Rahvaerakond
    *   EESTIMAA ÜHENDATUD VASAKPARTEI
    *   Eesti Rahvuslased ja Konservatiivid
    *   Eesti Reformierakond
    *   Eesti Vabaduspartei - Põllumeeste Kogu
    *   Erakond Eesti 200
    *   Erakond Eestimaa Rohelised
    *   Erakond Parempoolsed
    *   ISAMAA Erakond
    *   KOOS organisatsioon osutab suveräänsusele
    *   Sotsiaaldemokraatlik Erakond
    *   Vabaerakond Aru Pähe
    *   Rahva Ühtsuse Erakond

    *Ignoreeri kõiki muid mainitud poliitilisi organisatsioone või parteisid, mis ei kuulu sellesse nimekirja.*
    **Nimetuste vastavus:** Ole tähelepanelik lühendite, kõnekeelsete ja alternatiivsete partei nimede ning akronüümide puhul.
    
    Kasuta artikli konteksti ja oma teadmisi, et määrata, millisele parteile kuulub vastav mainimine.

*   **Poliitikud:** Tuleta meelde ja loetle *kõik* mainitud poliitikud (sealhulgas riigiteenistujad, valimistel kandideerivad isikud, partei juhid jne). Kasuta täisnimesid ja vajadusel ametikohti. *Määratle iga poliitiku praegune parteiline kuuluvus*. Väldi dubleerimist.

**2. Toonuse analüüs (sentimendi analüüs):**

*   **Autori suhtumise hindamine:** Iga *mainitud partei* (üleval olevast nimekirjast) ja *kõigi* mainitud poliitikute puhul määra autori suhtumine, kasutades skaalat 0 kuni 10, kus:
    *   0: Väga negatiivne suhtumine.
    *   5: Neutraalne suhtumine.
    *   10: Väga positiivne suhtumine.

*   **Suhtumise mõju parteide hindamisele:**  *Kui parteid ei mainita otseselt, aga mainitakse poliitikuid, kes on partei *praegused* liikmed, siis peab autori suhtumine nende poliitikute suhtes *mõjutama* partei suhtumise hindamist.*

*   **Hindamise põhjendus:** Iga hindamise jaoks (parteide ja poliitikute puhul) esita lühike, kuid *konkreetne* põhjendus, viidates või tsiteerides *konkreetseid lauseid, sõnu või väiteid* artikli tekstist, mis kinnitavad sinu hindamist. Ära kirjuta lihtsalt "neutraalne mainimine", vaid selgita, *miks* sa seda neutraalseks pead (näiteks "Mainitakse ainult sündmuse osalejate loetelus, ilma hinnanguteta"). *Parteide hindamise põhjenduses tooda välja, kas poliitikute suhtumine mõjutas hindamist ja kui jah, siis kuidas.*
*   **Vahepealne lugemine:** Arvesta konteksti, irooniat, sarkasmi, varjatud vihjeid ja muid retoorilisi vahendeid, mis võivad viidata autori tegelikule suhtumisele, isegi kui see ei ole otseselt väljendatud.

**3. Objektiivsuse hindamine:**

*   **Pealkiri:** Hinda artikli *pealkirja* objektiivsust skaalal 0 kuni 10 (0 - väga kallutatud, 10 - täiesti objektiivne). Esita põhjendus. Arvesta, kas pealkiri peegeldab artikli sisu, kas kasutatakse emotsionaalselt värvitud keelt, liialdusi või moonutusi.
*   **Artikli tekst:** Hinda kogu artikli teksti objektiivsust skaalal 0 kuni 10 (0 - väga kallutatud, 10 - täiesti objektiivne). Esita põhjendus. Arvesta, kas esitatakse erinevaid seisukohti, kas kasutatud on usaldusväärseid allikaid, kas esinevad faktide või arvamuste manipuleerimise tunnused."""