import feedparser
import numpy
import time
import os
import sys

shows_list = ['adapt', 'analogue', 'automators', 'bonanza', 'b-sides', 'clockwise', 'connected', 'cortex', 'departures', 'focused', 'liftoff', 'mpu', 'makedo', 'material', 'originality', 'parallel', 'pictorial', 'presentable', 'rd', 'remaster', 'roboism', 'rocket', 'penaddict', 'tc', 'topfour', 'radar', 'ungeniused', 'upgrade']

old_shows_list = ['almanac', 'bionic', 'canvas', 'cmdspace', 'disruption', 'download', 'inquisitive', 'isometric', 'ltoe', 'mixedfeelings', 'playingforfun', 'query', 'subnet', 'prompt', 'virtual']

h2 = "## "
h3 = "### "

show_output = []
old_show_output = []
summary_output = []

intervals = (
    ('years', 31536000),
    #('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
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
    old_show_output.append(h3 +d['feed']['title'] + "\n")
    old_show_output.append(display_time(total_len,5) + "\n")
    old_show_output.append("Number of shows: " + str(num_shows) + "\n")
    avg = total_len / num_shows
    old_show_output.append("Average Length: " + display_time(avg,5) + "\n")
    old_show_output.append("\n-------------------------------------------------\n")
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
    show_output.append(h3 +d['feed']['title'] + "\n")
    show_output.append(display_time(total_len,5) + "\n")
    show_output.append("Number of shows: " + str(num_shows) + "\n")
    avg_length = total_len / num_shows
    show_output.append("Average Length: " + display_time(avg_length,5) + "\n")
    show_output.append("Average gap: " + display_time(avg_gap, 5) + "\n")
    shows_per_year = 31536000 / avg_gap
    yearly_output = avg_length * shows_per_year
    monthly_output = yearly_output / 12
    std_dev = numpy.std(diff_gap)
    show_output.append("Standard deviation: " + display_time(std_dev,5) + "\n")
    show_output.append("Shows per year: {:.1f}\n".format(shows_per_year))
    show_output.append("Monthly show output: " + display_time(monthly_output, 5) + "\n")

    show_output.append("\n-------------------------------------------------\n")
    return total_len, yearly_output


def main():
    os.system('git pull')
    running_total = 0
    yearly_output = 0
    for show in shows_list:
        total, yearly = parse_prediction_feed(show)
        running_total += total
        yearly_output += yearly
    for show in old_shows_list:
        running_total += parse_feed(show)
    time_to_one_year = ((31536000 - running_total)/yearly_output) * 31536000
    summary_output.append(h2 + 'Total shows: ' + str(len(shows_list) + len(old_shows_list)) + "\n")
    summary_output.append(h3 +'Total shows length: ' + display_time(running_total,5) + "\n")    

    summary_output.append(h2 + "Total active shows: " + str(len(shows_list)) + "\n")
    summary_output.append(h3 + "Yearly output: " + display_time(yearly_output) + "\n")
    summary_output.append(h3 + "Monthly output: " + display_time(yearly_output/12) + "\n")

    summary_output.append(h2 + "Time untill 1 year of content: " + display_time(time_to_one_year, 2) + "\n")
    summary_output.append("\n-------------------------------------------------\n")

    file = open("README.md","w")
    for s in summary_output:
        file.write(s)
    for s in show_output:
        file.write(s)
    for s in old_show_output:
        file.write(s)
    file.close()

    os.system('git add README.md')
    os.system('git commit -m "Updated Relay show stats"')
    os.system('git push')
    sys.exit(0)

if __name__ == "__main__":
    main()


