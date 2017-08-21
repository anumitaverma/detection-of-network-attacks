import re
import numpy as np
import collections
import subprocess
import csv


class Parser:
    def __init__(self):
        self.reg = re.compile(r"^.*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\.")
        self.result_dict = {}
        self.packet_rates = []
        self.unique_ips = []
        self.total_ips = []
        self.shannon_entropy_list = []
        self.produce_txt_files()

    def produce_txt_files(self):
        for i in range(21, 26):
            pkt_rate = subprocess.Popen(
                'capinfos Malware_Project/outside_week_1/outside.tcpdump.' + str(i) + '| grep "Average packet rate" |'
                                                                                    ' awk \'{print $4}\' ',
                stdout=subprocess.PIPE, shell=True)
            pkt_rate_str = str(pkt_rate.communicate()[0])
            self.packet_rates.append(pkt_rate_str)
            subprocess.Popen('tcpdump -qns 0 -X -r /home/urvik/Malware_Project/outside_week_1/outside.tcpdump.' + str(i) +
                             '> /home/urvik/Malware_Project/outside_week_1/outside_tcpdump_' + str(i) + '.txt',
                             shell=True)
        self.parse_data()

    def parse_data(self):
        ct = 0
        for i in range(21, 26):
            print "Iteration: " + str(i)
            filename = open("/home/urvik/Malware_Project/outside_week_1/outside_tcpdump_" + str(i) + ".txt", "r")
            for line in filename:
                internal_result = self.reg.findall(line)
                if internal_result != []:
                    result_string = "" .join(str(val) for val in internal_result)
                    self.result_dict[ct] = result_string
                    ct += 1
                    # result.append(internal_result)

            set_of_list = set(self.result_dict.values())
            print "total ips: " + str(len(self.result_dict.values()))
            print "distinct values:" + str(len(set_of_list))
            self.total_ips.append(len(self.result_dict.values()))
            self.unique_ips.append(len(set_of_list))
            self.shannon_entropy(set_of_list)

    def shannon_entropy(self, set_of_list):
        counter = collections.Counter(set_of_list)
        counts = np.array(counter.values(), dtype=float)
        prob = counts/counts.sum()
        shannon_entropy = (-prob*np.log2(prob)).sum()
        print "Entropy: " + str(shannon_entropy)
        self.shannon_entropy_list.append(shannon_entropy)

parser = Parser()
print parser.packet_rates
print parser.unique_ips
print parser.shannon_entropy_list

rows = zip(parser.total_ips, parser.unique_ips, parser.packet_rates, parser.shannon_entropy_list)
my_file = open("results_1.csv", 'wb')
wr = csv.writer(my_file)
for row in rows:
    wr.writerow(row)
