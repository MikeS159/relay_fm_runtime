import feedparser
import numpy
import time
import os
import sys
from git import Repo
from datetime import datetime

shows_list = ['adapt', 'analogue', 'automators', 'bonanza', 'b-sides', 'clockwise', 'connected', 'cortex', 'departures', 'focused', 'liftoff', 'mpu', 'makedo', 'material', 'originality', 'parallel', 'pictorial', 'presentable', 'rd', 'remaster', 'roboism', 'rocket', 'penaddict', 'tc', 'topfour', 'radar', 'ungeniused', 'upgrade']

old_shows_list = ['almanac', 'bionic', 'canvas', 'cmdspace', 'disruption', 'download', 'inquisitive', 'isometric', 'ltoe', 'mixedfeelings', 'playingforfun', 'query', 'subnet', 'prompt', 'virtual']

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

intervals = (
    ('years', 31536000),
    #('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('mins', 60),
    ('secs', 1),
    )

def display_time(seconds, granularity=2):
    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{:.0f} {}".format(value, name))
    return ', '.join(result[:granularity])

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
        total_len += int(length)    
    old_show_output.append("|**" + d['feed']['title'] + "**|")
    old_show_output.append(display_time(total_len,4) + "|")
    old_show_output.append(str(num_shows) + "|")
    avg = total_len / num_shows
    old_show_output.append(display_time(avg,4) + "|\n")
    return total_len

def parse_prediction_feed(feed_name):
    base_feed = 'https://www.relay.fm/'
    end_feed = '/feed'
    total_feed = base_feed + feed_name + end_feed
    d = feedparser.parse(total_feed)    
    ents = d['entries']
    total_len = 0
    num_shows = len(ents)
    time_list = []
    for e in ents:
        length = e['itunes_duration']
        total_len += int(length)
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


def main():
    now = datetime.now()
    use_git = False
    if len(sys.argv) > 1:
        print("Using Git")
        use_git = True
        path = sys.argv[1]
        git_repo = Repo(path)
        git_repo.git.pull()

    running_total = 0
    yearly_output = 0
    for show in shows_list:
        total, yearly = parse_prediction_feed(show)
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

        file = open(path + "/docs/index.md","w")
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

    current_time = now.strftime("%d/%m/%Y %H:%M:%S")
    file.write("\nGenerated at: " + current_time + "\n")

    file.close()

    if use_git:
        git_repo.git.add('.')
        git_repo.git.commit(m="Updated Relay show stats")
        git_repo.git.push()

    sys.exit(0)

if __name__ == "__main__":
    main()


