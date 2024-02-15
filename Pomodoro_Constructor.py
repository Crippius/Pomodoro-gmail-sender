import pandas as pd # To store all the informations inside a Dataframe
import matplotlib.pyplot as plt # To plot all the data in a meaningful way
import numpy as np # For those sweeeeet and useful languages

from matplotlib import rcParams # To change the font used by matplotliv
import matplotlib.font_manager as fm
from matplotlib.ticker import MaxNLocator

from fpdf import FPDF # To create and deploy the PDF that can later be downloaded

from datetime import datetime, timedelta # To manipulate dates
from shutil import move # To move the pdf inside the correct directory
from os import remove, path # To remove the images created
from math import pi # To use polar coordinates in spider plot
from calendar import monthrange
from plot_calendar import plot_calendar

HEIGHT = 297 # Height of PDF
WIDTH = 210 # Width of PDF

PLOT_HEIGHT = 75 # Height of plot inside PDF
LEFT_PLOT = 5 # Plot in left side of PDF
RIGHT_PLOT = WIDTH//2 # right side of PDF

FULL = WIDTH-10
HALF = (WIDTH//2)-5
THIRD = WIDTH//3


COLORS = ("#f35243", "#fedfbe", "#f37d43", "#f3437d", "#f3aa43", "#fecfbe", "#febecd", "#feefbe", "#fd9773", "#fdaa8c", "#fee2d7")


def spider_plot(categories:list, values:list) -> None: # DESCRIPTION: Create spider plot 
    # PARAMETERS: categories (list): labels to add on top of plot | values (list): values that need to be plotted

    angles = [n / float(len(categories)) * 2 * pi for n in range(len(categories))] # Getting angles
    
    angles += angles[:1] # Adding first value to both lists (needed to close the circle)
    values += values[:1] 

    ax = plt.subplot(111, polar=True)
    plt.xticks(angles[:-1], categories)

    ax.set_rlabel_position(0)
    first_digit = int(str(max(values))[0]) # Setting up labels to read the graph better
    if first_digit < 5:
        labels = [i*10**(len(str(max(values)))-1) for i in [j for j in (1, 2, 3, 4) if j*6/5<first_digit]] + [max(values)]
    else:
        labels = [i*10**(len(str(max(values)))-1) for i in [j for j in (2, 4, 6, 8) if j*6/5<first_digit]] + [max(values)]

    plt.yticks(labels, [str(i) for i in labels], color="grey")
    plt.ylim(0,max(values)*12/10 if max(values) != 0 else 10)
    
    ax.plot(angles, values, linewidth=1, linestyle='solid', color="#f35243")
    ax.fill(angles, values, alpha=0.5, color="#fedfbe") # Creating plot


def inverted_barh_plot(y:list, x:list) -> None: # DESCRIPTION: Invert barh plot (instead of left to right -> right to left):
    # PARAMETERS: y (list): labels for barh plot | x (list): values of barh plot            |########     ->       #######|                                                                     |###          ->           ###|

    fig, ax = plt.subplots() 

    ax.barh(y, x, align='center', color='#26d367')
    ax.set_yticks([]) # Removing labels
    ax.set_yticklabels([])

    ax.invert_yaxis()
    ax.invert_xaxis() # Inverting axes
    ax2 = ax.twinx()

    ax2.set_ylim(ax.get_ylim())
    ax2.set_yticks(y) # Setting up labels again



def get_time_dict(df, weekday=False):
    x_pos = [timedelta(hours=i//2, minutes=30*(i%2)) for i in range(0, 48)]
    x_pos[6:]+x_pos[:6]

    if not weekday:
        slotted_dict = {i:0 for i in x_pos}
    else:
        slotted_dict = {}

    for _, row in df.iterrows():
        if not pd.isnull(row.orario) and row.orario != 0:
            orario = pd.to_timedelta(row.orario[:5]+":00")
            giorno = row.data.day_name()
            for i in range(row.pomodori):
                if weekday:
                    if (giorno, orario) not in slotted_dict:
                        slotted_dict[(giorno, orario)] = 0
                    slotted_dict[(giorno, orario)] += 1
                else:
                    slotted_dict[orario] += 1
                orario += timedelta(minutes=30)
                if orario == timedelta(days=1):
                    orario -= timedelta(days=1)

    return slotted_dict



def add_labels_to_bar(plot:plt, labels:list, font_size:int=18, dir:str="vertical", pos:str="external") -> None: 
    # DESCRIPTION: Adds auxiliary labels near the sides of the bars 
    # PARAMETERS: plot (plt) = plot in which the labels need to be added | labels (str) = string that need to be annotated
    # prop (font) = font used to write labels | font_size (int) = size of font | dir (str) = direction of plot (horizontal or vertical)
    # pos (str) = put labels on top of bar or just outside it (internal or external)

    #TODO: add external/internal options to vertical bars
    if dir == "vertical": 
        plt.ylim(0, plt.ylim()[1]+plt.ylim()[1]/10) # Make plot larger to create space for labels
        maxi = max([rect1.get_height() for rect1 in plot]) # Biggest y value in plot

        for rect1, label in zip(plot, labels): 
            plt.annotate(
                label, 
                (rect1.get_x() + rect1.get_width()/2, rect1.get_height()+maxi/100), # x and y positions
                ha="center",
                va="bottom",
                fontsize=font_size
            )
            
    else: 
        plt.xlim(0, plt.xlim()[1]+plt.xlim()[1]/10)
        maxi = max([rect1.get_y() for rect1 in plot]) # Biggest x value in plot

        for rect1, label in zip(plot, labels):

            if pos == "external":
                x = rect1.get_y() + rect1.get_width()+maxi/100
                ha = "right"
            else:
                x = plt.xlim()[1]/50
                ha = "left"

            plt.annotate(
                label,
                (x, rect1.get_y()),
                ha=ha,
                va="bottom",
                fontsize=font_size,
            )
    
    return


def concentrate_values(in_dict:dict, max_values:int, others:bool, lang="en") -> dict: 
    # DESCRIPTION: make dictionary smaller by remvoing keys with smaller values
    # PARAMETERS: in_dict (dict) = dictionary that is going to be modified | max_values (int) = number of unique dict keys
    # others (bool) = add additional key with sum of values of the last keys in it

    if len(in_dict.keys()) <= max_values: # If dict already smaller than the maximum value, don't modify it
        return in_dict
    
    out_dict = {}
    for i in list(in_dict.keys())[:max_values-others]:
        out_dict[i] = in_dict[i]
    
    if others:                                                                                          # N.B. "altri" == "others"
        if len(list(in_dict.keys())[max_values-others:]) == 1: # Edge case: when only one key is remaining, don't show "Altri", but the key
            out_dict[list(in_dict.keys())[max_values-others]] = in_dict[list(in_dict.keys())[max_values-others]]
        else:
            txt = {"en":"Others", "it":"Altri"}
            out_dict[txt[lang]] = sum([i for i in list(in_dict.values())[max_values-others:]])
    
    return out_dict


def sort_dict(in_dict:dict, max_values:int=-1, reverse:bool=True, others:bool=True, lang="en") -> dict: 
    # DESCRIPTION: Given a dict, it sorts its keys by its values (and concentrates them if its wanted)
    # PARAMETERS: in_dict (dict) = dictionary that is modified | max_values (int) = number of unique dict keys (if -1 no maximum)
    # reverse (bool) = return dict in decreasing order if true | others (bool) = include condensed keys w/ smaller keys

    out_dict = {}
    sorted_keys = sorted(in_dict, key=in_dict.get, reverse=True) 
    for w in sorted_keys:
        out_dict[w] = in_dict[w]

    if max_values != -1: # Concentrating keys (if wanted)
        out_dict = concentrate_values(out_dict, max_values, others, lang)

    if reverse: # Reversing (if true)
        out_dict = {k:out_dict[k] for k in list(out_dict.keys())[::-1]}

    return out_dict


def max_and_index(lst:list) -> tuple: # DESCRIPTION: returns the maximum value and the index in which it is placed
    # PARAMETERS: lst (list): list that needs to be checked
    # RETURNS: tuple (int, int): maximum value and its index in the list

    best = float("-inf")
    best_index = -1
    for i in range(len(lst)):
        if type(lst[i]) != int:
            continue
        if lst[i] > best:
            best = lst[i]
            best_index = i
    return best, best_index


def add_nl(string:str, newline:int=10):
    new_str = ""
    curr_line = 0
    for word in string.split(" "):
        length = len(word)
        if length+curr_line > newline:
            if length < newline:
                new_str += "\n"+word
                curr_line = length
            else:
                new_str += "\n" if len(new_str) != 0 else ""
                times = 0
                while len(word[times*newline:]) < newline:
                    new_str += word[times*newline:(times+1)*newline]+"\n"
                    times += 1
                new_str += word[times*newline:]
                curr_line = len(string[times*newline:])
        else:
            new_str += " "+word
            curr_line += 1+length
    return new_str



class Pomodoro_Constructor(FPDF): # Main class that is used in this program, inherits FPDF class, adding new functionalities

    month_dict = {1:"Gennaio", 2:"Febbraio", 3:"Marzo", 4:"Aprile", 5:"Maggio", 6:"Giugno", 
                  7:"Luglio", 8:"Agosto", 9:"Settembre", 10:"Ottobre", 11:"Novembre", 12:"Dicembre"}
    
    def __init__(self, file:str, voti:str="", format:str="month", month:int=0, year:int=0): 

        # DESCRIPTION: Initialize class, with FPDF's initialization a dataframe is created and cleaned,
        # the group (or chatters) name and a counter are stored, Structure with basic info is built
        
        if not path.exists(file):
            print("No such file exists")
            self.ok = 0
        else:
            self.ok = 1

        if month != 0 and month in range(1, 12+1):
            self.month_num = month
        else:
            self.month_num = datetime.now().month-1 if datetime.now().month-1 != 0 else 12
        
        self.month = self.month_dict[self.month_num]

        if year != 0:
            self.year = year
        else:
            self.year = datetime.now().year-1 if self.month_num == 12 else datetime.now().year

        self.last_day = monthrange(self.year, self.month_num)[1]

        self.format = format
        
        self.dir = f"pdfs/{self.year}"
        if self.format == "month":
            str_num = str(self.month_num) if self.month_num >= 10 else "0"+str(self.month_num)
            self.filename = f"Pomodoro Report - {str_num} {self.month} {self.year}"
        elif self.format == "year":
            self.filename = f"Pomodoro Report - {self.year}"
        elif self.format == "degree":
            self.filename = f"Pomodoro Report - The Final Report"

        FPDF.__init__(self) 

        self.counter = 0

        self.df = pd.read_excel(file) # Creating Dataframe
        self.df.columns = ["data", "materia", "tipo", "pomodori", "orario"]

        if voti != "":
            if not path.exists(file):
                print("No such file exists")
                self.ok = 0
            else:
                self.ok = 1
            self.voti = pd.read_excel(voti)
            self.voti.columns = ["materia", "voto", "cfu", "anno", "semestre", "prof", "tipo", "colore", "appunti"]


        fe = fm.FontEntry(
            fname="C:/Users/cripp/Google Drive/programming/repos/pomodoro-gmail-sender/fonts",
            name='Bebas Neue')
        fm.fontManager.ttflist.insert(0, fe) # or append is fine
        rcParams['font.family'] = fe.name # = 'your custom ttf font name'
        rcParams["xtick.labelsize"] = 18
        rcParams["ytick.labelsize"] = 18
        rcParams["font.size"] = 20
        rcParams['figure.titlesize'] = 20
        self.add_font('Bebas', '', "fonts/BebasNeue.ttf")

        self.add_first_page()

    def __str__(self):

        form = {"month":f"{self.month} {self.year}",
                "year":f"{self.year}",
                "degree":f"The Final Report"} # Needs to change
                
        return f"pdfs/Pomodoro Report - {form[self.format]}.pdf"


    def add_first_page(self): # DESCRIPTION: Adding the background of the pdf + aestethics

        self.add_page()
        self.image('images/background.png', x=70, y=0, w = 2*WIDTH//3, h = HEIGHT)
        self.image('images/pomodoro.png', x=90, y=20, w=HALF+5)
        self.image('images/linea.png', x=70, y=0, w = 3, h = HEIGHT)
        self.set_font("Bebas", size=60)
        self.set_text_color(255, 255, 255)

        if self.format == "month":
            self.image(f'images/{self.month.lower()}.png', x = 0, y = 0, w = WIDTH//3, h = HEIGHT)
            txt = f"REPORT MENSILE\n{self.month} {self.year}"
            self.set_xy(77, 100)
            self.cell(WIDTH, 30, "REPORT MENSILE")
            self.set_xy(77, 130)
            self.cell(WIDTH, 30, f"{self.month} {self.year}")
        elif self.format == "year":
            self.image(f'images/anno.png', x = 0, y = 0, w = WIDTH//3, h = HEIGHT)
            self.set_xy(77, 100)
            self.cell(WIDTH, 30, "REPORT ANNUALE")
            self.set_xy(77, 130)
            self.set_font_size(100)
            self.cell(WIDTH, 40, f"{self.year}")
        elif self.format == "degree":
            self.set_font_size(55)
            self.image(f'images/laurea.png', x = 0, y = 0, w = WIDTH//3, h = HEIGHT)
            self.set_xy(77, 100)
            self.cell(WIDTH, 30, "REPORT FINALE")
            self.set_xy(77, 130)
            self.set_font_size(85)
            self.cell(WIDTH, 40, f"Laurea")
            self.set_xy(77, 160)
            self.cell(WIDTH, 40, f"Triennale")

            
        else:
            self.image(self.image(f'images/linea.png', x = 0, y = 0, w = WIDTH//3, h = HEIGHT))
            self.set_xy(77, 100)
            self.cell(WIDTH, 30, "ERRORE")
        
        self.set_auto_page_break(False)
        self.set_xy(0, -30)
        self.set_font_size(20)
        self.multi_cell(FULL, 10, "Tommaso Crippa\nThe Pomodoro Technique", align="R")
        
        self.set_xy(5+WIDTH//3, -20)
        self.set_font_size(15)
        self.cell(FULL, 10, "1 pomodoro == 25 minuti")

        self.set_text_color(0, 0, 0)

    
    def add_new_page(self, title):
        self.add_page()
        self.image(f'images/triangolo.png', x = WIDTH-50, y = 0, w=50, h=50)

        self.set_xy(15, 0)
        self.set_font_size(50)
        self.cell(WIDTH, 50, title)
        self.ln(40)


    def update_counter(self) -> None: # Simple function that updates counter
        self.counter += 1
    

    def add_image(self, x:int, y:int, w:int) -> None: # Adds image to pdf file, given x and y coordinates
        self.image(f"{self.counter}.png", x = x, y = y, w = w, h=PLOT_HEIGHT)

    
    def prep(self, plot:bool=True) -> bool: # DESCRIPTION: Does necessary preparations before starting function
        # PARAMETERS: plot (bool): updates counter and closes last plot before starting if True

        if plot:
            self.update_counter()
            plt.close()
        
    
    def h0(self, w, txt, x=0, y=0, align=""):
        self.set_x(15)
        if not (x==0 and y == 0):
            self.set_xy(x, y)

        self.set_font_size(45)
        self.set_font(style="U")
        self.multi_cell(w, 45, txt, align=align)
        self.set_font(style="")
    
    def h1(self, w, txt, x=0, y=0, align=""):
        self.set_x(15)
        if not (x==0 and y == 0):
            self.set_xy(x, y)

        self.set_font_size(30)
        self.multi_cell(w, 30, txt, align=align)
        self.set_font(style="")
    
    def h2(self, w, txt, x=0, y=0, align=""):
        self.set_x(15)
        if not (x==0 and y == 0):
            self.set_xy(x, y)

        self.set_font_size(25)
        self.multi_cell(w, 25, txt, align=align)

    def h3(self, w, txt, x=0, y=0, align=""):
        self.set_x(15)
        if not (x==0 and y == 0):
            self.set_xy(x, y)

        self.set_font_size(21)
        self.multi_cell(w, 21, txt, align=align)

    def h4(self, w, txt, x=0, y=0, align=""):
        self.set_x(15)
        if not (x==0 and y == 0):
            self.set_xy(x, y)

        self.set_font_size(18)
        self.multi_cell(w, 18, txt, align=align)

    def h5(self, w, txt, x=0, y=0, align=""):
        self.set_x(15)
        if not (x==0 and y == 0):
            self.set_xy(x, y)

        self.set_font_size(11)
        self.multi_cell(w, 11, txt, align=align)

    def average(self, offset=0):
        if self.format == "year":
            year = self.year+offset
            num_pomodori = sum(self.df.pomodori[self.df.data.dt.to_period('Y').dt.to_timestamp() == pd.to_datetime(f'01-01-{year}')])
            num_giorni = len(pd.date_range(f"01-01-{year}", f"12-31-{year}", freq="D"))
        
        elif self.format == "month":
            month = self.month_num+offset
            year = self.year
            while month <= 0:
                month += 12
                year -= 1
            last_day = monthrange(year, month)[1]

            num_pomodori = sum(self.df.pomodori[self.df.data.dt.to_period('M').dt.to_timestamp() == pd.to_datetime(f'{month}-01-{year}')])
            num_giorni = len(pd.date_range(f"{month}-01-{year}", f"{month}-{last_day}-{year}", freq="D"))
        
        elif self.format == "degree":
            num_pomodori = sum(self.df.pomodori)
            num_giorni = len(pd.date_range(f"7-12-2021", f"7-18-2024", freq="D"))
        
        return round(num_pomodori/num_giorni, 2)

    def plot_number_of_messages(self, x:int, y:int, w:int=HALF) -> None: 
        # DESCRIPTION: create plot in which are displayed the number of messages sent in a given timeframe (from days to years), and add it to PDF
        # PARAMETERS: pos ("left"/"right") = position in the pdf | interval (day/week/month) = interval messages are stored
        self.prep()

        
        if self.format == "month":
            x_pos = pd.date_range(f"{self.month_num}-01-{self.year}", f"{self.month_num}-{self.last_day}-{self.year}", freq="D") # Getting range of all dates from first message to today 
        elif self.format == "year":
            x_pos = pd.date_range(f"01-01-{self.year}", f"12-31-{self.year}", freq="D")
        elif self.format == "degree":
            x_pos = pd.date_range(f"7-12-2021", f"7-18-2024", freq="W")
        
        roll = [sum(self.df.pomodori[self.df.data == f"{self.month_num if self.format =='month' else '01'}-01-{self.year}"]) / (7 if self.format == "degree" else 1)]*(3 if self.format=="month" else 5)
        
        y_pos = []
        rolling_averages = []


        for i in x_pos: # Getting the points
            if self.format == "month" or self.format == "year":
                point = sum(self.df.pomodori[self.df.data == i])
            else:
                point = sum(self.df.pomodori[(self.df.data.dt.isocalendar().week == i.weekofyear) & (self.df.data.dt.year == i.year)]) // 7
            roll = roll[1:]+[point]
            rolling_averages.append(sum(roll)/len(roll))
            y_pos.append(point)
        
        
        if w == FULL:
            plt.figure(figsize=(11, 5))

        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
        
        if self.format == "month":
            width = 1
        if self.format == "year":
            width = 1.5
        if self.format == "degree":
            width = 3   
        plt.bar(x_pos, y_pos, color="#f35243", alpha=0.75, width=width) # Plotting       
        plt.plot(x_pos, rolling_averages, color="#f3437d", linewidth=2)
        
        if self.format == "month":
            plt.xticks(x_pos, [i.strftime("%d") for i in x_pos])
        elif self.format == "year":
            plt.xticks(x_pos, ["" if int(i.strftime("%d")) != 1 else i.strftime("%m") for i in x_pos])
        elif self.format == "degree":
            plt.xticks(x_pos, ["" for i in x_pos])
            pass
        
        plt.axhline(y=sum(y_pos)/len(y_pos), color="r", linestyle="--")
        plt.grid(axis="y")
        plt.ylim(0)

        if self.format == "degree":
            for i in [pd.to_datetime("01-01-2022"), pd.to_datetime("01-01-2023"), pd.to_datetime("01-01-2024")]:
                plt.axvline(x=i, color="black", linestyle="-.")
            for i in [pd.to_datetime("20-08-2021"), pd.to_datetime("07-02-2022"), pd.to_datetime("07-02-2023"), pd.to_datetime("06-02-2024")]:
                plt.text(i, max(y_pos)*0.95, str(i.year), color='black', ha='center', va='bottom')

        plt.title("Numero di pomodori al giorno")    
        
        plt.savefig(str(self.counter), transparent=True)
        self.add_image(x, y, w)
    

    def last_period(self, x:int, y:int, w:int=HALF, return_to:int=3) -> None:
        self.prep()
        

        end = pd.to_datetime(f'{self.month_num if self.format=="month" else "01"}-01-{self.year}')
        start = end
        for _ in range(return_to):
            if self.format == "month":
                start = start.replace(day=1) - timedelta(days=1)
            elif self.format == "year":
                start = start.replace(day=1, month=1) - timedelta(days=1)
            elif self.format == "degree":
                start = start.replace(day=1, month=1) - timedelta(days=1)

        if self.format == "degree":
            x_pos = [pd.to_datetime('2021-07-12'),pd.to_datetime('2022-07-12'), pd.to_datetime('2023-07-12')]
        else:
            x_pos = pd.date_range(start, end, freq="MS" if self.format == "month" else "YS")
        y_pos = []

        for i in x_pos: # Getting the points
            if self.format == "degree":
                point = sum(self.df.pomodori[(self.df.data >= i) & (self.df.data < i + pd.DateOffset(years=1))])
            else:
                point = sum(self.df.pomodori[self.df.data.dt.to_period('M' if self.format=="month" else 'Y').dt.to_timestamp() == i])
            y_pos.append(point)

        if w == FULL:
            plt.figure(figsize=(11, 5))

        barlist = plt.bar(x_pos, y_pos, color="#f35243", width=20 if self.format=="month" else 240) # Plotting
        
        if (self.format == "degree"):
            m, mi = y_pos[0], 0
            M, Mi = y_pos[0], 0
            for i in range(len(x_pos)):
                if (y_pos[i] < m):
                    m = y_pos[i]
                    mi = i
                if (y_pos[i] > M):
                    M = y_pos[i]
                    Mi = i
            barlist[mi].set_color("m")
            barlist[Mi].set_color("g")

        else:
            barlist[-1].set_color("g" if y_pos[-1] >= y_pos[-2] else "m")

        if self.format == "month":
            plt.xticks(x_pos, [self.month_dict[int(i.strftime("%m"))] for i in x_pos])
        elif self.format == "year":
            plt.xticks(x_pos, [i.strftime("%Y") for i in x_pos])
        elif self.format == "degree":
            plt.xticks(x_pos, [i.strftime("%y")+"/"+str(int(i.strftime("%y"))+1) for i in x_pos])

        plt.grid(axis="y")

        plt.title(f"Numero di pomodori negli ultimi {'mesi' if self.format=='month' else 'anni'}", pad=10) 

        plt.savefig(str(self.counter), transparent=True)
        self.add_image(x, y, w)

        if self.format == "degree":
            return round(sum(y_pos) / len(y_pos), 2)
    
    
    def confront_months(self, x:int, y:int, w:int=HALF, return_to:int=1):
        self.prep()


        x_pos = []

        if self.format == "month":
            year = self.year-return_to-1
            for _ in range(return_to+1):
                year += 1
                x_pos.append(pd.to_datetime(f'{self.month_num}-01-{year}'))
        elif self.format == "year":
            x_pos = [pd.to_datetime(f'{i}-01-{self.year}') for i in range(1, 12+1)]
        elif self.format == "degree":
            start_month = 7
            for year in range(2021, 2024+1):
                for month in range(start_month, 12+1):
                    if (month == 8) and (year == 2024):
                        break
                    x_pos.append(pd.to_datetime(f'{month}-01-{year}'))
                start_month = 1


        y_pos = []

        for i in x_pos: # Getting the points
            point = sum(self.df.pomodori[self.df.data.dt.to_period('M').dt.to_timestamp() == i])
            y_pos.append(point)
        
        if w == FULL:
            plt.figure(figsize=(11, 5))

        if self.format == "month":
            barlist = plt.bar(x_pos, y_pos, color="#f35243", width=250) # Plotting
            barlist[-1].set_color("g" if y_pos[-1] >= y_pos[-2] else "m")
            plt.xticks(x_pos, [i.strftime("%Y") for i in x_pos])
            plt.title("Numero di pomodori negli ultimi anni", pad=10)
        
        else:
            barlist = plt.bar(x_pos, y_pos, color="#f35243", width=20)
            barlist[y_pos.index(max(y_pos))].set_color("g")
            barlist[y_pos.index(min(y_pos))].set_color("m")
            if (self.format == "year"):
                plt.xticks(x_pos, [i.strftime("%m") for i in x_pos])
            else:
                plt.xticks(x_pos, [i.strftime("%m") if int(i.strftime("%m"))%3 == 0 else "" for i in x_pos])
                for i in [pd.to_datetime("01-01-2022"), pd.to_datetime("01-01-2023"), pd.to_datetime("01-01-2024")]:
                    plt.axvline(x=i, color="black", linestyle="-.")
                for i in [pd.to_datetime("20-08-2021"), pd.to_datetime("07-02-2022"), pd.to_datetime("07-02-2023"), pd.to_datetime("06-02-2024")]:
                    plt.text(i, max(y_pos)*0.95, str(i.year), color='black', ha='center', va='bottom')

            plt.title("Numero di pomodori per ogni mese")

        plt.ylim(0)
        plt.grid(axis="y")
        
        
        plt.savefig(str(self.counter), transparent=True)
        self.add_image(x, y, w)
        if self.format == "month":
            return y_pos[-1], y_pos[-2]
        elif self.format == "year":
            return (x_pos[y_pos.index(max(y_pos))].strftime("%b"), max(y_pos)), (x_pos[y_pos.index(min(y_pos))].strftime("%b"), min(y_pos))
        else:
            return (x_pos[y_pos.index(max(y_pos))].strftime("%m/%y"), max(y_pos)), (x_pos[y_pos.index(min(y_pos))].strftime("%m/%y"), min(y_pos))


    def best_streak(self, x:int, y:int, w:int=HALF) -> tuple:
        self.prep()

        best = []
        counter = []
        temp = pd.to_datetime(f"{self.month_num}-01-{self.year}")
        for _ in range(self.last_day):
            if len(self.df[self.df.data == temp]) == 0:
                if len(counter) > len(best):
                    best = counter
                counter = []
            else:
                counter.append((int(temp.strftime("%m")), int(temp.strftime("%d"))))
            temp += timedelta(days=1)

        plot_calendar(self.year, self.month_num, True, best)
        
        plt.savefig(str(self.counter), transparent=True)
        self.add_image(x, y, w)

        if len(best) == 0:
            return (0, "00/00/00"), (0, "00/00/00"), 0
        
        return best[0], best[-1], len(best)
                
      

    def plot_day_of_the_week(self, x, y, w:int=HALF) -> tuple: # DESCRIPTION: Plotting number of messages sent per weekday
        self.prep()

        weekday = {"en":["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                   "it":["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]}
        if self.format == "month":            
            curr_df = self.df[self.df.data.dt.to_period('M').dt.to_timestamp() == pd.to_datetime(f'{self.month_num}-01-{self.year}')]
        elif self.format == "year":
            curr_df = self.df[self.df.data.dt.to_period('Y').dt.to_timestamp() == pd.to_datetime(f'01-01-{self.year}')]
        elif self.format == "degree":
            curr_df = self.df

        y_pos = [sum(curr_df.pomodori[curr_df.data.dt.day_name() == i]) for i in weekday["en"]]

        spider_plot(weekday["it"], y_pos)
        plt.title("Numero di pomodori per giornata")

        plt.savefig(str(self.counter), transparent=True)
        self.add_image(x, y, w)

        tuple_values= sorted(zip(weekday["it"], y_pos), key=lambda x:x[1])
        weekend = sum([j if i in ["Sabato", "Domenica"] else 0 for i, j in tuple_values])
        
        worst, best = tuple_values[0], tuple_values[-1]
        return worst, best, weekend


    def plot_time_of_messages(self, x, y, w:int=HALF): # DESCRIPTION: Plot number of messages per time period
        # PARAMETERS: pos ("left"/"right") = position in the pdf
        self.prep()

        if self.format == "month":
            slotted_dict = get_time_dict(self.df[self.df.data.dt.to_period('M').dt.to_timestamp() == pd.to_datetime(f'{self.month_num}-01-{self.year}')])
        elif self.format == "year":
            slotted_dict = get_time_dict(self.df[self.df.data.dt.to_period('Y').dt.to_timestamp() == pd.to_datetime(f'01-01-{self.year}')])
        elif self.format == "degree":
            slotted_dict = get_time_dict(self.df)

        slotted_dict = {f"{'0' if i < timedelta(hours=10) else ''}{str(i)[:-3]}":j for i,j in slotted_dict.items()} # Changing xticks to make them easier to look at in plot
        
        dates = list(slotted_dict.keys())[6:]+list(slotted_dict.keys())[:6]
        pomodori = list(slotted_dict.values())[6:]+list(slotted_dict.values())[:6]

        plt.plot_date(dates, pomodori, color="#f35243")
        plt.grid(axis="y")
        plt.fill_between(dates, pomodori, color="#fedfbe")

        N=6 # Spacing xticks to avoid overlapping
        
        x_pos = [dates[i] if not i%N else "" for i in range(len(dates))]
        plt.xticks(x_pos)
        plt.title("Numero di pomodori per periodo del giorno")
        plt.ylim(0)

        plt.savefig(str(self.counter), transparent=True)
        self.add_image(x, y, w)
        slotted_dict = sort_dict(slotted_dict, reverse=True, others=False)
        night_hours = sum(slotted_dict[i] for i in [f"0{i//2}:{3*(i%2)}0" for i in range(0, 10)])

        worst, best = list(slotted_dict.items())[0], list(slotted_dict.items())[-1]
        return worst, best, night_hours



    def plot_classes(self, x, y, w:int=HALF) -> None: # DESCRIPTION: Plotting number of messages sent per weekday
        self.prep()

        if self.format == "month":
            curr_df = self.df[self.df.data.dt.to_period('M').dt.to_timestamp() == pd.to_datetime(f'{self.month_num}-01-{self.year}')]
        elif self.format == "year":
            curr_df = self.df[self.df.data.dt.to_period('Y').dt.to_timestamp() == pd.to_datetime(f'01-01-{self.year}')]
        elif self.format == "degree":
            curr_df = self.df

        
        x_pos = curr_df.materia.unique()
        y_pos = [sum(curr_df.pomodori[curr_df.materia == i]) for i in x_pos]
        x_pos = [add_nl(i) for i in  curr_df.materia.unique()]
        
        if self.format == "month":
            if len(y_pos) == 0:
                patches, texts, autotexts = plt.pie([1], labels=["0"], colors=COLORS, textprops={"fontsize":16},
                                            autopct=lambda x: f"0 pomodori",
                                            wedgeprops={"edgecolor":"k",'linewidth': 3})    

            patches, texts, autotexts = plt.pie(y_pos, labels=x_pos, colors=COLORS, textprops={"fontsize":16},
                                        autopct=lambda x: f"{int(round((x/100)*sum(y_pos), 0))} pomodori\n({round(x, 2)}%)" if x > 10 else "",
                                        wedgeprops={"edgecolor":"k",'linewidth': 3})    
            for text in texts:
                text.set_fontsize(20)
        else:
            plt.bar(list(range(len(y_pos))), y_pos, color=COLORS, edgecolor="black")
            offset = y_pos.index(max(y_pos))
            for i in range(len(y_pos)):
                num, txt = y_pos[i], x_pos[i]
                align = list(range(len(y_pos)))[i] - (0.09*len(txt[:txt.find("\n")]))
                plt.text(list(range(len(y_pos)))[i] - (0.25 if len(str(num)) == 2 else 0.35), num-max(y_pos)*7//100, str(num))
                plt.text(align, num+max(y_pos)*1//100, str(txt) if (i+offset)%2 else "", fontsize=18)
            plt.xticks(list(range(len(y_pos))), [x_pos[i] if (i+offset+1)%2 else "" for i in range(len(x_pos))], fontsize=16)

        plt.title("Numero di pomodori per materia")
        plt.savefig(str(self.counter), transparent=True, bbox_inches='tight' if self.format == "year" else "")
        self.add_image(x, y, w)

    def plot_type_of_study(self, x, y, w:int=HALF) -> None:
        self.prep()

        if self.format == "month":
            curr_df = self.df[self.df.data.dt.to_period('M').dt.to_timestamp() == pd.to_datetime(f'{self.month_num}-01-{self.year}')]
        elif self.format == "year":
            curr_df = self.df[self.df.data.dt.to_period('Y').dt.to_timestamp() == pd.to_datetime(f'01-01-{self.year}')]
        elif self.format == "degree":
            curr_df = self.df
        
        x_pos = curr_df.tipo.unique()
        y_pos = [sum(curr_df.pomodori[curr_df.tipo == i]) for i in x_pos]

        if len(y_pos) == 0:
            patches, texts, autotexts = plt.pie([1], labels=["0"], colors=COLORS, textprops={"fontsize":16},
                                        autopct=lambda x: f"0 pomodori",
                                        wedgeprops={"edgecolor":"k",'linewidth': 3})    

        patches, texts, autotexts = plt.pie(y_pos, labels=x_pos, colors=COLORS, textprops={"fontsize":16},
                                    autopct=lambda x: f"{int(round((x/100)*sum(y_pos), 0))} pomodori\n({round(x, 2)}%)" if x > 15 else "",
                                    wedgeprops={"edgecolor":"k",'linewidth': 3}) 
        for text in texts:
            text.set_fontsize(20)   

        plt.title("Numero di pomodori per tipo di studio")
        plt.savefig(str(self.counter), transparent=True)
        self.add_image(x, y, w)

    def time_pivot_table(self, x, y, w):
        self.prep()

        if self.format == "month":
            curr_df = self.df[self.df.data.dt.to_period('M').dt.to_timestamp() == pd.to_datetime(f'{self.month_num}-01-{self.year}')]
        elif self.format == "year":
            curr_df = self.df[self.df.data.dt.to_period('Y').dt.to_timestamp() == pd.to_datetime(f'01-01-{self.year}')]
        elif self.format == "degree":
            curr_df = self.df

        times = [timedelta(hours=i//2, minutes=30*(i%2)) for i in range(0, 48)]
        times = times[6:]+times[:6]

        weekday = {"en":["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                   "it":["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]}
        
        weekdays = weekday["it"]*len(times)

        times = times*len(weekday["it"])

        time_weekday_dict = get_time_dict(curr_df, weekday=True)
        
        pomodori = []
        for i in range(len(times)):
            if (weekday["en"][i%7], times[i]) in time_weekday_dict:
                pomodori.append(time_weekday_dict[(weekday["en"][i%7], times[i])])
            else:
                pomodori.append(0)
        
        pivot = pd.DataFrame({"Giornata":weekdays, "Orario":times, "Pomodori":pomodori})

        pivot = pd.pivot_table(pivot, values='Pomodori', columns='Orario', index='Giornata')

        sorted_days = weekday["it"]
        pivot = pivot.reindex(sorted_days)

        sorted_columns = sorted(pivot.columns, key=lambda x: (x - pd.to_timedelta('03:00:00')) % pd.Timedelta(days=1))

        pivot = pivot[sorted_columns]


        
        fig, ax = plt.subplots(figsize=(11, 4))

        ax.matshow(pivot, cmap='inferno', aspect=1.5)
        

        # Customize the plot
        plt.yticks(np.arange(len(pivot.index)), pivot.index)

        plt.xticks(np.arange(len(pivot.columns)), [str(pivot.columns[i])[7:12] if i%2 == 0 else "" for i in range(len(pivot.columns))], rotation=90)

        plt.title("Numero di pomodori per periodo della giornata")

        plt.savefig(str(self.counter), transparent=True)
        self.add_image(x, y, w)


    def report_materia(self, materia):
        self.prep()

        nomignoli = {"Algoritmi e Principi dell'Informatica":"Algoritmi e Principi di Inf.",
                     "Progetto di Ingegneria Informatica":"Progetto di Ing. Inf.",
                     "Geometria e Algebra Lineare":"Geometria e Algebra Lin.",
                     "Architettura dei calcolatori":"Arch. dei Calcolatori e S.O."}

        if materia in nomignoli:
            self.add_new_page(nomignoli[materia])
        else:
            self.add_new_page(materia)

        if self.format == "month":
            curr_df = self.df[self.df.data.dt.to_period('M').dt.to_timestamp() == pd.to_datetime(f'{self.month_num}-01-{self.year}')]
        elif self.format == "year":
            curr_df = self.df[self.df.data.dt.to_period('Y').dt.to_timestamp() == pd.to_datetime(f'01-01-{self.year}')]
        elif self.format == "degree":
            curr_df = self.df
        
        curr_df = curr_df[curr_df.materia == materia]

        riga = self.voti[self.voti.materia == materia]
        if riga.size != 0:
            _, voto, cfu, anno, sem, prof, tipo, colore, appunti = riga.values[0]
        else:
            voto, anno, cfu, sem, prof, tipo, colore, appunti = 0, "Primo", "Primo", "0", "BO", "matematica", "bianco", 0

        self.h2(WIDTH, x=15, y=30, txt=f"{anno} anno - {sem} Semestre")
        self.h2(WIDTH, x=15, y=40, txt=f"Prof. {prof} - {cfu} cfu")

        border_colors = {"verde": (0, 255, 0), "viola":(255, 0, 255), "blu":(0, 0, 255), "bianco":(0, 0, 0)} 
        r, g, b = border_colors[colore]
        self.set_draw_color(r, g, b)
        self.rect(x=155, y=45, w=40, h=40, round_corners=True)
        self.image(f"images/{tipo}.png", x=160, y=50, w=30, h=30)

        self.h0(w=2*WIDTH//3, x=0, y=50, txt="Voto finale: " + str(voto), align="C")
        
        self.image("images/quadrilatero.png", x=0, y=95, w=WIDTH, h=HEIGHT//4+5)

        min_date = min(curr_df.data)
        max_date = max(curr_df.data) 

        x_pos = pd.date_range(min_date.strftime('%m-%d-%Y'), max_date.strftime('%m-%d-%Y'), freq="D")

        roll = [sum(curr_df.pomodori[self.df.data == min_date])*3]
        
        y_pos = []
        rolling_averages = []


        for i in x_pos: # Getting the points
            point = sum(curr_df.pomodori[curr_df.data == i])
            roll = roll[1:]+[point]
            rolling_averages.append(sum(roll)/len(roll))
            y_pos.append(point)

        plt.figure(figsize=(11, 5))
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.bar(x_pos, y_pos, color="#f35243", alpha=0.75, width=2) # Plotting      
        plt.plot(x_pos, rolling_averages, color="#f3437d")

        plt.xticks(x_pos, [x_pos[i].strftime("%d-%m-%y") if (i == 0 or i == len(x_pos)-1) else "" for i in range(len(x_pos))])
        
        plt.axhline(y=sum(y_pos)/len(y_pos), color="r", linestyle="--")
        plt.grid(axis="y")
        plt.ylim(0)
        plt.title("Numero di pomodori al giorno")    
        
        plt.savefig(str(self.counter), transparent=True)
        self.add_image(0, 100, FULL)       

        num_pomodori = sum(curr_df.pomodori)
        self.h1(WIDTH, x=0, y=170, txt=f"Ho studiato per {num_pomodori} pomodori!", align="C")
        self.h4(WIDTH, x=0, y=185, txt = f"(corrispondono a {round(num_pomodori*25/60,2)} ore!)", align="C")
        
        self.set_draw_color(0, 0, 0)
        self.line(x1=0, y1=200, x2=250, y2=200)

        self.prep()
        x_pos = curr_df.tipo.unique()
        y_pos = [sum(curr_df.pomodori[curr_df.tipo == i]) for i in x_pos]

        if len(y_pos) == 0:
            _, texts, _ = plt.pie([1], labels=["0"], colors=COLORS, textprops={"fontsize":16},
                                        autopct=lambda x: f"0 pomodori",
                                        wedgeprops={"edgecolor":"k",'linewidth': 3})    

        _, texts, _ = plt.pie(y_pos, labels=x_pos, colors=COLORS, textprops={"fontsize":16},
                                    autopct=lambda x: f"{int(round((x/100)*sum(y_pos), 0))} pomodori\n({round(x, 2)}%)" if x > 15 else "",
                                    wedgeprops={"edgecolor":"k",'linewidth': 3}) 
        for text in texts:
            text.set_fontsize(20)   

        plt.title("Numero di pomodori per tipo di studio")
        plt.savefig(str(self.counter), transparent=True)

        self.add_image(x=110, y=210, w=HALF)

        self.h3(WIDTH, x=20, y=215, txt=f"° Qualità appunti: {appunti} / 5.0")

        voto_int = int(voto) if voto != "30L" else 30

        self.h3(WIDTH, x=20, y=235, txt=f"° Qualità studio: {round(num_pomodori/voto_int, 2)}")
        self.h4(WIDTH, x=73, y=236.5, txt="# pomodori / 1 voto")

        sessioni = [
        ("01-01-2022", "15-02-2022"),
        ("01-06-2022", "15-07-2022"),
        ("01-01-2023", "15-02-2023"),
        ("01-06-2023", "15-07-2023"),
        ("01-01-2024", "15-02-2024"),
        ("01-06-2024", "15-07-2024"),
        ]

        sessioni = [(pd.to_datetime(start, dayfirst=True), pd.to_datetime(end, dayfirst=True)) for start, end in sessioni]

        in_sessione = 0
        for _, i in curr_df.iterrows():
            for start, end in sessioni:
                if start <= i.data and i.data <= end:
                    in_sessione += i.pomodori
                    break

        self.h3(WIDTH, x= 20, y=255, txt=f"° Pomodori in sessione: {int(100*round(in_sessione/num_pomodori, 2))}%")


    def report_progetti(self, y, nome1, nome2, github):

        self.image("images/quadrilatero.png", x=THIRD, y=y, w=THIRD, h=50)

        self.line(x1=0, y1=y, x2=WIDTH, y2=y)

        self.h2(w=FULL, x=5, y=y+2, txt=nome1, align="C")
        self.h2(w=FULL, x=5, y=y+12, txt=nome2, align="C")

        self.h4(w=THIRD-10, x=THIRD+10, y=y+30, txt=github, align="C")
        self.image("images/github.png", x=THIRD+30-len(github)-1, y=y+34.5, w=7.5, h=7.5)
        self.link(w=THIRD, x=THIRD, y=y+33, h=10, link=f"https://github.com/Crippius/{github}")


        progetto = f"Progetto di {nome1} {nome2}"
        self.h3(w=THIRD, x=0, y=y, txt=f"Prof. {self.voti[self.voti.materia == progetto].iloc[0].prof}", align="C")
        self.h3(w=THIRD, x=0, y=y+13, txt=f"{self.voti[self.voti.materia == progetto].iloc[0].cfu} cfu", align="C")

        self.set_font(style="U")
        self.h1(w=THIRD, x=0, y=y+23, txt=f"Voto: {self.voti[self.voti.materia == progetto].iloc[0].voto}", align="C")
        self.set_font(style="")

        num_pomodori = sum(self.df[(self.df.materia == f"{nome1} {nome2}") & (self.df.tipo == "PROGETTO")].pomodori)
        
        self.h4(w=THIRD, x=2*THIRD, y=y+2, txt=f"Pomodori totali:", align="C")
        self.h1(w=THIRD, x=2*THIRD, y=y+10, txt=f"{num_pomodori}", align="C")
        self.h4(w=THIRD, x=2*THIRD, y=y+30, txt=f"({round(num_pomodori*25/60, 2)} ore!)", align="C")

        self.line(x1=0, y1=y+50, x2=WIDTH, y2=y+50)

    

    def add_last_page(self):

        self.add_page()

        self.image('images/background.png', x=0, y=0, w = WIDTH, h = HEIGHT)

        self.image('images/pomodoro.png', x=HALF//2-4, y=30, w=120)

        self.set_font_size(80)
        self.set_text_color(255, 255, 255)
        self.set_y(105)
        self.multi_cell(w=WIDTH-18, txt="Keep\ncalm", align="C")
        self.set_y(165)
        self.set_font_size(35)
        self.multi_cell(w=WIDTH-18, txt="and", align="C")
        self.set_y(180)
        self.set_font_size(80)
        self.multi_cell(w=WIDTH-18, txt="pomodora\na manetta", align="C")

        self.set_auto_page_break(False)
        self.set_xy(0, -30)
        self.set_font_size(20)
        self.multi_cell(FULL, 10, "Tommaso Crippa\nThe Pomodoro Technique", align="R")
        self.set_text_color(0, 0, 0)
    
    def save(self, dir="", title="") -> None: # DESCRIPTION: Save file if nothing has gone wrong, remove images created
        self.prep(plot=False)

        self.add_last_page()

        if dir == "":
            self.dir = f"pdfs/{self.year}"
        else:
            self.dir = dir

        if title != "":
            self.filename = title

        self.output(f'{self.filename}')

        move(f'{self.filename}', f'{self.dir}/{self.filename}.pdf') 
        while self.counter != 0: # Remove the images created
            if path.exists(f"{self.counter}.png"):
                remove(f"{self.counter}.png")
            self.counter -= 1