import feedparser
import numpy
import time
import os
import sys
from git import Repo
from datetime import datetime

shows_list = []
old_shows_list = []

h2 = "## "
h3 = "### "
dblel = "\n\n"
hoz_sep = "|"
vert_head = "|Show|Total Length|Number of Shows|Average Length|Average Gap|Standard Deviation|Shows Per Year|Monthly Show Output|"
vert_sep = "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"
vert_head_old = "|Show|Total Length|Number of Shows|Average Length|"
vert_sep_old = "|:---:|:---:|:---:|:---:|"

show_output = []
old_show_output = []
summary_output = []
new_show_output = []
shows_Checked = []

intervals = (
    ('years', 31536000),
    #('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('mins', 60),
    ('secs', 1),
    )

class Show:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


def display_time(seconds, granularity=2):
    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{:.0f} {}".format(value, name))
    return ' '.join(result[:granularity])

def parse_feed(feed_name):
    base_feed = 'https://www.relay.fm/'
    end_feed = '/feed'
    total_feed = base_feed + feed_name + end_feed
    d = feedparser.parse(total_feed)    
    ents = d['entries']
    total_len = 0
    num_shows = len(ents)
    for e in ents:
        length = e['itunes_duration']
        total_len += int(float(length)) #1
    old_show_output.append("|**" + d['feed']['title'] + "**|")
    old_show_output.append(display_time(total_len,4) + "|")
    old_show_output.append(str(num_shows) + "|")
    avg = total_len / num_shows
    old_show_output.append(display_time(avg,4) + "|\n")
    return total_len

def parse_prediction_feed(feed_name, last_checked):
    base_feed = 'https://www.relay.fm/'
    end_feed = '/feed'
    total_feed = base_feed + feed_name + end_feed
    d = feedparser.parse(total_feed)    
    ents = d['entries']
    total_len = 0
    num_shows = len(ents)
    time_list = []

    update_needed = False
    s = ents[0]['id']
    s = s.replace("http://relay.fm/", "")
    ss = s.split('/')
    if(len(ss) == 2):
        show_Checked = Show(name=ss[0], episode=ss[1])
        shows_Checked.append(show_Checked)
        if int(ss[1]) > int(last_checked):
            update_needed = True
            print("Update Needed")
    
    for e in ents:
        length = e['itunes_duration']
        if ((e['itunes_episode'] == '39') and (e['id'] == 'http://relay.fm/parallel/39')):
            length = '3929'
        total_len += int(float("".join(length.split()))) #2
        time_list.append(time.mktime(e['published_parsed']))
    time_list = list(reversed(time_list))
    diff_gap = numpy.diff(time_list)
    avg_gap = numpy.average(diff_gap)
    avg_length = total_len / num_shows
    shows_per_year = 31536000 / avg_gap
    yearly_output = avg_length * shows_per_year
    monthly_output = yearly_output / 12
    std_dev = numpy.std(diff_gap)


    show_output.append("|**" + d['feed']['title'] + "**|")
    show_output.append(display_time(total_len, 4) + "|")
    show_output.append(str(num_shows) + "|")
    show_output.append(display_time(avg_length, 4) + "|")
    show_output.append(display_time(avg_gap, 3) + "|")
    show_output.append(display_time(std_dev, 3) + "|")
    show_output.append("{:.1f}".format(shows_per_year) + "|")
    show_output.append(display_time(monthly_output, 4) + "|\n")

    return total_len, yearly_output


def getShows():
    master_Feed = "https://www.relay.fm/master/feed"
    d = feedparser.parse(master_Feed)    
    ents = d['entries']
    newest_Shows = []
    names = []
    for e in ents:
        s = e['id']
        s = s.replace("http://relay.fm/", "")
        ss = s.split('/')
        if(len(ss) == 2):
            showToAdd = Show(name=ss[0], episode=ss[1])
            # Shows are newest first, so duplicates won't be added
            if(ss[0] not in names):
                newest_Shows.append(showToAdd)
            names.append(ss[0])
    return newest_Shows

def readShowList(path):
    old_shows = []
    current_shows = []
    file = open(path + "oldShows.txt", "r")
    for f in file:
        old_shows.append(f.rstrip())
    file = open(path + "currentShows.txt", "r")
    for f in file:
        showInfo = f.rstrip().split(":")        
        if(len(showInfo) == 2):
            showToAdd = Show(name=showInfo[0], lastCheckedEpisode=showInfo[1])            
            current_shows.append(showToAdd)            
    return old_shows, current_shows      

def compareShows(latest_shows, shows_list):
    needs_update = []
    new_shows = []
    for latest in latest_shows:
        showName = latest.name
        found = False
        last_Episode = -1
        for show in shows_list:
            if show.name == showName:
                found = True
                last_Episode = show.lastCheckedEpisode
                break
        if found:
            if int(last_Episode) < int(latest.episode):
                needs_update.append(showName)
        else:
            new_shows.append(showName)
    return needs_update, new_shows

def main():
    now = datetime.now()
    use_git = False
    path = ""
    if len(sys.argv) > 1:
        print("Using Git")
        use_git = True
        path = sys.argv[1] + "/"
        git_repo = Repo(path)
        git_repo.git.pull()

    old_shows_list, shows_list = readShowList(path)
    latest_shows = getShows()
    shows_to_update, new_shows = compareShows(latest_shows, shows_list)

    #sys.exit(0)
    running_total = 0
    yearly_output = 0
    for show in shows_list:
        total, yearly = parse_prediction_feed(show.name, show.lastCheckedEpisode)
        running_total += total
        yearly_output += yearly
    for show in old_shows_list:
        running_total += parse_feed(show)
    time_to_one_year = ((31536000 - running_total)/yearly_output) * 31536000
    summary_output.append(h2 + 'Total shows: ' + str(len(shows_list) + len(old_shows_list)) + dblel)
    summary_output.append(h3 +'Total shows length: ' + display_time(running_total,4) + dblel)

    summary_output.append(h2 + "Total active shows: " + str(len(shows_list)) + dblel)
    summary_output.append(h3 + "Yearly output: " + display_time(yearly_output, 3) + dblel)
    summary_output.append(h3 + "Monthly output: " + display_time(yearly_output/12, 3) + dblel)

    summary_output.append(h2 + "Time untill 1 year of content: " + display_time(time_to_one_year, 2) + dblel)
    summary_output.append("\n-------------------------------------------------\n\n")

    file = 0
    if use_git:
        file = open(path + "docs/index.md","w")
    else:
        file = open("docs/index.md","w")

    for s in summary_output:
        file.write(s)
    file.write("\n")
    file.write(h2 + "Active Shows")
    file.write("\n")
    file.write(vert_head + "\n")
    file.write(vert_sep + "\n")
    for s in show_output:
        file.write(s)
    file.write("\n-------------------------------------------------\n\n")
    file.write(h2 + "Retired Shows")
    file.write("\n")
    file.write(vert_head_old + "\n")
    file.write(vert_sep_old + "\n")
    for s in old_show_output:
        file.write(s)

    for new_show in new_shows:
        file.write("\nNew show needs adding - " + new_show)
    
    current_time = now.strftime("%H:%M:%S %d/%m/%Y")
    file.write("\nGenerated at: " + current_time + "\n")

    file.close()

    if use_git:
        file = open(path + "currentShows.txt","w")
    else:
        file = open("currentShows.txt","w")
    for checked in shows_Checked:
        s = str(checked.name) + ":" + str(checked.episode) + "\n"
        file.write(s)
    file.close()

    if use_git:
        git_repo.git.add('.')
        git_repo.git.commit(m="Updated Relay show stats")
        git_repo.git.push()

    sys.exit(0)

if __name__ == "__main__":
    main()


