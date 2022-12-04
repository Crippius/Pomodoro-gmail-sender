import pandas as pd # To store all the informations inside a Dataframe
import matplotlib.pyplot as plt # To plot all the data in a meaningful way

from matplotlib import rcParams # To change the font used by matplotliv
import matplotlib.font_manager as fm
from matplotlib.ticker import MaxNLocator

from fpdf import FPDF # To create and deploy the PDF that can later be downloaded

from datetime import date, datetime, timedelta # To manipulate the dates we
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
        if not pd.isnull(row.orario):
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

    def __init__(self, file:str, format:str, month:int=0, year:int=0): 

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
        

        self.month_dict = {1:"Gennaio", 2:"Febbraio", 3:"Marzo", 4:"Aprile", 5:"Maggio", 6:"Giugno", 
                      7:"Luglio", 8:"Agosto", 9:"Settembre", 10:"Ottobre", 11:"Novembre", 12:"Dicembre"}
        self.month = self.month_dict[self.month_num]

        if year != 0:
            self.year = year
        else:
            self.year = datetime.now().year-1 if self.month_num == 12 else datetime.now().year

        self.last_day = monthrange(self.year, self.month_num)[1]

        self.format = format

        FPDF.__init__(self) 

        self.counter = 0

        self.df = pd.read_excel(file) # Creating Dataframe

        self.df.columns = ["data", "materia", "tipo", "pomodori", "orario"]

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
                "seasonal":f"{self.month} {self.year}"} # Needs to change
                
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
        elif self.format == "season":
            self.set_font_size(55)
            self.image(f'images/stagione.png', x = 0, y = 0, w = WIDTH//3, h = HEIGHT)
            self.set_xy(77, 100)
            self.cell(WIDTH, 30, "REPORT STAGIONALE")
            self.set_xy(77, 130)
            self.set_font_size(85)
            self.cell(WIDTH, 40, f"{self.year-1}-{self.year}")
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
        
    
    def h1(self, w, txt, x=0, y=0, align=""):
        self.set_x(15)
        if not (x==0 and y == 0):
            self.set_xy(x, y)

        self.set_font_size(30)
        self.multi_cell(w, 30, txt, align=align)
    
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

    def plot_number_of_messages(self, x:int, y:int, w:int=HALF) -> None: 
        # DESCRIPTION: create plot in which are displayed the number of messages sent in a given timeframe (from days to years), and add it to PDF
        # PARAMETERS: pos ("left"/"right") = position in the pdf | interval (day/week/month) = interval messages are stored
        self.prep()

        
        if self.format == "month":
            x_pos = pd.date_range(f"{self.month_num}-01-{self.year}", f"{self.month_num}-{self.last_day}-{self.year}", freq="D") # Getting range of all dates from first message to today 
        else:
            x_pos = pd.date_range(f"01-01-{self.year}", f"12-31-{self.year}", freq="D")
        
        roll = [sum(self.df.pomodori[self.df.data == f"{self.month_num if self.format =='month' else '01'}-01-{self.year}"])]*(3 if self.format=="month" else 7)
        
        y_pos = []
        rolling_averages = []


        for i in x_pos: # Getting the points

            point = sum(self.df.pomodori[self.df.data == i])
            roll = roll[1:]+[point]
            rolling_averages.append(sum(roll)/len(roll))
            y_pos.append(point)
        
        
        if w == FULL:
            plt.figure(figsize=(11, 5))

        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))

        plt.bar(x_pos, y_pos, color="#f35243", alpha=0.75) # Plotting
        plt.plot(x_pos, rolling_averages, color="#f3437d", linewidth=(2 if self.format == "month" else 1.5))
        
        if self.format == "month":
            plt.xticks(x_pos, [i.strftime("%d") for i in x_pos])
        else:
            plt.xticks(x_pos, ["" if int(i.strftime("%d")) != 1 else i.strftime("%m") for i in x_pos])

        
        plt.axhline(y=sum(y_pos)/len(y_pos), color="r", linestyle="--")
        plt.grid(axis="y")
        plt.ylim(0)

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
            else:
                start = start.replace(day=1, month=1) - timedelta(days=1)

        
        x_pos = pd.date_range(start, end, freq="MS" if self.format == "month" else "YS")
        y_pos = []

        for i in x_pos: # Getting the points
            point = sum(self.df.pomodori[self.df.data.dt.to_period('M' if self.format=="month" else 'Y').dt.to_timestamp() == i])
            y_pos.append(point)

        if w == FULL:
            plt.figure(figsize=(11, 5))

        barlist = plt.bar(x_pos, y_pos, color="#f35243", width=20 if self.format=="month" else 240) # Plotting

        barlist[-1].set_color("g" if y_pos[-1] >= y_pos[-2] else "m")

        if self.format == "month":
            plt.xticks(x_pos, [self.month_dict[int(i.strftime("%m"))] for i in x_pos])
        else:
            plt.xticks(x_pos, [i.strftime("%Y") for i in x_pos])

        plt.grid(axis="y")
        
        plt.title(f"Numero di pomodori negli ultimi {'mesi' if self.format=='month' else 'anni'}", pad=10) 

        plt.savefig(str(self.counter), transparent=True)
        self.add_image(x, y, w)
    
    
    def confront_months(self, x:int, y:int, w:int=HALF, return_to:int=1):
        self.prep()


        x_pos = []

        if self.format == "month":
            year = self.year-return_to-1
            for _ in range(return_to+1):
                year += 1
                x_pos.append(pd.to_datetime(f'{self.month_num}-01-{year}'))
        else:
            x_pos = [pd.to_datetime(f'{i}-01-{self.year}') for i in range(1, 12+1)]

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
            plt.xticks(x_pos, [i.strftime("%m") for i in x_pos])
            plt.title("Numero di pomodori per ogni mese")

        plt.ylim(0)
        plt.grid(axis="y")
        
        
        plt.savefig(str(self.counter), transparent=True)
        self.add_image(x, y, w)
        if self.format == "month":
            return y_pos[-1], y_pos[-2]
        else:
            return (x_pos[y_pos.index(max(y_pos))].strftime("%b"), max(y_pos)), (x_pos[y_pos.index(min(y_pos))].strftime("%b"), min(y_pos))


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
        else:
            curr_df = self.df[self.df.data.dt.to_period('Y').dt.to_timestamp() == pd.to_datetime(f'01-01-{self.year}')]
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
        else:
            slotted_dict = get_time_dict(self.df[self.df.data.dt.to_period('Y').dt.to_timestamp() == pd.to_datetime(f'01-01-{self.year}')])
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
        else:
            curr_df = self.df[self.df.data.dt.to_period('Y').dt.to_timestamp() == pd.to_datetime(f'01-01-{self.year}')]
        
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
        else:
            curr_df = self.df[self.df.data.dt.to_period('Y').dt.to_timestamp() == pd.to_datetime(f'01-01-{self.year}')]
        
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
            dir = "pdfs"
        

        if title != "":
            out = title
        elif self.format == "month":
            out = f"Pomodoro Report - {self.month} {self.year}"
        elif self.format == "year":
            out = f"Pomodoro Report - {self.year}"
        elif self.format == "seasonal":
            out = f"Pomodoro Report - {self.month} {self.year}" # Needs to change
        self.output(f'{out}')
        move(f'{out}', f'{dir}/{out}.pdf')
        while self.counter != 0:
            if path.exists(f"{self.counter}.png"):
                remove(f"{self.counter}.png")
            self.counter -= 1