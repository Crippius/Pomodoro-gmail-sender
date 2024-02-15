from calendar import monthrange
from datetime import datetime
from Pomodoro_Constructor import FULL, HALF, HEIGHT, LEFT_PLOT, RIGHT_PLOT, WIDTH, THIRD, Pomodoro_Constructor
from send_email import send_email
import pandas as pd
import config
from git import Repo

def commit(pdf):

    date = datetime.now()

    repo = Repo(config.repo)
    index = repo.index
    
    index.add(f"{pdf.dir}/{pdf.filename}.pdf")
    if pdf.format != "degree":
        index.commit(message=f"Auto-committed {date.month-1 if date.month != 1 else 12}/{str(date.year if date.month != 1 else date.year-1)[-2:]} pomodoro report")
    else:
        index.commit(message=f"Auto-committed THE FINAL POMODORO REPORT")
    origin = repo.remote(name='origin')
    origin.push()


def format_email(pdf:Pomodoro_Constructor):

    date = datetime.now()
    
    if pdf.format == "month": 
        subject = f"Pomodoro Report - {pdf.month} {pdf.year}"
        file = f"{pdf.dir}/{pdf.filename}.pdf"
        avg = pdf.average()
        avg_last = pdf.average(-1)
        txt = ""
        if avg < 1:
            txt = "In questo mese si poteva fare di meglio..."
        elif avg < avg_last:
            txt = "Continua così!"
        else:
            txt = "Stai andando alla grande!!!"
        body = f"""
Ciao!

In allegato è presente il report mensile di pomodori completati nel mese di {pdf.month}
{txt}

Tommaso Crippa"""

    elif pdf.format == "year":
        subject = f"Pomodoro Report - {pdf.year}"
        file = f"{pdf.dir}/{pdf.filename}.pdf"
        avg = pdf.average()
        avg_last = pdf.average(-1)
        txt = ""
        if avg < 1:
            txt = "In questo anno si poteva fare di meglio..."
        elif avg < avg_last:
            txt = "Continua così!"
        else:
            txt = "Stai andando alla grande!!!"
        body = f"""
Ciao!

In allegato è presente il report annuale di pomodori completati nel {pdf.year}
{txt}

Tommaso Crippa"""        

    elif pdf.format == "degree":
        subject = f"Pomodoro Report - The Final Report"
        file = f"{pdf.dir}/{pdf.filename}.pdf"

        body = f"""
Ciao!

In allegato è presente il report di pomodori completati di TUTTA la Laurea Triennale
Buona lettura!!!

Tommaso Crippa"""        

    sender = config.sender
    password = config.api_key
    sender_name = config.name
    
    receivers = config.receivers

    for receiver in receivers:
        send_email(subject, body, 
                sender, receiver, 
                password, sender_name, file)
        

def degree(file, voti=None, save_pdf=True, send_pdf=True, commit_pdf=True):

    pdf = Pomodoro_Constructor(file=file, voti=voti, format="degree")

    pdf.add_new_page("Pomodori completati")

    num_pomodori = sum(pdf.df.pomodori)

    avg = pdf.average()

    pdf.h1(WIDTH, x=15, y=40, txt=f"In totale ho completato {num_pomodori} pomodori!")
    pdf.h2(WIDTH, x=15, y=58, txt=f"In media sono {avg} pomodori al giorno!")

    ore = num_pomodori*25//60
    minuti = num_pomodori*25%60
    
    pdf.h4(HALF, x=HALF, y=62, txt=f"Sono {ore} ore e {minuti} minuti!", align="R")

    pdf.plot_number_of_messages(x=LEFT_PLOT, y=80, w=FULL)
    
    pdf.image("images/quadrilatero.png", x=0, y=15+HEIGHT//2, w=WIDTH, h=HEIGHT//2)

    avg_anno =pdf.last_period(x=LEFT_PLOT, y=170, w=HALF, return_to=2)


    pdf.h3(WIDTH//2, x=HALF+15, y=170, txt=f"In media sono stati fatti")
    pdf.h3(WIDTH//2, x=HALF+15, y=180, txt=f"{avg_anno} pomodori per ogni")
    pdf.h3(WIDTH//2, x=HALF+15, y=190, txt=f"anno accademico")

    best, worst = pdf.confront_months(x=RIGHT_PLOT, y=210, w=HALF)

    pdf.h3(HALF-10, x=15, y=249, txt=f"Miglior mese: {best[0]} ({best[1]} pomodori)", align="R")
    pdf.h3(HALF-10, x=15, y=259, txt=f"Peggior mese: {worst[0]} ({worst[1]} pomodori)", align="R")

    if voti != None:
        for materia in pdf.voti[pdf.voti.anno == "Primo"].materia.unique():
            pdf.report_materia(materia)

    pdf.add_new_page("Periodi di studio")

    worst, best, weekend = pdf.plot_day_of_the_week(x=LEFT_PLOT, y=45, w=HALF)

    pdf.h3(w=WIDTH, x=HALF, y=60, txt=f"Miglior giorno: {best[0]} ({best[1]} pomodori)")
    pdf.h3(w=WIDTH, x=HALF, y=75, txt=f"Peggior giorno: {worst[0]} ({worst[1]} pomodori)")
    pdf.h3(w=WIDTH, x=HALF, y=90, txt=f"{weekend} pomodori fatti nei weekend")

    pdf.image("images/quadrilatero.png", x=0, y=122, w=WIDTH, h=HEIGHT//4+5)

    pdf.time_pivot_table(x=LEFT_PLOT, y=128, w=FULL)

    worst, best, night_hours = pdf.plot_time_of_messages(x=RIGHT_PLOT, y=210, w=HALF)
    
    pdf.h3(w=WIDTH//2, x=0, y=222, txt=f"Miglior periodo: {best[0]} ({best[1]} pomodori)", align="R")
    pdf.h3(w=WIDTH//2, x=0, y=237, txt=f"Peggior periodo: {worst[0]} ({worst[1]} pomodori)", align="R")
    pdf.h3(w=WIDTH//2, x=0, y=252, txt=f"{night_hours} pomodori fatti di notte", align="R")

    if voti != None:
        for materia in pdf.voti[pdf.voti.anno == "Secondo"].materia.unique():
            pdf.report_materia(materia)

    pdf.add_new_page("Progetti")

    pdf.h3(w=WIDTH, x=15, y=50, txt="La tesi consiste nel completamento di 3 progetti:")

    pdf.report_progetti(y=70, nome1="Algoritmi e Principi", nome2="dell'Informatica", github="progetto_api")
    
    num_pomodori = sum(pdf.df[(pdf.df.tipo == "PROGETTO") 
                            & ((pdf.df.materia == "Algoritmi e Principi dell'Informatica") |
                               (pdf.df.materia == "Reti Logiche") |
                               (pdf.df.materia == "Ingegneria del Software"))].pomodori)
    pdf.h3(w=WIDTH, x=0, y=120, txt=f"Numero totale di pomodori per questi progetti: {num_pomodori} ({round(num_pomodori*25/60, 2)} ore!)", align="C")
    
    pdf.report_progetti(y=140, nome1="Reti", nome2="Logiche", github="progetto_rl")

    voto_api = pdf.voti[pdf.voti.materia == "Progetto di Algoritmi e Principi dell'Informatica"].iloc[0].voto
    voto_api = int(voto_api) if voto_api != "30L" else 30
    voto_rl = pdf.voti[pdf.voti.materia == "Progetto di Reti Logiche"].iloc[0].voto
    voto_rl = int(voto_rl) if voto_rl != "30L" else 30
    voto_swing = pdf.voti[pdf.voti.materia == "Progetto di Ingegneria del Software"].iloc[0].voto
    voto_swing = int(voto_swing) if voto_swing != "30L" else 30
    punteggio = 1 + round((voto_api+voto_rl+3*voto_swing)/30, 2)
    pdf.h3(w=WIDTH, x=0, y=190, txt=f"Punteggio aggiunto al voto di laurea: 1+({voto_api}*1+{voto_rl}*1+{voto_swing}*3)/30 = {punteggio}", align="C")
    
    pdf.report_progetti(y=210, nome1="Ingegneria", nome2="del Software", github="progetto_swing")

    if voti != None:
        for materia in pdf.voti[pdf.voti.anno == "Terzo"].materia.unique():
            pdf.report_materia(materia)

    pdf.add_new_page("Conclusione")
    
    media=0

    pdf.set_draw_color(0, 255, 0)
    pdf.rect(x=0, y=60, w=HALF+4, h=39, style="D")
    pdf.rect(x=HALF+5, y=100, w=HALF+4, h=39, style="D")
    pdf.rect(x=0, y=181, w=HALF+4, h=38, style="D")
    pdf.rect(x=HALF+5, y=220, w=HALF+4, h=39, style="D")
    pdf.set_draw_color(255, 0, 255)
    pdf.rect(x=HALF+5, y=60, w=HALF+4, h=39, style="D")
    pdf.rect(x=0, y=100, w=HALF+4, h=39, style="D")
    pdf.rect(x=HALF+5, y=181, w=HALF+4, h=38, style="D")
    pdf.rect(x=0, y=220, w=HALF+4, h=39, style="D")


    pdf.set_draw_color(0, 0, 0)

    max_pom = 0
    max_materia = ""
    min_pom = float("+inf")
    min_materia = ""
    for mat in pdf.voti.materia.unique():
        if mat.split(" ")[0] == "Progetto" and mat.split(" ")[-1] != "Informatica":
            continue
        temp = sum(pdf.df[pdf.df.materia == mat].pomodori) 
        if temp > max_pom:
            max_pom = temp
            max_materia = mat
        if temp < min_pom:
            min_pom = temp
            min_materia = mat
        voto = pdf.voti[pdf.voti.materia == mat].iloc[0].voto
        voto = int(voto) if voto != "30L" else 30
        media += (voto/30) * pdf.voti[pdf.voti.materia == mat].iloc[0].cfu
    punteggio += (media/175)*110

    pdf.h3(w=HALF+5, x=0, y=60, txt="Materia più studiata:", align="C")
    pdf.h3(w=HALF+5, x=0, y=70, txt=f"{max_materia}", align="C")
    pdf.h3(w=HALF+5, x=0, y=80, txt=f"({max_pom} pomodori)", align="C")
    pdf.h3(w=HALF+5, x=HALF+5, y=60, txt="Materia meno studiata:", align="C")
    pdf.h3(w=HALF+5, x=HALF+5, y=70, txt=f"{min_materia}", align="C")
    pdf.h3(w=HALF+5, x=HALF+5, y=80, txt=f"({min_pom} pomodori)", align="C")

    max_qual = 0
    max_materia = ""
    min_qual = float("+inf")
    min_materia = ""
    for mat in pdf.voti.materia.unique():
        if mat.split(" ")[0] == "Progetto" and mat.split(" ")[-1] != "Informatica":
            continue
        temp_pom = sum(pdf.df[pdf.df.materia == mat].pomodori)
        temp_voto = pdf.voti[pdf.voti.materia == mat].iloc[0].voto
        temp_voto = int(temp_voto) if temp_voto != "30L" else 30
        temp = temp_pom / temp_voto
        if temp > max_qual:
            max_qual = temp
            max_materia = mat
        if temp < min_qual:
            min_qual = temp
            min_materia = mat

    pdf.h3(w=HALF+5, x=HALF+5, y=100, txt="Migliore qualità studio:", align="C")
    pdf.h3(w=HALF+5, x=HALF+5, y=110, txt=f"{min_materia}", align="C")
    pdf.h3(w=HALF+5, x=HALF+5, y=120, txt=f"({round(min_qual, 2)} # pomodori / 1 voto)", align="C")
    pdf.h3(w=HALF+5, x=0, y=100, txt="Peggiore qualità studio:", align="C")
    pdf.h3(w=HALF+5, x=0, y=110, txt=f"{max_materia}", align="C")
    pdf.h3(w=HALF+5, x=0, y=120, txt=f"({round(max_qual, 2)} # pomodori / 1 voto)", align="C")

    pdf.image("images/quadrilatero.png", x=0, y=140, w=WIDTH, h=40)
    pdf.line(x1=0, y1=140, x2=WIDTH, y2=140)
    pdf.line(x1=0, y1=180, x2=WIDTH, y2=180)

    pdf.h4(w=FULL, x=0, y=140, txt=f"Voto di laurea:", align="C")
    lode = "" if punteggio < 111 else " e lode"
    pdf.h0(w=FULL, x=0, y=142, txt=f"{int(round(punteggio, 0))}{lode}", align="C")

    pdf.h3(w=HALF+5, x=HALF+5, y=185, txt=f"Pomodori fatti di notte:", align="C")
    pdf.h3(w=HALF+5, x=HALF+5, y=195, txt=f"{night_hours} pomodori", align="C")


    pom = 0
    data = ""
    for dat in pdf.df.data.unique():
        temp = sum(pdf.df[pdf.df.data == dat].pomodori) 
        if temp > pom:
            pom = temp
            data = dat
    data = pd.to_datetime(data)
    pdf.h3(w=HALF+5, x=0, y=180, txt="Giorno più studioso:", align="C")
    pdf.h3(w=HALF+5, x=0, y=190, txt=f"{data.strftime('%d/%m/%y')}", align="C")
    pdf.h3(w=HALF+5, x=0, y=200, txt=f"({pom} pomodori)", align="C")
    
    max_app = 0
    max_materia = ""
    min_app = float("+inf")
    min_materia = ""
    for mat in pdf.voti.materia.unique():
        if mat.split(" ")[0] == "Progetto" and mat.split(" ")[-1] != "Informatica":
            continue
        temp = pdf.voti[pdf.voti.materia == mat].iloc[0].appunti
        if temp > max_app:
            max_app = temp
            max_materia = mat
        if temp < min_app:
            min_app = temp
            min_materia = mat

    pdf.h3(w=HALF+5, x=HALF+5, y=220, txt="Migliori appunti:", align="C")
    pdf.h3(w=HALF+5, x=HALF+5, y=230, txt=f"{max_materia}", align="C")
    pdf.h3(w=HALF+5, x=HALF+5, y=240, txt=f"({max_app}/5.0)", align="C")
    pdf.h3(w=HALF+5, x=0, y=220, txt="Peggiori appunti:", align="C")
    pdf.h3(w=HALF+5, x=0, y=230, txt=f"{min_materia}", align="C")
    pdf.h3(w=HALF+5, x=0, y=240, txt=f"({min_app}/5.0)", align="C")


    if not save_pdf:
        pdf.save(dir="test_pdfs")
        return
    pdf.save()

    if send_pdf:
        format_email(pdf)
    
    if commit_pdf:
        commit(pdf)


def yearly(file, save_pdf=True, send_pdf=True, commit_pdf=True):

    pdf = Pomodoro_Constructor(file=file, format="year")

    pdf.add_new_page("Pomodori completati")

    num_pomodori = sum(pdf.df.pomodori[pdf.df.data.dt.to_period('Y').dt.to_timestamp() == pd.to_datetime(f'01-01-{pdf.year}')])

    avg = pdf.average()

    pdf.h1(WIDTH, x=15, y=40, txt=f"Nel {pdf.year} sono stati completati {num_pomodori} pomodori!")
    pdf.h2(WIDTH, x=15, y=58, txt=f"In media sono {avg} pomodori al giorno!")

    ore = num_pomodori*25//60
    minuti = num_pomodori*25%60
    
    pdf.h4(HALF, x=HALF, y=62, txt=f"Sono {ore} ore e {minuti} minuti!", align="R")

    pdf.plot_number_of_messages(x=LEFT_PLOT, y=80, w=FULL)
    
    pdf.image("images/quadrilatero.png", x=0, y=15+HEIGHT//2, w=WIDTH, h=HEIGHT//2)

    pdf.last_period(x=LEFT_PLOT, y=170, w=HALF, return_to=2)

    last = pdf.year-1
    num_pomodori_last = sum(pdf.df.pomodori[pdf.df.data.dt.to_period('Y').dt.to_timestamp() == pd.to_datetime(f'01-01-{last}')])
    num_giorni_last = len(pd.date_range(f"01-01-{last}", f"12-31-{last}", freq="D"))
    avg_last = round(num_pomodori_last/num_giorni_last, 2)

    pdf.h3(WIDTH//2, x=HALF+15, y=175, txt=f"{'+' if num_pomodori-num_pomodori_last > 0 else '-'}{round(abs(num_pomodori-num_pomodori_last), 2)} in {'meno' if num_pomodori-num_pomodori_last<0 else 'più'} dello scorso anno")
    pdf.h3(WIDTH//2, x=HALF+15, y=190, txt=f"({'+' if num_pomodori-num_pomodori_last > 0 else '-'}{round(abs(avg-avg_last), 2)} pomodori al giorno)")

    best, worst = pdf.confront_months(x=RIGHT_PLOT, y=210, w=HALF)

    pdf.h3(HALF-10, x=15, y=249, txt=f"Miglior mese: {best[0]} ({best[1]} pomodori)", align="R")
    pdf.h3(HALF-10, x=15, y=259, txt=f"Peggior mese: {worst[0]} ({worst[1]} pomodori)", align="R")

    pdf.add_new_page("Attività dell'anno")
    
    worst, best, weekend = pdf.plot_day_of_the_week(x=LEFT_PLOT, y=45, w=HALF)

    pdf.h3(w=WIDTH, x=HALF, y=60, txt=f"Miglior giorno: {best[0]} ({best[1]} pomodori)")
    pdf.h3(w=WIDTH, x=HALF, y=75, txt=f"Peggior giorno: {worst[0]} ({worst[1]} pomodori)")
    pdf.h3(w=WIDTH, x=HALF, y=90, txt=f"{weekend} pomodori fatti nei weekend")

    pdf.image("images/quadrilatero.png", x=0, y=122, w=WIDTH, h=HEIGHT//4+5)
    
    pdf.plot_classes(x=LEFT_PLOT, y=125, w=HALF)

    pdf.plot_type_of_study(x=RIGHT_PLOT, y=130, w=HALF)

    worst, best, night_hours = pdf.plot_time_of_messages(x=RIGHT_PLOT, y=210, w=HALF)
    
    pdf.h3(w=WIDTH, x=15, y=220, txt=f"Miglior periodo: {best[0]} ({best[1]} pomodori)")
    pdf.h3(w=WIDTH, x=15, y=235, txt=f"Peggior periodo: {worst[0]} ({worst[1]} pomodori)")
    pdf.h3(w=WIDTH, x=15, y=250, txt=f"{night_hours} pomodori fatti di notte")

    if not save_pdf:
        pdf.save(dir="test_pdfs")
        return
    pdf.save()

    if send_pdf:
        format_email(pdf)
    
    if commit_pdf:
        commit(pdf)

def monthly(file, save_pdf=True, send_pdf=True, commit_pdf=True):

    pdf = Pomodoro_Constructor(file=file, format="month")

    pdf.add_new_page("Pomodori completati")

    num_pomodori = sum(pdf.df.pomodori[pdf.df.data.dt.to_period('M').dt.to_timestamp() == pd.to_datetime(f'{pdf.month_num}-01-{pdf.year}')])
    
    avg = pdf.average()

    pdf.h1(WIDTH, x=15, y=40, txt=f"A {pdf.month} sono stati completati {num_pomodori} pomodori!")
    pdf.h2(WIDTH, x=15, y=58, txt=f"In media sono {avg} pomodori al giorno!")

    ore = num_pomodori*25//60
    minuti = num_pomodori*25%60
    
    pdf.h4(HALF, x=HALF, y=62, txt=f"Sono {ore} ore e {minuti} minuti!", align="R")

    pdf.plot_number_of_messages(x=LEFT_PLOT, y=80, w=FULL)
    
    pdf.image("images/quadrilatero.png", x=0, y=15+HEIGHT//2, w=WIDTH, h=HEIGHT//2)

    pdf.last_period(x=LEFT_PLOT, y=170, w=HALF, return_to=3)

    last_month = pdf.month_num-1 if pdf.month_num != 1 else 12
    last_year =  pdf.year if pdf.month_num != 1 else pdf.year-1
    num_pomodori_last = sum(pdf.df.pomodori[pdf.df.data.dt.to_period('M').dt.to_timestamp() == pd.to_datetime(f'{last_month}-01-{last_year}')])
    num_giorni_last = len(pd.date_range(f"{last_month}-01-{last_year}", f"{last_month}-{monthrange(last_year, (last_month)%13)[1]}-{last_year}", freq="D"))
    avg_last = round(num_pomodori_last/num_giorni_last, 2)

    pdf.h3(WIDTH//2, x=HALF+15, y=175, txt=f"{'+' if num_pomodori-num_pomodori_last > 0 else '-'}{round(abs(num_pomodori-num_pomodori_last), 2)} in {'meno' if num_pomodori-num_pomodori_last<0 else 'più'} dello scorso mese")
    pdf.h3(WIDTH//2, x=HALF+15, y=190, txt=f"({'+' if num_pomodori-num_pomodori_last > 0 else '-'}{round(abs(avg-avg_last), 2)} pomodori al giorno)")

    this_year, last_year = pdf.confront_months(x=RIGHT_PLOT, y=210, w=HALF)

    pdf.h3(HALF-20, x=15, y=249, txt=f"{'+' if this_year-last_year > 0 else '-'}{abs(this_year-last_year)} in {'meno' if this_year-last_year<0 else 'più'} dello scorso anno", align="R")
    pdf.h3(HALF-20, x=15, y=259, txt=f"({'+' if this_year-last_year > 0 else '-'}{round(abs((this_year/pdf.last_day)-(last_year/pdf.last_day)), 2)} pomodori al giorno)", align="R")
    
    pdf.add_new_page("Attività del mese")

    worst, best, weekend = pdf.plot_day_of_the_week(x=LEFT_PLOT, y=50, w=HALF)

    pdf.h3(w=WIDTH, x=HALF, y=60, txt=f"Miglior giorno: {best[0]} ({best[1]} pomodori)")
    pdf.h3(w=WIDTH, x=HALF, y=75, txt=f"Peggior giorno: {worst[0]} ({worst[1]} pomodori)")
    pdf.h3(w=WIDTH, x=HALF, y=90, txt=f"{weekend} pomodori fatti nei weekend")

    pdf.image("images/quadrilatero.png", x=0, y=126, w=WIDTH, h=HEIGHT//4)

    pdf.plot_classes(x=LEFT_PLOT, y=130, w=HALF)

    pdf.plot_type_of_study(x=RIGHT_PLOT, y=130, w=HALF)

    worst, best, night_hours = pdf.plot_time_of_messages(x=RIGHT_PLOT, y=210, w=HALF)
    
    pdf.h3(w=WIDTH, x=15, y=220, txt=f"Miglior periodo: {best[0]} ({best[1]} pomodori)")
    pdf.h3(w=WIDTH, x=15, y=235, txt=f"Peggior periodo: {worst[0]} ({worst[1]} pomodori)")
    pdf.h3(w=WIDTH, x=15, y=250, txt=f"{night_hours} pomodori fatti di notte")
    
    if not save_pdf:
        pdf.save(dir="test_pdfs")
        return
    pdf.save()

    if send_pdf:
        format_email(pdf)
    
    if commit_pdf:
        commit(pdf)

if __name__ == "__main__":

    file = config.excel
    date = datetime.now()

    if date.day == 1:
        monthly(file)
        if date.month == 1:
            yearly(file)
    

