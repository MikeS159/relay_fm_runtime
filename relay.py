import xml.etree.ElementTree as ET
import feedparser
import numpy
import time

shows_list = ['adapt', 'analogue', 'automators', 'bonanza', 'b-sides', 'clockwise', 'connected', 'cortex', 'departures', 'focused', 'liftoff', 'mpu', 'makedo', 'material', 'originality', 'parallel', 'pictorial', 'presentable', 'rd', 'remaster', 'roboism', 'rocket', 'penaddict', 'tc', 'topfour', 'radar', 'ungeniused', 'upgrade']

old_shows_list = ['almanac', 'bionic', 'canvas', 'cmdspace', 'disruption', 'download', 'inquisitive', 'isometric', 'ltoe', 'mixedfeelings', 'playingforfun', 'query', 'subnet', 'prompt', 'virtual']

h2 = "## "
h3 = "### "

intervals = (
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
            result.append("{} {}".format(value, name))
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
    print(h3 +d['feed']['title'] + "\n")
    print(display_time(total_len,5) + "\n")
    print("Number of shows: " + str(num_shows) + "\n")
    avg = total_len / num_shows
    print("Average Length: " + display_time(avg,5) + "\n")
    print("\n-------------------------------------------------\n")
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
    time_list = list(reverse(time_list))
    diff_gap = numpy.diff(time_list)
    avg_gap = numpy.average(diff)
    print(h3 +d['feed']['title'] + "\n")
    print(display_time(total_len,5) + "\n")
    print("Number of shows: " + str(num_shows) + "\n")
    avg = total_len / num_shows
    print("Average Length: " + display_time(avg,5) + "\n")
    print("Average gap: " + display_time(avg_gap, 5) + "\n")
    print("\n-------------------------------------------------\n")
    return total_len


def main():
    running_total = 0    
    for show in shows_list:
        running_total += parse_feed(show)
    for shoe in old_shows_list:
        running_total += parse_feed(show)
    print(h2 + 'Total shows: ' + str(len(shows_list)) + "\n")
    print(h2 +'Total show length ')
    print(h2 + display_time(running_total,5) + "\n")

if __name__ == "__main__":
    main()


