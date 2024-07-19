# Pomodoro Report Generator 🍅

Personal project to keep track of all the pomodori I completed during my years as a student.

You don't know what the Pomodoro Technique is? Check it out [here](https://www.pomodorotechnique.com/).

## How does it work?

![example](https://imgur.com/JwdRjZo.png)

Every first of the month, at 12:00, My pc's Task Scheduler executes the main.py program, which creates a pdf using the Pomodoro_Constructor class,
commits it into this repo, and sends it as an email attachment to the people interested.

The Pomodoro_Constructor class is in the homonym python file and inherits the FPDF class and expands it with new plot functions to add to the report
and some QOL functions to abstract some boring procedures.
##
#### Check out the latest release [here!](https://github.com/Crippius/pomodoro-report-generator/blob/main/pdfs/Pomodoro%20Report%20-%20The%20Final%20Report.pdf)

All reports are written in Italian since they're created for my personal use but hopefully the visuals help understand what's written

I really think this project helps me be more productive, since even in the days when I feel lazy, 
I convince myself to start studying to make my next report look as good as possible!

Therefore what do I have to say other than...

![Pomodora a manetta](https://imgur.com/2cXlpuY.png)