from calendar import monthrange
from datetime import datetime
from Pomodoro_Constructor import FULL, HALF, HEIGHT, LEFT_PLOT, RIGHT_PLOT, WIDTH, Pomodoro_Constructor, get_time_dict, sort_dict
from send_email import send_email
import pandas as pd
import config
from git import Repo

def commit(pdf):

    date = datetime.now()

    repo = Repo(config.repo)
    index = repo.index
    
    index.add(items=pdf)

    index.commit(message=f"Auto-committed {date.month-1 if date.month != 1 else 12}/{str(date.year if date.month != 1 else date.year-1)[-2:]} pomodoro report")

    origin = repo.remote(name='origin')
    origin.push()


def format_email(pdf, txt):

    subject = f"Pomodoro Report - {pdf.month} {pdf.year}"
    body = f"""
Ciao!

In allegato è presente il report mensile di pomodori completati nel mese di {pdf.month}
{txt}

Tommaso Crippa"""

    sender = config.sender
    password = config.api_key
    sender_name = config.name
    file = f"pdfs/Pomodoro Report - {pdf.month} {pdf.year}.pdf"
    receivers = config.receivers if date.day == 1 else [config.receivers[0]] # To avoid sending emails to others not involved

    for receiver in receivers:
        send_email(subject, body, 
                sender, receiver, 
                password, sender_name, file)

def seasonal(file, email=True):

    # pdf = Pomodoro_Constructor(file, "season")

    # pdf.save()

    pass

def yearly(file, save_pdf=True, send_pdf=True, commit_pdf=True):

    pdf = Pomodoro_Constructor(file, "year")

    pdf.add_new_page("Pomodori completati")

    num_pomodori = sum(pdf.df.pomodori[pdf.df.data.dt.to_period('Y').dt.to_timestamp() == pd.to_datetime(f'01-01-{pdf.year}')])

    num_giorni = len(pd.date_range(f"01-01-{pdf.year}", f"12-31-{pdf.year}", freq="D"))
    avg = round(num_pomodori/num_giorni, 2)

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
        txt = ""
        if avg < 1:
            txt = "In questo anno si poteva fare di meglio..."
        elif avg < avg_last:
            txt = "Continua così!"
        else:
            txt = "Stai andando alla grande!!!"
        format_email(pdf, txt)
    
    if commit_pdf:
        commit(str(pdf))

def monthly(file, save_pdf=True, send_pdf=True, commit_pdf=True):

    pdf = Pomodoro_Constructor(file, "month")

    pdf.add_new_page("Pomodori completati")

    num_pomodori = sum(pdf.df.pomodori[pdf.df.data.dt.to_period('M').dt.to_timestamp() == pd.to_datetime(f'{pdf.month_num}-01-{pdf.year}')])
    num_giorni = len(pd.date_range(f"{pdf.month_num}-01-{pdf.year}", f"{pdf.month_num}-{pdf.last_day}-{pdf.year}", freq="D"))
    avg = round(num_pomodori/num_giorni, 2)

    pdf.h1(WIDTH, x=15, y=40, txt=f"A {pdf.month} sono stati completati {num_pomodori} pomodori!")
    pdf.h2(WIDTH, x=15, y=58, txt=f"In media sono {avg} pomodori al giorno!")

    ore = num_pomodori*25//60
    minuti = num_pomodori*25%60
    
    pdf.h4(HALF, x=HALF, y=62, txt=f"Sono {ore} ore e {minuti} minuti!", align="R")

    pdf.plot_number_of_messages(x=LEFT_PLOT, y=80, w=FULL)
    
    pdf.image("images/quadrilatero.png", x=0, y=15+HEIGHT//2, w=WIDTH, h=HEIGHT//2)

    pdf.last_period(x=LEFT_PLOT, y=170, w=HALF, return_to=3)

    last = pdf.month_num-1 if pdf.month_num != 1 else 12
    num_pomodori_last = sum(pdf.df.pomodori[pdf.df.data.dt.to_period('M').dt.to_timestamp() == pd.to_datetime(f'{last}-01-{pdf.year}')])
    num_giorni_last = len(pd.date_range(f"{last}-01-{pdf.year}", f"{last}-{monthrange(pdf.year, (last)%13)[1]}-{pdf.year}", freq="D"))
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
        txt = ""
        if avg < 1:
            txt = "In questo mese si poteva fare di meglio..."
        elif avg < avg_last:
            txt = "Continua così!"
        else:
            txt = "Stai andando alla grande!!!"
        format_email(pdf, txt)
    
    if commit_pdf:
        commit(str(pdf))

if __name__ == "__main__":

    file = config.excel
    date = datetime.now()

    if date.day == 1:
        monthly(file)
        if date.month == 1:
            yearly(file)
    else:
        yearly(file, False, False)
    

