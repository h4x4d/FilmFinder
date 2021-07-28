import sqlite3
import os
conn = sqlite3.connect('data.db')
cur = conn.cursor()
r = 0
mas = ['а', 'б', 'в', ' ', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

n = ['A_zori_zdes_tikhiye_CD1_RUS_1972.srt', 'Back_to_the_future_RUS_1985b.srt', 'Beautiful_mind_CD2_RUS_2001.srt', 'Blind_Side_RUS_2009_20100603021226.srt', 'Brat_2_RUS_2000.srt', 'Brat_RUS_1997.srt', 'Coco.2017.DVDScr.XVID.AC3.HQ.Hive-CM8[EtMovies].srt', 'Dark_Knight_RUS_2008_20081211182812.srt',  'Dvadtsatyj_vek_nachinaetsya_CD2_RUS_1986.srt', 'Dzhango.Osvobozhdennyi.2012.R.srt', 'Fight_Club_RUS_1999z.srt', 'Forrest_Gump_CD1_RUS_1994y.srt', 'Gladiator_RUS_2000a.srt', 'Godfather_RUS_1972t.srt', 'Green_Book_2018_DVDScr_Xvid_AC3_HQ_Hive-CM8.rus.srt', 'Green_Mile_1999d.srt', 'Heart_Of_A_Dog_RUS_1988_20120608171305.srt', 'Heavens_Door_RUS_2009_20091121173223.srt', 'Inside_Out_RUS_2015_20151018104653.srt', 'Interstellar.2014.D.DVDScr.srt', 'Iron_giant_RUS_1999.srt', 'Ivan_Vasiljevich_menjaet_professiju_RUS_1973.srt', 'Leon_RUS_1994g.srt', 'Life_is_beautiful_RUS_1997.SRT', 'Lock_Stock_2_Smoking_Barrels_RUS_1998a.srt', 'Matrix CD1 RU.srt', 'Monsters_Inc_RUS_2001_d.srt', 'Ofitsery_RUS_1971.srt', 'Ostrov_sokrovich_01_RUS_1988.srt', 'Pianist_RUS_2002s.srt', 'Pirats_ of_The_Caribbean_(2003)_(RUS)_(F)_CD1.srt', 'Princess_Mononoke_CD1_RUS_1997.srt', 'Pulp_fiction_RUS_1994h.srt', 'Seven_Pounds_RUS_2008_20090205164606.srt', 'shawshank_hoh.srt', 'Shrek_RUS_2001_g.srt', 'Shutter Island.srt', 'Silence_of_the_lambs_RUS_1991.srt', 'Snatch_RUS_2000_g.srt', 'Soul_RUS_2020_20210306221255.srt', 'Spirited_away_RUS_2001.srt', 'Spisok.Shindlera.1993.RUS.srt', 'Tajna_tretjej_planety_RUS_1981.srt', 'The Prestige (2006) rus.srt', 'The.Lion.King.2019.1080p.BluRay.x264-SPARKS.srt', 'The_Return_Of_The_King_SSE_RU.srt', 'Titanic_RUS_1997.SRT', 'WALLE_RUS_2008_20090522120915.srt', 'Клаус_2019_WEB-DLRip.srt', 'Ушедшие.srt']
for i in n:
    f = open(i, 'r')
    d = f.read().split('\n\n')
    d = [i.strip().split('\n') for i in d]
    q = []
    for i in d:
        try:
            s = i[1].split(' --> ')
            w = ' '.join(i[2:])
            o = w.lower()
            newtext = ''
            for k in o:
                if k in  mas:
                    newtext += k
            s.append(w)
            s.append(newtext)
            s.append(r)
            q.append(s)

        except ValueError and IndexError:
            pass
    r += 1
    print(r)
    cur.executemany("INSERT INTO subtitles VALUES(?, ?, ?, ?, ?);", q)
    conn.commit()
